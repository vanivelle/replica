# 🔄 FLUXOS DE INTEGRAÇÃO - OpenJarvis Agent System

## Fluxo 1: Padrão Simples (Direto)

```
┌──────────────────┐
│   Client/User    │
└────────┬─────────┘
         │
         │ POST /v1/managed-agents
         │ {
         │   "name": "my-reviewer",
         │   "agent_type": "monitor_operative",
         │   "config": {"temperature": 0.7}
         │ }
         ↓
┌──────────────────────────────────────┐
│   Agent CRUD Route Handler           │
│   (agent_manager_routes.py)          │
└────────┬─────────────────────────────┘
         │
         │ AgentManager.create_agent()
         ↓
┌──────────────────────────────────────┐
│   AgentManager (manager.py)          │
│   - Generates ID                     │
│   - SQLite INSERT                    │
│   - Returns agent spec               │
└────────┬─────────────────────────────┘
         │
         │ Agent created & idle
         ↓
┌──────────────────────────────────────┐
│   managed_agents table               │
│   id: "ag-abc123"                    │
│   status: "idle"                     │
│   config_json: {...}                 │
└──────────────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────┐
│   Response to Client                 │
│ {                                    │
│   "id": "ag-abc123",                 │
│   "name": "my-reviewer",             │
│   "status": "idle",                  │
│   "created_at": 1731xxx              │
│ }                                    │
└──────────────────────────────────────┘
```

---

## Fluxo 2: Template-Based (ECC)

```
┌──────────────────────────────────────┐
│   Client/User                        │
│ GET /v1/managed-agents/templates     │
└────────┬─────────────────────────────┘
         │
         │ List available specs
         ↓
┌──────────────────────────────────────┐
│   AgentManager.get_templates()       │
│   (scans agent_templates table)      │
└────────┬─────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────┐
│   agent_templates table              │
│   [                                  │
│     {                                │
│       "id": "code-reviewer",         │
│       "name": "Code Reviewer",       │
│       "capabilities": [...]          │
│       "ecc_source": "agents/..."     │
│     }                                │
│   ]                                  │
└────────┬─────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────┐
│   Response to Client                 │
│   [48 agent templates]               │
└──────────────────────────────────────┘


┌──────────────────────────────────────┐
│   Client Selects Template            │
│ POST /v1/managed-agents              │
│ {                                    │
│   "template_id": "code-reviewer",    │
│   "name": "prod-reviewer"            │
│ }                                    │
└────────┬─────────────────────────────┘
         │
         │ AgentManager.create_from_template()
         ↓
┌──────────────────────────────────────┐
│   AgentFactory                       │
│   1. Load ECC/agents/code-rev.md     │
│   2. Parse templates                 │
│   3. Instantiate type-specific agent │
│   4. Load default tools              │
│   5. Inject capabilities             │
└────────┬─────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────┐
│   Agent Instance Created             │
│   ├─ Type: MonitorOperative          │
│   ├─ Tools: [search, analyze, code]  │
│   ├─ Memory: Initialized             │
│   └─ Status: ready                   │
└────────┬─────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────┐
│   SQLite: managed_agents + tasks     │
│   Agent stored and ready             │
└──────────────────────────────────────┘
```

---

## Fluxo 3: Consciência Coletiva (Inteligente)

```
┌──────────────────────────────────────┐
│   User Input                         │
│ "Find Python security issues         │
│  and suggest refactoring"            │
└────────┬─────────────────────────────┘
         │
         │ POST /v1/intelligently-route
         ↓
┌──────────────────────────────────────┐
│   Collective Consciousness Router    │
│   (new component to build)           │
│                                      │
│   1. Parse requirements              │
│   ├─ Keywords: [python, security]    │
│   ├─ Tasks: [find, suggest]          │
│   └─ Complexity: medium              │
│                                      │
│   2. Query agent_templates           │
│   ├─ security-reviewer: tags match   │
│   ├─ python-reviewer: tags match     │
│   ├─ refactor-cleaner: tags match    │
│   └─ build-resolver: no match        │
│                                      │
│   3. Scoring phase                   │
│   ├─ security-reviewer: 0.95         │
│   ├─ python-reviewer: 0.87           │
│   └─ refactor-cleaner: 0.82          │
│                                      │
│   4. Orchestrate dispatch            │
│   ├─ Create task for Agent1          │
│   ├─ Create task for Agent2          │
│   └─ Assign Agent3 as fallback       │
│                                      │
│   5. Fallback strategy               │
│   └─ If no local agent ≥ 0.7,       │
│      use Anthropic/Claude API        │
│                                      │
└────────┬─────────────────────────────┘
         │
         ├─────────────────┬─────────────────┬──────────────────┐
         │                 │                 │                  │
         ↓                 ↓                 ↓                  ↓
    ┌──────────┐      ┌──────────┐     ┌──────────┐      ┌──────────┐
    │ Agent 1  │      │ Agent 2  │     │ Agent 3  │      │ Cloud    │
    │Security  │      │ Python   │     │Refactor  │      │ Fallback │
    │Reviewer  │      │Reviewer  │     │Cleaner   │      │ (Claude) │
    └────┬─────┘      └────┬─────┘     └────┬─────┘      └────┬─────┘
         │                 │                 │                 │
         │ [Tool Invocation Loop]            │                 │
         │ • search: "python security"       │                 │
         │ • analyze: code patterns          │                 │
         │ • report: findings                │                 │
         │                                   │                 │
         ↓                 ↓                 ↓                 ↓
    ┌──────────────┐  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Findings     │  │ Code Issues  │ │ Refactored   │ │ Alternative  │
    │ [issues...]  │  │ [metrics...] │ │ Code [src]   │ │ Solution     │
    └──────────────┘  └──────────────┘ └──────────────┘ └──────────────┘
         │                 │                 │                 │
         └────────────┬────┴────────┬────────┴────────┬────────┘
                      │            │                 │
                      ↓            ↓                 ↓
              ┌─────────────────────────────────────────────┐
              │  Aggregation & Merge Phase                 │
              │ • Deduplicate findings                     │
              │ • Merge recommendations                    │
              │ • Calculate confidence scores              │
              │ • Prioritize by severity                   │
              └────────────┬─────────────────────────────────┘
                           │
                           ↓
              ┌─────────────────────────────────────────────┐
              │  Final Response to User                     │
              │ {                                          │
              │   "agents": [                              │
              │     {                                      │
              │       "id": "ag-sec",                      │
              │       "role": "security",                  │
              │       "confidence": 0.95,                  │
              │       "findings": [...]                    │
              │     },                                     │
              │     {...}                                  │
              │   ],                                       │
              │   "aggregated": {                          │
              │     "critical_issues": 3,                  │
              │     "recommendations": [...],              │
              │     "suggested_refactoring": [...]         │
              │   },                                       │
              │   "confidence": 0.91,                      │
              │   "processing_time": "2.3s"                │
              │ }                                          │
              └─────────────────────────────────────────────┘
```

---

## Fluxo 4: Multi-Turn Stateful Operations

```
Turn 1:
┌─────────────────────┐
│ User: "Review this" │
└────────┬────────────┘
         │
         │ Create Task
         ↓
┌─────────────────────────────────────┐
│ Agent processes                     │
│ - Tool invocation                   │
│ - Store progress in agent_tasks     │
│ - Store messages in agent_messages  │
└────────┬────────────────────────────┘
         │
         │ Checkpoint saved
         ↓
┌─────────────────────────────────────┐
│ agent_checkpoints table:            │
│ id, agent_id, tick_id, state_json   │
│ conversation_state: [msg1, msg2...] │
│ tool_state: {search: {...}, ...}    │
└─────────────────────────────────────┘

Turn 2:
┌──────────────────────────────┐
│ User: "Dive deeper"          │
└────────┬─────────────────────┘
         │
         │ Load Checkpoint
         ↓
┌────────────────────────────────────────┐
│ Replay history to Agent                │
│ • Conversation context                 │
│ • Previous tool results                │
│ • Memory summary (16k chars max)       │
└────────┬───────────────────────────────┘
         │
         │ Agent continues
         ↓
┌────────────────────────────────────────┐
│ New tool invocations                   │
│ Informed by prior context              │
└────────┬───────────────────────────────┘
         │
         │ Checkpoint saved again
         ↓
┌────────────────────────────────────────┐
│ agent_checkpoints updated              │
│ Summary memory fed forward              │
└────────────────────────────────────────┘

Turn N:
┌──────────────────────────┐
│ Continuous stateful flow │
│ (as many turns as needed)│
└──────────────────────────┘
```

---

## Fluxo 5: Real-Time Streaming (WebSocket)

```
┌────────────────┐
│   Client       │
│ (Browser/CLI)  │
└────────┬───────┘
         │
         │ WS /v1/managed-agents/{agent_id}/stream
         │ (WebSocket upgrade)
         ↓
┌──────────────────────────┐
│ WebSocket Handler        │
│ (stream_bridge.py)       │
└────────┬─────────────────┘
         │
         │ Agent begins execution
         │ (background thread)
         ↓
┌──────────────────────────────────────┐
│ Event Loop (Agent Execution)         │
│                                      │
│ 1. Tool Resolution                   │
│    Event: {"type": "tool_select",... │
│    Sent to WS client instantly       │
│                                      │
│ 2. Tool Execution                    │
│    Event: {"type": "executing",      │
│    "tool": "search", "params": {...} │
│    Sent with progress updates        │
│                                      │
│ 3. Tool Results                      │
│    Event: {"type": "result",         │
│    "tool": "search", "data": {...}   │
│    Sent immediately                  │
│                                      │
│ 4. Reasoning/Analysis                │
│    Event: {"type": "reasoning",      │
│    "chunk": "LLM token stream"       │
│    Sent as tokens arrive (streaming) │
│                                      │
│ 5. Decision Making                   │
│    Event: {"type": "decision",       │
│    "action": "next_tool"             │
│    Sent on completion                │
│                                      │
│ 6. Final Results                     │
│    Event: {"type": "complete",       │
│    "findings": [...],                │
│    "summary": "..."                  │
│    Sent at end                       │
│                                      │
└────────┬─────────────────────────────┘
         │
         ├─────────────────┬─────────────────┤
         │                 │                 │
         ↓                 ↓                 ↓
    ┌────────┐        ┌────────┐       ┌────────┐
    │ Event  │        │ Event  │       │ Event  │
    │ 1,2,3  │        │ 4,5    │       │ 6      │
    │        │        │        │       │        │
    │ Client │        │ Client │       │ Client │
    │ updates│        │ updates│       │ updates│
    │ UI     │        │ UI     │       │ UI     │
    │ real   │        │ real   │       │ real   │
    │ time   │        │ time   │       │ time   │
    └────────┘        └────────┘       └────────┘
```

---

## Fluxo 6: ECC Catalog Parser (Implementar)

```
┌─────────────────────────────────────┐
│ ECC Repository Structure            │
│                                     │
│ ecc/agents/                         │
│ ├── code-reviewer.md                │
│ ├── python-reviewer.md              │
│ ├── security-reviewer.md            │
│ ├── architecture-reviewer.md        │
│ ├── build-resolvers/                │
│ │   ├── python-build-resolver.md    │
│ │   ├── java-build-resolver.md      │
│ │   └── (3 more)                    │
│ └── (40+ more agents)               │
│                                     │
│ schemas/                            │
│ ├── code-reviewer-prompt.txt        │
│ ├── python-reviewer-config.json     │
│ └── (tools & capabilities)          │
│                                     │
└────────┬────────────────────────────┘
         │
         │ ECC Catalog Parser
         │ (new: ecc_parser.py)
         ↓
┌────────────────────────────────────────┐
│ 1. Read ECC files                      │
│    ├─ glob ecc/agents/*.md             │
│    ├─ extract frontmatter (YAML)       │
│    ├─ parse description                │
│    └─ extract capabilities section     │
│                                        │
│ 2. Build AgentSpec objects             │
│    {                                   │
│      "id": "code-reviewer",            │
│      "name": "Code Reviewer",          │
│      "agent_type": "monitor_operative",│
│      "description": "...",             │
│      "tags": ["code", "review"],       │
│      "capabilities": [                 │
│        "web_search",                   │
│        "code_analysis",                │
│        "suggestion"                    │
│      ],                                │
│      "default_config": {               │
│        "temperature": 0.7,             │
│        "max_tokens": 2048              │
│      }                                 │
│    }                                   │
│                                        │
│ 3. Validate specs                      │
│    ├─ Check required fields            │
│    ├─ Verify tools exist               │
│    └─ Ensure types are valid           │
│                                        │
│ 4. Store in agent_templates            │
│    INSERT INTO agent_templates (...)   │
│    VALUES (...) [48 rows]              │
│                                        │
└────────┬───────────────────────────────┘
         │
         ↓
┌────────────────────────────────────────┐
│ agent_templates Table                  │
│                                        │
│ id              name              type │
│ code-reviewer   Code Reviewer   ...    │
│ py-reviewer     Python Reviewer ...    │
│ sec-reviewer    Security Rev    ...    │
│ arch-reviewer   Architecture    ...    │
│ py-build        Python Builder  ...    │
│ java-build      Java Builder    ...    │
│ kotlin-build    Kotlin Builder  ...    │
│ go-build        Go Builder      ...    │
│ rust-build      Rust Builder    ...    │
│ deep-research   Deep Research   ...    │
│ ... (38 more)                          │
│                                        │
└────────┬───────────────────────────────┘
         │
         │ Now accessible via API
         ↓
┌────────────────────────────────────────┐
│ GET /v1/managed-agents/templates       │
│ Returns all 48 agent specs             │
└────────────────────────────────────────┘
```

---

## Fluxo 7: Agent Factory (Dinâmica)

```
┌────────────────────────────────────────┐
│ Client Request                         │
│ POST /v1/managed-agents                │
│ {                                      │
│   "template_id": "security-reviewer",  │
│   "name": "prod-security-checker",     │
│   "config": {"temperature": 0.3}       │
│ }                                      │
└────────┬───────────────────────────────┘
         │
         │ AgentManager.create_from_template()
         ↓
┌────────────────────────────────────────┐
│ AgentFactory.create()                  │
│ (new component to build)               │
│                                        │
│ 1. Fetch spec from agent_templates     │
│    SELECT * FROM agent_templates       │
│    WHERE id = 'security-reviewer'      │
│                                        │
│    Result:                             │
│    {                                   │
│      "agent_type": "monitor_operative",│
│      "default_config": {...},          │
│      "capabilities": ["search", ...]   │
│    }                                   │
│                                        │
│ 2. Merge configs                       │
│    merged = default_config.update(     │
│      user_config                       │
│    )                                   │
│    // temperature: 0.3 (user override) │
│                                        │
│ 3. Instantiate correct agent type      │
│    switch(agent_type) {                │
│      case "monitor_operative":         │
│        agent = MonitorOperative(       │
│          config=merged,                │
│          capabilities=capabilities     │
│        )                               │
│      case "openhands":                 │
│        agent = NativeOpenhands(...)    │
│      ...                               │
│    }                                   │
│                                        │
│ 4. Load tools dynamically              │
│    for tool in capabilities:           │
│      tool_instance = tool_resolver.    │
│      instantiate(tool)                 │
│      agent.register_tool(tool_instance)│
│                                        │
│ 5. Initialize memory                   │
│    agent.memory = MemoryBackend(       │
│      agent_id=agent_id                 │
│    )                                   │
│                                        │
│ 6. Save to SQLite                      │
│    INSERT INTO managed_agents (...)    │
│    INSERT INTO agent_capabilities (...}│
│                                        │
└────────┬───────────────────────────────┘
         │
         ↓
┌────────────────────────────────────────┐
│ Agent Instance Created & Ready         │
│                                        │
│ ├─ ID: ag-xyz789                       │
│ ├─ Type: MonitorOperative              │
│ ├─ Name: prod-security-checker        │
│ ├─ Config: {temperature: 0.3}          │
│ ├─ Tools: [web_search, code_analysis] │
│ ├─ Memory: Initialized                 │
│ ├─ Status: idle                        │
│ └─ Created_at: timestamp               │
│                                        │
└────────┬───────────────────────────────┘
         │
         ↓
┌────────────────────────────────────────┐
│ Response to Client                     │
│ {                                      │
│   "id": "ag-xyz789",                   │
│   "name": "prod-security-checker",     │
│   "status": "idle",                    │
│   "created_at": "2026-11-04T..."       │
│ }                                      │
└────────────────────────────────────────┘
```

---

**Data:** 2026-11-04  
**Status:** 7 fluxos mapeados | Pronto para implementação
