import sys
import json
import time
from pathlib import Path

# Adiciona o JARVIS ao path caso precise de utilitários
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def run_sync():
    """
    Executa a sincronização dos arquivos do Google Drive com o NotebookLM.
    Utiliza o ambiente e autenticação do skill do Antigravity.
    """
    try:
        import patchright.sync_api as p_api
    except ImportError:
        print("❌ Patchright não encontrado. Certifique-se de rodar este script com o VENV do skill.")
        sys.exit(1)
    
    # Configurações do Oráculo
    BASE_DIR = Path(__file__).parent.parent.parent
    CONFIG_PATH = BASE_DIR / "engine" / "config" / "oracle.json"
    SKILL_DATA_DIR = Path(r"C:\Users\pietr\.antigravity\skills\notebooklm\data")
    BROWSER_PROFILE = SKILL_DATA_DIR / "browser_state" / "browser_profile"
    STATE_FILE = SKILL_DATA_DIR / "browser_state" / "state.json"

    if not CONFIG_PATH.exists():
        print(f"❌ Configuração não encontrada em {CONFIG_PATH}")
        return

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    with p_api.sync_playwright() as pw:
        # Lançar navegador com o perfil do skill onde o login já foi feito
        print("🚀 Lançando navegador (Chrome Persistent)...")
        context = pw.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_PROFILE),
            channel="chrome",
            headless=True, 
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        # Workaround para cookies de sessão que o Playwright às vezes perde no persistent
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    state = json.load(f)
                    if 'cookies' in state:
                        context.add_cookies(state['cookies'])
            except:
                pass
        
        page = context.new_page()
        url = config["notebook_url"]
        print(f"🌐 Navegando para o Notebook: {url}")
        
        try:
            page.goto(url, wait_until="networkidle", timeout=60000)
            # Aguarda renderização dos componentes internos
            time.sleep(8) 
            
            print("🔍 Iniciando sincronização de fontes...")
            
            for source_name in config["sources"]:
                print(f"  🔄 Processando: {source_name}")
                
                # Estratégia: No NotebookLM, o botão de refresh/sync aparece na linha da fonte.
                # O usuário indicou o label: "Clique para sincronizar com o Google Drive"
                try:
                    # Tenta clicar no botão de sincronização associado ao nome do arquivo
                    # Usamos um seletor que busca o botão que contém o label informado pelo usuário
                    # e que está próximo ao texto do arquivo.
                    
                    # 1. Tentar localizar o botão de sync exato pelo label
                    # O seletor abaixo tenta achar o botão que tem o label e está na mesma 'linha' (ancestor comum) do texto
                    sync_button = page.get_by_label("Clique para sincronizar com o Google Drive").filter(
                        has_text=None # O botão em si não tem texto, só o label
                    )
                    
                    # Como podem haver vários botões, precisamos filtrar pelo que está perto do source_name
                    # Ou simplesmente iterar e ver qual está visível/habilitado
                    
                    count = sync_button.count()
                    clicked = False
                    
                    for i in range(count):
                        btn = sync_button.nth(i)
                        # Verifica se o texto do arquivo está no container pai deste botão
                        # Geralmente a estrutura é div > (text, button)
                        parent_text = btn.evaluate("node => node.closest('div').parentElement.innerText")
                        if source_name in parent_text:
                            btn.click()
                            print(f"    ✅ Sincronização enviada para {source_name}")
                            clicked = True
                            time.sleep(3) # Aguarda o clique ser processado
                            break
                    
                    if not clicked:
                        # Fallback: tenta localizar por seletor de classe comum em botões de refresh se o label não funcionar
                        print(f"    ⚠️ Botão por label não encontrado para {source_name}, tentando busca por proximidade...")
                        # Pegamos o texto da fonte e clicamos no botão mais próximo
                        page.get_by_text(source_name, exact=False).click() # Ativa o hover se necessário
                        time.sleep(1)
                        # Clica no botão de refresh (o ícone de setinhas circulares)
                        # No NotebookLM v2 costuma ser um botão com ícone 'sync' ou 'refresh'
                        page.get_by_role("button", name="Sincronizar").first.click()
                
                except Exception as e:
                    print(f"    ❌ Falha ao processar {source_name}: {e}")

            print("🏁 Ciclo de atualização concluído.")
            
        except Exception as e:
            print(f"❌ Erro de navegação: {e}")
            
        finally:
            context.close()

if __name__ == "__main__":
    run_sync()
