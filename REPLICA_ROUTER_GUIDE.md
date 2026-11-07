# ReplicaRouter - Intelligent Multi-Provider Routing Integration

## 🎯 Overview

ReplicaRouter é uma solução completa de roteamento inteligente que integra OmniRoute + 9Router patterns, permitindo escolher automaticamente o melhor provider baseado em:

- **Latência**: Métricas em tempo real de cada provider
- **Custo**: Preços por 1k tokens (Gemini $$$, Ollama $$, Grok $$$)
- **Especialidade**: Roteamento automático por tipo de tarefa (code, research, data, etc)
- **Qualidade**: Score de qualidade e taxa de sucesso
- **Feedback**: Aprendizado a partir de avaliações de usuário

## 📦 Arquitetura

```
┌─────────────────────────────────────────────┐
│  OpenJarvis API Server (FastAPI)            │
├─────────────────────────────────────────────┤
│  POST /v1/chat/completions (model="auto")   │
│  + X-Replica-Specialty: code|research|...   │
└─────────────────────────┬───────────────────┘
                          │
                    ReplicaRouter
                  ┌─────────────────┐
                  │ ProviderRegistry│◄─── 8 providers
                  │ RoutingWeights  │     padrão
                  │ RoutingContext  │
                  └────────┬────────┘
                           │
        ┌──────────┬───────┼───────┬──────────┐
        │          │       │       │          │
    ECC-Code  Gemini  Ollama  Grok  Claude  Vertex
    Specialist ($$)  ($)  ($$$) ($$$) ($$)

📊 Métricas em tempo real
📈 Aprendizado adaptativo
💰 Estimativas de custo
⭐ Avaliações de usuário
```

## 🚀 Uso Rápido

### 1. Chat com Roteamento Automático

```bash
curl -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H "X-Replica-Specialty: code" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [
      {"role": "user", "content": "Como otimizar este código Python?"}
    ],
    "max_tokens": 2048
  }'
```

**Resultado**: Router escolhe automaticamente o melhor provider para análise de código.

### 2. Selecionar Provider

```bash
curl -X POST http://127.0.0.1:8000/v1/routing/select \
  -H "Content-Type: application/json" \
  -d '{
    "specialty": "research",
    "priority": "quality",
    "tokens_estimate": 2000
  }'
```

**Resposta**:
```json
{
  "provider": "grok-api",
  "score": 0.749,
  "reason": "Primary selection",
  "alternatives": [
    ["claude-sonnet", 0.745],
    ["gemini-pro", 0.712]
  ]
}
```

### 3. Métricas em Tempo Real

```bash
# Todos os providers
curl http://127.0.0.1:8000/v1/routing/metrics

# Provider específico
curl http://127.0.0.1:8000/v1/routing/metrics?provider=ecc-code-specialist
```

### 4. Estimativa de Custo

```bash
curl "http://127.0.0.1:8000/v1/routing/cost?provider=gemini-pro&tokens=5000"
```

**Resposta**:
```json
{
  "provider": "gemini-pro",
  "tokens": 5000,
  "cost_usd": 0.005,
  "cost_per_1k": 0.001
}
```

### 5. Submeter Feedback

```bash
curl -X POST http://127.0.0.1:8000/v1/routing/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "ecc-code-specialist",
    "success": true,
    "latency_ms": 287,
    "tokens_used": 1500,
    "user_rating": 4.8
  }'
```

### 6. Especialidades Disponíveis

```bash
curl http://127.0.0.1:8000/v1/routing/specialties
```

## 🔧 Arquivos Criados/Modificados

### Arquivos Criados

1. **`src/openjarvis/routing/replica_router.py`** (23KB)
   - Core do ReplicaRouter
   - ProviderRegistry com 8 providers padrão
   - Métricas em tempo real
   - Singleton global

2. **`src/openjarvis/server/routing_routes.py`** (14KB)
   - API endpoints FastAPI
   - `/v1/routing/select` - Selecionar provider
   - `/v1/routing/metrics` - Métricas
   - `/v1/routing/cost` - Custo
   - `/v1/routing/feedback` - Feedback
   - `/v1/routing/stats` - Estatísticas
   - `/v1/routing/providers` - Listar providers
   - `/v1/routing/health` - Health check
   - `/v1/routing/specialties` - Especialidades

3. **`test_replica_router.py`** (12KB)
   - Teste completo de todos endpoints
   - 9 casos de teste
   - Relatório resumido

### Arquivos Modificados

1. **`src/openjarvis/routing/__init__.py`**
   - Exporta ReplicaRouter, get_router(), enums

2. **`src/openjarvis/server/app.py`**
   - Import de routing_router
   - Registro do router ao FastAPI app

3. **`src/openjarvis/server/chat_completions.py`**
   - Integração com ReplicaRouter
   - Suporte a `model="auto"`
   - Header `X-Replica-Specialty`
   - Registro automático de métricas

## 📊 Providers Suportados

| Provider | Tipo | Specialty | Custo | Latência | Quality |
|----------|------|-----------|-------|----------|---------|
| ecc-code-specialist | ECC Agent | code | $$ | 300ms | 0.95 |
| gemini-pro | Cloud | general | $ | 400ms | 0.85 |
| ollama-llama2 | Local | general | FREE | 200ms | 0.75 |
| grok-api | Cloud | research | $$ | 600ms | 0.88 |
| claude-sonnet | Cloud | reasoning | $$$ | 500ms | 0.92 |
| vertex-bison | Cloud | general | $$ | 450ms | 0.80 |
| minimax-budget | Cloud | general | $ | 350ms | 0.65 |
| kiro-free | Free | general | FREE | 800ms | 0.60 |

## 🎯 Especialidades

```
CODE      → ecc-code-specialist, claude-sonnet, gemini-pro
RESEARCH  → grok-api, claude-sonnet, gemini-pro
DATA      → ecc-code-specialist, vertex-bison, gemini-pro
GENERAL   → gemini-pro, claude-sonnet, ollama-llama2
REASONING → claude-sonnet, ecc-code-specialist, gemini-pro
CREATIVE  → claude-sonnet, gemini-pro, grok-api
```

## 🔍 Exemplo Completo

### Cenário: Análise de Código

```bash
# 1. Fazer request com roteamento automático
curl -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H "X-Replica-Specialty: code" \
  -d '{
    "model": "auto",
    "messages": [
      {"role": "user", "content": "Analise o algoritmo de sorting"}
    ],
    "max_tokens": 2000,
    "temperature": 0.3
  }'

# Response (exemplo):
# {
#   "provider": "ecc-code-specialist",
#   "model": "auto",
#   "choices": [
#     {
#       "message": {
#         "role": "assistant",
#         "content": "O algoritmo de sorting utiliza quicksort com O(n log n)..."
#       }
#     }
#   ]
# }

# 2. Submeter feedback sobre a qualidade
curl -X POST http://127.0.0.1:8000/v1/routing/feedback \
  -d '{
    "provider": "ecc-code-specialist",
    "success": true,
    "latency_ms": 287,
    "tokens_used": 1500,
    "user_rating": 4.8
  }'

# 3. Verificar métricas atualizadas
curl http://127.0.0.1:8000/v1/routing/metrics?provider=ecc-code-specialist

# Response (atualizado com novo feedback):
# {
#   "provider": "ecc-code-specialist",
#   "user_rating": 4.8,
#   "total_requests": 3,
#   ...
# }
```

## 📈 Prioridades de Roteamento

- **`balanced`** (padrão): Ponderação igual entre custo, qualidade, latência
- **`cost`**: Maximize economia (50% bonus em score de custo)
- **`speed`**: Minimize latência (50% bonus em score de latência)
- **`quality`**: Maximize qualidade (50% bonus em score de qualidade)

## 🔐 Segurança

- Thread-safe com locks RLock
- Singleton global thread-safe
- Isolamento de contextos de requisição
- Validação de entrada em todos endpoints

## 📝 Integração com /v1/chat/completions

O endpoint `/v1/chat/completions` agora suporta:

```
X-Replica-Specialty: code|research|data|general|reasoning|creative
```

Quando `model="auto"`, o router:
1. Interpreta a especialidade do header
2. Seleciona o melhor provider
3. Executa a requisição
4. Registra latência real e sucesso
5. Retorna resultado com metadados de roteamento

## ✅ Validation

Teste com:
```bash
python test_replica_router.py
```

Ou teste individual:
```bash
python test_router_quick.py
```

## 🚀 Próximos Passos

1. **Treinar modelos de aprendizado**: 
   - Usar feedback histórico para melhorar ponderações
   - Implementar reinforcement learning

2. **Fallback automático**:
   - Se provider falha, tentar próximo da lista
   - Circuit breaker para providers fora do ar

3. **Multi-regional**:
   - Rote para provider mais próximo geograficamente
   - Reduz latência global

4. **Rate limiting integrado**:
   - Detectar quando quota de provider está próxima de esgotar
   - Balancear carga entre múltiplos accounts

5. **Token optimization**:
   - Implementar RTK compression de 9Router
   - Economizar 20-40% tokens em requisições

## 📞 API Reference

### Endpoints

- `POST /v1/routing/select` - Seleciona provider
- `GET /v1/routing/metrics` - Métricas
- `GET /v1/routing/cost` - Estimativa de custo
- `GET /v1/routing/stats` - Estatísticas
- `POST /v1/routing/feedback` - Feedback
- `GET /v1/routing/providers` - Lista providers
- `GET /v1/routing/health` - Health check
- `GET /v1/routing/specialties` - Especialidades

### Headers

- `X-Replica-Specialty`: Especialidade da requisição

### Modelos

```python
RoutingRequest:
  - specialty: str
  - priority: str
  - tokens_estimate: int
  - max_latency_ms: int
  - max_cost_per_request: float
  - min_quality_score: float

UsageFeedback:
  - provider: str
  - success: bool
  - latency_ms: float
  - tokens_used: int
  - user_rating: float (1-5)
```

---

**Status**: ✅ IMPLEMENTADO E TESTADO
**Última Atualização**: 2026-11-05
