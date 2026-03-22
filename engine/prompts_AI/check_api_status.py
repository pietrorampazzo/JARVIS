from dotenv import load_dotenv
import os
import sys
import asyncio
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, PermissionDenied, GoogleAPICallError

# --- Constantes de Cores ---
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

async def check_combination(api_key: str, model_name: str) -> tuple[str, str, str]:
    """
    Verifica uma única combinação de chave/modelo de forma assíncrona.
    Retorna uma tupla com (model_name, status, message).
    """
    status = ""
    message = ""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        # Usar uma chamada que não consome tokens de geração é mais eficiente
        await model.count_tokens_async("test")
        
        status = f"{GREEN}[ DISPONÍVEL ]{RESET}"
        message = "Ok"

    except ResourceExhausted:
        status = f"{YELLOW}[ ESGOTADO ]{RESET}"
        message = "Quota (RPM/TPM/RPD) provavelmente excedida."
    except PermissionDenied as e:
        status = f"{RED}[ INVÁLIDA ]{RESET}"
        if "API key not valid" in str(e):
             message = "A chave de API não é válida."
        else:
            message = "Chave de API inválida ou sem permissão para este modelo."
    except GoogleAPICallError as e:
        status = f"{RED}[ ERRO API ]{RESET}"
        message = f"Erro na chamada da API: {str(e)[:100]}..."
    except Exception as e:
        status = f"{RED}[ ERRO INESPERADO ]{RESET}"
        # Mostra o tipo de exceção para facilitar a depuração
        message = f"{type(e).__name__}: {str(e)[:100]}..."

    return model_name, status, message

async def main():
    """
    Função principal que carrega as chaves do .env e as verifica contra uma lista fixa de modelos.
    """
    print(f"{BLUE}--- Verificador de Status das Chaves e Modelos da API Google ---{RESET}")

    load_dotenv() 
    
    api_keys_with_names = {}
    # Itera para encontrar chaves como GOOGLE_API_KEY, GOOGLE_API_KEY2, etc.
    # Corrigido para lidar com chaves duplicadas no .env, usando apenas a primeira ocorrência.
    key_values_seen = set()
    for i in range(1, 15): # Aumentado para 15 para mais flexibilidade
        key_name = f"GOOGLE_API_KEY{i if i > 1 else ''}"
        key_value = os.getenv(key_name)
        if key_value and key_value not in key_values_seen:
            api_keys_with_names[key_name] = key_value
            key_values_seen.add(key_value)

    if not api_keys_with_names:
        print(f"{RED}Nenhuma chave de API (GOOGLE_API_KEY, GOOGLE_API_KEY2, etc) encontrada no seu arquivo .env.{RESET}")
        return

    # Lista de modelos é agora fixa para evitar problemas de parsing do .env
    models_to_try = [
    "gemini-robotics-er-1.5-preview",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",

    ]
        
    if not models_to_try:
        print(f"{YELLOW}A lista de modelos para testar está vazia.{RESET}")
        return

    for key_name, key_value in api_keys_with_names.items():
        print(f"\nVerificando chave: {key_name} (final: ...{key_value[-4:]})")
        print("-" * (18 + len(key_name) + 15))
        
        tasks = [check_combination(key_value, model_name) for model_name in models_to_try]
        results = await asyncio.gather(*tasks)
        
        for model_name, status, message in results:
            # Garante alinhamento correto das colunas
            print(f"  - {model_name:<30} {status:<28} {message if message != 'Ok' else ''}")

if __name__ == "__main__":
    try:
        # Define a política de eventos do Windows para evitar erros de loop no asyncio
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nVerificação cancelada pelo usuário.")
