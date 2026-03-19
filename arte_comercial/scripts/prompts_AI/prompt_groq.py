from groq import Groq
import os
from dotenv import load_dotenv
import argparse
import sys

load_dotenv()
api_key = os.getenv("QROQ_API_KEY")

client = Groq(api_key=api_key)

import sys

def gerar_conteudo(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
              {
                "role": "user",
                "content": prompt
              }
            ],
            temperature=0.6,
            max_tokens=4096,
            top_p=0.95,
            stream=False,
            stop=None
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Ocorreu um erro durante a chamada para a IA: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate content using Groq API.')
    parser.add_argument('prompt', type=str, help='The prompt to send to the Groq API.')
    args = parser.parse_args()
    
    resultado_da_ia = gerar_conteudo(args.prompt)
    
    if resultado_da_ia:
        print(resultado_da_ia)
