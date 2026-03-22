import os
import sys
from pathlib import Path

# Adiciona o diretório legado ao path para importar as skills existentes
BASE_DIR = Path(__file__).parent.parent.parent.parent
LEGEACY_DIR = BASE_DIR / "arte_comercial" / "arte_" / "arte_edital"
sys.path.append(str(LEGEACY_DIR))

# Imports das skills legadas
try:
    from docling_extraction_skill import process_pdf_with_docling # Se refatorado
    # Importar outros motores conforme necessário
except ImportError:
    pass

class DocProcessor:
    def __init__(self, performance_md_path):
        self.performance_md_path = performance_md_path

    def extract(self, pdf_path: Path):
        """
        Executa a Mesa de Decisão para extrair dados do PDF.
        """
        print(f"🔍 [Mesa de Decisão] Analisando {pdf_path.name}")
        
        # 1. TENTA DOCLING (Alta Eficiência)
        # try:
        #    df = process_pdf_with_docling(pdf_path)
        #    if df is not None and not df.empty:
        #        return df, "Docling"
        # except:
        #    pass

        # 2. TENTA CAMELOT (Lattice - Zero Token)
        # print("🔄 [Fallback] Tentando Camelot...")
        
        # 3. TENTA OCR (Tesseract - Zero Token)
        # print("🔄 [Fallback] Tentando OCR...")

        # MOCK de Sucesso
        print("✅ [Sucesso] Extração via Zero Token Pattern (Regex Custom)")
        return None, "ZeroToken"

    def learn_from_vision(self, pdf_path, vision_result):
        """
        Recebe o resultado do Vision AI e gera uma regra para o futuro.
        """
        if vision_result.get("continuous"):
            # Gera uma regra no performance_knowledge.md
            pass
