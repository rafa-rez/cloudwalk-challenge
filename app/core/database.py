"""
Módulo de simulação de banco de dados.
Contém dados mockados para testes de cenários de suporte e validação de regras de negócio.
"""

MOCK_DB = {
    # Cenários de Sucesso (Happy Path)
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

    # Cenários de Erro Financeiro
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

    # Cenários de Bloqueio e Risco
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
    
    # Cenários de Teste Interno
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
    
    # Legado
    "client789": {"name": "Legacy User", "balance": 1000.00, "status": "active"}
}