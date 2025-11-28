# app/core/config.py
import os
import logging
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# 1. Carrega Variáveis de Ambiente
load_dotenv()

# 2. Configuração Central de Logging
# Evita ter que configurar basicConfig em todo arquivo
def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = get_logger("CoreConfig")

# 3. Configuração Singleton do LLM
# Todos os agentes usarão esta instância
GROQ_API_KEY = os.getenv("CHAVE_GROQ")

if not GROQ_API_KEY:
    logger.warning("CHAVE_GROQ não encontrada no .env. O sistema pode falhar.")

llm = ChatGroq(
    temperature=0, 
    model_name=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
    api_key=GROQ_API_KEY
)