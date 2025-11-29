import streamlit as st
import textwrap
from app.frontend.styles import CIRCUIT_BOARD_CSS

def render_modern_flow(active_agent: str = None):
    """
    Renderiza o diagrama de fluxo de agentes (estilo Circuit Board).
    Destaca visualmente o agente ativo no processamento atual.

    Args:
        active_agent (str, optional): Nome do agente ativo para aplicar classe CSS de destaque.
    """
    
    def get_class(agent_name):
        base = "node-card"
        if active_agent == agent_name:
            return f"{base} active-node pulsing"
        return base

    # textwrap.dedent remove a indentação do Python para que o Markdown não interprete como bloco de código
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
    
    st.markdown(CIRCUIT_BOARD_CSS + html_content, unsafe_allow_html=True)