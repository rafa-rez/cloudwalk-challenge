import streamlit as st
import os
import uuid

from app.frontend.styles import GLOBAL_CSS, LOG_TABLE_CSS, TEST_METRICS_CSS
from app.frontend.components.tab_architecture import render_tab_architecture
from app.frontend.components.tab_chat import render_tab_chat
from app.frontend.components.tab_tests import render_tab_tests

# Configuração da Página
st.set_page_config(
    page_title="Rafael Rezende - CloudWalk Swarm",
    page_icon="⚡",
    layout="wide"
)

# Configuração de Ambiente
API_URL = os.getenv("API_URL", "http://localhost:8000/api/chat")

# Injeção de Estilos Globais
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown(LOG_TABLE_CSS, unsafe_allow_html=True)
st.markdown(TEST_METRICS_CSS, unsafe_allow_html=True)

# Inicialização do Estado da Sessão (Session State)
if "chat_session_id" not in st.session_state:
    st.session_state.chat_session_id = str(uuid.uuid4())

if "context_messages" not in st.session_state:
    st.session_state.context_messages = []

if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

def main():
    """
    Função principal de renderização do Frontend Streamlit.
    Gerencia a navegação entre as abas principais da aplicação.
    """
    st.title("Agent Swarm - Rafael Rezende")

    tab1, tab2, tab3 = st.tabs(["🧊 Chat Stateless", "🧠 Chat Stateful", "🧪 Bateria de Testes"])

    with tab1:
        render_tab_architecture(API_URL)

    with tab2:
        render_tab_chat(API_URL)

    with tab3:
        render_tab_tests(API_URL)

if __name__ == "__main__":
    main()