from langchain_core.tools import tool
from app.core.database import MOCK_DB

@tool
def get_user_profile(user_id: str) -> str:
    """
    Consulta dados cadastrais e saldo atual do usuário no banco de dados.
    """
    if not user_id: return "Erro: ID do usuário não fornecido."
    
    clean_id = str(user_id).strip().lower()
    # Tenta busca exata (lower) ou fallback para original
    user = MOCK_DB.get(clean_id) or MOCK_DB.get(str(user_id).strip())
    
    if user: return str(user)
    return f"Usuário '{user_id}' não encontrado na base."

@tool
def check_transfer_status(user_id: str) -> str:
    """
    Verifica restrições de conta (bloqueios, inatividade) para operações financeiras.
    """
    clean_id = str(user_id).strip().lower()
    user = MOCK_DB.get(clean_id) or MOCK_DB.get(str(user_id).strip())
    
    if not user: return "Usuário não encontrado."
    
    if user['status'] == 'blocked_fraud_check':
        return "BLOQUEIO CRÍTICO: Conta sob análise de fraude."
    if user['status'] == 'inactive':
        return "CONTA INATIVA: Necessária atualização cadastral."
    if user['balance'] < 0:
        return f"SALDO INSUFICIENTE: Saldo negativo ({user['balance']})."

    return "Conta ativa e operacional."