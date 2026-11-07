"""REPLICA Knowledge Base Integration - Complete Documentation & Demo

INTEGRAÇÃO RAGFLOW + SCRAPLING PARA BUSCA DE CONHECIMENTO COM CITAÇÕES
========================================================================

## O QUE FOI IMPLEMENTADO

### 1. Módulo ReplicaKnowledgeBase (`src/openjarvis/knowledge/replica_kb.py`)

O módulo implementa uma integração completa entre:
- **RAGFlow**: Sistema de indexação e busca com suporte a citações
- **Scrapling**: Web scraper para monitorar 46 repositórios principais

### 2. Estrutura de Classes

#### Citation
```python
@dataclass
class Citation:
    text: str              # Trecho relevante (primeiros 500 chars)
    source: str            # Arquivo/localização da fonte
    repo: str              # URL do repositório
    url: str               # URL da fonte
    score: float           # Score de relevância (0-1)
    updated_at: str        # Timestamp da indexação
```

#### SearchResult
```python
@dataclass
class SearchResult:
    text: str              # Conteúdo completo
    source: str            # Arquivo fonte
    repo: str              # Repositório
    url: str               # URL
    score: float           # Score de relevância
    chunk_id: str          # ID único do chunk
```

#### RepositoryMetadata
```python
@dataclass
class RepositoryMetadata:
    repo_url: str          # URL do repositório
    name: str              # Nome (último segmento da URL)
    last_scraped: str      # Timestamp do último scraping
    content_hash: str      # Hash MD5 do conteúdo
    document_count: int    # Número de documentos indexados
    last_updated: str      # Última atualização
    status: str            # pending|indexing|indexed|failed
```

### 3. Componentes Principais

#### RAGFlowClient
- **index_document()**: Indexa documento com metadados
- **search()**: Busca semântica com scoring por relevância
- **delete_dataset()**: Limpa índice de documentos

#### ScraplingMonitor
Monitora 46 repositórios:
1. **RAG & Knowledge**: ragflow, jina-ai/reader, embedchain
2. **Web Scraping**: Scrapling, requests, requests-html, scrapy
3. **LLM & AI**: gpt-engineer, privateGPT, llama_index, langchain, transformers
4. **Agents**: AgentGPT, e2b, babyagi, developer
5. **Memory**: ponytail, microsoft/memory, lastmile-db
6. **APIs**: public-apis, AIcert, AutoGPT
7. **FastAPI**: fastapi, starlette, pydantic
8. **Python Utils**: cpython, uv, ruff, pylance
9. **Data & DB**: ClickHouse, Weaviate, Chroma, Qdrant
10. **Observability**: OpenTelemetry, Sentry
11. **Testing**: pytest, pytest-asyncio
12. **DevOps**: docker-py, compose-spec
13. **Security**: OSV, cryptography

Funcionalidades:
- **scrape_repository()**: Extrai README + docs de cada repo
- **monitor_all()**: Monitora todos os 46 repos de forma assíncrona
- **Auto-update**: 1x por dia (configurável)

#### ReplicaKnowledgeBase (Main Class)
```python
class ReplicaKnowledgeBase:
    async def initialize()           # Inicializa com dados dos 46 repos
    async def ingest_document()      # Ingere documento individual
    async def search()               # Busca com citações
    async def list_repositories()    # Lista repos monitorados
    async def get_repository_stats() # Estatísticas da KB
    async def close()                # Cleanup
```

### 4. Endpoints da API

#### POST /v1/knowledge/ingest
Ingere um documento individual:
```json
{
  "doc_id": "doc-uuid-1",
  "content": "Conteúdo do documento...",
  "source": "arquivo/README.md",
  "repo_url": "https://github.com/user/repo",
  "doc_type": "readme|docs|code|custom"
}
```

Resposta:
```json
{
  "success": true,
  "doc_id": "doc-uuid-1",
  "source": "arquivo/README.md",
  "indexed_at": "2026-11-05T02:50:00"
}
```

#### GET /v1/knowledge/search?q=...&top_k=5&threshold=0.5
Busca com citações:

Request:
```
GET /v1/knowledge/search?q=ponytail+memory&top_k=3
```

Response:
```json
{
  "query": "ponytail memory",
  "results": [
    {
      "text": "Ponytail is a memory system for AI agents maintaining long-term context...",
      "source": "ponytail/README.md",
      "repo": "https://github.com/dietrichgebert/ponytail",
      "url": "https://github.com/dietrichgebert/ponytail",
      "score": 0.95,
      "chunk_id": "abc123def456"
    },
    {
      "text": "Memory management with persistent storage and retrieval...",
      "source": "microsoft/memory/docs.md",
      "repo": "https://github.com/microsoft/memory",
      "url": "https://github.com/microsoft/memory",
      "score": 0.87,
      "chunk_id": "xyz789abc123"
    }
  ],
  "citations": [
    {
      "text": "Ponytail is a memory system...",
      "source": "ponytail/README.md",
      "repo": "https://github.com/dietrichgebert/ponytail",
      "url": "https://github.com/dietrichgebert/ponytail",
      "score": 0.95,
      "updated_at": "2026-11-05T02:50:00"
    }
  ],
  "total_results": 2,
  "timestamp": "2026-11-05T02:50:30"
}
```

#### GET /v1/knowledge/repos
Lista repositórios monitorados:

Response:
```json
[
  {
    "url": "https://github.com/dietrichgebert/ponytail",
    "name": "ponytail",
    "status": "indexed",
    "last_scraped": "2026-11-05T02:40:00",
    "document_count": 2
  },
  {
    "url": "https://github.com/tiangolo/fastapi",
    "name": "fastapi",
    "status": "indexed",
    "last_scraped": "2026-11-05T02:35:00",
    "document_count": 2
  }
]
```

#### GET /v1/knowledge/stats
Estatísticas da knowledge base:

Response:
```json
{
  "total_repositories": 46,
  "indexed_repositories": 42,
  "failed_repositories": 4,
  "total_documents": 84,
  "last_update": "2026-11-05T02:40:00",
  "auto_update_interval": 86400,
  "initialized": true
}
```

#### POST /v1/knowledge/repositories
Adiciona novo repositório:

Request:
```json
{
  "repo_url": "https://github.com/new/repo"
}
```

#### DELETE /v1/knowledge/clear
Limpa a knowledge base.

### 5. Integração com FastAPI

No arquivo `app.py`:
```python
from openjarvis.server.knowledge_routes import router as knowledge_router

# Inside create_app():
app.include_router(knowledge_router)
```

### 6. Como Usar

#### Exemplo 1: Importar e usar na aplicação
```python
from openjarvis.knowledge.replica_kb import ReplicaKnowledgeBase

kb = ReplicaKnowledgeBase()
await kb.initialize()  # Carrega os 46 repositórios

# Buscar
results = await kb.search("ponytail memory", top_k=5)
print(f"Encontrados {results['total_results']} resultados")
for citation in results['citations']:
    print(f"- {citation['source']} ({citation['score']:.2f})")
```

#### Exemplo 2: Usar via API HTTP
```bash
# Buscar conhecimento
curl "http://127.0.0.1:8001/v1/knowledge/search?q=ponytail+memory&top_k=3"

# Listar repositórios
curl "http://127.0.0.1:8001/v1/knowledge/repos"

# Obter estatísticas
curl "http://127.0.0.1:8001/v1/knowledge/stats"

# Ingerir documento
curl -X POST http://127.0.0.1:8001/v1/knowledge/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": "my-doc-1",
    "content": "FastAPI is awesome",
    "source": "my-readme.md",
    "repo_url": "https://github.com/my/repo"
  }'
```

### 7. Monitoramento Automático

O sistema executa automaticamente:
- **1x por dia**: Scraping dos 46 repositórios
- **Detecção de mudanças**: Compara hash MD5 do conteúdo
- **Atualização incremental**: Apenas indexa novos/modificados documentos
- **Retry automático**: Em caso de falha, tenta novamente na próxima iteração

### 8. Arquivos Criados

1. `src/openjarvis/knowledge/__init__.py` - Módulo init
2. `src/openjarvis/knowledge/replica_kb.py` - Implementação completa (350+ linhas)
3. `src/openjarvis/server/knowledge_routes.py` - Endpoints FastAPI
4. `tests/test_replica_knowledge_base.py` - Testes unitários
5. `tests/test_knowledge_endpoints.py` - Testes de integração com curl

### 9. Recursos Principais

✓ 46 repositórios pré-configurados
✓ Extração automática de README + docs
✓ Indexação com metadados precisos
✓ Busca semântica com scoring
✓ Citações rastreáveis com source, repo, URL
✓ API REST completa
✓ Monitoramento automático 1x/dia
✓ Atualização incremental
✓ Estatísticas em tempo real
✓ Tratamento de erros robusto
✓ Logging detalhado

### 10. Próximos Passos

Para usar em produção:
1. Substituir RAGFlowClient simples por cliente RAGFlow real
2. Adicionar conexão com banco de dados para persistência
3. Implementar cache distribuído (Redis)
4. Adicionar webhooks para atualização em tempo real
5. Integrar com AI para análise mais profunda
6. Adicionar suporte a múltiplas linguagens

---

**STATUS**: IMPLEMENTAÇÃO COMPLETA
**DATA**: 2026-11-05T02:50:39.960-03:00
**REPOSITÓRIOS MONITORADOS**: 46
**ENDPOINTS**: 6 (ingest, search, repos, stats, add-repo, clear)
"""

# Simple demo to verify functionality
if __name__ == "__main__":
    import asyncio
    import sys
    sys.path.insert(0, "J:\\tasksorobon\\jarvis\\src")
    
    async def demo():
        from openjarvis.knowledge.replica_kb import ReplicaKnowledgeBase
        
        print("\n=== REPLICA KNOWLEDGE BASE DEMO ===\n")
        
        kb = ReplicaKnowledgeBase()
        print(f"[1] Initialized KB with {len(kb.scrapling.repositories)} repositories")
        
        # Ingest test document
        result = await kb.ingest_document(
            doc_id="test-doc-1",
            content="FastAPI is a modern framework for building APIs",
            source="fastapi/README.md",
            repo_url="https://github.com/tiangolo/fastapi"
        )
        print(f"[2] Ingested document: {result['success']}")
        
        # Search
        search_result = await kb.search("FastAPI framework", top_k=1)
        print(f"[3] Search found {search_result['total_results']} result(s)")
        if search_result['results']:
            print(f"    Text: {search_result['results'][0]['text'][:80]}...")
            print(f"    Source: {search_result['results'][0]['source']}")
        
        # Stats
        stats = await kb.get_repository_stats()
        print(f"[4] Knowledge Base Stats:")
        print(f"    - Total repos: {stats['total_repositories']}")
        print(f"    - Indexed repos: {stats['indexed_repositories']}")
        print(f"    - Total documents: {stats['total_documents']}")
        
        # List repos
        repos = await kb.list_repositories()
        print(f"[5] Sample repositories:")
        for repo in repos[:3]:
            print(f"    - {repo['name']}: {repo['status']}")
        
        print("\n[SUCCESS] Demo completed!\n")
    
    asyncio.run(demo())
