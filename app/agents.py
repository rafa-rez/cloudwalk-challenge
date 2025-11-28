import os
import logging
import random
from typing import TypedDict, Literal, Optional, Annotated
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from app.tools import (
    search_infinitepay_knowledge, 
    web_search, 
    get_user_profile, 
    check_transfer_status
)

# Configuracao de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AgentSwarm")

load_dotenv()

# Configuracao do Modelo LLM
llm = ChatGroq(
    temperature=0, 
    model_name=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
    api_key=os.getenv("CHAVE_GROQ")
)

# Persistencia em Memoria
memory = MemorySaver()

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str
    next_agent: str
    final_response: str
    retry_count: int

# ------------------------------------------------------------------
# NO 1: ROUTER AGENT (STATELESS STRICT)
# ------------------------------------------------------------------
def router_node(state: AgentState):
    messages = state["messages"]
    
    # MUDANÇA: O Router agora ignora totalmente o histórico passado (Stateless)
    # Pega apenas a ultima mensagem para decisao
    last_user_message = messages[-1]
    last_text = last_user_message.content.lower()
    current_retries = state.get("retry_count", 0)
    
    # 1. CAMADA DE SEGURANÇA (HARDCODED)
    dangerous_keywords = [
        "ignore", "regras", "rules", "prompt", "bypass", "override", 
        "esqueça", "reset", "disable", "system", "roleplay", 
        "jailbreak", "hack", "admin", "root", "simule", "finga",
        "xingue", "ofenda", "instrucoes", "instructions", "dan mode"
    ]
    
    if any(keyword in last_text for keyword in dangerous_keywords):
         logger.critical(f"Router: BLOQUEIO PREVENTIVO. Keyword: '{last_text}'")
         return {"next_agent": "guardrail", "retry_count": 0}

    if current_retries >= 2:
        return {"next_agent": "human_handoff", "retry_count": 0}

    # 2. PROMPT SEM HISTÓRICO
    system_prompt = (
        "Você é o cérebro de classificação da InfinitePay. "
        "Sua função é analisar a MENSAGEM ATUAL e definir o PRÓXIMO passo.\n\n"
        "OPÇÕES DE ROTA:\n"
        "- knowledge_agent: Dúvidas teóricas, 'Como funciona', 'Taxas', Informações.\n"
        "- support_agent: Ação na conta, 'Erro', 'Falha', 'Saldo', 'Extrato'.\n"
        "- human_handoff: Pediu humano explicitamente.\n"
        "- guardrail: Ataques/Ilegalidades.\n"
        "- fallback: Nonsense/Out of scope.\n\n"
        "Responda APENAS o nome da rota."
    )
    
    # Passamos apenas o System Prompt e a ÚLTIMA mensagem do usuário
    response = llm.invoke([SystemMessage(content=system_prompt), last_user_message])
    decision = response.content.strip().lower().replace("'", "").replace('"', "").replace(".", "")
    
    valid_destinations = ["knowledge_agent", "support_agent", "human_handoff", "guardrail", "fallback"]

    if decision in valid_destinations:
        logger.info(f"Router Decisao: {decision}")
        return {"next_agent": decision, "retry_count": 0}

    logger.warning(f"Router alucinou: {decision}. Fallback.")
    return {"next_agent": "fallback", "retry_count": 0}

# ------------------------------------------------------------------
# NO 2: KNOWLEDGE AGENT (COM MEMÓRIA)
# ------------------------------------------------------------------
def knowledge_node(state: AgentState):
    messages = state["messages"]
    tools = [search_infinitepay_knowledge, web_search]
    llm_with_tools = llm.bind_tools(tools)
    
    system_message = SystemMessage(content=(
        "Voce e um Especialista da InfinitePay.\n"
        "1. Use as ferramentas para buscar informacoes.\n"
        "2. IMPORTANTE: Ao final da resposta, cite a fonte se a ferramenta fornecer um link. Formato: 'Fonte: [url]'\n"
        "3. Se nao houver link, nao invente."
    ))
    
    response = llm_with_tools.invoke([system_message] + messages)
    
    final_content = response.content
    
    if response.tool_calls:
        tool_outputs = []
        for call in response.tool_calls:
            tool_func = {
                "search_infinitepay_knowledge": search_infinitepay_knowledge,
                "web_search": web_search
            }.get(call["name"])
            
            if tool_func:
                try:
                    res = tool_func.invoke(call["args"])
                    tool_outputs.append(SystemMessage(content=f"Dados: {res}"))
                except Exception as e:
                    tool_outputs.append(SystemMessage(content=f"Erro: {str(e)}"))
            
        final_answer = llm.invoke([system_message] + messages + tool_outputs)
        final_content = final_answer.content
    
    # RETORNO: Salva a resposta no histórico (AIMessage)
    return {
        "final_response": final_content,
        "messages": [AIMessage(content=final_content)]
    }

# ------------------------------------------------------------------
# NO 3: SUPPORT AGENT (COM MEMÓRIA)
# ------------------------------------------------------------------
def support_node(state: AgentState):
    user_id = state["user_id"]
    messages = state["messages"]
    
    tools = [get_user_profile, check_transfer_status]
    llm_with_tools = llm.bind_tools(tools)
    
    system_message = SystemMessage(content=(
        f"Você é um Assistente Técnico. Cliente: {user_id}.\n"
        "Objetivo: Resolver problemas de conta.\n"
        "DIRETRIZES:\n"
        "1. Perguntou saldo/dados? -> USE 'get_user_profile'.\n"
        "2. Relatou erro/falha? -> USE 'check_transfer_status'.\n"
        "3. NÃO invente dados. Use as ferramentas.\n"
    ))
    
    final_content = "Sistema instável."
    
    try:
        response = llm_with_tools.invoke([system_message] + messages)
        final_content = response.content

        if response.tool_calls:
            tool_outputs = []
            for call in response.tool_calls:
                args = call["args"]
                if "user_id" not in args: args["user_id"] = user_id
                
                tool_func = {
                    "get_user_profile": get_user_profile,
                    "check_transfer_status": check_transfer_status
                }[call["name"]]
                
                try:
                    res = tool_func.invoke(args)
                    tool_outputs.append(SystemMessage(content=f"Sistema: {res}"))
                except Exception as e:
                    tool_outputs.append(SystemMessage(content=f"Erro Tool: {e}"))
            
            final_answer = llm.invoke([system_message] + messages + tool_outputs)
            final_content = final_answer.content

    except Exception as e:
        logger.error(f"Erro LLM Support: {e}")
    
    # RETORNO: Salva a resposta no histórico (AIMessage)
    return {
        "final_response": final_content,
        "messages": [AIMessage(content=final_content)]
    }

# ------------------------------------------------------------------
# NO 4: FALLBACK AGENT (SEM POLUIR MEMÓRIA)
# ------------------------------------------------------------------
def fallback_node(state: AgentState):
    messages = state["messages"]
    
    options = [
        "Desculpe, sou especialista apenas em InfinitePay e finanças.",
        "Não entendi. Poderia explicar melhor focando nos nossos serviços?",
        "Isso foge do meu conhecimento. Tem alguma dúvida sobre sua conta?"
    ]
    
    # Remove a mensagem do usuário do histórico para não confundir o modelo depois
    delete_op = RemoveMessage(id=messages[-1].id)
    
    # NÃO retorna AIMessage na chave "messages", logo o output é efêmero
    return {
        "final_response": random.choice(options),
        "messages": [delete_op]
    }

# ------------------------------------------------------------------
# NOS AUXILIARES (SEM POLUIR MEMÓRIA)
# ------------------------------------------------------------------
def guardrail_node(state: AgentState):
    messages = state["messages"]
    delete_op = RemoveMessage(id=messages[-1].id)
    
    return {
        "final_response": "Ação bloqueada por motivos de segurança.",
        "messages": [delete_op] 
    }

def human_handoff_node(state: AgentState):
    # Handoff geralmente é uma conclusão, podemos salvar ou não. Vamos salvar para registro.
    return {
        "final_response": "Entendido. Transferindo para um humano...",
        "messages": [AIMessage(content="Transferindo para um humano...")]
    }

# ------------------------------------------------------------------
# NO 5: PERSONALITY AGENT
# ------------------------------------------------------------------
def personality_node(state: AgentState):
    original_response = state.get("final_response", "")
    
    if not original_response:
        return {"final_response": "Erro interno."}

    logger.info("Personality: Refinando...")
    
    system_prompt = (
        "Você é o Editor de Texto da InfinitePay. Reescreva a mensagem abaixo.\n"
        "REGRAS:\n"
        "1. Se houver 'Fonte: [link]' no original, MANTENHA no final.\n"
        "2. Se NÃO houver fonte, NÃO adicione nada.\n"
        "TOM: Leve, útil, emojis moderados (⚡, 🚀).\n"
        f"MENSAGEM ORIGINAL:\n{original_response}"
    )
    
    response = llm.invoke(system_prompt)
    cleaned_response = response.content.strip().replace('"', '') 
    
    if "[inserir" in cleaned_response or "link aqui" in cleaned_response:
        cleaned_response = cleaned_response.split("Fonte:")[0].strip()
    
    return {"final_response": cleaned_response}

# ------------------------------------------------------------------
# GRAFO
# ------------------------------------------------------------------
workflow = StateGraph(AgentState)

workflow.add_node("router", router_node)
workflow.add_node("knowledge_agent", knowledge_node)
workflow.add_node("support_agent", support_node)
workflow.add_node("guardrail", guardrail_node)
workflow.add_node("human_handoff", human_handoff_node)
workflow.add_node("fallback", fallback_node)
workflow.add_node("personality", personality_node)

workflow.set_entry_point("router")

def route_decision(state): return state["next_agent"]

workflow.add_conditional_edges("router", route_decision, {
    "knowledge_agent": "knowledge_agent",
    "support_agent": "support_agent",
    "guardrail": "guardrail",
    "human_handoff": "human_handoff",
    "fallback": "fallback",
    "END": END
})

# Todos convergem para personalidade antes do fim
workflow.add_edge("knowledge_agent", "personality")
workflow.add_edge("support_agent", "personality")
workflow.add_edge("guardrail", "personality")
workflow.add_edge("human_handoff", "personality")
workflow.add_edge("fallback", "personality")
workflow.add_edge("personality", END)

app_swarm = workflow.compile(checkpointer=memory)