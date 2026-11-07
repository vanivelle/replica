# ReplicaRouter - Quick Reference

## Installation

Already integrated into OpenJarvis at:
- `src/openjarvis/routing/replica_router.py`
- `src/openjarvis/server/routing_routes.py`

## Quick Start

```python
from openjarvis.routing import get_router, SpecialtyType, RoutingContext

# Get router instance
router = get_router()

# Create routing context
context = RoutingContext(
    specialty=SpecialtyType.CODE,
    priority="quality",
    tokens_estimate=2000
)

# Select provider
provider, info = router.select_provider(context)
print(f"Selected: {provider} (score: {info.get('score'):.3f})")

# Record usage
router.record_usage(provider, success=True, latency_ms=287, tokens_used=1500)

# Get metrics
metrics = router.get_metrics(provider)
print(f"Latency: {metrics['avg_latency_ms']:.1f}ms")
print(f"Success rate: {metrics['success_rate']:.1%}")
```

## API Endpoints

```bash
# Health check
GET /v1/routing/health

# List all providers
GET /v1/routing/providers

# List specialties
GET /v1/routing/specialties

# Select best provider
POST /v1/routing/select
{
  "specialty": "code",
  "priority": "quality",
  "tokens_estimate": 2000
}

# Get metrics
GET /v1/routing/metrics
GET /v1/routing/metrics?provider=ecc-code-specialist

# Get cost estimate
GET /v1/routing/cost?provider=gemini-pro&tokens=5000

# Submit feedback
POST /v1/routing/feedback
{
  "provider": "ecc-code-specialist",
  "success": true,
  "latency_ms": 287,
  "tokens_used": 1500,
  "user_rating": 4.8
}

# Get statistics
GET /v1/routing/stats
```

## Specialties

```
CODE      - Code analysis, debugging, ECC agents
RESEARCH  - Research, RAGFlow, knowledge synthesis
DATA      - Data processing, analysis
GENERAL   - General chat, text
REASONING - Complex reasoning tasks
CREATIVE  - Creative tasks, brainstorming
```

## Providers Reference

| Name | Type | Specialty | Cost | Latency | Quality |
|------|------|-----------|------|---------|---------|
| ecc-code-specialist | ECC | CODE | $$ | 300ms | 0.95 |
| gemini-pro | Cloud | GENERAL | $ | 400ms | 0.85 |
| ollama-llama2 | Local | GENERAL | FREE | 200ms | 0.75 |
| grok-api | Cloud | RESEARCH | $$ | 600ms | 0.88 |
| claude-sonnet | Cloud | REASONING | $$$ | 500ms | 0.92 |
| vertex-bison | Cloud | DATA | $$ | 450ms | 0.80 |
| minimax-budget | Cloud | GENERAL | $ | 350ms | 0.65 |
| kiro-free | Free | GENERAL | FREE | 800ms | 0.60 |

## Chat with Auto Routing

```bash
curl -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H "X-Replica-Specialty: code" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "auto",
    "messages": [
      {"role": "user", "content": "Analyze this Python code..."}
    ],
    "max_tokens": 2048
  }'
```

## Scoring Algorithm

```
Score = (
  quality × 0.30 +
  cost × 0.20 +
  latency × 0.25 +
  reliability × 0.15 +
  availability × 0.10
) × priority_bonus × (1 + user_rating_bonus)
```

## Test Commands

```bash
# Quick test without server
python test_router_quick.py

# Integration test
python test_integration.py

# Full test against live server
python test_replica_router.py
```

## Files

**Core**
- `src/openjarvis/routing/replica_router.py` - Main implementation
- `src/openjarvis/server/routing_routes.py` - API endpoints

**Documentation**
- `REPLICA_ROUTER_GUIDE.md` - Full guide with 50+ examples
- `IMPLEMENTATION_SUMMARY.txt` - Technical details
- `CHECKPOINT_REPLICA_ROUTER.md` - Project checkpoint

**Tests**
- `test_router_quick.py` - 8 unit tests
- `test_integration.py` - 9 integration tests
- `test_replica_router.py` - Full API tests

---

**Status**: Ready for Production  
**Last Updated**: 2026-11-05  
**Version**: 1.0.0 Final
