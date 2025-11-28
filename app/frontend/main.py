# app/frontend/main.py
import streamlit as st
import os
import uuid

# Imports Modulares
from app.frontend.styles import GLOBAL_CSS, LOG_TABLE_CSS, TEST_METRICS_CSS
from app.frontend.components.tab_architecture import render_tab_architecture
from app.frontend.components.tab_chat import render_tab_chat
from app.frontend.components.tab_tests import render_tab_tests

# --- Configuração Inicial ---
st.set_page_config(
    page_title="Rafael Rezende - CloudWalk Swarm",
    page_icon="⚡",
    layout="wide"
)

API_URL = os.getenv("API_URL", "http://localhost:8000/api/chat")

# --- Injeção de CSS ---
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown(LOG_TABLE_CSS, unsafe_allow_html=True)
st.markdown(TEST_METRICS_CSS, unsafe_allow_html=True)

# --- Gerenciamento de Estado Global ---
if "chat_session_id" not in st.session_state:
    st.session_state.chat_session_id = str(uuid.uuid4())
if "context_messages" not in st.session_state:
    st.session_state.context_messages = []
if "audit_log" not in st.session_state:
    st.session_state.audit_log = []

# --- Renderização da Interface ---
st.title("Agent Swarm - Rafael Rezende")

tab1, tab2, tab3 = st.tabs([":🧊 Chat Stateless", "🧠 Chat Stateful", "🧪 Bateria de Testes"])

with tab1:
    render_tab_architecture(API_URL)

with tab2:
    render_tab_chat(API_URL)

with tab3:
    render_tab_tests(API_URL)