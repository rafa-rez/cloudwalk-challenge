import os
import logging
from functools import lru_cache
from typing import Optional
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Configuracao de Logging
logger = logging.getLogger(__name__)

# Constantes de Configuracao
PERSIST_DIRECTORY = "./chroma_db"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
SEARCH_K = 4  # Aumentado para fornecer mais contexto

@lru_cache(maxsize=1)
def get_embedding_function():
    """
    Inicializa e faz cache do modelo de embeddings.
    Usa lru_cache para garantir que o modelo so seja carregado na memoria uma vez (Singleton).

    Returns:
    - HuggingFaceEmbeddings: Instancia do modelo de embeddings.
    """
    logger.info(f"Carregando modelo de embeddings: {EMBEDDING_MODEL_NAME}")
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

def get_vectorstore() -> Chroma:
    """
    Retorna a instancia do banco vetorial ChromaDB configurada.
    
    Returns:
    - Chroma: Cliente do banco de dados conectado ao diretorio persistente.
    """
    if not os.path.exists(PERSIST_DIRECTORY):
        logger.error(f"Diretorio do banco vetorial nao encontrado: {PERSIST_DIRECTORY}")
        # Em producao, poderia levantar uma excecao critica aqui
    
    embedding_function = get_embedding_function()
    
    vectorstore = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embedding_function
    )
    return vectorstore

def query_rag(query: str) -> str:
    """
    Realiza uma busca por similaridade no banco vetorial e formata o contexto com fontes.

    O retorno inclui o conteudo e a URL de origem (metadata) para que o LLM possa citar a fonte.

    Parameters:
    - query (str): A pergunta ou termo de busca.

    Returns:
    - str: Contexto recuperado formatado com origem ou mensagem de erro.
    """
    if not query or not query.strip():
        logger.warning("Consulta RAG recebida vazia.")
        return "Consulta vazia."

    try:
        logger.info(f"Consultando RAG para: {query}")
        db = get_vectorstore()
        
        # Recupera os documentos mais similares
        retriever = db.as_retriever(search_kwargs={"k": SEARCH_K})
        docs = retriever.invoke(query)
        
        if not docs:
            logger.warning("Nenhum documento encontrado no RAG para a query.")
            return "Nenhuma informacao encontrada na base de conhecimento interna."

        # Formatacao enriquecida: Inclui a fonte (source) junto com o conteudo
        formatted_context = []
        for doc in docs:
            source = doc.metadata.get("source", "Fonte desconhecida")
            content = doc.page_content.replace("\n", " ") # Remove quebras de linha excessivas
            formatted_context.append(f"[Fonte: {source}]\nConteudo: {content}")

        return "\n\n".join(formatted_context)

    except Exception as e:
        logger.error(f"Erro critico ao consultar RAG: {str(e)}", exc_info=True)
        return "Erro interno ao acessar a base de conhecimento."