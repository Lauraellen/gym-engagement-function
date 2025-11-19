"""
Script para listar todos os agentes disponíveis no seu projeto AI Foundry
"""

import os
import json
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

# Carregar variáveis de ambiente do local.settings.json
with open("local.settings.json", "r") as f:
    settings = json.load(f)
    for key, value in settings.get("Values", {}).items():
        os.environ[key] = value

# Configurações
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")

print(f"🔍 Listando agentes do projeto:")
print(f"   Endpoint: {PROJECT_ENDPOINT}")
print()

try:
    # Criar cliente
    credential = DefaultAzureCredential()
    client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=credential
    )
    
    # Listar agentes
    print("📋 Agentes disponíveis:")
    print("-" * 80)
    
    agents = list(client.agents.list_agents())
    
    if not agents:
        print("❌ Nenhum agente encontrado!")
    else:
        for i, agent in enumerate(agents, 1):
            print(f"\n{i}. Nome: {agent.name}")
            print(f"   ID: {agent.id}")
            print(f"   Model: {agent.model}")
            if agent.description:
                print(f"   Descrição: {agent.description}")
            if agent.tools:
                print(f"   Tools: {len(agent.tools)} configuradas")
                for tool in agent.tools:
                    print(f"      - {tool}")
    
    print("\n" + "-" * 80)
    print(f"✅ Total: {len(agents)} agente(s)")

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
