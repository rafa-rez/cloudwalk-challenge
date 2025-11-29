import random
import logging
from langchain_core.messages import RemoveMessage, AIMessage
from app.core.config import llm

logger = logging.getLogger(__name__)

def fallback_node(state: dict) -> dict:
    """
    Nó de Fallback. Acionado quando a intenção do usuário não é compreendida.
    Remove a mensagem confusa do histórico para manter o contexto limpo.
    """
    messages = state["messages"]
    options = [
        "Desculpe, sou especialista apenas em InfinitePay e finanças.",
        "Não entendi. Poderia reformular focando em nossos serviços?",
        "Esse assunto foge do meu conhecimento técnico atual."
    ]
    
    # Remove input do usuário do histórico (Efêmero)
    delete_op = RemoveMessage(id=messages[-1].id)
    
    return {
        "final_response": random.choice(options),
        "messages": [delete_op]
    }

def guardrail_node(state: dict) -> dict:
    """
    Nó de Segurança (Guardrail).
    Bloqueia interações maliciosas e remove o prompt tóxico do histórico.
    """
    messages = state["messages"]
    delete_op = RemoveMessage(id=messages[-1].id)
    
    return {
        "final_response": "🚫 Ação bloqueada por motivos de segurança e compliance.",
        "messages": [delete_op] 
    }

def human_handoff_node(state: dict) -> dict:
    """
    Nó de Transbordo Humano.
    Inicia o protocolo de transferência para atendimento nível 2.
    """
    return {
        "final_response": "Entendido. Iniciando processo de transferência para um atendente humano.",
        "messages": [AIMessage(content="[Sistema] Transferindo para atendimento humano...")]
    }

def personality_node(state: dict) -> dict:
    """
    Agente de Personalidade (Editor).
    Refina a resposta final para adequação ao tom de voz da marca (Tone of Voice).
    
    Aplica filtros para não processar mensagens de erro ou segurança.
    """
    original_response = state.get("final_response", "")
    origin_agent = state.get("next_agent", "")
    
    if not original_response: return {"final_response": "Erro interno de resposta."}
    
    # Agentes que NÃO devem ter resposta reescrita (Segurança/Erro)
    ignored_agents = ["guardrail", "fallback"]
    
    if origin_agent in ignored_agents:
        return {"final_response": original_response}

    # Evita gastar tokens com respostas muito curtas
    if len(original_response) < 5: 
        return {"final_response": original_response}

    system_prompt = (
        "Você é o Editor de Texto da InfinitePay. Refine a resposta abaixo.\n"
        "REGRAS RÍGIDAS:\n"
        "1. Se houver 'Fonte: [url]' no texto original, VOCÊ DEVE MANTER no final.\n"
        "2. Se NÃO houver 'Fonte:' no original, JAMAIS INVENTE.\n"
        "3. TOM: Profissional, direto e amigável. Use emojis com moderação (⚡, 🚀, 👨‍💼).\n"
        f"TEXTO ORIGINAL:\n{original_response}"
    )
    
    try:
        response = llm.invoke(system_prompt)
        cleaned = response.content.strip().replace('"', '')
        
        # Sanitização Anti-Alucinação de Fontes
        if "Fonte:" in cleaned and "http" not in cleaned:
            cleaned = cleaned.split("Fonte:")[0].strip()
            
        return {"final_response": cleaned}
        
    except Exception as e:
        logger.error(f"Erro no Agente de Personalidade: {e}")
        return {"final_response": original_response}