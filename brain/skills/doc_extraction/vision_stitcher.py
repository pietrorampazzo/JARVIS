import os
from pathlib import Path
from google import genai
from engine.shared.shared import load_env

def validate_stitching(page_1_img, page_2_img):
    """
    Usa Gemini Vision para verificar se o item na última linha da pág 1 
    continua na primeira linha da pág 2.
    """
    env = load_env()
    api_key = env.get("GEMINI_API_KEY")
    if not api_key:
        return {"status": "error", "message": "API Key missing"}

    client = genai.Client(api_key=api_key)
    
    prompt = """
    Analise estas duas imagens que representam o final de uma página (Imagem 1) e o início da página seguinte (Imagem 2) de um edital de licitação.
    
    PERGUNTA:
    1. A tabela é contínua?
    2. O item que termina na Imagem 1 é o mesmo que começa na Imagem 2 (continuação de texto)?
    3. Se houver uma quebra de item, qual é o número do novo item na Imagem 2?
    
    Responda em JSON:
    {
      "continuous": true/false,
      "stitching_logic": "descrição do que observou",
      "new_item_id": "ID se houver"
    }
    """
    
    # Simulação de chamada Vision (precisa carregar imagens como bytes/PIL)
    # response = client.models.generate_content(
    #     model="gemini-2.0-flash",
    #     contents=[prompt, page_1_img, page_2_img]
    # )
    
    # Mock para teste inicial de integração
    return {
        "continuous": True,
        "stitching_logic": "O item 'Triângulo' continua com descrição de material na pág 2",
        "new_item_id": None
    }
