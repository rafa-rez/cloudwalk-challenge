# app/core/workflow.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Imports do Core
from app.core.state import AgentState

# --- IMPORTS FUTUROS (Passo 3: Agents) ---
# Se for rodar antes de criar os agentes, comente as linhas abaixo
from app.agents.router.node import router_node
from app.agents.knowledge.node import knowledge_node
from app.agents.support.node import support_node
from app.agents.utils.nodes import guardrail_node, fallback_node, human_handoff_node, personality_node

# Configuração de Memória
memory = MemorySaver()

# Definição do Grafo
workflow = StateGraph(AgentState)

# Adicionando Nós (Nodes)
workflow.add_node("router", router_node)
workflow.add_node("knowledge_agent", knowledge_node)
workflow.add_node("support_agent", support_node)
workflow.add_node("guardrail", guardrail_node)
workflow.add_node("human_handoff", human_handoff_node)
workflow.add_node("fallback", fallback_node)
workflow.add_node("personality", personality_node)

# Ponto de Entrada
workflow.set_entry_point("router")

# Lógica Condicional (Edges)
def route_decision(state):
    return state["next_agent"]

workflow.add_conditional_edges("router", route_decision, {
    "knowledge_agent": "knowledge_agent",
    "support_agent": "support_agent",
    "guardrail": "guardrail",
    "human_handoff": "human_handoff",
    "fallback": "fallback",
    "END": END
})

# Convergência para Personalidade
workflow.add_edge("knowledge_agent", "personality")
workflow.add_edge("support_agent", "personality")
workflow.add_edge("guardrail", "personality")
workflow.add_edge("human_handoff", "personality")
workflow.add_edge("fallback", "personality")

# Saída
workflow.add_edge("personality", END)

# Compilação do Swarm
app_swarm = workflow.compile(checkpointer=memory)