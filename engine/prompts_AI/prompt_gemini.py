import google.generativeai as genai_lib
import os 
from dotenv import load_dotenv
import argparse

print(f"google-generativeai version: {genai_lib.__version__}")

load_dotenv() 

api_key = os.getenv("GOOGLE_API_KEY4")
genai_lib.configure(api_key=api_key)

# Escolha o modelo que deseja usar.
model = genai_lib.GenerativeModel(model_name='gemini-1.5-flash')


# 3. A Função para "Promptar"
def gerar_conteudo(prompt):

    # 5. Enviando o Prompt e Recebendo a Resposta
    try:
        # A chamada principal que envia seu prompt para a API do Gemini
        response = model.generate_content(prompt)
        
        # A resposta da IA está no atributo .text
        return response.text
        
    except Exception as e:
        # É importante tratar possíveis erros (ex: problema de conexão, API key inválida)
        print(f"Ocorreu um erro durante a chamada para a IA: {e}")
        return None

# --- EXECUÇÃO DO CÓDIGO ---
# Exemplo de como usar a função
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate content using Gemini API.')
    parser.add_argument('prompt', type=str, help='The prompt to send to the Gemini API.')
    args = parser.parse_args()
    
    # Chamamos nossa função com essas variáveis
    resultado_da_ia = gerar_conteudo(args.prompt)
    
    # Verificamos se obtivemos um resultado e o imprimimos
    if resultado_da_ia:
        print(resultado_da_ia)