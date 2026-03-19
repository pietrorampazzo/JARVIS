import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração da API do Hugging Face
HUGGINGFACE_API_KEY = "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"

# Lista de modelos disponíveis
HUGGINGFACE_CHAT_MODELS = [
    "deepseek-ai/DeepSeek-R1",                    # ⭐ Mais poderoso
    "deepseek-ai/DeepSeek-V3",                  # ⭐ Muito poderoso
    "deepseek-ai/DeepSeek-V3-0324",             # ⭐ Versão atualizada
    "meta-llama/Llama-3.1-8B-Instruct",           # ⭐ Excelente balanceamento
    "meta-llama/Meta-Llama-3-8B-Instruct",      # ⭐ Muito confiável
    "meta-llama/Llama-2-7b-chat-hf",          # ⭐ Popular e testado
    "Qwen/Qwen2.5-7B-Instruct",                 # ⭐ Multilíngue
    "Qwen/Qwen2.5-3B-Instruct",                 # ⭐ Rápido e eficiente
    "mistralai/Mistral-7B-Instruct-v0.2",       # ⭐ Arquitetura eficiente
    "google/gemma-7b-it",                        # ⭐ Google open-source
    "google/gemma-2-9b-it",                    # ⭐ Versão 2 melhorada
    "openai/gpt-oss-20b",                        # ⭐ Estilo GPT
    "openai/gpt-oss-120b",                       # ⭐ Versão maior
]

# Inicializa o cliente de inferência
client = InferenceClient(
    api_key=HUGGINGFACE_API_KEY,
    base_url="https://router.huggingface.co/v1"
)

# Escolha o modelo que deseja usar
MODELO_ESCOLHIDO = "deepseek-ai/DeepSeek-R1"  # Você pode mudar para qualquer modelo da lista

# Função para gerar conteúdo
def gerar_conteudo():
    prompt = """
    
    
    Qual o raio da terra?
    
    
    """
    
    try:
        # Cria a conversa com o modelo
        chat_completion = client.chat.completions.create(
            model=MODELO_ESCOLHIDO,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,  # Limita o número máximo de tokens na resposta
            temperature=0.7,  # Controla a criatividade (0.0 = mais previsível, 1.0 = mais criativo)
        )
        
        # Retorna o conteúdo da resposta
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        # Tratamento de erros
        print(f"❌ Ocorreu um erro durante a chamada para a IA: {e}")
        return None

# Função alternativa usando text_generation (se o modelo não suportar chat completion)
def gerar_conteudo_alternativo():
    prompt = "Qual o raio da terra?"
    
    try:
        # Usa text_generation diretamente
        response = client.text_generation(
            prompt=prompt,
            max_new_tokens=500,
            temperature=0.7,
        )
        return response
        
    except Exception as e:
        print(f"❌ Erro no método alternativo: {e}")
        return None

# Função para listar modelos disponíveis
def listar_modelos():
    print("\n--- MODELOS DISPONÍVEIS ---")
    for i, modelo in enumerate(HUGGINGFACE_CHAT_MODELS, 1):
        print(f"{i}. {modelo}")
    print("---------------------------")

# Função para trocar de modelo
def trocar_modelo():
    listar_modelos()
    try:
        escolha = int(input("Escolha o número do modelo desejado: ")) - 1
        if 0 <= escolha < len(HUGGINGFACE_CHAT_MODELS):
            global MODELO_ESCOLHIDO
            MODELO_ESCOLHIDO = HUGGINGFACE_CHAT_MODELS[escolha]
            print(f"✅ Modelo alterado para: {MODELO_ESCOLHIDO}")
        else:
            print("❌ Escolha inválida")
    except ValueError:
        print("❌ Por favor, digite um número válido")

# --- EXECUÇÃO DO CÓDIGO ---
if __name__ == "__main__":
    print(f"🤖 Usando o modelo: {MODELO_ESCOLHIDO}")
    print("📝 Gerando resposta...")
    
    # Tenta primeiro com chat completion
    resultado_da_ia = gerar_conteudo()
    
    # Se falhar, tenta o método alternativo
    if resultado_da_ia is None:
        print("🔄 Tentando método alternativo...")
        resultado_da_ia = gerar_conteudo_alternativo()
    
    # Verifica se obteve um resultado e o imprime
    if resultado_da_ia:
        print("\n--- RESPOSTA DA IA ---")
        print(resultado_da_ia)
        print("--------------------")
    else:
        print("❌ Não foi possível obter uma resposta da IA")
    
    # Menu interativo (opcional)
    while True:
        print("\n--- MENU ---")
        print("1. Fazer outra pergunta")
        print("2. Trocar modelo")
        print("3. Listar modelos")
        print("4. Sair")
        
        escolha = input("Escolha uma opção: ")
        
        if escolha == "1":
            nova_pergunta = input("Digite sua pergunta: ")
            
            try:
                chat_completion = client.chat.completions.create(
                    model=MODELO_ESCOLHIDO,
                    messages=[{"role": "user", "content": nova_pergunta}],
                    max_tokens=500,
                    temperature=0.7,
                )
                print("\n--- RESPOSTA DA IA ---")
                print(chat_completion.choices[0].message.content)
                print("--------------------")
            except Exception as e:
                print(f"❌ Erro: {e}")
                
        elif escolha == "2":
            trocar_modelo()
            
        elif escolha == "3":
            listar_modelos()
            
        elif escolha == "4":
            print("👋 Até logo!")
            break
            
        else:
            print("❌ Opção inválida")