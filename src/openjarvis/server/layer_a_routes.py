"""
Layer A Foundation Routes - FastAPI endpoints for routing, discovery and orchestration
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime
import logging

from openjarvis.agents.ecc_parser import ECCParser, ECCCategory
from openjarvis.routing.omni_router import OmniRouter, RoutingContext
from openjarvis.graph.graphify_parser import GraphifyManager
from openjarvis.ponytail.tunnel_bridge import PonytailIntegration
from openjarvis.archify.generator import create_openjarvis_architecture_diagram

logger = logging.getLogger(__name__)

# ========== INITIALIZE COMPONENTS ==========

try:
    parser = ECCParser()
    parser.load_from_database()
    logger.info(f"[LAYER_A] ECC Parser loaded: {len(parser.agents)} agents")
except Exception as e:
    logger.error(f"[LAYER_A] Error loading ECC Parser: {e}")
    parser = None

try:
    router_omni = OmniRouter()
    logger.info("[LAYER_A] OmniRouter initialized")
except Exception as e:
    logger.error(f"[LAYER_A] Error initializing OmniRouter: {e}")
    router_omni = None

try:
    graphify_mgr = GraphifyManager()
    logger.info("[LAYER_A] Graphify Manager initialized")
except Exception as e:
    logger.error(f"[LAYER_A] Error initializing Graphify: {e}")
    graphify_mgr = None

try:
    ponytail_integration = PonytailIntegration()
    logger.info("[LAYER_A] Ponytail Integration initialized")
except Exception as e:
    logger.error(f"[LAYER_A] Error initializing Ponytail: {e}")
    ponytail_integration = None

try:
    archify_gen = create_openjarvis_architecture_diagram()
    logger.info("[LAYER_A] Archify Generator initialized")
except Exception as e:
    logger.error(f"[LAYER_A] Error initializing Archify: {e}")
    archify_gen = None

# Create router
router = APIRouter(prefix="/v1", tags=["foundation-layer-a"])

# ========== HEALTH & STATUS ==========

@router.get("/health")
async def health_check():
    """Check Foundation Layer health"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "ecc_parser": "ok" if parser else "error",
            "omni_router": "ok" if router_omni else "error",
            "graphify": "ok" if graphify_mgr else "error",
            "ponytail": "ok" if ponytail_integration else "error",
            "archify": "ok" if archify_gen else "error"
        }
    }


@router.get("/status")
async def layer_a_status():
    """Get detailed status of Layer A components"""
    if not parser:
        raise HTTPException(status_code=500, detail="ECC Parser not initialized")
    
    return {
        "layer": "A - Foundation",
        "status": "operational",
        "components": {
            "ecc_parser": {
                "agents_loaded": len(parser.agents),
                "unique_capabilities": 124,
                "unique_tags": 70
            },
            "omni_router": {
                "models_available": len(router_omni.registry.models) if router_omni else 0,
                "routing_decisions": len(router_omni.routing_history) if router_omni else 0
            },
            "graphify": "operational",
            "ponytail": "operational",
            "archify": "operational"
        }
    }

# ========== AGENT ENDPOINTS ==========

@router.get("/agents/ecc")
async def list_ecc_agents(
    category: Optional[str] = Query(None, description="Filter by category (CODE_REVIEW, ARCHITECTURE, etc)"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    capability: Optional[str] = Query(None, description="Filter by capability"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    List ECC agents with optional filters
    
    Examples:
    - GET /v1/agents/ecc
    - GET /v1/agents/ecc?category=CODE_REVIEW
    - GET /v1/agents/ecc?tag=security
    - GET /v1/agents/ecc?capability=review_code
    """
    if not parser:
        raise HTTPException(status_code=500, detail="ECC Parser not initialized")
    
    try:
        if category:
            try:
                cat = ECCCategory[category.upper()]
                agents = parser.get_agents_by_category(cat)
            except KeyError:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        elif tag:
            agents = parser.get_agents_by_tag(tag)
        elif capability:
            agents = parser.get_agents_by_capability(capability)
        else:
            agents = list(parser.agents.values())
        
        # Apply pagination
        paginated = agents[skip:skip + limit]
        
        return {
            "total": len(agents),
            "skip": skip,
            "limit": limit,
            "returned": len(paginated),
            "agents": [
                {
                    "id": a.id,
                    "name": a.name,
                    "category": a.category.value,
                    "description": a.description,
                    "capabilities": a.capabilities,
                    "confidence_score": a.confidence_score
                }
                for a in paginated
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/ecc/{agent_id}")
async def get_ecc_agent(agent_id: str):
    """
    Get complete details of an ECC agent
    
    Example: GET /v1/agents/ecc/ecc_code_reviewer_python
    """
    if not parser:
        raise HTTPException(status_code=500, detail="ECC Parser not initialized")
    
    agent = parser.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
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
        "version": agent.version,
        "requires_gpu": agent.requires_gpu,
        "estimated_latency_ms": agent.estimated_latency_ms
    }


@router.get("/agents/ecc/search")
async def search_ecc_agents(
    query: str = Query(..., min_length=1, description="Search query (name, tag, capability)"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Search ECC agents by name, description, or tags
    
    Example: GET /v1/agents/ecc/search?query=python&limit=5
    """
    if not parser:
        raise HTTPException(status_code=500, detail="ECC Parser not initialized")
    
    results = parser.search_agents(query)
    
    return {
        "query": query,
        "total": len(results),
        "returned": min(len(results), limit),
        "agents": [
            {
                "id": a.id,
                "name": a.name,
                "category": a.category.value,
                "description": a.description
            }
            for a in results[:limit]
        ]
    }


@router.get("/agents/ecc/stats")
async def get_ecc_statistics():
    """Get statistics about loaded ECC agents"""
    if not parser:
        raise HTTPException(status_code=500, detail="ECC Parser not initialized")
    
    stats = parser.get_statistics()
    return {
        "total_agents": stats["total_agents"],
        "by_category": stats["by_category"],
        "total_unique_capabilities": stats["total_unique_capabilities"],
        "total_unique_tags": stats["total_unique_tags"],
        "average_capabilities_per_agent": stats["average_capabilities_per_agent"]
    }

# ========== ROUTING ENDPOINTS ==========

@router.post("/routing/select-model")
async def select_model(
    task_type: str = Query(..., description="Task type (code_review, data_analysis, etc)"),
    priority: str = Query("balanced", pattern="^(cost|speed|quality|balanced)$"),
    max_latency_ms: int = Query(5000, ge=100),
    tokens_estimate: int = Query(1000, ge=100)
):
    """
    Select best model for a task using OmniRoute
    
    Example:
    POST /v1/routing/select-model?task_type=code_review&priority=quality
    """
    if not router_omni:
        raise HTTPException(status_code=500, detail="OmniRouter not initialized")
    
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
            "reason": info.get("reason"),
            "fallbacks": info.get("fallbacks", []),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error selecting model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/routing/stats")
async def get_routing_stats():
    """Get routing statistics"""
    if not router_omni:
        raise HTTPException(status_code=500, detail="OmniRouter not initialized")
    
    stats = router_omni.get_routing_stats()
    return stats


@router.get("/routing/models")
async def list_available_models(
    model_type: Optional[str] = Query(None, description="Filter by model type")
):
    """List all available models"""
    if not router_omni:
        raise HTTPException(status_code=500, detail="OmniRouter not initialized")
    
    models = router_omni.registry.list_models()
    
    return {
        "total": len(models),
        "models": [
            {
                "name": m.model_name,
                "type": m.model_type.value,
                "quality": m.quality_score,
                "cost": m.cost_per_1k_tokens,
                "latency_ms": m.avg_latency_ms,
                "availability": m.availability,
                "success_rate": m.success_rate
            }
            for m in models
        ]
    }

# ========== GRAPH ENDPOINTS ==========

@router.get("/graph/dependencies/{agent_id}")
async def get_agent_dependencies(agent_id: str, depth: Optional[int] = Query(None)):
    """
    Get dependencies of an agent
    
    Example: GET /v1/graph/dependencies/ecc_code_reviewer_python
    """
    if not parser:
        raise HTTPException(status_code=500, detail="ECC Parser not initialized")
    
    agent = parser.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    try:
        # Load agents into Graphify
        if graphify_mgr:
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
            
            deps = graphify_mgr.graph.find_dependencies(agent_id, depth=depth)
            
            return {
                "agent_id": agent_id,
                "dependencies": deps,
                "total_dependencies": (
                    len(deps.get("direct_agents", [])) + 
                    len(deps.get("transitive_agents", []))
                ),
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Graphify not initialized")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dependencies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/cycles")
async def detect_cycles():
    """Detect cycles in agent dependencies"""
    if not parser or not graphify_mgr:
        raise HTTPException(status_code=500, detail="Components not initialized")
    
    try:
        graphify_mgr.load_ecc_agents([
            {
                "id": a.id,
                "name": a.name,
                "category": a.category.value,
                "description": a.description,
                "dependencies": a.dependencies
            }
            for a in parser.agents.values()
        ])
        
        cycles = graphify_mgr.graph.detect_cycles()
        
        return {
            "has_cycles": len(cycles) > 0,
            "cycle_count": len(cycles),
            "cycles": cycles
        }
    except Exception as e:
        logger.error(f"Error detecting cycles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== TUNNEL ENDPOINTS ==========

@router.post("/tunnel/create")
async def create_tunnel(
    session_id: str = Query(..., description="Session ID"),
    compression_level: str = Query("balanced", pattern="^(minimal|light|balanced|comprehensive|aggressive)$")
):
    """
    Create a CLI tunnel with context compression
    
    Example:
    POST /v1/tunnel/create?session_id=my_session&compression_level=balanced
    """
    if not ponytail_integration:
        raise HTTPException(status_code=500, detail="Ponytail not initialized")
    
    try:
        context = {
            "session_id": session_id,
            "agents": [a.id for a in parser.agents.values()] if parser else [],
            "timestamp": datetime.now().isoformat()
        }
        
        tunnel_info = ponytail_integration.init_tunnel(session_id, context)
        
        return {
            "session_id": tunnel_info["session_id"],
            "tunnel_url": tunnel_info["tunnel_url"],
            "context_size": tunnel_info["context_size"],
            "compression_level": compression_level,
            "ready": tunnel_info["ready"],
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating tunnel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tunnel/{session_id}/stats")
async def get_tunnel_stats(session_id: str):
    """Get statistics for a tunnel"""
    if not ponytail_integration:
        raise HTTPException(status_code=500, detail="Ponytail not initialized")
    
    try:
        stats = ponytail_integration.bridge.get_session_stats(session_id)
        if not stats:
            raise HTTPException(status_code=404, detail=f"Tunnel {session_id} not found")
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tunnel stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tunnel/{session_id}")
async def close_tunnel(session_id: str):
    """Close a tunnel and return summary"""
    if not ponytail_integration:
        raise HTTPException(status_code=500, detail="Ponytail not initialized")
    
    result = ponytail_integration.close_tunnel(session_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

# ========== ARCHIFY ENDPOINTS ==========

@router.get("/archify/diagram")
async def get_architecture_diagram(
    format: str = Query("mermaid", pattern="^(mermaid|dot|json)$")
):
    """
    Get architecture diagram in different formats
    
    Examples:
    - GET /v1/archify/diagram?format=mermaid
    - GET /v1/archify/diagram?format=dot
    - GET /v1/archify/diagram?format=json
    """
    if not archify_gen:
        raise HTTPException(status_code=500, detail="Archify not initialized")
    
    try:
        if format == "mermaid":
            return JSONResponse(content={"format": "mermaid", "diagram": archify_gen.generate_mermaid()})
        elif format == "dot":
            return JSONResponse(content={"format": "dot", "diagram": archify_gen.generate_dot()})
        elif format == "json":
            import json
            diagram_json = json.loads(archify_gen.generate_json())
            return JSONResponse(content={"format": "json", "diagram": diagram_json})
    except Exception as e:
        logger.error(f"Error generating diagram: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/archify/stats")
async def get_archify_stats():
    """Get architecture diagram statistics"""
    if not archify_gen:
        raise HTTPException(status_code=500, detail="Archify not initialized")
    
    stats = archify_gen.get_network_stats()
    return {
        "total_components": stats["total_nodes"],
        "total_connections": stats["total_connections"],
        "by_layer": stats["by_layer"],
        "by_type": stats["by_type"]
    }

# ========== AGENT CREATION ENDPOINTS ==========

@router.post("/agents/create")
async def create_agent_instance(
    agent_id: str = Query(..., description="ECC Agent ID"),
    session_id: str = Query(..., description="Session ID")
):
    """
    Create an instance of an ECC agent
    
    Example:
    POST /v1/agents/create?agent_id=ecc_code_reviewer_python&session_id=sess_123
    """
    if not parser or not router_omni:
        raise HTTPException(status_code=500, detail="Components not initialized")
    
    try:
        from openjarvis.agents.agent_factory import AgentFactory
        
        factory = AgentFactory()
        agent = factory.create_agent(agent_id, session_id)
        
        return {
            "status": "created",
            "agent": agent,
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== ECC AGENT ENDPOINTS ==========

@router.get("/ecc/agents")
async def list_ecc_agents(
    category: Optional[str] = Query(None),
    specialization: Optional[str] = Query(None),
    search: Optional[str] = Query(None)
):
    """
    List all 42 ECC agents with optional filtering
    
    Examples:
    - GET /v1/ecc/agents
    - GET /v1/ecc/agents?category=reviewer
    - GET /v1/ecc/agents?specialization=python
    - GET /v1/ecc/agents?search=code
    """
    try:
        from openjarvis.agents.ecc_agent_loader import get_ecc_loader
        
        loader = get_ecc_loader()
        agents = loader.agent_list
        
        # Apply filters
        if category:
            agents = [a for a in agents if a["category"].lower() == category.lower()]
        
        if specialization:
            agents = [a for a in agents if a["specialized_for"].lower() == specialization.lower()]
        
        if search:
            agents = loader.search_agents(search)
        
        return {
            "total": len(agents),
            "agents": agents,
            "filtered_by": {
                "category": category,
                "specialization": specialization,
                "search": search
            }
        }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="ECC Agent Loader not initialized")
    except Exception as e:
        logger.error(f"Error listing ECC agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ecc/agents/{agent_id}")
async def get_ecc_agent(agent_id: str):
    """
    Get details of a specific ECC agent
    
    Example:
    GET /v1/ecc/agents/python-reviewer
    """
    try:
        from openjarvis.agents.ecc_agent_loader import get_agent
        
        agent = get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        return agent
    except HTTPException:
        raise
    except RuntimeError:
        raise HTTPException(status_code=503, detail="ECC Agent Loader not initialized")
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ecc/agents/category/{category}")
async def get_agents_by_category(category: str):
    """
    Get all agents in a specific category
    
    Example:
    GET /v1/ecc/agents/category/reviewer
    """
    try:
        from openjarvis.agents.ecc_agent_loader import get_ecc_loader
        
        loader = get_ecc_loader()
        agents = loader.get_agents_by_category(category)
        
        return {
            "category": category,
            "total": len(agents),
            "agents": agents
        }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="ECC Agent Loader not initialized")
    except Exception as e:
        logger.error(f"Error getting agents by category: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ecc/agents/specialization/{spec}")
async def get_agents_by_specialization(spec: str):
    """
    Get all agents specialized in a specific area
    
    Example:
    GET /v1/ecc/agents/specialization/python
    """
    try:
        from openjarvis.agents.ecc_agent_loader import get_ecc_loader
        
        loader = get_ecc_loader()
        agents = loader.get_agents_by_specialization(spec)
        
        return {
            "specialization": spec,
            "total": len(agents),
            "agents": agents
        }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="ECC Agent Loader not initialized")
    except Exception as e:
        logger.error(f"Error getting agents by specialization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ecc/stats")
async def get_ecc_statistics():
    """
    Get statistics about all loaded ECC agents
    
    Example:
    GET /v1/ecc/stats
    """
    try:
        from openjarvis.agents.ecc_agent_loader import get_ecc_loader
        
        loader = get_ecc_loader()
        stats = loader.get_statistics()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "statistics": stats
        }
    except RuntimeError:
        raise HTTPException(status_code=503, detail="ECC Agent Loader not initialized")
    except Exception as e:
        logger.error(f"Error getting ECC statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ecc/registry")
async def get_ecc_registry():
    """
    Get complete ECC agent registry for external use
    
    Example:
    GET /v1/ecc/registry
    """
    try:
        from openjarvis.agents.ecc_agent_loader import get_ecc_loader
        
        loader = get_ecc_loader()
        registry = loader.export_agent_registry()
        
        return registry
    except RuntimeError:
        raise HTTPException(status_code=503, detail="ECC Agent Loader not initialized")
    except Exception as e:
        logger.error(f"Error exporting ECC registry: {e}")
        raise HTTPException(status_code=500, detail=str(e))
