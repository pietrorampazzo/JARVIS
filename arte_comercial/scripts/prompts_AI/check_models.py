
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        raise ValueError("A variável de ambiente GOOGLE_API_KEY não foi definida.")
    genai.configure(api_key=GOOGLE_API_KEY)
except Exception as e:
    print(f"Erro ao configurar a API do Gemini: {e}")
    exit()

for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)
