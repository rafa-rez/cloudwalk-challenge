import streamlit as st
import requests
import uuid
import time
from datetime import datetime
from app.frontend.components.visualizer import render_modern_flow

def render_tab_architecture(api_url: str):
    """
    Renderiza a aba de arquitetura "Stateless".
    
    Permite enviar requisições isoladas para visualizar o comportamento do roteador
    sem influência de memória de contexto anterior.

    Args:
        api_url (str): URL base do endpoint da API.
    """
    col1, col2 = st.columns([1, 1.5])
    
    # --- Painel de Controle (Esquerda) ---
    with col1:
        st.subheader("Simulador de Arquitetura")
        st.info("Visualização técnica: Cada mensagem é processada isoladamente (Stateless).")
        
        prompt = st.text_area("Input:", height=100, placeholder="Ex: Como funciona o Pix?")
        
        if st.button("Enviar", type="primary"):
            if prompt:
                # Gera UUID novo para garantir que o backend trate como nova sessão
                temp_id = f"stateless_{str(uuid.uuid4())}"
                start_ts = time.time()
                
                with st.spinner("Processando..."):
                    try:
                        payload = {"message": prompt, "user_id": temp_id}
                        response = requests.post(api_url, json=payload)
                        data = response.json()
                        elapsed = time.time() - start_ts
                        
                        agent_resp = data["response"]
                        agent_used = data["agent_used"]
                        
                        # Atualiza Estado da Sessão
                        st.session_state.last_agent = agent_used
                        st.session_state.last_response = agent_resp
                        
                        # Registro de Auditoria
                        if "audit_log" not in st.session_state:
                            st.session_state.audit_log = []
                            
                        st.session_state.audit_log.insert(0, {
                            "time": datetime.now().strftime("%H:%M:%S"),
                            "input": prompt,
                            "output": agent_resp,
                            "agent": agent_used,
                            "latency": f"{elapsed:.2f}s"
                        })
                        
                    except Exception as e:
                        st.error(f"Erro de comunicação com a API: {e}")

        if "last_response" in st.session_state:
            st.success(f"🤖 **Resposta:** {st.session_state.last_response}")

    # --- Visualizador de Fluxo (Direita) ---
    with col2:
        st.subheader("Fluxo de Decisão")
        st.markdown("---")
        active = st.session_state.get("last_agent", None)
        render_modern_flow(active)

    # --- Tabela de Logs ---
    st.markdown("### 📜 Log da Sessão (Debug)")
    if "audit_log" in st.session_state and st.session_state.audit_log:
        rows_html = ""
        for log in st.session_state.audit_log:
            color = "#aaa"
            if "support" in log['agent']: color = "#ffa500"
            elif "knowledge" in log['agent']: color = "#00bfff"
            elif "guardrail" in log['agent']: color = "#ff4b4b"
            elif "fallback" in log['agent']: color = "#ffff00"
            elif "human" in log['agent']: color = "#d87093"

            rows_html += f"""<tr>
                <td>{log['time']}</td>
                <td>{log['input']}</td>
                <td><div class="log-output">{log['output']}</div></td>
                <td style="color: {color}; font-weight: bold;">{log['agent']}</td>
                <td>{log['latency']}</td>
            </tr>"""
        
        full_table = f"""
        <div class="log-container">
        <table class="log-table">
        <thead>
        <tr>
        <th width="10%">Hora</th>
        <th width="20%">Input</th>
        <th width="45%">Output</th>
        <th width="15%">Agente</th>
        <th width="10%">Tempo</th>
        </tr>
        </thead>
        <tbody>
        {rows_html}
        </tbody>
        </table>
        </div>
        """
        st.markdown(full_table, unsafe_allow_html=True)
    else:
        st.info("O histórico técnico aparecerá aqui.")