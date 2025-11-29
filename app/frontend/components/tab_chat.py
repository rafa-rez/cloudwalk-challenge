import streamlit as st
import requests
import uuid

def reset_conversation():
    """Reinicia o ID da sessão e limpa o histórico de mensagens local."""
    st.session_state.chat_session_id = str(uuid.uuid4())
    st.session_state.context_messages = []
    st.toast("Memória limpa! Nova thread iniciada.", icon="🧹")

def get_agent_badge(agent_name: str) -> str:
    """
    Gera o HTML de uma 'badge' visual indicando qual agente processou a mensagem.

    Args:
        agent_name (str): Identificador do agente retornado pela API.

    Returns:
        str: String HTML contendo a estilização e ícone do agente.
    """
    if not agent_name: return ""
    
    styles = {
        "support_agent":   {"color": "#ffa500", "icon": "🛠️", "label": "Support Agent"},
        "knowledge_agent": {"color": "#00bfff", "icon": "📚", "label": "Knowledge Agent"},
        "guardrail":       {"color": "#ff4b4b", "icon": "🛡️", "label": "Guardrail"},
        "human_handoff":   {"color": "#d87093", "icon": "👨‍💼", "label": "Human Handoff"},
        "fallback":        {"color": "#ffff00", "icon": "🤷", "label": "Fallback"},
        "router":          {"color": "#bc8f8f", "icon": "🧠", "label": "Router Direct"},
    }
    
    style = styles.get(agent_name, {"color": "#888", "icon": "🤖", "label": agent_name})
    
    return f"""
    <div style="
        display: inline-flex; align-items: center; gap: 5px;
        background-color: rgba(30,30,36, 0.8); 
        border: 1px solid {style['color']}; 
        border-radius: 12px; padding: 2px 10px; 
        font-size: 0.75rem; color: {style['color']}; 
        margin-top: 5px; font-family: monospace;">
        <span>{style['icon']}</span>
        <span>LOG: Classificado como <b>{style['label'].upper()}</b></span>
    </div>
    """

def render_tab_chat(api_url: str):
    """
    Renderiza a interface de chat contextual (Stateful).
    Mantém o histórico visual e interage com a mesma sessão no backend.

    Args:
        api_url (str): URL base do endpoint da API.
    """
    st.subheader("💬 Assistente Virtual (Com Memória)")
    
    c1, c2 = st.columns([6, 1])
    with c1:
        st.caption(f"Sessão ID: `{st.session_state.chat_session_id}` (Memória Ativa)")
    with c2:
        if st.button("🧹 Reset", help="Apagar memória"):
            reset_conversation()
            st.rerun()

    chat_container = st.container(height=500)
    
    # Renderização do Histórico
    with chat_container:
        if not st.session_state.context_messages:
            st.markdown("<div style='text-align: center; color: #666;'>Inicie a conversa...</div>", unsafe_allow_html=True)
        
        for msg in st.session_state.context_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
                # Exibe badge do agente se disponível
                if msg["role"] == "assistant" and "agent" in msg:
                    st.markdown(get_agent_badge(msg["agent"]), unsafe_allow_html=True)

    # Input do Usuário
    if user_input := st.chat_input("Digite sua dúvida..."):
        st.session_state.context_messages.append({"role": "user", "content": user_input})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)

        try:
            payload = {"message": user_input, "user_id": st.session_state.chat_session_id}
            
            with st.spinner("Digitando..."):
                response = requests.post(api_url, json=payload)
                data = response.json()
                agent_resp = data["response"]
                agent_used = data["agent_used"]
                
                # Armazena resposta e metadado do agente
                st.session_state.context_messages.append({
                    "role": "assistant", 
                    "content": agent_resp,
                    "agent": agent_used 
                })
                
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(agent_resp)
                        st.markdown(get_agent_badge(agent_used), unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erro de conexão: {e}")