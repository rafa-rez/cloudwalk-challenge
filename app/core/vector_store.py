import os
import logging
from functools import lru_cache
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

# Configurações do Vector Store
PERSIST_DIRECTORY = "./chroma_db"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
SEARCH_K = 4

@lru_cache(maxsize=1)
def get_embedding_function() -> HuggingFaceEmbeddings:
    """
    Inicializa e armazena em cache o modelo de embeddings.
    
    Returns:
        HuggingFaceEmbeddings: Instância do modelo configurado.
    """
    logger.info(f"Carregando modelo de embeddings: {EMBEDDING_MODEL_NAME}")
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

def get_vectorstore() -> Chroma:
    """
    Recupera a instância do banco vetorial ChromaDB.

    Returns:
        Chroma: Cliente conectado ao diretório de persistência.
    """
    if not os.path.exists(PERSIST_DIRECTORY):
        logger.error(f"Diretório do banco vetorial não encontrado: {PERSIST_DIRECTORY}")
    
    return Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=get_embedding_function()
    )

def query_rag(query: str) -> str:
    """
    Realiza busca semântica na base de conhecimento (RAG).

    Args:
        query (str): Pergunta ou termo de busca do usuário.

    Returns:
        str: Contexto formatado com fontes ou mensagem de erro.
    """
    if not query or not query.strip():
        return "Consulta vazia."

    try:
        db = get_vectorstore()
        retriever = db.as_retriever(search_kwargs={"k": SEARCH_K})
        docs = retriever.invoke(query)
        
        if not docs:
            return "Nenhuma informação relevante encontrada na base de conhecimento."
        
        formatted_context = []
        for doc in docs:
            src = doc.metadata.get("source", "Fonte desconhecida")
            content = doc.page_content.replace("\n", " ")
            formatted_context.append(f"[Fonte: {src}]\nConteúdo: {content}")
            
        return "\n\n".join(formatted_context)
        
    except Exception as e:
        logger.error(f"Falha na consulta RAG: {e}")
        return "Erro interno ao acessar base de conhecimento."