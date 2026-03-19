import os
import sys
from img2table.document import PDF
from img2table.ocr import TesseractOCR
import pandas as pd

def find_tesseract():
    """Tenta encontrar o executável do Tesseract em caminhos comuns."""
    # Lista de caminhos possíveis para o tesseract.exe
    # Priorizamos o caminho local do projeto sugerido pelo usuário
    possible_paths = [
        r'C:\Users\pietr\OneDrive\.vscode\arte_\scripts\bin\Tesseract-OCR\tesseract.exe',
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe"),
        os.path.expanduser(r"~\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"),
    ]
    
    # 1. Verifica caminhos comuns (prioritários)
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Tesseract encontrado em: {path}")
            return path

    # 2. Verifica se está no PATH
    import shutil
    path_in_path = shutil.which("tesseract")
    if path_in_path:
        print(f"Tesseract encontrado no PATH: {path_in_path}")
        return path_in_path
            
    print("AVISO: Tesseract não encontrado nos caminhos padrão nem no PATH.")
    print("Certifique-se de ter instalado o Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki")
    return None

def extrair_tabelas_ocr(pdf_path):
    print(f"Iniciando extração OCR para: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"Erro: Arquivo não encontrado: {pdf_path}")
        return

    # Tenta configurar o OCR
    tesseract_cmd = find_tesseract()
    
    if not tesseract_cmd:
        print("Erro: Não foi possível localizar o executável do Tesseract.")
        return

    # Adiciona o diretório do Tesseract ao PATH para que o img2table o encontre
    tesseract_dir = os.path.dirname(tesseract_cmd)
    if tesseract_dir not in os.environ["PATH"]:
        os.environ["PATH"] = tesseract_dir + os.pathsep + os.environ["PATH"]
        print(f"Diretório do Tesseract adicionado ao PATH: {tesseract_dir}")

    # Configura o OCR. 
    # n_threads=1 para evitar problemas de concorrência em algumas máquinas
    # lang='por' para português
    try:
        tesseract = TesseractOCR(n_threads=1, lang='por')
    except Exception as e:
        print(f"Erro ao inicializar Tesseract OCR: {e}")
        print("Verifique se o Tesseract está instalado e se o pacote de idioma 'por' (português) foi incluído na instalação.")
        return

    # Instancia o documento PDF
    pdf = PDF(src=pdf_path)

    output_filename = "tabelas_ocr.xlsx"
    print("Extraindo tabelas... Isso pode demorar um pouco dependendo do tamanho do arquivo.")

    try:
        # Extrai tabelas e exporta diretamente para Excel
        # O método to_xlsx retorna None, ele salva o arquivo direto
        pdf.to_xlsx(dest=output_filename,
                    ocr=tesseract,
                    implicit_rows=False,
                    borderless_tables=True,
                    min_confidence=50)
                    
        print(f"Extração concluída! Arquivo salvo em: {os.path.abspath(output_filename)}")
        
    except Exception as e:
        print(f"Erro durante a extração: {e}")

if __name__ == "__main__":
    local_pdf = r"C:\Users\pietr\OneDrive\.vscode\arte_\DOWNLOADS\EDITAIS\160005_900012026\termo_referencia_limpo.pdf"
    
    extrair_tabelas_ocr(local_pdf)
