from langchain_core.tools import tool
from app.core.database import MOCK_DB # Importa o banco centralizado

@tool
def get_user_profile(user_id: str) -> str:
    """Recupera informacoes cadastrais e saldo do usuario."""
    if not user_id: return "ID não fornecido."
    
    clean_id = str(user_id).strip().lower()
    user = MOCK_DB.get(clean_id) or MOCK_DB.get(str(user_id).strip())
    
    if user: return str(user)
    return f"Usuario '{user_id}' nao encontrado."

@tool
def check_transfer_status(user_id: str) -> str:
    """Verifica bloqueios e status para transferencias."""
    clean_id = str(user_id).strip().lower()
    user = MOCK_DB.get(clean_id) or MOCK_DB.get(str(user_id).strip())
    
    if not user: return "Usuario nao encontrado."
    
    if user['status'] == 'blocked_fraud_check':
        return "BLOQUEIO CRITICO: Suspeita de fraude."
    if user['status'] == 'inactive':
        return "CONTA INATIVA: Atualize cadastro."
    if user['balance'] < 0:
        return f"SALDO NEGATIVO: {user['balance']}."

    return "Conta ativa e sem restricoes."