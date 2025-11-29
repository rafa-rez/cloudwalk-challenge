import logging
from langchain_core.tools import tool
from duckduckgo_search import DDGS
from app.core.vector_store import query_rag

logger = logging.getLogger(__name__)

@tool
def search_infinitepay_knowledge(query: str) -> str:
    """
    Consulta a base de conhecimento oficial da InfinitePay (RAG).
    Ideal para dúvidas sobre taxas, produtos, maquininhas e processos.
    """
    return query_rag(query)

@tool
def web_search(query: str) -> str:
    """
    Realiza busca na web em tempo real utilizando DuckDuckGo.
    Utilize para fatos recentes, cotações ou informações externas à InfinitePay.
    """
    try:
        logger.info(f"Executando Web Search: {query}")
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            
            if not results:
                return "Nenhum resultado relevante encontrado na web."
            
            formatted_results = [f"- {r['title']}: {r['body']}" for r in results]
            return "\n".join(formatted_results)
            
    except Exception as e:
        logger.error(f"Falha no Web Search: {e}")
        return f"Erro ao realizar busca externa: {str(e)}"