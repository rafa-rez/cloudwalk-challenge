import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.core.workflow import app_swarm

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("API_Gateway")

app = FastAPI(
    title="InfinitePay Agent Swarm API",
    description="Interface de orquestração para sistema multi-agente com persistência de contexto.",
    version="1.2.0"
)

class UserRequest(BaseModel):
    """Payload de entrada para requisições de chat."""
    message: str
    user_id: str

class AgentResponse(BaseModel):
    """Estrutura padronizada de resposta da API."""
    response: str
    agent_used: str
    status: str = "success"

@app.post("/api/chat", response_model=AgentResponse)
async def chat_endpoint(request: UserRequest):
    """
    Processa interações de chat através do orquestrador multi-agente (Swarm).

    Utiliza o `user_id` para manter o estado da sessão no LangGraph e executa
    o fluxo de decisão de forma assíncrona para garantir alta concorrência.

    Args:
        request (UserRequest): Objeto contendo a mensagem do usuário e ID da sessão.

    Returns:
        AgentResponse: Objeto contendo a resposta gerada, o agente responsável e o status.

    Raises:
        HTTPException: Retorna 500 em caso de falhas críticas no processamento do grafo.
    """
    logger.info(f"Requisicao recebida | User ID: {request.user_id}")
    
    try:
        config = {"configurable": {"thread_id": request.user_id}}
        
        input_state = {
            "messages": [HumanMessage(content=request.message)],
            "user_id": request.user_id
        }
        
        # Execução assíncrona (ainvoke) para não bloquear o Event Loop do FastAPI
        result = await app_swarm.ainvoke(input_state, config=config)
        
        agent_used = result.get("next_agent", "router_fallback")
        final_text = result.get("final_response", "Sem resposta gerada.")
        
        logger.info(f"Processamento concluido | Agente: {agent_used}")
        
        return AgentResponse(
            response=final_text,
            agent_used=agent_used
        )
        
    except Exception as e:
        logger.error(f"Erro critico no processamento: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail="Ocorreu um erro interno ao processar sua solicitacao."
        )

@app.get("/health")
def health_check():
    """
    Endpoint para verificação de disponibilidade do serviço (Liveness Probe).
    
    Returns:
        dict: Status operacional do serviço.
    """
    return {"status": "operational", "service": "agent-swarm"}