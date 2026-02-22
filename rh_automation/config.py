# =============================================================
#  config.py
#  Centraliza todas as configurações em um único lugar.
#  Boas práticas: nunca colocar senhas/chaves diretamente no código.
# =============================================================

import os

from dotenv import load_dotenv  # Lê variáveis do arquivo .env

load_dotenv()  # Carrega o .env para os os.getenv() funcionarem

# Pega a chave de API do Google (definida no arquivo .env)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Nome do modelo Gemini que será usado
MODEL_NAME = "gemini-2.5-flash"
