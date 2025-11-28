# app/frontend/components/visualizer.py
import streamlit as st
import textwrap
from app.frontend.styles import CIRCUIT_BOARD_CSS

def render_modern_flow(active_agent=None):
    
    def get_class(agent_name):
        base = "node-card"
        if active_agent == agent_name:
            return f"{base} active-node pulsing"
        return base

    # Usamos textwrap.dedent para remover a indentação do Python
    # que o Markdown confunde com blocos de código
    html_content = textwrap.dedent(f"""
    <div class="circuit-board">
        <div class="node-card central-node">
            <div class="node-icon">🧠</div>
            <div class="node-title">ROUTER (Stateless)</div>
        </div>
        <div class="line-vertical"></div>
        <div class="line-horizontal"></div>
        <div class="agents-row">
            <div class="{get_class('knowledge_agent')}">
                <div class="node-icon">📚</div>
                <div class="node-title">Knowledge</div>
            </div>
            <div class="{get_class('support_agent')}">
                <div class="node-icon">🛠️</div>
                <div class="node-title">Support</div>
            </div>
            <div class="{get_class('guardrail')}">
                <div class="node-icon">🛡️</div>
                <div class="node-title">Guardrail</div>
            </div>
            <div class="{get_class('human_handoff')}">
                <div class="node-icon">👨‍💼</div>
                <div class="node-title">Humano</div>
            </div>
            <div class="{get_class('fallback')}">
                <div class="node-icon">🤷</div>
                <div class="node-title">Fallback</div>
            </div>
        </div>
        <div class="line-horizontal" style="margin-top: -10px; margin-bottom: 0;"></div>
        <div class="line-vertical"></div>
        <div class="node-card central-node" style="border-color: #ff00ff !important;">
            <div class="node-icon">✨</div>
            <div class="node-title">PERSONALITY</div>
        </div>
    </div>
    """)
    
    # Renderiza CSS + HTML com permissão explícita
    st.markdown(CIRCUIT_BOARD_CSS + html_content, unsafe_allow_html=True)