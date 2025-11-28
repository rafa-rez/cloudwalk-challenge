# app/frontend/styles.py

GLOBAL_CSS = """
<style>
    .stApp { background-color: #0e1117; }
    .main .block-container { padding-top: 2rem; padding-bottom: 5rem; }
    
    /* Scrollbar */
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: #1e1e24; }
    ::-webkit-scrollbar-thumb { background: #555; border-radius: 5px; }
    ::-webkit-scrollbar-thumb:hover { background: #7b61ff; }

    /* Estilo para Abas */
   .stTabs [role="tab"] {
    height: 58px !important;
    padding: 14px 32px !important; /* aumenta a largura */
    white-space: pre-wrap;
    background-color: #1e1e24;
    border-radius: 8px;
    color: white;
    font-weight: 600;
    font-size: 1.05rem;
}
    .stTabs [aria-selected="true"] { background-color: #7b61ff; color: white; }
</style>
"""

LOG_TABLE_CSS = """
<style>
    /* Estilo da Tabela de Log */
    .log-container {
        max-height: 400px; overflow-y: auto; border: 1px solid #444;
        border-radius: 8px; background-color: #1e1e24; margin-top: 10px;
    }
    .log-table { width: 100%; border-collapse: collapse; color: #ddd; font-family: sans-serif; font-size: 0.85rem; }
    .log-table th {
        position: sticky; top: 0; background-color: #2b2b35; padding: 12px;
        text-align: left; border-bottom: 2px solid #7b61ff; z-index: 1;
    }
    .log-table td { padding: 10px; border-bottom: 1px solid #333; vertical-align: top; }
    .log-output {
        white-space: pre-wrap; word-wrap: break-word; max-width: 450px;
        color: #ccc; font-family: monospace; background: rgba(0,0,0,0.2);
        padding: 5px; border-radius: 4px;
    }
</style>
"""

TEST_METRICS_CSS = """
<style>
    /* Estilo das Métricas de Teste */
    .metric-box {
        background-color: #262730; padding: 15px; border-radius: 8px;
        border-left: 5px solid #7b61ff; text-align: center; color: white;
    }
    .metric-val { font-size: 2rem; font-weight: bold; margin: 0; }
    .metric-lbl { font-size: 0.9rem; color: #aaa; margin: 0; }
</style>
"""

CIRCUIT_BOARD_CSS = """
<style>
    .circuit-board {
        display: flex; flex-direction: column; align-items: center;
        width: 100%; font-family: 'Source Sans Pro', sans-serif; padding: 20px 0;
    }
    .line-vertical { width: 2px; height: 30px; background-color: #555; }
    .line-horizontal { width: 90%; height: 2px; background-color: #555; margin-bottom: 20px; }
    .agents-row { 
        display: flex; flex-direction: row; gap: 10px; 
        justify-content: center; flex-wrap: wrap; width: 100%; margin-bottom: 20px;
    }
    .node-card {
        background-color: #262730 !important; border: 1px solid #444 !important;
        border-radius: 8px; padding: 10px; width: 130px; text-align: center;
        transition: all 0.3s ease; opacity: 0.5; color: #ffffff !important;
        position: relative; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .node-title { font-weight: 800; font-size: 0.9rem; margin-bottom: 4px; color: #ffffff !important; }
    .node-icon { font-size: 1.5rem; margin-bottom: 5px; }
    .central-node { 
        width: 200px; border: 2px solid #7b61ff !important; 
        opacity: 1 !important; z-index: 2; background-color: #1e1e24 !important;
    }
    .active-node {
        opacity: 1 !important; border: 2px solid #00ff7f !important;
        background-color: #132b1e !important; box-shadow: 0 0 15px rgba(0, 255, 127, 0.6) !important;
        transform: scale(1.05);
    }
    @keyframes pulse-green {
        0% { box-shadow: 0 0 0 0 rgba(0, 255, 127, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(0, 255, 127, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 255, 127, 0); }
    }
    .pulsing { animation: pulse-green 2s infinite; }
</style>
"""