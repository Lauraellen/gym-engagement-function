import azure.functions as func
import logging
import json
import requests
import os
from datetime import datetime
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

app = func.FunctionApp()

# Configurações
PROJECT_ENDPOINT = os.environ.get("PROJECT_ENDPOINT")
AGENT_ID = os.environ.get("AGENT_ID")
AGENT_API_KEY = os.environ.get("AGENT_API_KEY")
LOGIC_APP_TWILIO_URL = os.environ.get("LOGIC_APP_TWILIO_URL")

# Cliente do Agent (inicializado uma vez)
agent_client = None

def get_agent_client():
    """Inicializa o cliente do Agent (lazy loading)"""
    global agent_client
    if agent_client is None:
        try:
            credential = DefaultAzureCredential()
            agent_client = AIProjectClient(
                endpoint=PROJECT_ENDPOINT,
                credential=credential
            )
        except Exception as e:
            logging.warning(f"⚠️ Não foi possível inicializar o Agent Client: {e}")
            return None
    return agent_client

# TIMER TRIGGER - Executa automaticamente todo dia às 9h
# Cron: "0 0 9 * * *" = segundo minuto hora dia mês dia-da-semana
@app.function_name(name="EngajamentoDiarioAutomatico")
@app.schedule(schedule="0 0 9 * * *", 
              arg_name="timer",
              run_on_startup=False,
              use_monitor=True)
def engajamento_diario_automatico(timer: func.TimerRequest) -> None:
    """Executa AUTOMATICAMENTE todo dia às 9h"""
    
    logging.info('⏰ Timer disparado às 9h - Iniciando rotina automática')
    
    if timer.past_due:
        logging.info('⚠️ Timer está atrasado')
    
    # Executar a rotina
    resultado = processar_rotina_engajamento()
    
    logging.info(f'✅ Rotina automática concluída: {resultado["total_sms"]} SMS enviados')


# HTTP Trigger - Para testes manuais
@app.function_name(name="EngajamentoDiarioManual")
@app.route(route="engajamento", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def engajamento_diario_manual(req: func.HttpRequest) -> func.HttpResponse:
    """Para executar MANUALMENTE (testes)"""
    
    logging.info('🧪 Execução manual iniciada')
    
    try:
        resultado = processar_rotina_engajamento()
        
        return func.HttpResponse(
            json.dumps(resultado, ensure_ascii=False, indent=2),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        logging.error(f'❌ Erro: {str(e)}')
        return func.HttpResponse(
            json.dumps({"erro": str(e)}),
            mimetype="application/json",
            status_code=500
        )


def processar_rotina_engajamento():
    """Aciona o agente para fazer TODO o trabalho de engajamento"""
    
    data_hoje = datetime.now().strftime("%d/%m/%Y")
    resultado = {
        "data_execucao": data_hoje,
        "timestamp": datetime.now().isoformat(),
        "status": "iniciado",
        "resposta_agente": ""
    }
    
    logging.info('🤖 Acionando agente para processar rotina completa de engajamento...')
    
    # O AGENTE FAZ TUDO: busca, gera mensagens E envia!
    instrucao = """
Você é o Smart Buddy da SmartGym. Execute a rotina diária de engajamento:

1. **ANIVERSARIANTES**: 
   - Busque alunos ativos com aniversário hoje
   - Para cada um, gere uma mensagem personalizada de parabéns
   - Envie via smartbuddy_Tool

2. **BAIXA FREQUÊNCIA (Irregulares)**:
   - Busque alunos ativos com categoria_frequencia = 'Irregular'
   - Para cada um, gere mensagem motivacional para voltar a treinar
   - Envie via smartbuddy_Tool

3. **ALTA FREQUÊNCIA (Dedicados)**:
   - Busque alunos ativos com categoria_frequencia = 'Dedicado'
   - Para cada um, gere mensagem de reconhecimento mencionando quantos treinos fizeram
   - Envie via smartbuddy_Tool

Após concluir, retorne um resumo:
- Total de mensagens enviadas em cada categoria
- Algum problema encontrado
"""
    
    resposta = executar_agente_completo(instrucao)
    
    resultado["resposta_agente"] = resposta
    resultado["status"] = "concluído"
    
    logging.info(f'✅ Rotina de engajamento concluída')
    logging.info(f'📋 Resposta do agente:\n{resposta}')
    
    return resultado


def executar_agente_completo(instrucao: str) -> str:
    """Executa o agente e retorna a resposta completa (o agente faz tudo)"""
    
    logging.info(f'🤖 Instrução para agente:\n{instrucao}')
    
    try:
        client = get_agent_client()
        
        if client is None:
            logging.info("⚡ SDK falhou - usando HTTP direto")
            return executar_agente_http(instrucao)
        
        # Criar thread
        thread = client.agents.threads.create()
        logging.info(f"🧵 Thread criada: {thread.id}")
        
        # Enviar instrução
        client.agents.messages.create(
            thread_id=thread.id,
            role="user",
            content=instrucao
        )
        
        # Executar agente (ele vai chamar as tools automaticamente)
        run = client.agents.runs.create_and_process(
            thread_id=thread.id,
            agent_id=AGENT_ID
        )
        
        logging.info(f"▶️ Run status: {run.status}")
        
        if run.status == "completed":
            messages = client.agents.messages.list(thread_id=thread.id)
            
            for msg in messages:
                if msg.role == "assistant":
                    resposta = msg.content[0].text.value
                    
                    # Deletar thread
                    client.agents.threads.delete(thread.id)
                    
                    return resposta
        
        return f"⚠️ Agente não completou. Status: {run.status}"
        
    except Exception as e:
        logging.error(f'❌ Erro SDK: {str(e)}')
        logging.info("⚡ Tentando fallback HTTP")
        
        try:
            return executar_agente_http(instrucao)
        except Exception as e2:
            logging.error(f'❌ Erro HTTP: {str(e2)}')
            return f"❌ Erro: {str(e2)}"


def executar_agente_http(instrucao: str) -> str:
    """Fallback HTTP para executar agente"""
    
    try:
        base_url = PROJECT_ENDPOINT.replace("/api/projects/", "/openai/").replace(".services.ai.azure.com", ".openai.azure.com")
        
        headers = {
            "Content-Type": "application/json",
            "api-key": AGENT_API_KEY
        }
        
        # Criar thread
        response = requests.post(
            f"{base_url}/assistants/threads",
            headers=headers,
            params={"api-version": "2024-05-01-preview"},
            json={},
            timeout=10
        )
        response.raise_for_status()
        thread_id = response.json()["id"]
        logging.info(f"🧵 Thread HTTP: {thread_id}")
        
        # Enviar mensagem
        requests.post(
            f"{base_url}/assistants/threads/{thread_id}/messages",
            headers=headers,
            params={"api-version": "2024-05-01-preview"},
            json={"role": "user", "content": instrucao},
            timeout=10
        ).raise_for_status()
        
        # Criar run
        response = requests.post(
            f"{base_url}/assistants/threads/{thread_id}/runs",
            headers=headers,
            params={"api-version": "2024-05-01-preview"},
            json={"assistant_id": AGENT_ID},
            timeout=10
        )
        response.raise_for_status()
        run_id = response.json()["id"]
        
        # Aguardar conclusão
        import time
        for _ in range(120):  # 2 minutos max
            response = requests.get(
                f"{base_url}/assistants/threads/{thread_id}/runs/{run_id}",
                headers=headers,
                params={"api-version": "2024-05-01-preview"},
                timeout=10
            )
            status = response.json()["status"]
            
            if status == "completed":
                break
            elif status in ["failed", "cancelled", "expired"]:
                return f"❌ Run falhou: {status}"
            
            time.sleep(1)
        
        # Obter resposta
        response = requests.get(
            f"{base_url}/assistants/threads/{thread_id}/messages",
            headers=headers,
            params={"api-version": "2024-05-01-preview"},
            timeout=10
        )
        messages = response.json()["data"]
        
        for msg in messages:
            if msg["role"] == "assistant":
                return msg["content"][0]["text"]["value"]
        
        return "⚠️ Nenhuma resposta do agente"
        
    except Exception as e:
        logging.error(f'❌ Erro HTTP: {str(e)}')
        raise


# Endpoint de teste (não envia SMS)
@app.function_name(name="TestarConfiguracao")
@app.route(route="teste", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def testar_config(req: func.HttpRequest) -> func.HttpResponse:
    """Testa se está tudo configurado"""
    
    status = {
        "project_endpoint": "✅" if PROJECT_ENDPOINT else "❌ Faltando",
        "agent_id": "✅" if AGENT_ID else "❌ Faltando",
        "agent_api_key": "✅" if AGENT_API_KEY else "❌ Faltando",
    }
    
    # Teste simples com o Agent
    try:
        resposta = executar_agente_completo("Olá! Apenas confirme que você está funcionando.")
        status["teste_agent"] = f"✅ Funcionou"
        status["resposta"] = resposta[:100]
    except Exception as e:
        status["teste_agent"] = f"❌ Erro: {str(e)}"
    
    return func.HttpResponse(
        json.dumps(status, ensure_ascii=False, indent=2),
        mimetype="application/json"
    )