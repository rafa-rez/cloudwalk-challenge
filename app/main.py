import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agents import app_swarm
from langchain_core.messages import HumanMessage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("API")

app = FastAPI(title="InfinitePay Agent Swarm API", version="1.2.0")

class UserRequest(BaseModel):
    message: str
    user_id: str

@app.post("/api/chat")
async def chat_endpoint(request: UserRequest):
    logger.info(f"Msg recebida | User: {request.user_id}")
    try:
        # Configura thread_id para manter memoria da conversa
        config = {"configurable": {"thread_id": request.user_id}}
        
        input_data = {
            "messages": [HumanMessage(content=request.message)],
            "user_id": request.user_id
        }
        
        result = app_swarm.invoke(input_data, config=config)
        
        return {
            "response": result.get("final_response", "Sem resposta."),
            "agent_used": result.get("next_agent", "unknown")
        }
        
    except Exception as e:
        logger.error(f"Erro API: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno.")

@app.get("/health")
def health_check():
    return {"status": "ok"}