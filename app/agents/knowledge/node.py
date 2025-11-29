from langchain_core.messages import SystemMessage, AIMessage
from app.core.config import llm
from app.agents.knowledge.tools import search_infinitepay_knowledge, web_search

def knowledge_node(state: dict) -> dict:
    """
    Agente especialista em recuperação de informações (RAG + Web).
    Executa busca em base de conhecimento ou internet para responder dúvidas.

    Args:
        state (dict): Estado atual do grafo contendo histórico de mensagens.

    Returns:
        dict: Atualização de estado com resposta final e mensagens processadas.
    """
    messages = state["messages"]
    
    # Vinculação de ferramentas ao LLM
    tools = [search_infinitepay_knowledge, web_search]
    llm_with_tools = llm.bind_tools(tools)
    
    system_message = SystemMessage(content=(
        "Você é um Especialista da InfinitePay.\n"
        "1. Utilize as ferramentas disponíveis para buscar informações precisas.\n"
        "2. CITAÇÃO OBRIGATÓRIA: Ao final, cite a fonte se a ferramenta fornecer link. Formato: 'Fonte: [url]'\n"
        "3. Se não houver link disponível, não invente."
    ))
    
    # Execução inicial do modelo
    response = llm_with_tools.invoke([system_message] + messages)
    final_content = response.content
    
    # Processamento de chamadas de ferramentas (Tool Calls)
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
                    tool_outputs.append(SystemMessage(content=f"Dados recuperados: {res}"))
                except Exception as e:
                    tool_outputs.append(SystemMessage(content=f"Erro na ferramenta: {str(e)}"))
        
        # Geração da resposta final com base nos dados recuperados
        final_answer = llm.invoke([system_message] + messages + tool_outputs)
        final_content = final_answer.content
    
    return {
        "final_response": final_content,
        "messages": [AIMessage(content=final_content)]
    }