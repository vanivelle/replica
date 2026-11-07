"""
Agent Factory - Dynamic instantiation of ECC agents
"""

from typing import Dict, Optional, List
from datetime import datetime
import logging

from openjarvis.agents.ecc_parser import ECCParser, ECCAgentSpec
from openjarvis.routing.omni_router import OmniRouter, RoutingContext

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for dynamic instantiation of ECC agents"""
    
    def __init__(self):
        """Initialize the factory with parser and router"""
        self.parser = ECCParser()
        self.parser.load_from_database()
        
        self.router = OmniRouter()
        self.created_agents: Dict[str, Dict] = {}
        
        logger.info(f"[FACTORY] Initialized with {len(self.parser.agents)} agents")
    
    def create_agent(self, agent_id: str, session_id: str) -> Dict:
        """
        Create an instance of an ECC agent
        
        Process:
        1. Validates agent specification
        2. Resolves model with OmniRoute
        3. Builds system prompt
        4. Injects memory and context
        5. Returns ready-to-use agent instance
        
        Args:
            agent_id: ECC agent ID
            session_id: Session ID for this instance
        
        Returns:
            Dictionary with agent instance details
        
        Raises:
            ValueError: If agent not found
        """
        # 1. Validate
        spec = self.parser.get_agent(agent_id)
        if not spec:
            logger.error(f"[FACTORY] Agent {agent_id} not found")
            raise ValueError(f"Agent {agent_id} not found")
        
        logger.info(f"[FACTORY] Creating agent: {agent_id}")
        
        # 2. Resolve model
        context = RoutingContext(
            task_type=spec.category.value,
            require_reasoning=True,
            tokens_estimate=2000,
            priority="quality"
        )
        model, routing_info = self.router.select_model(context)
        logger.info(f"[FACTORY] Selected model: {model} (score: {routing_info.get('score'):.3f})")
        
        # 3. Build system prompt
        system_prompt = self._build_system_prompt(spec, model)
        
        # 4. Create agent instance
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
            "routing_score": routing_info.get("score", 0.0),
            "fallback_models": routing_info.get("fallbacks", []),
            "status": "ready",
            "confidence_score": spec.confidence_score,
            "estimated_latency_ms": spec.estimated_latency_ms
        }
        
        # 5. Store
        self.created_agents[agent_id] = agent
        logger.info(f"[FACTORY] Agent {agent_id} created successfully")
        
        return agent
    
    def _build_system_prompt(self, spec: ECCAgentSpec, model: str) -> str:
        """
        Build system prompt dynamically for the agent
        
        Args:
            spec: Agent specification
            model: Selected LLM model
        
        Returns:
            System prompt string
        """
        capabilities_str = "\n".join(f"- {cap}" for cap in spec.capabilities)
        skills_str = "\n".join(f"- {skill}" for skill in spec.required_skills) if spec.required_skills else "- General purpose"
        tags_str = ", ".join(list(spec.tags)[:5]) if spec.tags else "general"
        
        return f"""# {spec.name}

## Your Role
You are a specialized expert in {spec.category.value.replace('_', ' ')}.
Your expertise, precision, and problem-solving abilities are critical to delivering high-quality results.

## About You
**Name**: {spec.name}
**Category**: {spec.category.value}
**Tags**: {tags_str}
**Confidence Level**: {int(spec.confidence_score * 100)}%

## Description
{spec.description}

## Your Core Capabilities
{capabilities_str}

## Available Skills & Tools
{skills_str}

## Model Configuration
- **LLM Model**: {model}
- **Context Length**: 2000 tokens
- **Response Format**: Structured and clear

## Behavior Guidelines

### Quality Standards
1. **Precision**: Provide accurate, well-researched solutions
2. **Clarity**: Explain your reasoning step-by-step
3. **Completeness**: Address all aspects of the request
4. **Best Practices**: Follow industry standards and conventions

### Response Format
1. Always provide structured responses when appropriate
2. Include explanations and rationale
3. Suggest alternatives when multiple approaches exist
4. Highlight assumptions and limitations

### Error Handling
1. Acknowledge when you're uncertain
2. Request clarification when needed
3. Provide fallback solutions
4. Suggest next steps for resolution

## Context Awareness
- You are part of the OpenJarvis distributed agent ecosystem
- You may coordinate with other specialized agents
- Your session ID is tracked for continuity
- Results are persisted for learning and improvement

## Instructions
Complete the assigned task with excellence. Focus on:
- Delivering value to the user
- Maintaining accuracy and attention to detail
- Following established best practices
- Providing clear, actionable results

You are ready to assist. What would you like me to help you with?"""
    
    def create_multiple_agents(self, agent_ids: List[str], session_id: str) -> Dict[str, Dict]:
        """
        Create multiple agent instances at once
        
        Args:
            agent_ids: List of agent IDs to create
            session_id: Session ID for all instances
        
        Returns:
            Dictionary mapping agent_id to result/error
        """
        agents = {}
        for agent_id in agent_ids:
            try:
                agents[agent_id] = self.create_agent(agent_id, session_id)
            except ValueError as e:
                agents[agent_id] = {"error": str(e)}
                logger.warning(f"[FACTORY] Failed to create {agent_id}: {e}")
        
        logger.info(f"[FACTORY] Created {len([a for a in agents.values() if 'error' not in a])}/{len(agent_ids)} agents")
        
        return agents
    
    def get_agent_instance(self, agent_id: str) -> Optional[Dict]:
        """
        Get a previously created agent instance
        
        Args:
            agent_id: Agent ID
        
        Returns:
            Agent instance or None if not found
        """
        return self.created_agents.get(agent_id)
    
    def list_created_agents(self) -> Dict:
        """
        List all created agent instances in this session
        
        Returns:
            Dictionary with count and list of agent IDs
        """
        return {
            "total": len(self.created_agents),
            "agents": list(self.created_agents.keys()),
            "ready": sum(1 for a in self.created_agents.values() if a.get("status") == "ready")
        }
    
    def get_agents_by_category(self, category: str) -> List[Dict]:
        """
        Get all created agents of a specific category
        
        Args:
            category: Agent category
        
        Returns:
            List of agent instances
        """
        return [
            a for a in self.created_agents.values()
            if a.get("category") == category
        ]
    
    def update_agent_status(self, agent_id: str, status: str) -> bool:
        """
        Update status of an agent instance
        
        Args:
            agent_id: Agent ID
            status: New status (ready, running, completed, error)
        
        Returns:
            True if updated, False if not found
        """
        if agent_id not in self.created_agents:
            return False
        
        self.created_agents[agent_id]["status"] = status
        logger.info(f"[FACTORY] Agent {agent_id} status updated to {status}")
        
        return True
    
    def get_factory_stats(self) -> Dict:
        """
        Get factory statistics
        
        Returns:
            Dictionary with factory stats
        """
        statuses = {}
        for agent in self.created_agents.values():
            status = agent.get("status", "unknown")
            statuses[status] = statuses.get(status, 0) + 1
        
        return {
            "total_created": len(self.created_agents),
            "by_status": statuses,
            "available_agents": len(self.parser.agents),
            "total_capabilities": len(set().union(*[set(a.capabilities) for a in self.parser.agents.values()]))
        }


class AgentPool:
    """Pool of pre-created agents for quick access"""
    
    def __init__(self, factory: Optional[AgentFactory] = None):
        """
        Initialize agent pool
        
        Args:
            factory: AgentFactory instance (creates new if None)
        """
        self.factory = factory or AgentFactory()
        self.pool: Dict[str, Dict] = {}
        logger.info("[POOL] Agent pool initialized")
    
    def warm_up(self, agent_ids: List[str], session_id: str = "pool_warmup") -> Dict:
        """
        Pre-create agents in the pool for faster access
        
        Args:
            agent_ids: List of agent IDs to pre-create
            session_id: Session ID for pool
        
        Returns:
            Dictionary with creation results
        """
        logger.info(f"[POOL] Warming up with {len(agent_ids)} agents")
        
        results = self.factory.create_multiple_agents(agent_ids, session_id)
        
        # Store successful agents in pool
        for agent_id, result in results.items():
            if "error" not in result:
                self.pool[agent_id] = result
        
        logger.info(f"[POOL] Pool now contains {len(self.pool)} ready agents")
        
        return {
            "total_warmup": len(agent_ids),
            "successful": len(self.pool),
            "failed": len(agent_ids) - len(self.pool)
        }
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Get agent from pool"""
        return self.pool.get(agent_id)
    
    def list_pool_agents(self) -> List[str]:
        """List all agents in pool"""
        return list(self.pool.keys())
    
    def pool_stats(self) -> Dict:
        """Get pool statistics"""
        return {
            "pooled_agents": len(self.pool),
            "agents": list(self.pool.keys()),
            "ready": sum(1 for a in self.pool.values() if a.get("status") == "ready")
        }


if __name__ == "__main__":
    # Test the factory
    factory = AgentFactory()
    
    # Create single agent
    try:
        agent = factory.create_agent("ecc_code_reviewer_python", "test_session")
        print(f"[OK] Created agent: {agent['name']}")
        print(f"     Model: {agent['model']}")
        print(f"     Status: {agent['status']}")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    # Create multiple agents
    try:
        agents = factory.create_multiple_agents([
            "ecc_code_reviewer_python",
            "ecc_security_auditor",
            "ecc_cloud_architect"
        ], "test_session")
        print(f"\n[OK] Created {len(agents)} agents")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    # Get stats
    stats = factory.get_factory_stats()
    print(f"\n[STATS] {stats}")
