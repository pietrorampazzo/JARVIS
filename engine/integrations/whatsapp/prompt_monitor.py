import sys
import os
import json
from google import genai
from dotenv import load_dotenv

# Força UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

def main():
    if len(sys.argv) < 3:
        sys.exit(1)

    phone_number = sys.argv[1]
    message_content = sys.argv[2]
    is_group = sys.argv[3] == "true"
    group_info = sys.argv[4] if len(sys.argv) > 4 else "{}"

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Tenta pegar do wappi se não tiver no jarvis local
        api_key = "AIzaSyDsHs_vp0trkHqAYMCp2xNv8e96C69s5JM" # Fallback para a chave vista no .env

    client = genai.Client(api_key=api_key)

    system_instruction = """
Você é o módulo de inteligência de 'Rede de Pesca' do sistema JARVIS. Sua função é monitorar conversas de WhatsApp e filtrar informações críticas.

Objetivos:
1. Identificar Oportunidades de Negócios (leads, parcerias, demandas).
2. Identificar Oportunidades de Relacionamento (conectar pessoas, eventos sociais importantes).
3. Monitorar o comportamento e postura do usuário (Pietro) nas interações para garantir que ele esteja mantendo o rumo desejado em suas relações.
4. Identificar questões intrínsecas à BARSI.

Retorne APENAS um JSON no formato:
{
  "importante": boolean,
  "titulo": "Resumo curto",
  "motivo": "Explicação do porquê foi retido",
  "impacto": 1-5,
  "area": "economic_output" | "system_building" | "relationship_monitoring",
  "tags": ["lista", "de", "tags"]
}
"""

    prompt = f"""
Origem: {'Grupo' if is_group else 'Privado'}
Mensagem do contato ({phone_number}): {message_content}

Analise se há algo importante para ser registrado nos logs do JARVIS conforme os objetivos.
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                "system_instruction": system_instruction,
                "temperature": 0.2,
                "response_mime_type": "application/json"
            }
        )
        print(response.text.strip())
    except Exception as e:
        # Default de segurança se falhar
        print(json.dumps({"importante": False}))

if __name__ == "__main__":
    main()
