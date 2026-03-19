import fitz
import numpy as np
from collections import defaultdict
from pathlib import Path
from difflib import SequenceMatcher


# =========================
# CONFIGURAÇÕES
# =========================
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BASE_DIR = PROJECT_ROOT / "DOWNLOADS"
PASTA_EDITAIS = BASE_DIR / "EDITAIS"

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
# COLETA GLOBAL DE SPANS
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


# =========================
# AGRUPAMENTO DE SPANS REPETIDOS
# =========================
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


# =========================
# IDENTIFICAÇÃO DE RODAPÉS
# =========================
def identificar_rodapes(grupos, total_paginas):
    rodapes = []

    for grupo in grupos:
        paginas = {p for p, _ in grupo["ocorrencias"]}
        repeticao = len(paginas) / total_paginas

        if repeticao >= MIN_REPETICAO_PAGINAS:
            rodapes.append(grupo)

    return rodapes


# =========================
# REMOÇÃO SELETIVA
# =========================
def remover_rodapes(doc, rodapes):
    for grupo in rodapes:
        for page_idx, span in grupo["ocorrencias"]:
            page = doc[page_idx]
            rect = fitz.Rect(span["bbox"])
            page.add_redact_annot(rect, fill=(1, 1, 1))

    for page in doc:
        page.apply_redactions()


# =========================
# PIPELINE PRINCIPAL
# =========================
def limpar_pdf_rodape_intencional(pdf_entrada, pdf_saida):
    doc = fitz.open(pdf_entrada)
    total_paginas = len(doc)

    print(f"  Processando: {pdf_entrada.name}")
    print(f"  Total de páginas: {total_paginas}")

    spans_por_pagina = coletar_spans(doc)
    grupos = agrupar_spans(spans_por_pagina)
    rodapes = identificar_rodapes(grupos, total_paginas)

    if rodapes:
        print(f"  [+] Grupos de rodapé identificados: {len(rodapes)}")
        remover_rodapes(doc, rodapes)
        doc.save(pdf_saida)
        print(f"  [+] PDF salvo sem rodapés em: {pdf_saida.name}")
    else:
        print("  [!] Nenhum rodapé identificado para remoção.")
    
    doc.close()


# =========================
# EXECUÇÃO
# =========================
def main():
    """
    Executa a limpeza de rodapés em todos os arquivos 'termo_referencia.pdf'
    encontrados nas subpastas de PASTA_EDITAIS.
    """
    if not PASTA_EDITAIS.exists():
        print(f"[-] Pasta de editais não encontrada em: {PASTA_EDITAIS}")
        return

    print(f"--- Iniciando limpeza de rodapés em: {PASTA_EDITAIS} ---")

    for pasta_edital in sorted(p for p in PASTA_EDITAIS.iterdir() if p.is_dir()):
        pdf_input_path = pasta_edital / "termo_referencia.pdf"

        if pdf_input_path.exists():
            print(f"\n--- Processando pasta: {pasta_edital.name} ---")
            pdf_output_path = pdf_input_path.with_name(f"{pdf_input_path.stem}_limpo.pdf")
            
            if pdf_output_path.exists():
                print(f"  [!] Arquivo já limpo, pulando: {pdf_output_path.name}")
                continue

            try:
                limpar_pdf_rodape_intencional(pdf_input_path, pdf_output_path)
            except Exception as e:
                print(f"  [-] Erro ao processar {pdf_input_path.name}: {e}")

    print("\n=== PROCESSAMENTO DE LIMPEZA FINALIZADO ===")


if __name__ == "__main__":
    main()
