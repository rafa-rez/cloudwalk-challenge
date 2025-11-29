import logging
from langchain_core.messages import SystemMessage, AIMessage
from app.core.config import llm
from app.agents.support.tools import get_user_profile, check_transfer_status

logger = logging.getLogger(__name__)

def support_node(state: dict) -> dict:
    """
    Agente de Suporte Técnico.
    Responsável por operações sensíveis na conta do usuário e verificação de status.

    Args:
        state (dict): Estado atual contendo user_id e mensagens.

    Returns:
        dict: Resposta processada e atualização de estado.
    """
    user_id = state["user_id"]
    messages = state["messages"]
    
    tools = [get_user_profile, check_transfer_status]
    llm_with_tools = llm.bind_tools(tools)
    
    system_message = SystemMessage(content=(
        f"Você é um Assistente Técnico. Cliente ID: {user_id}.\n"
        "Objetivo: Resolver problemas de conta e fornecer dados cadastrais.\n"
        "DIRETRIZES:\n"
        "1. Para saldo/dados -> USE 'get_user_profile'.\n"
        "2. Para erro/falha/bloqueio -> USE 'check_transfer_status'.\n"
        "3. NÃO alucine dados."
    ))
    
    final_content = "Erro ao processar solicitação de suporte."
    
    try:
        response = llm_with_tools.invoke([system_message] + messages)
        final_content = response.content

        if response.tool_calls:
            tool_outputs = []
            for call in response.tool_calls:
                args = call["args"]
                if "user_id" not in args: args["user_id"] = user_id # Injeção de dependência (ID)
                
                tool_func = {
                    "get_user_profile": get_user_profile,
                    "check_transfer_status": check_transfer_status
                }.get(call["name"])
                
                if tool_func:
                    try:
                        res = tool_func.invoke(args)
                        tool_outputs.append(SystemMessage(content=f"Sistema: {res}"))
                    except Exception as e:
                        tool_outputs.append(SystemMessage(content=f"Erro na Ferramenta: {e}"))
            
            # Segunda passada no LLM com os dados da ferramenta
            final_answer = llm.invoke([system_message] + messages + tool_outputs)
            final_content = final_answer.content

    except Exception as e:
        logger.error(f"Erro crítico no Agente de Suporte: {e}")
        final_content = "Desculpe, o sistema de suporte está temporariamente indisponível."
    
    return {
        "final_response": final_content,
        "messages": [AIMessage(content=final_content)]
    }