# 🚀 Próximos Passos - Fase 2 (2-4 horas)

## Objetivo
Integrar a Camada A (Foundation Layer) com FastAPI e criar o Agent Factory para instanciação dinâmica de agentes.

---

## Passo 1: Criar Rotas FastAPI (1 hora)

### Arquivo: `src/openjarvis/server/layer_a_routes.py`

```python
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List

from openjarvis.agents.ecc_parser import ECCParser, ECCCategory
from openjarvis.routing.omni_router import OmniRouter, RoutingContext
from openjarvis.graph.graphify_parser import GraphifyManager
from openjarvis.ponytail.tunnel_bridge import PonytailIntegration
from openjarvis.archify.generator import create_openjarvis_architecture_diagram

# Inicializar componentes
parser = ECCParser()
parser.load_from_database()

router_omni = OmniRouter()
graphify_mgr = GraphifyManager()
ponytail_integration = PonytailIntegration()
archify_gen = create_openjarvis_architecture_diagram()

# Criar router
router = APIRouter(prefix="/v1", tags=["foundation-layer-a"])

# ========== ENDPOINTS ==========

@router.get("/agents/ecc")
async def list_ecc_agents(
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    capability: Optional[str] = Query(None)
):
    """
    Lista agentes ECC com filtros opcionais
    
    Exemplos:
    - GET /v1/agents/ecc
    - GET /v1/agents/ecc?category=CODE_REVIEW
    - GET /v1/agents/ecc?tag=security
    - GET /v1/agents/ecc?capability=review_code
    """
    try:
        if category:
            agents = parser.get_agents_by_category(ECCCategory[category.upper()])
        elif tag:
            agents = parser.get_agents_by_tag(tag)
        elif capability:
            agents = parser.get_agents_by_capability(capability)
        else:
            agents = list(parser.agents.values())
        
        return {
            "total": len(agents),
            "agents": [
                {
                    "id": a.id,
                    "name": a.name,
                    "category": a.category.value,
                    "description": a.description,
                    "capabilities": a.capabilities
                }
                for a in agents
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/ecc/{agent_id}")
async def get_ecc_agent(agent_id: str):
    """
    Obtém detalhes completos de um agente ECC
    
    Exemplo:
    GET /v1/agents/ecc/ecc_code_reviewer_python
    """
    agent = parser.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agente {agent_id} não encontrado")
    
    return {
        "id": agent.id,
        "name": agent.name,
        "category": agent.category.value,
        "description": agent.description,
        "capabilities": agent.capabilities,
        "required_skills": agent.required_skills,
        "dependencies": agent.dependencies,
        "tags": list(agent.tags),
        "confidence_score": agent.confidence_score,
        "version": agent.version
    }


@router.get("/agents/ecc/stats")
async def get_ecc_statistics():
    """
    Retorna estatísticas gerais dos agentes ECC
    """
    stats = parser.get_statistics()
    return {
        "total_agents": stats["total_agents"],
        "by_category": stats["by_category"],
        "total_unique_capabilities": stats["total_unique_capabilities"],
        "total_unique_tags": stats["total_unique_tags"],
        "average_capabilities_per_agent": stats["average_capabilities_per_agent"]
    }


@router.post("/routing/select-model")
async def select_model(
    task_type: str,
    priority: str = "balanced",
    max_latency_ms: int = 5000,
    tokens_estimate: int = 1000
):
    """
    Seleciona melhor modelo para uma tarefa
    
    Exemplo:
    POST /v1/routing/select-model
    {
        "task_type": "code_review",
        "priority": "quality",
        "max_latency_ms": 2000,
        "tokens_estimate": 2000
    }
    """
    try:
        context = RoutingContext(
            task_type=task_type,
            priority=priority,
            max_latency_ms=max_latency_ms,
            tokens_estimate=tokens_estimate
        )
        
        model, info = router_omni.select_model(context)
        
        return {
            "selected_model": model,
            "score": info.get("score"),
            "fallbacks": info.get("fallbacks", []),
            "reason": info.get("reason")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/routing/stats")
async def get_routing_stats():
    """
    Retorna estatísticas de roteamento
    """
    stats = router_omni.get_routing_stats()
    return stats


@router.get("/graph/dependencies/{agent_id}")
async def get_agent_dependencies(agent_id: str):
    """
    Retorna dependências de um agente
    
    Exemplo:
    GET /v1/graph/dependencies/ecc_code_reviewer_python
    """
    agent = parser.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agente {agent_id} não encontrado")
    
    try:
        # Carregar agentes no Graphify
        graphify_mgr.load_ecc_agents([
            {
                "id": a.id,
                "name": a.name,
                "category": a.category.value,
                "description": a.description,
                "capabilities": a.capabilities,
                "dependencies": a.dependencies
            }
            for a in parser.agents.values()
        ])
        
        deps = graphify_mgr.graph.find_dependencies(agent_id)
        return {
            "agent_id": agent_id,
            "dependencies": deps,
            "total_dependencies": (
                len(deps.get("direct_agents", [])) + 
                len(deps.get("transitive_agents", []))
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tunnel/create")
async def create_tunnel(
    session_id: str,
    compression_level: str = "balanced"
):
    """
    Cria um tunnel CLI com contexto comprimido
    
    Exemplo:
    POST /v1/tunnel/create
    {
        "session_id": "my_session",
        "compression_level": "balanced"
    }
    """
    try:
        context = {
            "session_id": session_id,
            "agents": [a.id for a in parser.agents.values()],
            "available_models": router_omni.registry.list_models()
        }
        
        tunnel_info = ponytail_integration.init_tunnel(session_id, context)
        
        return {
            "session_id": tunnel_info["session_id"],
            "tunnel_url": tunnel_info["tunnel_url"],
            "context_size": tunnel_info["context_size"],
            "compression_level": compression_level,
            "ready": tunnel_info["ready"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tunnel/{session_id}/stats")
async def get_tunnel_stats(session_id: str):
    """
    Retorna estatísticas de um tunnel
    """
    try:
        stats = ponytail_integration.bridge.get_session_stats(session_id)
        if not stats:
            raise HTTPException(status_code=404, detail=f"Tunnel {session_id} não encontrado")
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tunnel/{session_id}")
async def close_tunnel(session_id: str):
    """
    Fecha um tunnel e retorna resumo
    """
    result = ponytail_integration.close_tunnel(session_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/archify/diagram")
async def get_architecture_diagram(
    format: str = Query("mermaid", regex="^(mermaid|dot|json)$")
):
    """
    Retorna diagrama da arquitetura em diferentes formatos
    
    Exemplos:
    - GET /v1/archify/diagram?format=mermaid
    - GET /v1/archify/diagram?format=dot
    - GET /v1/archify/diagram?format=json
    """
    try:
        if format == "mermaid":
            return JSONResponse(content={"diagram": archify_gen.generate_mermaid()})
        elif format == "dot":
            return JSONResponse(content={"diagram": archify_gen.generate_dot()})
        elif format == "json":
            return JSONResponse(content={"diagram": archify_gen.generate_json()})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/archify/stats")
async def get_archify_stats():
    """
    Retorna estatísticas do diagrama
    """
    stats = archify_gen.get_network_stats()
    return stats


# ========== HEALTH CHECK ==========

@router.get("/health")
async def health_check():
    """
    Verifica saúde da Camada A
    """
    return {
        "status": "healthy",
        "components": {
            "ecc_parser": f"{len(parser.agents)} agentes",
            "omni_router": "operacional",
            "graphify": "operacional",
            "ponytail": "operacional",
            "archify": "operacional"
        }
    }
```

---

## Passo 2: Integrar Rotas ao App Principal (15 minutos)

### Modificar: `src/openjarvis/server/app.py`

Adicionar no final:
```python
from openjarvis.server.layer_a_routes import router as layer_a_router

# ... código existente ...

# Incluir rotas da Camada A
app.include_router(layer_a_router)
```

---

## Passo 3: Criar Agent Factory (1 hora)

### Arquivo: `src/openjarvis/agents/agent_factory.py`

```python
from typing import Dict, Optional
from datetime import datetime

from openjarvis.agents.ecc_parser import ECCParser, ECCAgentSpec
from openjarvis.routing.omni_router import OmniRouter, RoutingContext
from openjarvis.agents.manager import AgentManager


class AgentFactory:
    """Factory para instanciação dinâmica de agentes ECC"""
    
    def __init__(self, manager: Optional[AgentManager] = None):
        self.manager = manager
        self.parser = ECCParser()
        self.parser.load_from_database()
        self.router = OmniRouter()
        self.created_agents = {}
    
    def create_agent(self, agent_id: str, session_id: str) -> Dict:
        """
        Cria instância de agente ECC
        
        Processo:
        1. Valida especificação do agente
        2. Resolve modelo com OmniRoute
        3. Constrói system prompt
        4. Injeta memoria e contexto
        5. Retorna agente pronto para uso
        """
        # 1. Validar
        spec = self.parser.get_agent(agent_id)
        if not spec:
            raise ValueError(f"Agente {agent_id} não encontrado")
        
        # 2. Resolver modelo
        context = RoutingContext(
            task_type=spec.category.value,
            require_reasoning=True,
            tokens_estimate=2000
        )
        model, routing_info = self.router.select_model(context)
        
        # 3. Construir system prompt
        system_prompt = self._build_system_prompt(spec, model)
        
        # 4. Criar agente (integrará com manager quando disponível)
        agent = {
            "id": agent_id,
            "name": spec.name,
            "category": spec.category.value,
            "description": spec.description,
            "capabilities": spec.capabilities,
            "required_skills": spec.required_skills,
            "model": model,
            "system_prompt": system_prompt,
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "routing_score": routing_info.get("score"),
            "fallback_models": routing_info.get("fallbacks", []),
            "status": "ready"
        }
        
        # 5. Armazenar
        self.created_agents[agent_id] = agent
        
        return agent
    
    def _build_system_prompt(self, spec: ECCAgentSpec, model: str) -> str:
        """Constrói system prompt dinamicamente"""
        capabilities_str = "\n".join(f"- {cap}" for cap in spec.capabilities)
        skills_str = "\n".join(f"- {skill}" for skill in spec.required_skills)
        
        return f"""
        # {spec.name}
        
        ## Descrição
        {spec.description}
        
        ## Seu Papel
        Você é um especialista em {spec.category.value.replace('_', ' ')}.
        Sua experiência e conhecimento são fundamentais para resolver problemas complexos.
        
        ## Suas Capacidades
        {capabilities_str}
        
        ## Skills Disponíveis
        {skills_str}
        
        ## Modelo LLM
        Você está usando o modelo: {model}
        
        ## Instruções
        1. Forneça soluções precisas e bem-fundamentadas
        2. Explique seu raciocínio de forma clara
        3. Cite fontes e referências quando apropriado
        4. Considere casos extremos e cenários de erro
        5. Ofereça alternativas quando houver múltiplas abordagens
        
        ## Diretrizes de Qualidade
        - Priorize qualidade sobre quantidade
        - Use padrões e best practices da indústria
        - Mantenha código limpo e bem-documentado
        - Considere performance e escalabilidade
        
        Você está pronto para ajudar. Como posso assistir?
        """
    
    def create_multiple_agents(self, agent_ids: list, session_id: str) -> Dict[str, Dict]:
        """Cria múltiplos agentes de uma vez"""
        agents = {}
        for agent_id in agent_ids:
            try:
                agents[agent_id] = self.create_agent(agent_id, session_id)
            except ValueError as e:
                agents[agent_id] = {"error": str(e)}
        return agents
    
    def get_agent_instance(self, agent_id: str) -> Optional[Dict]:
        """Obtém instância criada de agente"""
        return self.created_agents.get(agent_id)
    
    def list_created_agents(self) -> Dict:
        """Lista todos os agentes criados"""
        return {
            "total": len(self.created_agents),
            "agents": list(self.created_agents.keys())
        }


# ========== ENDPOINT PARA FACTORY ==========

# Adicionar em layer_a_routes.py:

@router.post("/agents/create")
async def create_agent_instance(
    agent_id: str,
    session_id: str
):
    """
    Cria instância de agente ECC
    
    Exemplo:
    POST /v1/agents/create
    {
        "agent_id": "ecc_code_reviewer_python",
        "session_id": "sess_123"
    }
    """
    try:
        factory = AgentFactory()
        agent = factory.create_agent(agent_id, session_id)
        return agent
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Passo 4: Testes de Integração (1 hora)

### Arquivo: `tests/test_layer_a_integration.py`

```python
import pytest
from openjarvis.agents.ecc_parser import ECCParser
from openjarvis.routing.omni_router import OmniRouter, RoutingContext
from openjarvis.agents.agent_factory import AgentFactory


def test_ecc_agents_loaded():
    """Verifica se agentes ECC foram carregados"""
    parser = ECCParser()
    count = parser.load_from_database()
    assert count >= 42, f"Esperado >= 42 agentes, obtive {count}"


def test_model_selection():
    """Verifica seleção de modelos"""
    router = OmniRouter()
    context = RoutingContext(task_type="code_review")
    model, info = router.select_model(context)
    
    assert model is not None
    assert "score" in info
    assert info["score"] > 0


def test_agent_creation():
    """Verifica criação de instância de agente"""
    factory = AgentFactory()
    agent = factory.create_agent("ecc_code_reviewer_python", "sess_1")
    
    assert agent["id"] == "ecc_code_reviewer_python"
    assert agent["status"] == "ready"
    assert "model" in agent
    assert "system_prompt" in agent


def test_multiple_agents_creation():
    """Verifica criação de múltiplos agentes"""
    factory = AgentFactory()
    agent_ids = [
        "ecc_code_reviewer_python",
        "ecc_security_auditor",
        "ecc_cloud_architect"
    ]
    
    agents = factory.create_multiple_agents(agent_ids, "sess_1")
    assert len(agents) == len(agent_ids)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## Passo 5: Testes Manuais (30 minutos)

### 1. Iniciar servidor
```bash
cd J:\tasksorobon\jarvis
.\.venv\Scripts\Activate.ps1
python -m uvicorn openjarvis.server.app:app --reload
```

### 2. Testar endpoints
```bash
# Health check
curl http://127.0.0.1:8000/v1/health

# Listar agentes
curl http://127.0.0.1:8000/v1/agents/ecc

# Obter agente específico
curl http://127.0.0.1:8000/v1/agents/ecc/ecc_code_reviewer_python

# Selecionar modelo
curl -X POST http://127.0.0.1:8000/v1/routing/select-model \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "code_review",
    "priority": "quality"
  }'

# Criar instância
curl -X POST http://127.0.0.1:8000/v1/agents/create \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "ecc_code_reviewer_python",
    "session_id": "sess_123"
  }'

# Ver diagrama
curl http://127.0.0.1:8000/v1/archify/diagram?format=mermaid
```

---

## Checklist Final

- [ ] Arquivo `layer_a_routes.py` criado
- [ ] Rotas integradas ao `app.py`
- [ ] Arquivo `agent_factory.py` criado
- [ ] Testes de integração criados
- [ ] Servidor iniciado sem erros
- [ ] Todos os endpoints respondendo
- [ ] Factory criando agentes com sucesso
- [ ] Documentação atualizada

---

## 🎯 Resultado Esperado

```
POST /v1/agents/create
Response: {
    "id": "ecc_code_reviewer_python",
    "name": "Python Code Reviewer",
    "category": "code_review",
    "description": "Especialista em revisão de código Python...",
    "capabilities": [...],
    "model": "claude-opus",
    "system_prompt": "# Python Code Reviewer\n...",
    "session_id": "sess_123",
    "created_at": "2024-10-28T...",
    "routing_score": 0.92,
    "fallback_models": ["claude-sonnet", "gemini-pro"],
    "status": "ready"
}
```

---

## 📞 Suporte

Em caso de dúvidas, consulte:
- `FOUNDATION_LAYER_IMPLEMENTATION.md` - Documentação técnica
- `MODULES_REFERENCE.md` - Referência de APIs
- `FOUNDATION_QUICK_START.md` - Exemplos práticos
