import logging
from langchain_core.messages import SystemMessage, AIMessage
from app.core.config import llm
from app.agents.support.tools import get_user_profile, check_transfer_status

logger = logging.getLogger(__name__)

def support_node(state):
    user_id = state["user_id"]
    messages = state["messages"]
    
    tools = [get_user_profile, check_transfer_status]
    llm_with_tools = llm.bind_tools(tools)
    
    system_message = SystemMessage(content=(
        f"Você é um Assistente Técnico. Cliente ID: {user_id}.\n"
        "Objetivo: Resolver problemas de conta.\n"
        "DIRETRIZES:\n"
        "1. Perguntou saldo/dados? -> USE 'get_user_profile'.\n"
        "2. Relatou erro/falha? -> USE 'check_transfer_status'.\n"
        "3. NÃO invente dados."
    ))
    
    final_content = "Erro ao processar suporte."
    
    try:
        response = llm_with_tools.invoke([system_message] + messages)
        final_content = response.content

        if response.tool_calls:
            tool_outputs = []
            for call in response.tool_calls:
                args = call["args"]
                if "user_id" not in args: args["user_id"] = user_id # Injeta ID se faltar
                
                tool_func = {
                    "get_user_profile": get_user_profile,
                    "check_transfer_status": check_transfer_status
                }.get(call["name"])
                
                if tool_func:
                    try:
                        res = tool_func.invoke(args)
                        tool_outputs.append(SystemMessage(content=f"Sistema: {res}"))
                    except Exception as e:
                        tool_outputs.append(SystemMessage(content=f"Erro Tool: {e}"))
            
            final_answer = llm.invoke([system_message] + messages + tool_outputs)
            final_content = final_answer.content

    except Exception as e:
        logger.error(f"Support Error: {e}")
        final_content = "Desculpe, o sistema de suporte está instável."
    
    return {
        "final_response": final_content,
        "messages": [AIMessage(content=final_content)]
    }