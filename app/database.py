# app/database.py

MOCK_DB = {
    # --- CENÁRIOS FELIZES (HAPPY PATH) ---
    "client_happy": {
        "name": "João da Silva", 
        "balance": 1500.50, 
        "status": "active", 
        "segment": "retail",
        "last_login": "2024-11-20"
    },
    "client_pj_vip": {
        "name": "Tech Solutions Ltda", 
        "balance": 154300.00, 
        "status": "active", 
        "segment": "business_vip",
        "last_login": "2024-11-25"
    },

    # --- CENÁRIOS DE ERRO FINANCEIRO ---
    "client_debt": {
        "name": "Carlos Devedor", 
        "balance": -50.25, 
        "status": "active", 
        "segment": "retail",
        "last_login": "2024-11-10"
    },
    "client_zero": {
        "name": "Mariana Zerada", 
        "balance": 0.00, 
        "status": "active", 
        "segment": "retail",
        "last_login": "2024-11-26"
    },

    # --- CENÁRIOS DE BLOQUEIO/RISCO ---
    "client_blocked": {
        "name": "Roberto Fraude", 
        "balance": 5000.00, 
        "status": "blocked_fraud_check", 
        "segment": "risk",
        "last_login": "2024-11-01"
    },
    "client_inactive": {
        "name": "Ana Antiga", 
        "balance": 10.00, 
        "status": "inactive", 
        "segment": "retail",
        "last_login": "2022-05-20"
    },
    
    # --- CENÁRIOS DE TESTE DE SISTEMA ---
    "tester_rag": {
        "name": "QA Tester Knowledge",
        "balance": 100.00,
        "status": "active",
        "segment": "internal"
    },
    "attacker_user": {
        "name": "Unknown Actor",
        "balance": 0.00,
        "status": "active",
        "segment": "external"
    },
    # Mantendo compatibilidade com testes antigos se necessário
    "client789": {"name": "Legacy User", "balance": 1000.00, "status": "active"}
}