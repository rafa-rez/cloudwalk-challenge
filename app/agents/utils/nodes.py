import random
import logging
from langchain_core.messages import RemoveMessage, AIMessage
from app.core.config import llm

logger = logging.getLogger(__name__)

def fallback_node(state):
    messages = state["messages"]
    options = [
        "Desculpe, sou especialista apenas em InfinitePay e finanças.",
        "Não entendi. Poderia explicar melhor focando nos nossos serviços?",
        "Isso foge do meu conhecimento atual."
    ]
    # Remove input ruim e não salva output
    delete_op = RemoveMessage(id=messages[-1].id)
    return {
        "final_response": random.choice(options),
        "messages": [delete_op]
    }

def guardrail_node(state):
    messages = state["messages"]
    delete_op = RemoveMessage(id=messages[-1].id)
    return {
        "final_response": "🚫 Ação bloqueada por motivos de segurança e compliance.",
        "messages": [delete_op] 
    }

def human_handoff_node(state):
    # Mensagem base que será refinada pela personalidade
    return {
        "final_response": "Entendido. Iniciando processo de transferência para um atendente humano.",
        "messages": [AIMessage(content="[Sistema] Transferindo para atendimento humano...")]
    }

def personality_node(state):
    original_response = state.get("final_response", "")
    origin_agent = state.get("next_agent", "")
    
    if not original_response: return {"final_response": "Erro interno."}
    
    # --- CONFIGURAÇÃO DE FILTRO ---
    # Guardrail e Fallback: Mantemos estáticos (segurança/erro).
    # Human Handoff: AGORA PASSA (foi removido desta lista).
    ignored_agents = ["guardrail", "fallback"]
    
    if origin_agent in ignored_agents:
        return {"final_response": original_response}

    # Se a resposta for muito curta (ex: "Sim"), não gasta token
    if len(original_response) < 5: 
        return {"final_response": original_response}

    system_prompt = (
        "Você é o Editor de Texto da InfinitePay. Melhore a clareza e o tom.\n"
        "REGRAS ESTRITAS:\n"
        "1. Se houver 'Fonte: [url]' no texto original, VOCÊ DEVE MANTER no final.\n"
        "2. Se NÃO houver 'Fonte:' no original, JAMAIS INVENTE ou escreva 'Fonte:'.\n"
        "3. TOM: Útil, direto e amigável. Use emojis moderados (⚡, 🚀, 👨‍💼).\n"
        f"TEXTO ORIGINAL:\n{original_response}"
    )
    
    try:
        response = llm.invoke(system_prompt)
        cleaned = response.content.strip().replace('"', '')
        
        # Validação extra para garantir que não inventou fonte no handoff
        if "Fonte:" in cleaned and "http" not in cleaned:
            cleaned = cleaned.split("Fonte:")[0].strip()
            
        return {"final_response": cleaned}
        
    except Exception as e:
        logger.error(f"Erro no Personality: {e}")
        return {"final_response": original_response}