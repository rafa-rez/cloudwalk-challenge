# Arquivo: app/core/vector_store.py
import os
import logging
from functools import lru_cache
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Configurações
logger = logging.getLogger(__name__)
PERSIST_DIRECTORY = "./chroma_db"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
SEARCH_K = 4

@lru_cache(maxsize=1)
def get_embedding_function():
    logger.info(f"Carregando embeddings: {EMBEDDING_MODEL_NAME}")
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

def get_vectorstore() -> Chroma:
    if not os.path.exists(PERSIST_DIRECTORY):
        logger.error(f"Banco vetorial não encontrado em: {PERSIST_DIRECTORY}")
    
    return Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=get_embedding_function()
    )

def query_rag(query: str) -> str:
    if not query or not query.strip(): return "Consulta vazia."
    try:
        db = get_vectorstore()
        docs = db.as_retriever(search_kwargs={"k": SEARCH_K}).invoke(query)
        if not docs: return "Nenhuma informação encontrada."
        
        formatted = []
        for doc in docs:
            src = doc.metadata.get("source", "Fonte desconhecida")
            content = doc.page_content.replace("\n", " ")
            formatted.append(f"[Fonte: {src}]\nConteúdo: {content}")
            
        return "\n\n".join(formatted)
    except Exception as e:
        logger.error(f"Erro RAG: {e}")
        return "Erro ao acessar base de conhecimento."