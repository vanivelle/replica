# 🏛️ ANÁLISE ARQUITETURAL - OpenJarvis Agent Integration

## 📊 MAPEAMENTO ESTRUTURAL ATUAL

```
openjarvis/
├── src/openjarvis/
│   ├── agents/                          ← NÚCLEO AGENTE
│   │   ├── ecc/                         ← Repository de 48 agentes especializados
│   │   │   ├── agents/                  ├─ python-reviewer.md
│   │   │   │                            ├─ security-reviewer.md
│   │   │   │                            ├─ code-architect.md
│   │   │   │                            ├─ (45+ mais especializados)
│   │   │   │
│   │   │   ├── src/                     ← Implementações Python dos agentes
│   │   │   ├── schemas/                 ← Definições de prompt/config
│   │   │   ├── skills/                  ← Utilitários compartilhados
│   │   │   └── AGENTS.md                ← Catálogo completo
│   │   │
│   │   ├── manager.py                   ← AgentManager (Lifecycle + SQLite)
│   │   ├── tool_resolver.py             ← Tool instantiation & resolution
│   │   ├── monitor_operative.py          ← Agente base autônomo
│   │   ├── native_openhands.py           ← CodeAct-style agent
│   │   ├── native_react.py               ← ReAct chain agent
│   │   ├── deep_research.py              ← Multi-step research
│   │   └── [10+ agent primitives]
│   │
│   ├── server/                          ← API FastAPI
│   │   ├── app.py                       ├─ create_app() factory
│   │   ├── main.py                      ├─ Uvicorn entry point
│   │   ├── routes.py                    ├─ Chat completions (ATIVO)
│   │   ├── models.py                    ├─ Pydantic schemas
│   │   ├── agent_manager_routes.py      ├─ Agent CRUD (EXISTE!)
│   │   ├── channel_bridge.py            ├─ Multi-channel routing
│   │   └── stream_bridge.py             └─ WebSocket streaming
│   │
│   ├── memory/                          ← Persistência & State
│   │   ├── session_store.py             ├─ Session management
│   │   ├── memory_backend.py            ├─ Vector DB + recall
│   │   └── checkpoint_store.py          └─ Agent checkpoints
│   │
│   ├── core/                            ← Primitivos Base
│   │   ├── types.py                     ├─ Message, Role, ToolCall
│   │   ├── events.py                    ├─ Event bus (pub/sub)
│   │   └── paths.py                     └─ Config management
│   │
│   └── tools/                           ← Tool Registry
│       ├── web_search.py
│       ├── code_execution.py
│       ├── file_operations.py
│       └── (30+ tools)
│
└── configs/openjarvis/
    └── config.toml                      ← Configuration matrix
```

---

## 🔗 INTEGRAÇÕES IDENTIFICADAS

### ✅ JÁ IMPLEMENTADO

| Componente | Status | Localização | Função |
|-----------|--------|-------------|--------|
| **AgentManager** | ✅ Ativo | `agents/manager.py` | Persistência SQLite + lifecycle |
| **Tool Resolver** | ✅ Ativo | `agents/tool_resolver.py` | Instantiate + dependency resolution |
| **Agent CRUD Router** | ✅ Existe | `server/agent_manager_routes.py` | POST/GET/PATCH/DELETE endpoints |
| **Chat Route** | ✅ Testado | `server/routes.py` | `/v1/chat/completions` com mock |
| **Home Page** | ✅ Ativo | `server/main.py` | Dashboard interativo |

### 🔄 PENDENTE DE INTEGRAÇÃO

| Componente | Ação | Prioridade | Tokens |
|-----------|------|-----------|--------|
| **ECC Agents Catalog** | Mapear 48 specs em DB | 🔴 ALTA | Análise |
| **Unified Agent Factory** | Instanciar dinamicamente | 🔴 ALTA | Implementação |
| **Collective Consciousness Router** | Cloud-native routing | 🔴 ALTA | Arquitetura |
| **Memory Persistence** | Multi-turn stateful ops | 🟡 MÉDIA | Integração |
| **WebSocket Streaming** | Real-time events | 🟡 MÉDIA | Próxima fase |

---

## 🎯 ENDPOINTS AGENT CRUD EXISTENTES

### Route Base: `/v1/managed-agents`

```http
# Listar todos os agentes
GET /v1/managed-agents
Response: {"agents": [{"id": "...", "name": "...", "status": "idle"}]}

# Criar novo agente
POST /v1/managed-agents
Body: {
  "name": "my-agent",
  "agent_type": "monitor_operative",
  "config": {"temperature": 0.7},
  "template_id": "code-reviewer" (opcional)
}

# Obter detalhes de agente
GET /v1/managed-agents/{agent_id}
Response: {"id": "...", "status": "running", "summary_memory": "..."}

# Atualizar agente
PATCH /v1/managed-agents/{agent_id}
Body: {"name": "new-name", "status": "paused"}

# Deletar agente
DELETE /v1/managed-agents/{agent_id}

# Listar tarefas do agente
GET /v1/managed-agents/{agent_id}/tasks

# Criar tarefa para agente
POST /v1/managed-agents/{agent_id}/tasks
Body: {"description": "Find security issues"}

# Stream resposta do agente
WS /v1/managed-agents/{agent_id}/stream
```

---

## 🧠 CONSCIÊNCIA COLETIVA - ARQUITETURA

### Layer 1: Agent Primitives (Independentes)
```
┌─────────────────┬─────────────────┬──────────────────┬──────────────┐
│ MonitorOperative│ NativeOpenhands │ DeepResearch     │ NativeReAct  │
│ (autonomous)    │ (CodeAct)       │ (multi-turn)     │ (reasoning)  │
└─────────────────┴─────────────────┴──────────────────┴──────────────┘
         ↓                 ↓                  ↓                 ↓
       TOOLS          TOOLS               TOOLS             TOOLS
     (resolver)      (resolver)          (resolver)        (resolver)
```

### Layer 2: Unified Agent Factory
```
ECC Catalog (48 specs)
    ↓
AgentFactory.create(spec_id, overrides)
    ├─ Instancia tipo correto (Operative, OpenHands, etc)
    ├─ Carrega templates de ECC
    ├─ Injeta memoria compartilhada
    └─ Registra em SQLite
```

### Layer 3: Cloud-Native Router
```
User Request
    ↓
┌─────────────────────────────────────┐
│ Router ("Consciência Coletiva")     │
├─────────────────────────────────────┤
│ 1. Analyse capabilities required   │
│ 2. Score local agents              │
│ 3. Route to best-fit agent         │
│ 4. Fallback: Anthropic/Claude API  │
│ 5. Aggregate results               │
└─────────────────────────────────────┘
    ├─ Agent1 (specialized)
    ├─ Agent2 (fallback)
    └─ Cloud (last-resort)
```

### Layer 4: Stateful Memory
```
Session Store
    ├─ Conversation History
    ├─ Agent State Checkpoints
    ├─ Tool Execution Results
    └─ Learning Outcomes
```

---

## 📋 CHECKLIST DE INTEGRAÇÃO (Opção 1)

### FASE A: Unificação de Catálogos
- [ ] Parse ECC/agents/*.md (48 especificações)
- [ ] Criar schema unificado de AgentSpec
- [ ] Popular banco de dados com specs
- [ ] Expor via `/v1/managed-agents/templates`

### FASE B: Agent Factory Dinâmica
- [ ] `AgentFactory.create(spec_id, config)`
- [ ] Route a tipo correto (Operative/OpenHands/ReAct/etc)
- [ ] Carregar templates ECC
- [ ] Injetar tools baseado em categoria

### FASE C: Consciência Coletiva Router
- [ ] Analisar user request
- [ ] Score agentes disponíveis
- [ ] Roteamento inteligente
- [ ] Fallback para Anthropic/Claude

### FASE D: Persistência Stateful
- [ ] Checkpoints entre turns
- [ ] Memory injection em prompts
- [ ] Aprendizado entre sessões
- [ ] Auditoria de decisões

### FASE E: Interface & Streaming
- [ ] WebSocket para real-time updates
- [ ] Progress bars de agent execution
- [ ] Tool invocation visualization
- [ ] Result aggregation

---

## 🔌 INTEGRAÇÕES COM ECC

### ECC Agents a Integrar

```python
# Categoria: Code Review (8 agentes)
SPEC_HANDLERS = {
    "code-reviewer": MonitorOperative + WebTools,
    "python-reviewer": MonitorOperative + PythonTools,
    "security-reviewer": MonitorOperative + SecurityTools,
    "architecture-reviewer": MonitorOperative + AnalysisTools,
    ...
}

# Categoria: Build Resolution (5 agentes)
"python-build-resolver": NativeOpenhands + Execution,
"java-build-resolver": NativeOpenhands + Compilation,
...

# Categoria: Research (3 agentes)
"deep-research": DeepResearch + WebSearch,
"spec-miner": DeepResearch + DocumentTools,
...
```

### Unified Agent Instantiation

```python
# Antes: Manual coupling
from openjarvis.agents.native_openhands import NativeOpenhands
agent = NativeOpenhands(model="gpt-4", tools=[...])

# Depois: Dynamic via ECC catalog
agent = AgentFactory.create(
    spec_id="code-reviewer",
    config={"model": "gpt-4", "temperature": 0.7}
)
```

---

## 📊 ESTRUTURA DE BANCO DE DADOS

### Tabelas Existentes (manager.py)

```sql
managed_agents:
├─ id (TEXT, PK)
├─ name (TEXT)
├─ agent_type (TEXT)           ← "monitor_operative" | "openhands" | etc
├─ config_json (TEXT)          ← {"temperature": 0.7, ...}
├─ status (TEXT)               ← "idle" | "running" | "paused"
├─ summary_memory (TEXT)       ← Rolling context (16k chars max)
├─ created_at (REAL)
└─ updated_at (REAL)

agent_tasks:
├─ id (TEXT, PK)
├─ agent_id (FK → managed_agents)
├─ description (TEXT)
├─ status (TEXT)               ← "pending" | "running" | "complete"
├─ progress_json (TEXT)        ← {"step": 1, "current_tool": "search"}
├─ findings_json (TEXT)        ← [{"type": "issue", "data": {...}}]
└─ created_at (REAL)

agent_messages:
├─ id (TEXT, PK)
├─ agent_id (FK)
├─ direction (TEXT)            ← "user_to_agent" | "agent_to_user"
├─ content (TEXT)              ← Message content
├─ mode (TEXT)                 ← "queued" | "streaming"
├─ status (TEXT)               ← "pending" | "processed" | "failed"
└─ created_at (REAL)

agent_checkpoints:
├─ id (TEXT, PK)
├─ agent_id (FK)
├─ tick_id (TEXT)              ← Versão de iteração
├─ conversation_state (TEXT)   ← Serialized messages
├─ tool_state (TEXT)           ← Tool execution results
└─ created_at (REAL)
```

### Nova Tabela (Necessária)

```sql
agent_templates:           -- ECC Catalog
├─ id (TEXT, PK)          -- "code-reviewer" | "python-reviewer" | ...
├─ name (TEXT)
├─ agent_type (TEXT)      -- Tipo base
├─ description (TEXT)
├─ tags (TEXT)            -- JSON array: ["code", "review", "security"]
├─ default_config (TEXT)  -- Default overrides
├─ capabilities (TEXT)    -- JSON: tools + patterns
├─ ecc_source_path (TEXT) -- Link to ECC markdown
└─ created_at (REAL)
```

---

## 🎯 PADRÃO DE INTEGRAÇÃO

### Padrão 1: Direct Agent Use (Simples)
```
Client → POST /v1/managed-agents
       ├─ name: "my-python-reviewer"
       ├─ agent_type: "monitor_operative"
       └─ config: {"temperature": 0.7}

Response: {"id": "ag-abc123", "status": "idle"}

Client → POST /v1/managed-agents/ag-abc123/tasks
       └─ description: "Review my Python code"

Agent → Tool Invocation → Result Aggregation → Response
```

### Padrão 2: From ECC Template (Recomendado)
```
Client → GET /v1/managed-agents/templates
Response: [
  {
    "id": "code-reviewer",
    "name": "Code Reviewer",
    "capabilities": ["search", "analyze", "suggest"]
  }
]

Client → POST /v1/managed-agents
       ├─ template_id: "code-reviewer"
       ├─ name: "my-reviewer"
       └─ config: {...overrides}

AgentFactory.create() → Load ECC/agents/code-reviewer.md
                     → Instancia correto
                     → Injeta tools
                     → Retorna pronto
```

### Padrão 3: Consciência Coletiva (Inteligente)
```
Client → POST /v1/intelligently-route
       └─ description: "Find Python security issues and refactor"

CollectiveRouter:
  1. Parse requirements
  2. Score agents: [security-reviewer: 0.95, python-reviewer: 0.87]
  3. Dispatch: [security-reviewer, python-reviewer]
  4. Monitor: Real-time progress
  5. Aggregate: Merge findings
  6. Fallback: Anthropic if needed

Response: {
  "agents": [
    {"id": "ag-1", "role": "security", "findings": [...], "confidence": 0.95}
    {"id": "ag-2", "role": "quality", "findings": [...], "confidence": 0.87}
  ],
  "aggregated": {...},
  "confidence": 0.91
}
```

---

## 🔒 PADRÃO OPENAPI LIMPO

### Todas as rotas seguem padrão

```python
@router.get("/v1/managed-agents", response_model=ListAgentsResponse)
async def list_agents() -> ListAgentsResponse:
    """List all managed agents."""
    return ListAgentsResponse(agents=[...])

@router.post("/v1/managed-agents", response_model=Agent, status_code=201)
async def create_agent(req: CreateAgentRequest) -> Agent:
    """Create new managed agent."""
    return agent

# ✅ Clean:
# - Type hints explicit
# - Response models defined
# - Status codes correct
# - Docstrings present
# - No linting errors
```

---

## 📈 ROADMAP PRÓXIMAS FASES

```
✅ Fase 1: Ambiente Python 3.12 + FastAPI
✅ Fase 2: Chat endpoint testado
✅ Fase 3: Home page + docs
⏳ Fase 4: ECC Integration + Agent CRUD (VOCÊ ESTÁ AQUI)
   ├─ Parse ECC catalog
   ├─ Unified AgentFactory
   ├─ Collective routing
   └─ SQLite persistence
⏳ Fase 5: Memory + Stateful operations
   ├─ Session checkpoints
   ├─ Multi-turn context
   └─ Learning persistence
⏳ Fase 6: WebSocket + Real-time streaming
   ├─ Progress updates
   ├─ Tool invocation events
   └─ Result aggregation
⏳ Fase 7: Production scalability
   ├─ Redis backend
   ├─ Celery workers
   └─ Multi-node deployment
```

---

## 🎯 CONCLUSÕES ARQUITETURAIS

### ✅ O Que Já Existe
- AgentManager com SQLite (pronto)
- Agent CRUD routes (pronto para uso)
- Tool resolver system (funcional)
- Multiple agent primitives (10+)
- Server infrastructure (FastAPI completo)

### 🔄 O Que Falta
- ECC catalog unificado (specs)
- AgentFactory dinâmica
- Collective consciousness router
- Memory injection em prompts
- WebSocket streaming

### 💡 Próximo Passo Crítico
**Implementar AgentFactory + ECC Catalog Parser**

Esta é a ponte entre:
- Arquivos markdown estáticos em ECC
- Agentes instanciados dinamicamente
- Sistema distribuído de consciência coletiva

**Estimativa:** 4-6 horas de desenvolvimento
**Retorno:** Foundation sólida para todas as fases futuras

---

**Data:** 2026-11-04 04:21:50 UTC-3  
**Status:** Análise completa | Pronto para implementação  
**Próxima Ação:** Implementar ECC Catalog Parser + AgentFactory
