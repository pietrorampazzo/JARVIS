import re
import zipfile
import rarfile
import shutil
from pathlib import Path
import fitz  # PyMuPDF
import pandas as pd


# =============================================================================
# CONFIGURAÇÕES
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BASE_DIR = PROJECT_ROOT / "DOWNLOADS"
PASTA_EDITAIS = BASE_DIR / "EDITAIS"


# =============================================================================
# DESCOMPACTAÇÃO RECURSIVA
# =============================================================================

def descompactar_recursivamente(pasta: Path):
    """
    Descompacta todos os arquivos .zip encontrados recursivamente dentro da pasta,
    movendo o conteúdo para a própria pasta do edital.
    """
    while True:
        arquivos_zip = list(pasta.rglob("*.zip"))
        arquivos_rar = list(pasta.rglob("*.rar"))
        
        if not arquivos_zip and not arquivos_rar:
            break
 
        # Processa ZIPs
        for zip_path in arquivos_zip:
            temp_dir = pasta / f"_tmp_zip_{zip_path.stem}"
            temp_dir.mkdir(exist_ok=True)
            try:
                with zipfile.ZipFile(zip_path, "r") as z:
                    z.extractall(temp_dir)
                for item in temp_dir.rglob("*"):
                    if item.is_file():
                        destino = pasta / item.name
                        contador = 1
                        while destino.exists():
                            destino = pasta / f"{item.stem}_{contador}{item.suffix}"
                            contador += 1
                        shutil.move(str(item), str(destino))
                zip_path.unlink()
            finally:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)

        # Processa RARs
        for rar_path in arquivos_rar:
            temp_dir = pasta / f"_tmp_rar_{rar_path.stem}"
            temp_dir.mkdir(exist_ok=True)
            try:
                with rarfile.RarFile(rar_path, "r") as r:
                    r.extractall(temp_dir)
                for item in temp_dir.rglob("*"):
                    if item.is_file():
                        destino = pasta / item.name
                        contador = 1
                        while destino.exists():
                            destino = pasta / f"{item.stem}_{contador}{item.suffix}"
                            contador += 1
                        shutil.move(str(item), str(destino))
                rar_path.unlink()
            except Exception as e:
                print(f"  [!] Erro ao descompactar RAR {rar_path.name}: {e}")
            finally:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)


# =============================================================================
# ACHATAR ESTRUTURA
# =============================================================================

def achatar_estrutura(pasta: Path):
    """
    Move todos os arquivos de subpastas para a raiz da pasta do edital.
    """
    for subdir in [d for d in pasta.iterdir() if d.is_dir()]:
        for file in subdir.rglob("*"):
            if file.is_file():
                destino = pasta / file.name
                contador = 1
                while destino.exists():
                    destino = pasta / f"{file.stem}_{contador}{file.suffix}"
                    contador += 1
                shutil.move(str(file), str(destino))
        shutil.rmtree(subdir)


# =============================================================================
# EXTRAÇÃO DE ITENS DO PDF (RELACAOITENS)
# =============================================================================

def extrair_itens_pdf_texto(text: str) -> list[dict]:
    """Extrai itens estruturados do texto de um PDF 'Relação de Itens'."""
    items = []
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    item_pattern = re.compile(r'(\d+)\s*-\s*([^0-9]+?)(?=Descrição Detalhada:)', re.DOTALL | re.IGNORECASE)
    item_matches = list(item_pattern.finditer(text))

    for i, match in enumerate(item_matches):
        item_num = match.group(1).strip()
        item_nome = match.group(2).strip()
        start_idx = int(match.start())
        end_idx = int(item_matches[i + 1].start()) if i + 1 < len(item_matches) else len(text)
        item_text = text[start_idx:end_idx]

        descricao_match = re.search(r'Descrição Detalhada:\s*(.*?)(?=Tratamento Diferenciado:|Aplicabilidade Decreto|$\s*)', item_text, re.DOTALL | re.IGNORECASE)
        descricao = descricao_match.group(1).strip() if descricao_match else ""
        item_completo = f"{item_nome} {re.sub(r'\s+', ' ', re.sub(r'[^\w\s:,.()/-]', '', descricao))}"

        quantidade_match = re.search(r'Quantidade Total:\s*(\d+)', item_text, re.IGNORECASE)
        quantidade = quantidade_match.group(1) if quantidade_match else ""

        valor_unitario_match = re.search(r'Valor Unitário[^:]*:\s*R?\$?\s*([\d.,]+)', item_text, re.IGNORECASE)
        valor_unitario = valor_unitario_match.group(1) if valor_unitario_match else ""

        valor_total_match = re.search(r'Valor Total[^:]*:\s*R?\$?\s*([\d.,]+)', item_text, re.IGNORECASE)
        valor_total = valor_total_match.group(1) if valor_total_match else ""

        unidade_match = re.search(r'Unidade de Fornecimento:\s*([^0-9\n]+?)(?=\s|$|\n)', item_text, re.IGNORECASE)
        unidade = unidade_match.group(1).strip() if unidade_match else ""

        local_match = re.search(r'Local de Entrega[^:]*:\s*([^(\n]+?)(?:\s*\(|$|\n)', item_text, re.IGNORECASE)
        local = local_match.group(1).strip() if local_match else ""

        items.append({
            "Nº": item_num, "DESCRICAO": item_completo, "QTDE": quantidade,
            "VALOR_UNIT": valor_unitario, "VALOR_TOTAL": valor_total,
            "UNID_FORN": unidade, "LOCAL_ENTREGA": local
        })
    return items

def processar_relacao_itens(pdf_path: Path) -> pd.DataFrame:
    texto = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            texto += page.get_text()

    itens = extrair_itens_pdf_texto(texto)
    return pd.DataFrame(itens)


def calcular_valores_faltantes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula VALOR_TOTAL ou VALOR_UNIT faltantes com base na QTDE.
    """
    if df.empty:
        return df

    df_proc = df.copy()

    for col in ['QTDE', 'VALOR_UNIT', 'VALOR_TOTAL']:
        if col not in df_proc.columns:
            print(f"  [!] Coluna '{col}' ausente, pulando cálculo de valores.")
            return df

    def clean_currency(series):
        if pd.api.types.is_numeric_dtype(series):
            return series
        
        series_str = series.astype(str).str.replace(r'R?\$\s?', '', regex=True)
        # Assumindo formato brasileiro (1.234,56), remove '.' e troca ',' por '.'
        series_cleaned = series_str.str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        return pd.to_numeric(series_cleaned, errors='coerce')

    df_proc['QTDE'] = pd.to_numeric(df_proc['QTDE'], errors='coerce')
    df_proc['VALOR_UNIT'] = clean_currency(df_proc['VALOR_UNIT'])
    df_proc['VALOR_TOTAL'] = clean_currency(df_proc['VALOR_TOTAL'])

    qtde_valida = df_proc['QTDE'].notna() & (df_proc['QTDE'] > 0)
    unit_presente = df_proc['VALOR_UNIT'].notna()
    total_presente = df_proc['VALOR_TOTAL'].notna()
    unit_ausente = df_proc['VALOR_UNIT'].isna()
    total_ausente = df_proc['VALOR_TOTAL'].isna()

    # Calcula VALOR_TOTAL quando ausente
    mascara_calc_total = total_ausente & unit_presente & qtde_valida
    df_proc.loc[mascara_calc_total, 'VALOR_TOTAL'] = df_proc['VALOR_UNIT'] * df_proc['QTDE']

    # Calcula VALOR_UNIT quando ausente
    mascara_calc_unit = unit_ausente & total_presente & qtde_valida
    df_proc.loc[mascara_calc_unit, 'VALOR_UNIT'] = df_proc['VALOR_TOTAL'] / df_proc['QTDE']

    # Arredonda valores para 2 casas decimais
    df_proc['VALOR_UNIT'] = df_proc['VALOR_UNIT'].round(2)
    df_proc['VALOR_TOTAL'] = df_proc['VALOR_TOTAL'].round(2)

    return df_proc


def renomear_termo_referencia(pasta: Path):
    """
    Renomeia o arquivo PDF que não é 'RelacaoItens' para 'termo_referencia.pdf'.
    """
    todos_os_pdfs = list(pasta.glob("*.pdf"))
    pdfs_relacao_itens = list(pasta.glob("RelacaoItens*.pdf"))
    outros_pdfs = [p for p in todos_os_pdfs if p not in pdfs_relacao_itens]

    if len(outros_pdfs) == 1:
        antigo_path = outros_pdfs[0]
        novo_path = pasta / "termo_referencia.pdf"

        if antigo_path == novo_path:
            return

        if novo_path.exists():
            print(f"  [!] 'termo_referencia.pdf' já existe. Não foi possível renomear {antigo_path.name}.")
        else:
            try:
                antigo_path.rename(novo_path)
                print(f"  [+] Renomeado: {antigo_path.name} -> {novo_path.name}")
            except Exception as e:
                print(f"  [!] Erro ao renomear {antigo_path.name}: {e}")

    elif len(outros_pdfs) > 1:
        print(f"  [!] Encontrados {len(outros_pdfs)} PDFs além do 'RelacaoItens'. Nenhum foi renomeado.")
        for i, pdf_path in enumerate(outros_pdfs):
            print(f"    {i+1}: {pdf_path.name}")


# =============================================================================
# PIPELINE POR PASTA
# =============================================================================

def processar_pasta_edital(pasta: Path):
    print(f"\n--- Processando {pasta.name} ---")

    descompactar_recursivamente(pasta)
    achatar_estrutura(pasta)

    renomear_termo_referencia(pasta)

    pdfs = list(pasta.glob("RelacaoItens*.pdf"))
    if not pdfs:
        print("  [!] Nenhum RelacaoItens.pdf encontrado.")
        return

    df_final = pd.DataFrame()
    for pdf in pdfs:
        df = processar_relacao_itens(pdf)
        df_final = pd.concat([df_final, df], ignore_index=True)

    if df_final.empty:
        print("  [-] Nenhum item extraído.")
        return

    df_final = calcular_valores_faltantes(df_final)

    saida = pasta / f"{pasta.name}_itens.xlsx"
    df_final.to_excel(saida, index=False)
    print(f"  [+] Itens salvos em: {saida.name}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    if not PASTA_EDITAIS.exists():
        print("[-] Pasta EDITAIS não encontrada.")
        return

    for pasta in sorted(p for p in PASTA_EDITAIS.iterdir() if p.is_dir()):
        processar_pasta_edital(pasta)

    print("\n=== PROCESSAMENTO FINALIZADO ===")


if __name__ == "__main__":
    main()
