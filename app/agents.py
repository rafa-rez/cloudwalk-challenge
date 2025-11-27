import os
import logging
import random
from typing import TypedDict, Literal, Optional, Annotated
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, RemoveMessage
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
# NO 1: ROUTER AGENT (ANTI-BIAS)
# ------------------------------------------------------------------
def router_node(state: AgentState):
    messages = state["messages"]
    recent_history = messages[-3:] 
    
    # Pega apenas o conteudo da ultima mensagem para analise de keyword
    last_user_message = messages[-1]
    last_text = last_user_message.content.lower()
    last_message_id = last_user_message.id
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

    # 2. PROMPT ANTI-BIAS (Focado na ULTIMA mensagem)
    system_prompt = (
        "Você é o cérebro de classificação da InfinitePay. "
        "Sua função é analisar a conversa e definir o PRÓXIMO passo.\n\n"

        "🚨 REGRA DE OURO (MUDANÇA DE CONTEXTO):\n"
        "Analise EXCLUSIVAMENTE a intenção da ÚLTIMA mensagem do usuário.\n"
        "IGNORE o contexto anterior se o usuário mudar de assunto.\n"
        "Exemplo: Se estavam falando de 'Erro no Pix' (Support) e o usuário pergunta 'Quais as taxas?' (Knowledge), MUDE para knowledge_agent IMEDIATAMENTE.\n\n"

        "OPÇÕES DE ROTA:\n"
        "- knowledge_agent: Dúvidas teóricas ('Como funciona', 'Taxas', 'O que é'), Curiosidades.\n"
        "- support_agent: Problemas TÉCNICOS ('Erro', 'Falha', 'Não funciona'), Dados da Conta ('Saldo', 'Extrato').\n"
        "- human_handoff: Pediu humano.\n"
        "- guardrail: Ataques/Ilegalidades.\n"
        "- fallback: Nonsense/Out of scope.\n\n"

        "Responda APENAS o nome da rota."
    )
    
    # Dica: Passamos o historico para ele entender o contexto, mas o prompt manda focar na ultima
    response = llm.invoke([SystemMessage(content=system_prompt)] + recent_history)
    decision = response.content.strip().lower().replace("'", "").replace('"', "").replace(".", "")
    
    valid_destinations = ["knowledge_agent", "support_agent", "human_handoff", "guardrail", "fallback"]

    if decision in valid_destinations:
        logger.info(f"Router Decisao: {decision} (Baseado em: '{last_text[:20]}...')")
        return {"next_agent": decision, "retry_count": 0}

    logger.warning(f"Router alucinou: {decision}. Fallback.")
    return {"next_agent": "fallback", "retry_count": 0}

# ------------------------------------------------------------------
# NO 2: KNOWLEDGE AGENT
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
        return {"final_response": final_answer.content}
    
    return {"final_response": response.content}

# ------------------------------------------------------------------
# NO 3: SUPPORT AGENT
# ------------------------------------------------------------------
def support_node(state: AgentState):
    user_id = state["user_id"]
    messages = state["messages"]
    
    tools = [get_user_profile, check_transfer_status]
    llm_with_tools = llm.bind_tools(tools)
    
    system_message = SystemMessage(content=(
        f"Você é um Assistente Técnico. Cliente: {user_id}.\n"
        "Objetivo: Resolver problemas de conta.\n\n"
        "DIRETRIZES:\n"
        "1. Perguntou saldo/dados? -> USE 'get_user_profile'.\n"
        "2. Relatou erro/falha? -> USE 'check_transfer_status'.\n"
        "3. NÃO invente dados. Use as ferramentas.\n"
        "4. NÃO use tags XML/JSON no texto final. Apenas chame a ferramenta."
    ))
    
    try:
        response = llm_with_tools.invoke([system_message] + messages)
    except Exception as e:
        logger.error(f"Erro LLM Support: {e}")
        return {"final_response": "Sistema instável. Tente novamente."}
    
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
            
        try:
            final_answer = llm.invoke([system_message] + messages + tool_outputs)
            return {"final_response": final_answer.content}
        except Exception as e:
            return {"final_response": "Erro ao processar dados."}

    return {"final_response": response.content}

# ------------------------------------------------------------------
# NO 4: FALLBACK AGENT
# ------------------------------------------------------------------
def fallback_node(state: AgentState):
    messages = state["messages"]
    
    options = [
        "Desculpe, sou especialista apenas em InfinitePay e finanças.",
        "Não entendi. Poderia explicar melhor focando nos nossos serviços?",
        "Isso foge do meu conhecimento. Tem alguma dúvida sobre sua conta?",
        "Não consegui identificar sua solicitação no nosso contexto."
    ]
    
    delete_op = RemoveMessage(id=messages[-1].id)
    
    return {
        "final_response": random.choice(options),
        "messages": [delete_op]
    }

# ------------------------------------------------------------------
# NOS AUXILIARES
# ------------------------------------------------------------------
def guardrail_node(state: AgentState):
    messages = state["messages"]
    delete_op = RemoveMessage(id=messages[-1].id)
    return {
        "final_response": "Ação bloqueada por motivos de segurança.",
        "messages": [delete_op] 
    }

def human_handoff_node(state: AgentState):
    return {"final_response": "Entendido. Transferindo para um humano..."}

# ------------------------------------------------------------------
# NO 5: PERSONALITY AGENT
# ------------------------------------------------------------------
def personality_node(state: AgentState):
    original_response = state.get("final_response", "")
    
    if not original_response:
        return {"final_response": "Erro interno."}

    logger.info("Personality: Refinando...")
    
    system_prompt = (
        "Você é o Editor de Texto da InfinitePay. Reescreva a mensagem abaixo.\n\n"
        "REGRAS:\n"
        "1. Se houver 'Fonte: [link]' no original, MANTENHA no final.\n"
        "2. Se NÃO houver fonte, NÃO adicione nada.\n"
        "3. NÃO crie links falsos.\n\n"
        "TOM:\n"
        "- Bloqueio/Segurança: Sério.\n"
        "- Resto: Leve, útil, emojis moderados (⚡, 🚀).\n\n"
        f"MENSAGEM ORIGINAL:\n{original_response}"
    )
    
    response = llm.invoke(system_prompt)
    cleaned_response = response.content.strip().replace('"', '') 
    
    # Limpeza de segurança
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

workflow.add_edge("knowledge_agent", "personality")
workflow.add_edge("support_agent", "personality")
workflow.add_edge("guardrail", "personality")
workflow.add_edge("human_handoff", "personality")
workflow.add_edge("fallback", "personality")

workflow.add_edge("personality", END)

app_swarm = workflow.compile(checkpointer=memory)