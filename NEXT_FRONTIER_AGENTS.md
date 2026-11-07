# 🎯 Próxima Frente de Batalha: Integração de Agentes Autônomos

## Status Atual ✅
- **API FastAPI:** Rodando e respondendo
- **Endpoint de Chat:** Funcional com mock engine
- **Documentação OpenAPI:** Disponível

```
http://127.0.0.1:8000/v1/chat/completions ✓ 200 OK
```

---

## 🚀 Arquitetura de Agentes do OpenJarvis

Baseado na análise do código-fonte, o projeto possui uma arquitetura multi-camadas de agentes:

### 1. **Camada de Gerenciamento de Agentes** 
   - **Local:** `src/openjarvis/agents/manager.py`
   - **Responsabilidade:** Gerenciar ciclo de vida persistente de agentes
   - **Storage:** SQLite com tabelas:
     - `managed_agents`: Registro de agentes
     - `agent_tasks`: Tarefas atribuídas
     - `channel_bindings`: Integração com canais (Telegram, Discord, etc)
     - `agent_checkpoints`: Snapshots de estado

### 2. **Tipos de Agentes Disponíveis** 📦
   ```
   ├── monitor_operative.py      (Monitor de Operações)
   ├── simple.py                  (Simples/Básico)
   ├── native_react.py            (ReAct - Reasoning + Acting)
   ├── native_openhands.py        (OpenHands - IDE Integration)
   ├── deep_research.py           (Deep Research - Pesquisa Profunda)
   ├── proactive_agent.py         (Proativo - Análise de Padrões)
   ├── channel_agent.py           (Canal - Multi-plataforma)
   ├── hybrid/                    (Híbridos - Composição de Estratégias)
   └── orchestrator.py            (Orquestrador - Coordenador de Agentes)
   ```

### 3. **Rotas de API para Agentes** 🔌
   - **Local:** `src/openjarvis/server/agent_manager_routes.py`
   - **Endpoints:**
     - `POST /agents` - Criar novo agente
     - `GET /agents` - Listar agentes
     - `GET /agents/{agent_id}` - Detalhes de agente
     - `POST /agents/{agent_id}/tasks` - Submeter tarefa
     - `WebSocket /agents/{agent_id}/stream` - Stream de respostas

---

## 🎮 Próximos Passos Recomendados

### **Fase 1: Setup Básico de Agentes** (PRÓXIMO IMEDIATO)
**Objetivo:** Criar e testar um agente simples via API

1. ✅ Criar um agente MonitorOperative básico
2. ✅ Expor endpoint POST `/agents` que retorna agent_id
3. ✅ Testar criação via API REST
4. ✅ Persistir em SQLite

**Comando para teste:**
```bash
curl -X POST http://127.0.0.1:8000/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Agent Alpha",
    "type": "monitor_operative",
    "config": {
      "model": "gpt-4",
      "tools": ["search", "code_execution"]
    }
  }'
```

### **Fase 2: Submissão de Tarefas** (SECUNDÁRIA)
**Objetivo:** Permitir que agentes executem tarefas

1. Endpoint POST `/agents/{agent_id}/tasks` 
2. Task queue persistente
3. Execução assíncrona
4. Tracking de progresso

### **Fase 3: Streaming de Resultados** (AVANÇADA)
**Objetivo:** Real-time feedback durante execução

1. WebSocket `/agents/{agent_id}/stream`
2. Event bus para notificações
3. Checkpoint system para recuperação

### **Fase 4: Composição de Agentes** (ORCHESTRATION)
**Objetivo:** Multi-agente orquestrado

1. Agente coordenador (Orchestrator)
2. Delegação automática de tasks
3. Agregação de resultados

---

## 📊 Estrutura de Dados Necessária

### **Agente (Modelo)**
```python
{
    "id": "agent-uuid-123",
    "name": "Bot de Pesquisa",
    "type": "deep_research",
    "config": {
        "model": "gpt-4",
        "temperature": 0.7,
        "tools": ["search", "summarize", "extract"]
    },
    "status": "idle|running|blocked",
    "created_at": "2026-11-04T...",
    "updated_at": "2026-11-04T...",
    "summary_memory": "Conhecimento acumulado..."
}
```

### **Tarefa (Modelo)**
```python
{
    "id": "task-uuid-456",
    "agent_id": "agent-uuid-123",
    "description": "Pesquise sobre IA e retorne resumo",
    "status": "pending|running|completed|failed",
    "progress": {
        "current_step": 2,
        "total_steps": 5,
        "details": "Executando pesquisa..."
    },
    "findings": [
        {"type": "research", "content": "..."},
        {"type": "summary", "content": "..."}
    ],
    "created_at": "2026-11-04T..."
}
```

---

## 🔧 Implementação Imediata

### Arquivo a criar: `src/openjarvis/server/agents_api.py`

```python
"""FastAPI routes for autonomous agents."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

router = APIRouter(prefix="/agents", tags=["agents"])

class AgentConfig(BaseModel):
    model: str = "gpt-4"
    temperature: float = 0.7
    tools: List[str] = []
    max_iterations: int = 10

class CreateAgentRequest(BaseModel):
    name: str
    type: str = "simple"
    config: Optional[AgentConfig] = None

class Agent(BaseModel):
    id: str
    name: str
    type: str
    status: str = "idle"
    created_at: str

@router.post("/", response_model=Agent)
async def create_agent(req: CreateAgentRequest, request: Request):
    """Create a new autonomous agent."""
    agent_id = str(uuid.uuid4())
    agent = {
        "id": agent_id,
        "name": req.name,
        "type": req.type,
        "config": req.config or AgentConfig(),
        "status": "idle",
        "created_at": datetime.utcnow().isoformat(),
    }
    
    # TODO: Persist to SQLite via manager
    # manager = request.app.state.agent_manager
    # manager.create_agent(agent)
    
    return Agent(**agent)

@router.get("/")
async def list_agents(request: Request):
    """List all agents."""
    # TODO: Fetch from SQLite
    return {"agents": []}

@router.get("/{agent_id}")
async def get_agent(agent_id: str, request: Request):
    """Get agent details."""
    # TODO: Fetch from SQLite
    return {"error": "Not implemented"}

@router.post("/{agent_id}/tasks")
async def submit_task(agent_id: str, description: str, request: Request):
    """Submit a task to an agent."""
    # TODO: Create task in queue
    return {"task_id": str(uuid.uuid4())}
```

---

## 🎯 Ordem de Prioridade

### **PRONTA PARA COMEÇAR:**
1. ✅ Criar arquivo `agents_api.py` com CRUD básico
2. ✅ Integrar com `app.py`: `include_router(agents_router)`
3. ✅ Testar endpoints de criação/listagem
4. ✅ Conectar ao gerenciador persistente

### **DEPOIS:**
5. Task queue e execução
6. WebSocket streaming
7. Agent composition

---

## 💬 Qual Frente Você Prefere Atacar?

**A. 🔧 Implementar API básica de agentes** (CRUD)
   → Rápido, validação rápida de conceito

**B. 🎭 Integrar agente existente (MonitorOperative)** (Funcional)
   → Usa código já existente, mais realista

**C. 🌊 Streaming + Orquestração** (Avançado)
   → Começa pelo fim, mais complexo mas poderoso

**D. 📡 Task Queue com Redis/Celery** (Escalável)
   → Preparar para produção desde o início

---

## 📞 Call to Action

Escolha a frente e vamos implementar! Qual será?
