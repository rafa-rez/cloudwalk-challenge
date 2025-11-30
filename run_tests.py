import sys
import time
import pytest

class TestExecutionReporter:
    """
    Plugin customizado para o Pytest.
    Intercepta o resultado de cada teste para gerar um relatório visual simplificado no terminal.
    """

    def pytest_runtest_logreport(self, report):
        if report.when == 'call':
            # Extrai o nome do teste e limpa a formatação de parametrização
            node_id = report.nodeid.split("::")[-1]
            
            if "[" in node_id:
                scenario_name = node_id.split("[")[1].replace("]", "")
                display_name = f"Cenário: {scenario_name}"
            else:
                display_name = node_id

            # Renderiza status
            if report.passed:
                print(f"✅ {display_name:<50} ... PASSOU")
            elif report.failed:
                print(f"❌ {display_name:<50} ... FALHOU")


def run_suite():
    """
    Função principal de execução da suíte de testes (Wrapper do Pytest).
    Gerencia o tempo de execução e o código de saída para CI/CD.
    """
    print("\n" + "="*60)
    print("🚀 INICIANDO BATERIA DE TESTES DE INTEGRAÇÃO (SWARM)")
    print("="*60 + "\n")
    
    start_time = time.time()
    
    # Executa pytest com flags de silêncio 
    exit_code = pytest.main(
        ["-q", "--tb=no", "-p", "no:warnings", "tests/"], 
        plugins=[TestExecutionReporter()]
    )
    
    duration = time.time() - start_time
    
    print("\n" + "-"*60)
    if exit_code == 0:
        print(f"🏆 SUCESSO: Todos os testes aprovados em {duration:.2f}s")
    else:
        print(f"⚠️ FALHA: Verifique os logs acima. Tempo: {duration:.2f}s")
    print("-"*(60) + "\n")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    run_suite()