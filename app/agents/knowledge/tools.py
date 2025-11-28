import logging
from langchain_core.tools import tool
from duckduckgo_search import DDGS
from langchain_core.messages import SystemMessage

# Importa a função de RAG que já existe no seu projeto (app/vector_store.py)
from app.core.vector_store import query_rag

logger = logging.getLogger(__name__)

@tool
def search_infinitepay_knowledge(query: str) -> str:
    """
    Busca informacoes oficiais sobre produtos e servicos da InfinitePay.
    Use para dúvidas sobre taxas, maquininhas, cadastro, etc.
    """
    return query_rag(query)

@tool
def web_search(query: str) -> str:
    """Realiza buscas gerais na internet (fatos recentes, cotações, etc)."""
    try:
        logger.info(f"Busca Web: {query}")
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            
            if not results:
                return "Nenhum resultado encontrado."
            
            return "\n".join([f"- {r['title']}: {r['body']}" for r in results])
            
    except Exception as e:
        logger.error(f"Erro Web Search: {e}")
        return f"Erro na busca: {str(e)}"