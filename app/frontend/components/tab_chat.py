# app/frontend/components/tab_chat.py
import streamlit as st
import requests
import uuid

def reset_conversation():
    st.session_state.chat_session_id = str(uuid.uuid4())
    st.session_state.context_messages = []
    st.toast("Memória limpa! Nova thread iniciada.", icon="🧹")

def get_agent_badge(agent_name):
    """
    Retorna HTML formatado com a cor correspondente ao agente.
    """
    if not agent_name: return ""
    
    # Definição de Cores e Ícones
    styles = {
        "support_agent":   {"color": "#ffa500", "icon": "🛠️", "label": "Support Agent"},
        "knowledge_agent": {"color": "#00bfff", "icon": "📚", "label": "Knowledge Agent"},
        "guardrail":       {"color": "#ff4b4b", "icon": "🛡️", "label": "Guardrail"},
        "human_handoff":   {"color": "#d87093", "icon": "👨‍💼", "label": "Human Handoff"},
        "fallback":        {"color": "#ffff00", "icon": "🤷", "label": "Fallback"},
        "router":          {"color": "#bc8f8f", "icon": "🧠", "label": "Router Direct"},
    }
    
    # Fallback para agentes desconhecidos
    style = styles.get(agent_name, {"color": "#888", "icon": "🤖", "label": agent_name})
    
    # HTML da Etiqueta (Badge)
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
    st.subheader("💬 Assistente Virtual (Com Memória)")
    
    # Header com ID e Botão
    c1, c2 = st.columns([6, 1])
    with c1:
        st.caption(f"Sessão ID: `{st.session_state.chat_session_id}` (Memória Ativa)")
    with c2:
        if st.button("🧹 Reset", help="Apagar memória"):
            reset_conversation()
            st.rerun()

    chat_container = st.container(height=500)
    
    # --- RENDERIZAÇÃO DO HISTÓRICO ---
    with chat_container:
        if not st.session_state.context_messages:
            st.markdown("<div style='text-align: center; color: #666;'>Inicie a conversa...</div>", unsafe_allow_html=True)
        
        for msg in st.session_state.context_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
                # Se for mensagem do assistente e tiver o dado do agente, mostra o log
                if msg["role"] == "assistant" and "agent" in msg:
                    st.markdown(get_agent_badge(msg["agent"]), unsafe_allow_html=True)

    # --- INPUT DO USUÁRIO ---
    if user_input := st.chat_input("Digite sua dúvida..."):
        # 1. Adiciona input visualmente
        st.session_state.context_messages.append({"role": "user", "content": user_input})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)

        # 2. Envia para API
        try:
            payload = {"message": user_input, "user_id": st.session_state.chat_session_id}
            
            with st.spinner("Digitando..."):
                response = requests.post(api_url, json=payload)
                data = response.json()
                agent_resp = data["response"]
                agent_used = data["agent_used"]
                
                # 3. Salva a resposta COM O METADADO DO AGENTE
                st.session_state.context_messages.append({
                    "role": "assistant", 
                    "content": agent_resp,
                    "agent": agent_used  # <--- Importante para o log aparecer depois
                })
                
                # 4. Renderiza a resposta imediatamente
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(agent_resp)
                        # Renderiza o badge logo após a resposta
                        st.markdown(get_agent_badge(agent_used), unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Erro de conexão: {e}")