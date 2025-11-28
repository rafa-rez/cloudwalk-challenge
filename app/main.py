import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.core.workflow import app_swarm
from langchain_core.messages import HumanMessage

# Configuracao de Logging da API
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("API_Gateway")

app = FastAPI(
    title="InfinitePay Agent Swarm API",
    description="API de orquestracao multi-agente com persistencia de estado.",
    version="1.2.0"
)

class UserRequest(BaseModel):
    """Modelo de dados para requisicao de chat."""
    message: str
    user_id: str

class AgentResponse(BaseModel):
    """Modelo de dados para resposta da API."""
    response: str
    agent_used: str
    status: str = "success"

@app.post("/api/chat", response_model=AgentResponse)
async def chat_endpoint(request: UserRequest):
    """
    Endpoint principal de chat.
    
    Funcionalidades:
    - Processa mensagens do usuario.
    - Mantem contexto da conversa (memoria) baseado no user_id.
    - Gerencia excecoes e erros de processamento.

    Args:
        request (UserRequest): Payload JSON contendo mensagem e user_id.

    Returns:
        AgentResponse: Resposta processada pelo enxame de agentes.
    """
    logger.info(f"Requisicao recebida | User ID: {request.user_id}")
    
    try:
        # Configuracao de persistencia: user_id atua como thread_id
        config = {"configurable": {"thread_id": request.user_id}}
        
        # Estado de entrada (apenas o necessario, o resto vem da memoria)
        input_state = {
            "messages": [HumanMessage(content=request.message)],
            "user_id": request.user_id
        }
        
        # Execucao do Grafo
        result = app_swarm.invoke(input_state, config=config)
        
        # Identificacao do agente final (pode ser o proprio router em caso de fallback)
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
            detail="Ocorreu um erro interno ao processar sua solicitacao. Tente novamente."
        )

@app.get("/health")
def health_check():
    """Endpoint de verificacao de saude da aplicacao."""
    return {"status": "operational", "service": "agent-swarm"}