from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.core.state import AgentState
from app.agents.router.node import router_node
from app.agents.knowledge.node import knowledge_node
from app.agents.support.node import support_node
from app.agents.utils.nodes import guardrail_node, fallback_node, human_handoff_node, personality_node

# Configuração de persistência em memória (Checkpointer)
memory = MemorySaver()

# Inicialização do Grafo de Estado
workflow = StateGraph(AgentState)

# Registro de Nós (Nodes)
workflow.add_node("router", router_node)
workflow.add_node("knowledge_agent", knowledge_node)
workflow.add_node("support_agent", support_node)
workflow.add_node("guardrail", guardrail_node)
workflow.add_node("human_handoff", human_handoff_node)
workflow.add_node("fallback", fallback_node)
workflow.add_node("personality", personality_node)

# Definição do Ponto de Entrada
workflow.set_entry_point("router")

def route_decision(state: AgentState) -> str:
    """Extrai a decisão de roteamento do estado."""
    return state["next_agent"]

# Arestas Condicionais (Roteamento Dinâmico)
workflow.add_conditional_edges("router", route_decision, {
    "knowledge_agent": "knowledge_agent",
    "support_agent": "support_agent",
    "guardrail": "guardrail",
    "human_handoff": "human_handoff",
    "fallback": "fallback",
    "END": END
})

# Arestas de Convergência (Normalização de Saída)
# Todos os fluxos operacionais convergem para o agente de personalidade
workflow.add_edge("knowledge_agent", "personality")
workflow.add_edge("support_agent", "personality")
workflow.add_edge("guardrail", "personality")
workflow.add_edge("human_handoff", "personality")
workflow.add_edge("fallback", "personality")

# Finalização do Fluxo
workflow.add_edge("personality", END)

# Compilação do App Swarm
app_swarm = workflow.compile(checkpointer=memory)