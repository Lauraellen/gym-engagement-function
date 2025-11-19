"""Script para testar a função localmente SEM o Azure Functions runtime"""
import os
import json

# Carregar variáveis de ambiente do local.settings.json
with open('local.settings.json') as f:
    settings = json.load(f)
    for key, value in settings['Values'].items():
        os.environ[key] = value

# Importar as funções do function_app
from function_app import processar_rotina_engajamento, executar_agente_completo


def teste_agente_simples():
    """Testa o agente com uma instrução simples"""
    print("\n" + "="*60)
    print("🧪 TESTE: Verificar comunicação com agente")
    print("="*60)
    
    instrucao = "Olá! Apenas confirme que você está funcionando e liste quantos alunos ativos existem na base."
    
    resposta = executar_agente_completo(instrucao)
    
    print(f"\n✅ Resposta do agente:")
    print(resposta)


def teste_busca_aniversariantes():
    """Testa apenas a busca de aniversariantes (sem enviar SMS)"""
    print("\n" + "="*60)
    print("🧪 TESTE: Buscar aniversariantes (SEM enviar SMS)")
    print("="*60)
    
    instrucao = """
Busque os alunos ativos com aniversário hoje usando o openiaSmartBuddy.
Apenas LISTE os nomes e telefones encontrados, NÃO envie mensagens.
"""
    
    resposta = executar_agente_completo(instrucao)
    
    print(f"\n✅ Resposta do agente:")
    print(resposta)


def teste_rotina_completa():
    """Testa a rotina completa (o agente VAI enviar SMS de verdade!)"""
    print("\n" + "="*60)
    print("🧪 TESTE: Rotina completa de engajamento")
    print("="*60)
    print("\n⚠️  ATENÇÃO: Este teste VAI ENVIAR SMS DE VERDADE!\n")
    
    confirmacao = input("Deseja continuar? (digite 'SIM' para confirmar): ")
    
    if confirmacao.upper() != "SIM":
        print("\n❌ Teste cancelado pelo usuário")
        return
    
    resultado = processar_rotina_engajamento()
    
    print("\n" + "="*60)
    print("📊 RESULTADO FINAL:")
    print("="*60)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    print("\n🚀 INICIANDO TESTES LOCAIS\n")
    print("Escolha um teste:")
    print("  1 - Teste simples (verificar conexão com agente)")
    print("  2 - Buscar aniversariantes (SEM enviar SMS)")
    print("  3 - Rotina completa (VAI ENVIAR SMS!)")
    print()
    
    # Escolha qual teste rodar:
    
    # 1. Teste simples
    teste_agente_simples()
    
    # 2. Teste busca aniversariantes (sem enviar)
    # teste_busca_aniversariantes()
    
    # 3. Teste completo (ENVIA SMS DE VERDADE!)
    # teste_rotina_completa()
    
    print("\n✅ Testes concluídos!\n")
