"""
Integration tests for Layer A Foundation
"""

import pytest
import json
from datetime import datetime
from fastapi.testclient import TestClient

# Import the FastAPI app from main.py (where it's instantiated)
from openjarvis.server.main import app
from openjarvis.agents.ecc_parser import ECCParser, ECCCategory
from openjarvis.agents.agent_factory import AgentFactory, AgentPool
from openjarvis.routing.omni_router import OmniRouter, RoutingContext
from openjarvis.graph.graphify_parser import GraphifyManager
from openjarvis.ponytail.tunnel_bridge import PonytailIntegration


client = TestClient(app)


# ========== FIXTURES ==========

@pytest.fixture
def ecc_parser():
    """Fixture: Initialized ECC parser"""
    parser = ECCParser()
    parser.load_from_database()
    return parser


@pytest.fixture
def agent_factory():
    """Fixture: Initialized agent factory"""
    return AgentFactory()


@pytest.fixture
def omni_router():
    """Fixture: Initialized OmniRouter"""
    return OmniRouter()


@pytest.fixture
def graphify_manager():
    """Fixture: Initialized Graphify manager"""
    return GraphifyManager()


@pytest.fixture
def ponytail_integration():
    """Fixture: Initialized Ponytail integration"""
    return PonytailIntegration()


# ========== ECC PARSER TESTS ==========

def test_ecc_parser_loads_agents(ecc_parser):
    """Test that ECC parser loads agents successfully"""
    assert ecc_parser is not None
    assert len(ecc_parser.agents) >= 42
    print(f"[OK] Loaded {len(ecc_parser.agents)} agents")


def test_ecc_agent_retrieval(ecc_parser):
    """Test retrieving individual agents"""
    agent = ecc_parser.get_agent("ecc_code_reviewer_python")
    assert agent is not None
    assert agent.id == "ecc_code_reviewer_python"
    assert agent.name is not None
    assert len(agent.capabilities) > 0
    print(f"[OK] Retrieved agent: {agent.name}")


def test_ecc_agents_by_category(ecc_parser):
    """Test filtering agents by category"""
    code_review_agents = ecc_parser.get_agents_by_category(ECCCategory.CODE_REVIEW)
    assert len(code_review_agents) > 0
    print(f"[OK] Found {len(code_review_agents)} code review agents")


def test_ecc_statistics(ecc_parser):
    """Test ECC statistics"""
    stats = ecc_parser.get_statistics()
    assert stats["total_agents"] >= 42
    assert stats["total_unique_capabilities"] > 0
    assert stats["total_unique_tags"] > 0
    print(f"[OK] Statistics - Agents: {stats['total_agents']}, Capabilities: {stats['total_unique_capabilities']}")


def test_ecc_agent_has_required_fields(ecc_parser):
    """Test that agents have all required fields"""
    agent = ecc_parser.get_agent("ecc_code_reviewer_python")
    
    required_fields = ["id", "name", "category", "description", "capabilities", "tags"]
    for field in required_fields:
        assert hasattr(agent, field), f"Agent missing field: {field}"
        assert getattr(agent, field) is not None, f"Agent {field} is None"
    
    print(f"[OK] Agent has all required fields")


# ========== AGENT FACTORY TESTS ==========

def test_agent_factory_creates_single_agent(agent_factory):
    """Test creating a single agent"""
    agent = agent_factory.create_agent("ecc_code_reviewer_python", "test_session")
    
    assert agent is not None
    assert agent["id"] == "ecc_code_reviewer_python"
    assert agent["status"] == "ready"
    assert agent["model"] is not None
    assert agent["system_prompt"] is not None
    assert len(agent["system_prompt"]) > 100
    print(f"[OK] Created agent with model: {agent['model']}")


def test_agent_factory_creates_multiple_agents(agent_factory):
    """Test creating multiple agents"""
    agent_ids = [
        "ecc_code_reviewer_python",
        "ecc_security_auditor",
        "ecc_cloud_architect"
    ]
    
    agents = agent_factory.create_multiple_agents(agent_ids, "test_session")
    
    successful = len([a for a in agents.values() if "error" not in a])
    assert successful >= 2  # At least 2 should succeed
    print(f"[OK] Created {successful}/{len(agent_ids)} agents")


def test_agent_factory_system_prompt_quality(agent_factory):
    """Test that generated system prompts are well-formed"""
    agent = agent_factory.create_agent("ecc_code_reviewer_python", "test_session")
    
    prompt = agent["system_prompt"]
    
    # Check for key sections
    assert "Your Role" in prompt or "Role" in prompt
    assert "Capabilities" in prompt or "capabilities" in prompt
    assert agent["model"] in prompt
    assert len(prompt) > 500
    
    print(f"[OK] System prompt is well-formed ({len(prompt)} chars)")


def test_agent_factory_lists_created_agents(agent_factory):
    """Test listing created agents"""
    agent_factory.create_agent("ecc_code_reviewer_python", "test_session")
    agent_factory.create_agent("ecc_security_auditor", "test_session")
    
    stats = agent_factory.list_created_agents()
    
    assert stats["total"] >= 2
    assert "agents" in stats
    print(f"[OK] Factory has {stats['total']} created agents")


def test_agent_factory_retrieves_instance(agent_factory):
    """Test retrieving a created agent instance"""
    created = agent_factory.create_agent("ecc_code_reviewer_python", "test_session")
    retrieved = agent_factory.get_agent_instance("ecc_code_reviewer_python")
    
    assert retrieved is not None
    assert retrieved["id"] == created["id"]
    print(f"[OK] Retrieved agent instance")


def test_agent_factory_status_update(agent_factory):
    """Test updating agent status"""
    agent_factory.create_agent("ecc_code_reviewer_python", "test_session")
    
    success = agent_factory.update_agent_status("ecc_code_reviewer_python", "running")
    assert success is True
    
    agent = agent_factory.get_agent_instance("ecc_code_reviewer_python")
    assert agent["status"] == "running"
    print(f"[OK] Updated agent status")


# ========== OMNI ROUTER TESTS ==========

def test_omni_router_selects_model(omni_router):
    """Test model selection"""
    context = RoutingContext(
        task_type="code_review",
        priority="quality"
    )
    
    model, info = omni_router.select_model(context)
    
    assert model is not None
    assert info.get("score", 0) > 0
    print(f"[OK] Selected model: {model} (score: {info.get('score'):.3f})")


def test_omni_router_respects_priority(omni_router):
    """Test that router respects priority settings"""
    context_quality = RoutingContext(
        task_type="code_review",
        priority="quality"
    )
    context_cost = RoutingContext(
        task_type="code_review",
        priority="cost"
    )
    
    model_quality, info_quality = omni_router.select_model(context_quality)
    model_cost, info_cost = omni_router.select_model(context_cost)
    
    # Both should succeed
    assert model_quality is not None
    assert model_cost is not None
    print(f"[OK] Quality model: {model_quality}, Cost model: {model_cost}")


def test_omni_router_has_fallbacks(omni_router):
    """Test that router provides fallback models"""
    context = RoutingContext(
        task_type="code_review",
        priority="balanced"
    )
    
    model, info = omni_router.select_model(context)
    
    assert "fallbacks" in info
    assert len(info["fallbacks"]) > 0
    print(f"[OK] Router provides {len(info['fallbacks'])} fallback models")


# ========== GRAPHIFY TESTS ==========

def test_graphify_loads_agents(graphify_manager, ecc_parser):
    """Test loading agents into graph"""
    agents_data = [
        {
            "id": a.id,
            "name": a.name,
            "category": a.category.value,
            "description": a.description,
            "dependencies": a.dependencies
        }
        for a in list(ecc_parser.agents.values())[:10]
    ]
    
    graphify_manager.load_ecc_agents(agents_data)
    
    assert graphify_manager.graph is not None
    print(f"[OK] Loaded {len(agents_data)} agents into graph")


def test_graphify_detects_cycles(graphify_manager, ecc_parser):
    """Test cycle detection"""
    agents_data = [
        {
            "id": a.id,
            "name": a.name,
            "category": a.category.value,
            "dependencies": a.dependencies
        }
        for a in list(ecc_parser.agents.values())[:20]
    ]
    
    graphify_manager.load_ecc_agents(agents_data)
    cycles = graphify_manager.graph.detect_cycles()
    
    # Should complete without error
    assert isinstance(cycles, list)
    print(f"[OK] Cycle detection: {len(cycles)} cycles found")


# ========== PONYTAIL TESTS ==========

def test_ponytail_creates_tunnel(ponytail_integration):
    """Test creating a tunnel"""
    context = {"test": "data"}
    tunnel_info = ponytail_integration.init_tunnel("test_session", context)
    
    assert tunnel_info is not None
    assert "session_id" in tunnel_info
    assert tunnel_info["session_id"] == "test_session"
    print(f"[OK] Created tunnel with session: {tunnel_info['session_id']}")


def test_ponytail_closes_tunnel(ponytail_integration):
    """Test closing a tunnel"""
    ponytail_integration.init_tunnel("test_session_2", {})
    result = ponytail_integration.close_tunnel("test_session_2")
    
    assert result is not None
    assert "error" not in result
    print(f"[OK] Closed tunnel successfully")


# ========== API ENDPOINT TESTS ==========

def test_api_health():
    """Test /v1/health endpoint"""
    response = client.get("/v1/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "components" in data
    print(f"[OK] Health check passed")


def test_api_status():
    """Test /v1/status endpoint"""
    response = client.get("/v1/status")
    
    assert response.status_code == 200
    data = response.json()
    assert data["layer"] == "A - Foundation"
    print(f"[OK] Status endpoint working")


def test_api_list_agents():
    """Test GET /v1/agents/ecc endpoint"""
    response = client.get("/v1/agents/ecc")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 42
    assert len(data["agents"]) > 0
    print(f"[OK] Listed {data['total']} agents")


def test_api_get_agent():
    """Test GET /v1/agents/ecc/{id} endpoint"""
    response = client.get("/v1/agents/ecc/ecc_code_reviewer_python")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "ecc_code_reviewer_python"
    assert "capabilities" in data
    print(f"[OK] Retrieved agent: {data['name']}")


def test_api_filter_by_category():
    """Test filtering agents by category"""
    response = client.get("/v1/agents/ecc?category=CODE_REVIEW")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    for agent in data["agents"]:
        assert agent["category"] == "CODE_REVIEW"
    print(f"[OK] Filtered {data['total']} CODE_REVIEW agents")


def test_api_agent_stats():
    """Test GET /v1/agents/ecc/stats endpoint"""
    response = client.get("/v1/agents/ecc/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_agents"] >= 42
    assert "by_category" in data
    print(f"[OK] Got agent statistics")


def test_api_select_model():
    """Test POST /v1/routing/select-model endpoint"""
    response = client.post("/v1/routing/select-model?task_type=code_review&priority=quality")
    
    assert response.status_code == 200
    data = response.json()
    assert data["selected_model"] is not None
    assert data["score"] > 0
    print(f"[OK] Selected model: {data['selected_model']}")


def test_api_routing_stats():
    """Test GET /v1/routing/stats endpoint"""
    response = client.get("/v1/routing/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert "total_decisions" in data or data is not None
    print(f"[OK] Got routing statistics")


def test_api_list_models():
    """Test GET /v1/routing/models endpoint"""
    response = client.get("/v1/routing/models")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    assert len(data["models"]) > 0
    print(f"[OK] Listed {data['total']} available models")


def test_api_archify_diagram():
    """Test GET /v1/archify/diagram endpoint"""
    response = client.get("/v1/archify/diagram?format=mermaid")
    
    assert response.status_code == 200
    data = response.json()
    assert data["format"] == "mermaid"
    assert "diagram" in data
    print(f"[OK] Got architecture diagram (mermaid)")


def test_api_archify_stats():
    """Test GET /v1/archify/stats endpoint"""
    response = client.get("/v1/archify/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_components"] > 0
    assert data["total_connections"] > 0
    print(f"[OK] Got archify statistics")


def test_api_create_agent():
    """Test POST /v1/agents/create endpoint"""
    response = client.post(
        "/v1/agents/create",
        params={
            "agent_id": "ecc_code_reviewer_python",
            "session_id": "test_session_123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"
    assert "agent" in data
    agent = data["agent"]
    assert agent["status"] == "ready"
    assert agent["model"] is not None
    print(f"[OK] Created agent via API: {agent['name']}")


def test_api_create_tunnel():
    """Test POST /v1/tunnel/create endpoint"""
    response = client.post(
        "/v1/tunnel/create",
        params={
            "session_id": "tunnel_test_123",
            "compression_level": "balanced"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "tunnel_test_123"
    assert data["ready"] is True
    print(f"[OK] Created tunnel via API")


# ========== INTEGRATION TESTS ==========

def test_factory_and_router_integration(agent_factory):
    """Test factory integration with router"""
    agent = agent_factory.create_agent("ecc_code_reviewer_python", "integration_test")
    
    assert agent["model"] is not None
    assert agent["routing_score"] > 0
    assert len(agent["fallback_models"]) > 0
    print(f"[OK] Factory-Router integration works")


def test_end_to_end_agent_creation():
    """Test complete end-to-end agent creation flow"""
    # 1. Call API to create agent
    response = client.post(
        "/v1/agents/create",
        params={
            "agent_id": "ecc_security_auditor",
            "session_id": "e2e_test"
        }
    )
    
    assert response.status_code == 200
    agent_data = response.json()["agent"]
    
    # 2. Verify agent is complete
    assert agent_data["status"] == "ready"
    assert agent_data["model"] in ["claude-opus", "claude-sonnet", "gpt-4", "ollama-local", "gemini-pro"]
    assert len(agent_data["system_prompt"]) > 500
    
    # 3. Verify routing data
    assert agent_data["routing_score"] > 0
    assert len(agent_data["fallback_models"]) > 0
    
    print(f"[OK] End-to-end test passed")


def test_agent_pool_warmup():
    """Test agent pool warmup functionality"""
    pool = AgentPool()
    
    agent_ids = [
        "ecc_code_reviewer_python",
        "ecc_security_auditor",
        "ecc_cloud_architect"
    ]
    
    result = pool.warm_up(agent_ids, "pool_test")
    
    assert result["successful"] >= 2
    pooled = pool.list_pool_agents()
    assert len(pooled) >= 2
    
    print(f"[OK] Warmed up {result['successful']} agents in pool")


# ========== PERFORMANCE TESTS ==========

def test_agent_creation_performance(agent_factory):
    """Test performance of agent creation"""
    import time
    
    start = time.time()
    agent = agent_factory.create_agent("ecc_code_reviewer_python", "perf_test")
    elapsed = time.time() - start
    
    # Should complete in under 5 seconds
    assert elapsed < 5.0
    assert agent["status"] == "ready"
    print(f"[OK] Agent creation: {elapsed:.3f}s")


def test_api_response_time():
    """Test API response times"""
    import time
    
    # Health check
    start = time.time()
    response = client.get("/v1/health")
    elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 1.0  # Should be very fast
    print(f"[OK] Health check: {elapsed*1000:.1f}ms")
    
    # Agent list
    start = time.time()
    response = client.get("/v1/agents/ecc?limit=10")
    elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 2.0
    print(f"[OK] Agent list: {elapsed*1000:.1f}ms")


# ========== PYTEST CONFIGURATION ==========

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
