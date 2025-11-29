import os
import logging
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

def get_logger(name: str) -> logging.Logger:
    """
    Configura e retorna um logger padronizado para a aplicação.

    Evita a duplicação de handlers e garante formatação consistente.

    Args:
        name (str): Nome do módulo chamador.

    Returns:
        logging.Logger: Instância configurada do logger.
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
    return logger

logger = get_logger("CoreConfig")

GROQ_API_KEY = os.getenv("CHAVE_GROQ")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if not GROQ_API_KEY:
    logger.warning("Variável de ambiente CHAVE_GROQ não detectada. O sistema pode apresentar falhas.")

# Instância Singleton do LLM para uso compartilhado entre agentes
llm = ChatGroq(
    temperature=0, 
    model_name=GROQ_MODEL,
    api_key=GROQ_API_KEY
)