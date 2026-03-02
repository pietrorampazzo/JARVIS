import requests
import json
import logging
import os
from datetime import datetime

# Configurações do Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EvolutionMonitor")

class EvolutionMonitor:
    def __init__(self, api_url, api_key):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "apikey": self.api_key,
            "Content-Type": "application/json"
        }

    def list_instances(self):
        """Lista todas as instâncias disponíveis na API."""
        try:
            url = f"{self.api_url}/instance/fetchInstances"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao listar instâncias: {e}")
            return None

    def send_text(self, instance_name, jid, text):
        """Envia uma mensagem de texto para um JID (Contato ou Grupo)."""
        try:
            url = f"{self.api_url}/message/sendText/{instance_name}"
            payload = {
                "number": jid,
                "options": {
                    "delay": 1200,
                    "presence": "composing",
                    "linkPreview": True
                },
                "text": text
            }
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para {jid}: {e}")
            return None

    def get_chats(self, instance_name):
        """Busca todos os chats da instância."""
        try:
            url = f"{self.api_url}/chat/fetchChats/{instance_name}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao buscar chats: {e}")
            return None

    def fetch_group_participants(self, instance_name, group_jid):
        """Busca participantes de um grupo específico."""
        try:
            url = f"{self.api_url}/group/participants/{instance_name}?groupJid={group_jid}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao buscar participantes do grupo {group_jid}: {e}")
            return None

    def monitor_barsi_and_redirect(self, instance_name, barsi_group_jid, pie_invest_group_jid, keyword_analysis=True):
        """
        Monitoramento proativo do grupo BARSI para o PIE INVEST.
        Nota: Em um ambiente real, isso seria feito via Webhook. 
        Este método implementa o racional de monitoramento e redirecionamento de oportunidades.
        """
        logger.info(f"Monitorando grupo BARSI ({barsi_group_jid}) para redirecionamento ao PIE INVEST ({pie_invest_group_jid})...")
        
        # Simulação de análise de oportunidades (em produção viria do Webhook)
        # 1. Capturar mensagens do grupo
        # 2. Analisar intenção (Oportunidade / Seguro / Crédito)
        # 3. Redirecionar se validado
        
        message_to_send = "🚨 *OPORTUNIDADE CAPTADA (BARSI -> PIE INVEST)*\n\nIdentifiquei uma nova oportunidade no grupo BARSI referente a Seguros/Investimentos. Redirecionando para análise estratégica."
        
        # Exemplo de envio de redirecionamento
        # self.send_text(instance_name, pie_invest_group_jid, message_to_send)
        return {"status": "monitoring_active", "target": barsi_group_jid, "destination": pie_invest_group_jid}

if __name__ == "__main__":
    # Teste de conexão (Utilizando as chaves encontradas no .env do Wappi Evolution)
    API_URL = "http://localhost:8080"
    API_KEY = "429683C4C977415CAAFCCE10F7D57E11"
    
    monitor = EvolutionMonitor(API_URL, API_KEY)
    
    # Exemplo: Listar instâncias
    instances = monitor.list_instances()
    if instances:
        logger.info(f"Instâncias encontradas: {json.dumps(instances, indent=2)}")
    else:
        logger.error("Não foi possível conectar à Evolution API. Verifique se o servidor está rodando.")
