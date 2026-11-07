# 🚀 Quick Start - OpenJarvis API

## Status Atual: ✅ Totalmente Operacional

```
🟢 Servidor: http://127.0.0.1:8000 (rodando)
🟢 Testes: 4/4 passando (100%)
🟢 Endpoints: 7 funcionais
🟢 Performance: <100ms por requisição
```

---

## 📋 Checklist de Funcionalidades

- ✅ Python 3.12.16 configurado
- ✅ Dependências instaladas (67 packages)
- ✅ FastAPI servidor rodando
- ✅ Home page interativa
- ✅ Endpoints funcionais
- ✅ Documentação Swagger
- ✅ Chat endpoint testado
- ✅ Mock engine respondendo
- ⏳ Agent CRUD API (próximo)

---

## 🧪 Testar o Chat Endpoint

### Opção 1: PowerShell (Recomendado para UTF-8)

```powershell
$json = '{"model":"gemma2:latest","messages":[{"role":"user","content":"Olá, Jarvis. Status do sistema?"}]}'
$bytes = [System.Text.Encoding]::UTF8.GetBytes($json)

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/chat/completions" `
    -Method Post `
    -ContentType "application/json; charset=utf-8" `
    -Body $bytes

$response.choices[0].message.content
```

### Opção 2: cURL (Windows)

```bash
curl -X POST http://127.0.0.1:8000/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -d "{\"model\":\"gemma2:latest\",\"messages\":[{\"role\":\"user\",\"content\":\"Olá, Jarvis. Status do sistema?\"}]}"
```

### Opção 3: Script PowerShell

```bash
cd J:\tasksorobon\jarvis
.\TEST_API.ps1
```

---

## 🔄 Ciclo de Desenvolvimento

### Iniciar Servidor

```bash
cd J:\tasksorobon\jarvis
.\.venv\Scripts\python -m uvicorn openjarvis.server.main:app --host 127.0.0.1 --port 8000 --reload
```

### Acessar Recursos

| Recurso | URL |
|---------|-----|
| Home Page | http://127.0.0.1:8000 |
| API Docs | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| OpenAPI Spec | http://127.0.0.1:8000/openapi.json |
| Status | http://127.0.0.1:8000/status |
| Modelos | http://127.0.0.1:8000/v1/models |

### Modificar e Recarregar

1. Edite um arquivo em `src/openjarvis/server/`
2. Salve (Ctrl+S)
3. Servidor recarrega automaticamente (~2 segundos)
4. Teste novamente

---

## 📊 Dados de Teste

### Requisição Simples
```json
{
  "model": "gpt-4",
  "messages": [
    {"role": "user", "content": "Olá"}
  ]
}
```

### Requisição Completa
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {"role": "user", "content": "Contar até 5"}
  ],
  "temperature": 0.5,
  "max_tokens": 50
}
```

### Conversação Multi-turno
```json
{
  "model": "claude-3-opus",
  "messages": [
    {"role": "user", "content": "Qual é o seu nome?"},
    {"role": "assistant", "content": "Meu nome é Claude."},
    {"role": "user", "content": "E qual é a sua função?"}
  ]
}
```

---

## 🎯 Próximas Etapas (Escolha Uma)

### ⭐ Opção 1: Agent CRUD API (2-4h)
Implementar endpoints para gerenciar agentes:
```
POST   /agents              # Criar
GET    /agents              # Listar
GET    /agents/{id}         # Detalhes
DELETE /agents/{id}         # Remover
```

**Começar:**
```bash
# Criar arquivo
touch src/openjarvis/server/agents_api.py

# Adicionar rotas em app.py
# Testar com scripts PowerShell
```

---

### 🤖 Opção 2: MonitorOperative (1-2d)
Integrar agente autônomo com tools reais:
```python
from openjarvis.agents.monitor_operative import MonitorOperative

# Criar instância
agent = MonitorOperative()

# Executar com tools
```

**Começar:**
```bash
# Revisar src/openjarvis/agents/monitor_operative.py
# Entender tool resolution
# Testar com web search + code execution
```

---

### ⚡ Opção 3: WebSocket Streaming (3-5d)
Sistema de fila com eventos em tempo real:
```
POST   /agents/{id}/tasks           # Criar tarefa
WS     /agents/{id}/stream          # Stream events
GET    /tasks/{task_id}             # Status
DELETE /tasks/{task_id}             # Cancelar
```

**Começar:**
```bash
# Adicionar WebSocket route
# Integrar Redis (opcional)
# Testar com ws client
```

---

### 🌐 Opção 4: Distributed (10+d)
Escalabilidade com Redis + Celery:
- Redis backend
- Celery workers
- Flower monitoring
- Load balancing

**Começar:**
```bash
# uv add redis celery flower
# Configurar broker
# Deploy workers
```

---

## 📚 Documentação de Referência

- [API_STATUS_DASHBOARD.md](./API_STATUS_DASHBOARD.md) - Guia estratégico completo
- [CHAT_ENDPOINT_TEST_REPORT.md](./CHAT_ENDPOINT_TEST_REPORT.md) - Resultados de testes
- [TEST_API.ps1](./TEST_API.ps1) - Script de testes automatizado

---

## 🔧 Troubleshooting

### Servidor não inicia

```bash
# Verificar porta
netstat -ano | findstr :8000

# Matar processo existente
taskkill /PID <PID> /F

# Reiniciar
.\.venv\Scripts\python -m uvicorn openjarvis.server.main:app --reload
```

### JSON encoding errors

Use PowerShell com charset UTF-8:
```powershell
$bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
Invoke-RestMethod ... -Body $bytes
```

### Import errors

Verificar venv:
```bash
.\.venv\Scripts\python -c "import openjarvis; print('OK')"

# Reinstalar dependências
uv sync --extra server
```

---

## 📈 Métricas Atuais

| Métrica | Valor |
|---------|-------|
| Uptime | +5 minutos |
| Requests | 4 testadas |
| Success Rate | 100% |
| Response Time | <100ms |
| Tokens/Request | 30 (mock) |
| Models | 3+ (mock) |
| Endpoints | 7 ✅ |

---

## 🎯 Decisão: Qual Opção?

Responda com **1, 2, 3 ou 4** e começaremos imediatamente! 🚀

| Opção | Benefício | Tempo | Complexity |
|-------|----------|-------|-----------|
| 1 | Foundation rápida ⭐ | 2-4h | ⚡⚡ |
| 2 | Agentes reais 🤖 | 1-2d | ⚡⚡⚡ |
| 3 | Real-time ⚡ | 3-5d | ⚡⚡⚡⚡ |
| 4 | Production 🌐 | 10+d | ⚡⚡⚡⚡⚡ |

---

**Última atualização:** 2026-11-04 04:15:16 UTC-3  
**Status:** ✅ Pronto para integração de agentes
