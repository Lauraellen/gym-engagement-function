"""Teste completo: verifica as consultas do agente para cada categoria"""
import os, json

# Carregar env ANTES de importar function_app
with open('local.settings.json') as f:
    for k,v in json.load(f)['Values'].items():
        os.environ[k] = v

from function_app import executar_agente_completo

print("=" * 70)
print("🧪 TESTE 1: Aniversariantes (SEM enviar SMS)")
print("=" * 70)
instrucao = """
Busque os alunos ativos com aniversário hoje usando openiaSmartBuddy.
Apenas LISTE os resultados (nome, telefone, email), NÃO envie mensagens.
"""
resposta = executar_agente_completo(instrucao)
print(f"\n✅ Resposta do agente:")
print(resposta)

print("\n" + "=" * 70)
print("🧪 TESTE 2: Dedicados (SEM enviar SMS)")
print("=" * 70)
instrucao = """
Busque alunos ativos com categoria_frequencia = 'Dedicado' usando openiaSmartBuddy.
Apenas LISTE os resultados (nome, telefone, checkins_ultimo_mes), NÃO envie mensagens.
"""
resposta = executar_agente_completo(instrucao)
print(f"\n✅ Resposta do agente:")
print(resposta)

print("\n" + "=" * 70)
print("🧪 TESTE 3: Irregulares (SEM enviar SMS)")
print("=" * 70)
instrucao = """
Busque alunos ativos com categoria_frequencia = 'Irregular' usando openiaSmartBuddy.
Apenas LISTE os resultados (nome, telefone), NÃO envie mensagens.
"""
resposta = executar_agente_completo(instrucao)
print(f"\n✅ Resposta do agente:")
print(resposta)

print("\n" + "=" * 70)
print("🧪 TESTE 4: Verificar tool smartbuddy_Tool (SEM enviar de verdade)")
print("=" * 70)
print("⚠️  ATENÇÃO: Este teste é apenas informativo.")
print("Para testar envio real, use teste_local.py e escolha opção 3.")

print("\n" + "=" * 70)
print("✅ TESTES CONCLUÍDOS")
print("=" * 70)
print("\nProximos passos:")
print("  1. Se as consultas retornaram dados corretos, use teste_local.py")
print("  2. Escolha opção 3 (rotina completa) para testar envio de SMS real")
print("  3. Confirme com 'SIM' para enviar mensagens de verdade")
