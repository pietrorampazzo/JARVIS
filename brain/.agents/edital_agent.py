import os
import time
import json
import shutil
import zipfile
import subprocess
from pathlib import Path
from datetime import datetime

# Import das novas skills
try:
    from brain.skills.doc_extraction.doc_processor import DocProcessor
    from brain.skills.doc_extraction.vision_stitcher import validate_stitching
except ImportError:
    # Fallback se caminhos de import falharem no runtime
    DocProcessor = None
    validate_stitching = None

# --- CONFIGURAÇÕES DE CAMINHO ---
BASE_DIR = Path(__file__).parent.parent.parent
EDITAIS_DIR = BASE_DIR / "arte_comercial" / "downloads" / "EDITAIS"
SKILLS_DIR = BASE_DIR / "brain" / "skills"
BINARY_DIR = SKILLS_DIR / "doc_extraction" / "bin"
PERFORMANCE_MD = BASE_DIR / "brain" / "config" / "performance_knowledge.md"
AGENT_LOG = BASE_DIR / "logs" / "edital_agent.log"
LAST_SCAN_FILE = BASE_DIR / "logs" / "edital_last_scan.json"

# Binários
TESSERACT_PATH = BINARY_DIR / "Tesseract-OCR" / "tesseract.exe"
POPPLER_PATH = BINARY_DIR / "Release-25.07.0-0" / "bin"

# Pula se não existir a pasta EDITAIS
if not EDITAIS_DIR.exists():
    EDITAIS_DIR.mkdir(parents=True, exist_ok=True)

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{timestamp}] {message}"
    print(msg)
    with open(AGENT_LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def get_processed_folders():
    if LAST_SCAN_FILE.exists():
        with open(LAST_SCAN_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_processed_folders(folders):
    with open(LAST_SCAN_FILE, "w") as f:
        json.dump(list(folders), f)

def process_folder(folder_path: Path):
    log(f"🚀 Iniciando processamento em: {folder_path.name}")
    
    # 1. Descompactação (Zero Token)
    # Procura por .zip e .rar (precisa de patool ou similar)
    # Por enquanto usando zipfile básico
    for zip_file in folder_path.glob("*.zip"):
        log(f"📦 Descompactando {zip_file.name}...")
        try:
            with zipfile.ZipFile(zip_file, 'r') as z:
                z.extractall(folder_path)
            zip_file.unlink()
        except Exception as e:
            log(f"⚠️ Erro no zip {zip_file.name}: {e}")

    # 2. Identificação de Termo de Referência
    # (Futura integração com Gemini para ser preciso)
    pdfs = list(folder_path.glob("*.pdf"))
    tr_pdf = None
    for pdf in pdfs:
        if "termo" in pdf.name.lower() or "referencia" in pdf.name.lower():
            tr_pdf = pdf
            break
    
    if not tr_pdf and pdfs:
        tr_pdf = pdfs[0] # Fallback
    
    if not tr_pdf:
        log(f"❌ Nenhum PDF encontrado em {folder_path.name}")
        return False

    log(f"📄 TR Detectado: {tr_pdf.name}")
    
    # 3. EXTRAÇÃO (Coração do Agente)
    # Aqui chamaremos os motores (Docling, Camelot, OCR)
    # Por agora, registramos no log a intenção
    log(f"🛠️ Roda extrator Zero Token em {tr_pdf.name}...")
    
    if DocProcessor:
        processor = DocProcessor(PERFORMANCE_MD)
        df, engine = processor.extract(tr_pdf)
        log(f"✅ Extraído via: {engine}")
    
    # 4. Sutura Vision (Mestre de Costura) - Se necessário
    if validate_stitching:
        # Exemplo: validar transição entre página 1 e 2
        res = validate_stitching(None, None) # Mock imagens
        log(f"🧵 Stitching Check: {res['stitching_logic']}")

    # Marcador de sucesso
    (folder_path / ".jarvis_processed").touch()
    return True

def run_batch():
    log("👁️ Agente ARTE Edital em modo BATCH DIÁRIO. Processando pendências...")
    processed = get_processed_folders()
    
    try:
        current_folders = {d.name for d in EDITAIS_DIR.iterdir() if d.is_dir()}
        new_folders = current_folders - processed
        
        if new_folders:
            log(f"📦 Encontradas {len(new_folders)} novas pastas para processar.")
            for name in new_folders:
                path = EDITAIS_DIR / name
                # Verifica se a pasta tem "conteúdo" (não está vazia)
                if any(path.iterdir()):
                    success = process_folder(path)
                    if success:
                        processed.add(name)
            
            save_processed_folders(processed)
            log("✅ Processamento em lote concluído.")
        else:
            log("✨ Nenhuma nova pasta encontrada para processar.")
            
    except Exception as e:
        log(f"🔥 Erro na execução batch: {e}")

if __name__ == "__main__":
    run_batch()
