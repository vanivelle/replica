"""API routes for REPLICA identity and status endpoints."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Request

from openjarvis.identity.replica import get_replica_identity

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/replica", tags=["replica"])


@router.get("/info", response_model=dict[str, Any])
async def get_replica_info() -> dict[str, Any]:
    """
    Get REPLICA identity information.
    
    Returns comprehensive information about REPLICA including name, type,
    specialties, and lore.
    
    Returns
    -------
    dict[str, Any]
        REPLICA identity information
    """
    replica = get_replica_identity()
    return replica.to_dict()


@router.get("/status", response_model=dict[str, Any])
async def get_replica_status(request: Request) -> dict[str, Any]:
    """
    Get REPLICA operational status.
    
    Returns real-time status including agent count, memory backend state,
    and routing information.
    
    Returns
    -------
    dict[str, Any]
        Operational status information
    """
    replica = get_replica_identity()
    app = request.app
    
    # Get agent manager stats
    agent_manager = getattr(app.state, "agent_manager", None)
    agents_active = 0
    if agent_manager is not None:
        try:
            agents = agent_manager.list_agents()
            agents_active = len(agents)
        except Exception as e:
            logger.debug(f"Failed to get agent count: {e}")
    
    # Get memory backend status
    memory_backend = getattr(app.state, "memory_backend", None)
    memory_status = "operational" if memory_backend is not None else "unavailable"
    
    return {
        "name": replica.name,
        "status": replica.status,
        "operational_mode": "REA",  # Reasoning-Evidence-Attribution
        "agents_active": agents_active,
        "agents_total": replica.agents_count,
        "memory_backend": replica.memory_backend,
        "memory_status": memory_status,
        "routing_status": "operational",
        "timestamp": "present",  # Can be replaced with actual timestamp
    }


@router.post("/greeting", response_model=dict[str, Any])
async def get_replica_greeting(request: Request) -> dict[str, Any]:
    """
    Get REPLICA's initial greeting message.
    
    Returns a personalized greeting in Portuguese-Brazilian, introducing
    REPLICA and its capabilities.
    
    Returns
    -------
    dict[str, Any]
        Greeting message and metadata
    """
    replica = get_replica_identity()
    
    greeting_message = (
        f"Olá. Eu sou {replica.name}, assistente alienígena soberano do "
        f"ecossistema OpenJarvis.\n\n"
        f"Minhas especialidades incluem análise tática, engenharia de IA e "
        f"roteamento inteligente. Opero com {replica.agents_count} agentes "
        f"especializados e memória persistente via {replica.memory_backend}.\n\n"
        f"Como posso auxiliá-lo hoje?"
    )
    
    return {
        "message": greeting_message,
        "language": "pt-BR",
        "speaker": replica.name,
        "operational_mode": "REA",
        "context_ready": True,
    }


@router.get("/system-prompt", response_model=dict[str, str])
async def get_replica_system_prompt() -> dict[str, str]:
    """
    Get REPLICA's system prompt for chat completions.
    
    Returns the full system prompt that injects REPLICA's personality
    and operational guidelines into chat completion requests.
    
    Returns
    -------
    dict[str, str]
        System prompt content
    """
    replica = get_replica_identity()
    return {"system_prompt": replica.system_prompt}
