from langchain_core.messages import SystemMessage, AIMessage
from app.core.config import llm
from app.agents.knowledge.tools import search_infinitepay_knowledge, web_search

def knowledge_node(state):
    messages = state["messages"]
    
    # Define as ferramentas exclusivas deste agente
    tools = [search_infinitepay_knowledge, web_search]
    llm_with_tools = llm.bind_tools(tools)
    
    system_message = SystemMessage(content=(
        "Voce e um Especialista da InfinitePay.\n"
        "1. Use as ferramentas para buscar informacoes.\n"
        "2. IMPORTANTE: Ao final da resposta, cite a fonte se a ferramenta fornecer um link. Formato: 'Fonte: [url]'\n"
        "3. Se nao houver link, nao invente."
    ))
    
    # 1. Primeira chamada ao LLM (pode decidir usar tools)
    response = llm_with_tools.invoke([system_message] + messages)
    final_content = response.content
    
    # 2. Execução das Tools (se houver chamadas)
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
        
        # 3. Resposta final pós-tool
        final_answer = llm.invoke([system_message] + messages + tool_outputs)
        final_content = final_answer.content
    
    return {
        "final_response": final_content,
        "messages": [AIMessage(content=final_content)]
    }