# app/core/state.py
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    O Estado Global do Swarm.
    Contém o histórico de mensagens, ID do usuário e dados de controle de fluxo.
    """
    messages: Annotated[list, add_messages]
    user_id: str
    next_agent: str
    final_response: str
    retry_count: int