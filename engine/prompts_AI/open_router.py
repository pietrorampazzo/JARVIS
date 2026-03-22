import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPEN_ROUTER")

URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

PERGUNTA = "Qual o raio da Terra?"

MODELOS = [
    "deepseek/deepseek-r1-0528:free",
    "qwen/qwen-2.5-vl-7b-instruct:free"
]

def perguntar(modelo):

    payload = {
        "model": modelo,

        # ⭐ CAMPO CORRETO
        "providers": ["modelrun"],

        "messages": [
            {"role": "user", "content": PERGUNTA}
        ]
    }

    r = requests.post(URL, headers=HEADERS, json=payload)

    print("\nSTATUS:", r.status_code)
    print(r.text)


for m in MODELOS:
    perguntar(m)
