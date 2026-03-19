import fitz
import camelot
import pandas as pd
import numpy as np
import os
import re
from collections import defaultdict
from pathlib import Path
from difflib import SequenceMatcher

# =========================
# CONFIGURAÇÕES GERAIS
# =========================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = PROJECT_ROOT / "DOWNLOADS"
PASTA_EDITAIS = BASE_DIR / "EDITAIS"

# ===== LIMPEZA DE RODAPÉ =====
MIN_REPETICAO_PAGINAS = 0.6   # aparece em pelo menos 60% das páginas
SIMILARIDADE_TEXTO = 0.85    # similaridade textual mínima
TOL_Y = 12                   # tolerância vertical (px)
TOL_X = 20                   # tolerância horizontal (px)

# =========================
# UTILIDADES
# =========================
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

# =========================
# ETAPA 1: LIMPEZA DE RODAPÉ
# =========================
def coletar_spans(doc):
    spans_por_pagina = []
    for page in doc:
        spans = []
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    spans.append({
                        "text": span["text"].strip(),
                        "bbox": span["bbox"]
                    })
        spans_por_pagina.append(spans)
    return spans_por_pagina

def agrupar_spans(spans_por_pagina):
    grupos = []
    for page_idx, spans in enumerate(spans_por_pagina):
        for span in spans:
            if not span["text"]:
                continue
            
            x0, y0, x1, y1 = span["bbox"]
            inserido = False

            for grupo in grupos:
                g = grupo["ref"]
                gx0, gy0, gx1, gy1 = g["bbox"]

                if (
                    abs(y0 - gy0) <= TOL_Y and
                    abs(x0 - gx0) <= TOL_X and
                    similar(span["text"], g["text"]) >= SIMILARIDADE_TEXTO
                ):
                    grupo["ocorrencias"].append((page_idx, span))
                    inserido = True
                    break

            if not inserido:
                grupos.append({
                    "ref": span,
                    "ocorrencias": [(page_idx, span)]
                })
    return grupos

def identificar_rodapes(grupos, total_paginas):
    rodapes = []
    for grupo in grupos:
        paginas = {p for p, _ in grupo["ocorrencias"]}
        repeticao = len(paginas) / total_paginas
        if repeticao >= MIN_REPETICAO_PAGINAS:
            rodapes.append(grupo)
    return rodapes

def remover_rodapes(doc, rodapes):
    for grupo in rodapes:
        for page_idx, span in grupo["ocorrencias"]:
            page = doc[page_idx]
            rect = fitz.Rect(span["bbox"])
            page.add_redact_annot(rect, fill=(1, 1, 1))

    for page in doc:
        page.apply_redactions()

def limpar_pdf_rodape_intencional(pdf_entrada, pdf_saida):
    doc = fitz.open(pdf_entrada)
    total_paginas = len(doc)

    print(f"    Total de páginas: {total_paginas}")

    spans_por_pagina = coletar_spans(doc)
    grupos = agrupar_spans(spans_por_pagina)
    rodapes = identificar_rodapes(grupos, total_paginas)

    if rodapes:
        print(f"    [+] Grupos de rodapé identificados: {len(rodapes)}")
        remover_rodapes(doc, rodapes)
    else:
        print("    [!] Nenhum rodapé identificado para remoção (mas será copiado limpo).")
    
    # Salvar doc limpando/copiando.
    doc.save(pdf_saida)
    print(f"    [+] PDF sem rodapés em: {pdf_saida.name}")
    doc.close()

# =========================
# ETAPA 2: EXTRAÇÃO DE TABELAS
# =========================
def clean_cell(cell):
    if cell is None or str(cell).strip() == '':
        return ""
    return re.sub(r"\s+", " ", str(cell)).strip()

def is_item_start(cell):
    if not cell:
        return False
    cell = str(cell).strip()
    if re.match(r"^\d+\b", cell):
        return True
    if re.match(r"^ITEM\s*\d+", cell, re.IGNORECASE):
        return True
    return False

def extract_tables_with_camelot(pdf_path):
    print(f"    📄 Extraindo tabelas com Camelot...")
    tables = camelot.read_pdf(str(pdf_path), pages='all', flavor='lattice')
    all_rows = []
    for table in tables:
        df = table.df
        for _, row in df.iterrows():
            cleaned_row = [clean_cell(cell) for cell in row]
            if any(cleaned_row):
                all_rows.append(cleaned_row)
                
    print(f"    ✅ Total de linhas extraídas: {len(all_rows)}")
    return all_rows

def group_items(rows):
    items = []
    current_item = None
    for row in rows:
        first_cell = row[0] if row else ""
        if is_item_start(first_cell):
            if current_item:
                items.append(current_item)
            current_item = row.copy()
        else:
            if current_item:
                current_item = [a + " " + b if a and b else a or b for a, b in zip(current_item, row)]
    if current_item:
        items.append(current_item)
    return items

def export_items(items, output_path):
    if not items:
        print("    ⚠️ Nenhum item identificado. Arquivo Excel não gerado.")
        return False

    max_cols = max(len(i) for i in items)
    normalized = []
    for item in items:
        row = item + [""] * (max_cols - len(item))
        normalized.append(row)

    df = pd.DataFrame(normalized)
    df.to_excel(output_path, index=False, header=False)
    print(f"    📁 Arquivo salvo em: {output_path.name}")
    return True

def extrair_excel_de_pdf(pdf_path, pasta_saida):
    rows = extract_tables_with_camelot(pdf_path)
    items = group_items(rows)

    pdf_folder_name = pasta_saida.name
    output_filename = f"{pdf_folder_name}_referencia.xlsx"
    output_path = pasta_saida / output_filename

    sucesso = export_items(items, output_path)
    return sucesso

# =========================
# PIPELINE PRINCIPAL
# =========================
def main():
    """
    Executa a pipeline completa: 
    1. Acha o PDF correspondente em cada pasta (ignora 'RelacaoItens')
    2. Limpa rodapés -> `_limpo.pdf`
    3. Extrai tabelas organizadas -> `_referencia.xlsx`
    """
    if not PASTA_EDITAIS.exists():
        print(f"[-] Pasta de editais não encontrada em: {PASTA_EDITAIS}")
        return

    print(f"\n--- Iniciando Pipeline de Extração em: {PASTA_EDITAIS} ---")

    for pasta_edital in sorted(p for p in PASTA_EDITAIS.iterdir() if p.is_dir()):
        print(f"\n--- Processando pasta: {pasta_edital.name} ---")
        
        # Encontrar PDF ignorando RelacaoItens e o que já foi limpo no passado
        pdf_alvo = None
        for arquivo in pasta_edital.glob("*.pdf"):
            nome = arquivo.name.lower()
            if "relacaoitens" not in nome and not nome.endswith("_limpo.pdf"):
                pdf_alvo = arquivo
                break
        
        if not pdf_alvo:
            print("  [!] Nenhum PDF principal encontrado para processar (ignorando RelacaoItens).")
            continue
            
        print(f"  > PDF selecionado: {pdf_alvo.name}")
        pdf_limpo = pdf_alvo.with_name(f"{pdf_alvo.stem}_limpo.pdf")
        
        # 1. Limpeza
        if not pdf_limpo.exists():
            print(f"  > Iniciando etapa de limpeza de rodapé...")
            try:
                limpar_pdf_rodape_intencional(pdf_alvo, pdf_limpo)
            except Exception as e:
                print(f"  [-] Erro na limpeza: {e}")
                continue
        else:
            print(f"  > [!] Arquivo limpo ({pdf_limpo.name}) já existe, pulando etapa 1.")
            
        # 2. Extração
        xlsx_name = f"{pasta_edital.name}_referencia.xlsx"
        xlsx_path = pasta_edital / xlsx_name
        
        if not xlsx_path.exists() and pdf_limpo.exists():
            print(f"  > Iniciando etapa de extração de tabelas...")
            try:
                extrair_excel_de_pdf(pdf_limpo, pasta_edital)
            except Exception as e:
                print(f"  [-] Erro na extração: {e}")
        elif xlsx_path.exists():
            print(f"  > [!] Arquivo excel ({xlsx_name}) já existe, pulando etapa 2.")

    print("\n=== PIPELINE FINALIZADO COM SUCESSO ===")

if __name__ == "__main__":
    main()
