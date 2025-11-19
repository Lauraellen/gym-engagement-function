# 🏋️ SmartGym - Rotina de Engajamento Automático

Azure Function que executa diariamente às 9h para enviar mensagens personalizadas de engajamento via SMS para alunos da SmartGym.

## 📋 Funcionalidades

A rotina automatizada envia 3 tipos de mensagens via SMS:

1. **🎂 Aniversariantes**: Mensagem de parabéns para alunos com aniversário do dia
2. **💪 Irregulares**: Mensagem motivacional para alunos com baixa frequência
3. **🏆 Dedicados**: Mensagem de reconhecimento para alunos com alta frequência

## 🤖 Arquitetura

A função utiliza um **agente Azure AI** (`SmartBuddyAgent`) que:
- Consulta o banco de dados via `openiaSmartBuddy` tool (Azure AI Search)
- Gera mensagens personalizadas dinamicamente
- Envia SMS usando `smartbuddy_Tool` (Logic App + Twilio)

## 🚀 Deploy

```powershell
func azure functionapp publish gym-engagement-function
```

## 🧪 Testes Locais

### Teste Simples (verificar conexão com agente)
```powershell
python teste_local.py
```

### Teste por Categoria (sem enviar SMS)
```powershell
python teste_completo.py
```

### Teste Completo (ENVIA SMS REAL!)
Edite `teste_local.py` e descomente a função `teste_rotina_completa()`, depois execute.

## ⚙️ Configuração Local

Crie o arquivo `local.settings.json` (não commitado):

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "PROJECT_ENDPOINT": "https://[seu-projeto].services.ai.azure.com/api/projects/[projeto-id]",
    "AGENT_ID": "asst_[seu-agent-id]",
    "AGENT_API_KEY": "[sua-api-key]",
    "LOGIC_APP_TWILIO_URL": "[url-logic-app-twilio]"
  }
}
```

## 📅 Agendamento

- **Timer Trigger**: `0 0 9 * * *` (9h da manhã, todos os dias)
- **Timezone**: Configurado para horário do Brasil

## 🔐 Autenticação

- **Local**: Usa `AGENT_API_KEY` do `local.settings.json`
- **Azure**: Usa **Managed Identity** (System-Assigned) com role `Cognitive Services User`

## 📊 Monitoramento

Logs e traces disponíveis em:
- **Azure AI Foundry**: Tracing → veja todas as execuções e tools chamadas
- **Azure Portal**: Function App → Log Stream
- **Application Insights**: Queries customizadas

## 🛠️ Stack

- **Runtime**: Python 3.12
- **Azure Functions**: v2 (decorators)
- **SDK**: azure-ai-projects >= 1.0.0
- **Autenticação**: DefaultAzureCredential (Managed Identity)

## 📂 Estrutura

```
gym-engagement-function/
├── function_app.py           # Function principal
├── requirements.txt          # Dependências
├── host.json                 # Configuração Azure Functions
├── local.settings.json       # Variáveis ambiente (local, gitignored)
├── teste_local.py            # Testes locais
├── teste_completo.py         # Testes por categoria
└── listar_agentes.py         # Utilitário para listar agents
```

## 📝 Endpoints

### Timer (Automático)
- **Nome**: `EngajamentoDiarioAutomatico`
- **Trigger**: Diário às 9h

### HTTP (Manual)
- **Nome**: `EngajamentoDiarioManual`
- **URL**: `https://gym-engagement-function.azurewebsites.net/api/engajamento`
- **Método**: POST
- **Auth**: Function Key

### Teste de Configuração
- **Nome**: `TestarConfiguracao`
- **URL**: `https://gym-engagement-function.azurewebsites.net/api/teste`
- **Método**: GET
- **Auth**: Anonymous

## 🔄 Workflow Completo

1. Timer dispara às 9h (ou trigger manual via HTTP)
2. Function envia instrução completa ao agente
3. Agente executa autonomamente:
   - Busca alunos aniversariantes → Gera mensagens → Envia via SMS
   - Busca alunos irregulares → Gera mensagens → Envia via SMS
   - Busca alunos dedicados → Gera mensagens → Envia via SMS
4. Agente retorna resumo com totais e problemas
5. Function loga resultado

## 📄 Licença

Projeto privado - SmartGym
