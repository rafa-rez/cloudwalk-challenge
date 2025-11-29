from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    Define a estrutura de estado global compartilhada entre os nós do grafo (Swarm).

    Attributes:
        messages (list): Histórico de mensagens da conversa (LangChain Message objects).
        user_id (str): Identificador único da sessão do usuário.
        next_agent (str): Próximo nó a ser executado no grafo.
        final_response (str): Texto final gerado para ser enviado ao usuário.
        retry_count (int): Contador para controle de loops e handoff.
    """
    messages: Annotated[list, add_messages]
    user_id: str
    next_agent: str
    final_response: str
    retry_count: int