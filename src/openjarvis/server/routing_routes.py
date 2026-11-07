"""API routes for intelligent multi-provider routing and metrics."""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Request, Header, HTTPException
from pydantic import BaseModel, Field

from openjarvis.routing import get_router, SpecialtyType, RoutingContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/routing", tags=["routing"])


# ---- Request/Response Models ----

class RoutingRequest(BaseModel):
    """Request for intelligent routing decision"""
    specialty: str = Field(
        default="general",
        description="Task specialty: code, research, data, general, reasoning, creative"
    )
    priority: str = Field(
        default="balanced",
        description="Priority: cost, speed, quality, balanced"
    )
    tokens_estimate: int = Field(
        default=1000,
        description="Estimated tokens for the request"
    )
    max_latency_ms: int = Field(
        default=5000,
        description="Maximum acceptable latency in milliseconds"
    )
    max_cost_per_request: float = Field(
        default=0.10,
        description="Maximum acceptable cost in USD"
    )
    min_quality_score: float = Field(
        default=0.7,
        description="Minimum acceptable quality score (0-1)"
    )
    prefer_provider: Optional[str] = Field(
        default=None,
        description="Preferred provider name"
    )


class RoutingResponse(BaseModel):
    """Response with routing decision and alternatives"""
    provider: str = Field(description="Selected provider")
    score: float = Field(description="Routing score (0-1)")
    reason: str = Field(description="Reason for selection")
    alternatives: list = Field(description="Alternative providers with scores")
    metadata: Dict[str, Any] = Field(description="Additional metadata")


class MetricsResponse(BaseModel):
    """Provider metrics response"""
    provider: str
    type: str
    specialty: str
    avg_latency_ms: float
    success_rate: float
    availability: float
    cost_per_1k_tokens: float
    quality_score: float
    total_requests: int
    requests_per_minute: float
    user_rating: Optional[float]


class CostEstimate(BaseModel):
    """Cost estimation response"""
    provider: str
    tokens: int
    cost_usd: float
    cost_per_1k: float


class UsageFeedback(BaseModel):
    """Feedback on provider usage"""
    provider: str
    success: bool
    latency_ms: float
    tokens_used: int = 0
    user_rating: Optional[float] = None


# ---- Routes ----

@router.post("/select", response_model=RoutingResponse)
async def select_provider(
    request: RoutingRequest,
    request_obj: Request,
    x_replica_specialty: Optional[str] = Header(None)
) -> RoutingResponse:
    """
    Select the best provider based on request context.
    
    Supports optional X-Replica-Specialty header to override specialty:
    - code: Code analysis, debugging, ECC agents
    - research: Research, RAGFlow, knowledge synthesis
    - data: Data processing, analysis
    - general: General chat, text
    - reasoning: Complex reasoning tasks
    - creative: Creative tasks, brainstorming
    
    Query Parameters:
    - specialty: Primary specialty for routing
    - priority: Optimization priority (cost/speed/quality/balanced)
    - tokens_estimate: Estimated token count
    - max_latency_ms: Max acceptable latency
    - max_cost_per_request: Max acceptable cost
    - min_quality_score: Minimum quality threshold
    
    Returns:
    - Selected provider
    - Routing score
    - Alternative providers
    
    Example:
        curl -X POST http://127.0.0.1:8000/v1/routing/select \
          -H "X-Replica-Specialty: code" \
          -H "Content-Type: application/json" \
          -d '{
            "tokens_estimate": 2000,
            "priority": "quality"
          }'
    """
    router_instance = get_router()
    
    # Override specialty from header if provided
    specialty = x_replica_specialty or request.specialty
    
    # Map specialty string to enum
    try:
        spec_enum = SpecialtyType[specialty.upper()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid specialty: {specialty}. Must be one of: {', '.join([s.value for s in SpecialtyType])}"
        )
    
    # Create routing context
    context = RoutingContext(
        specialty=spec_enum,
        priority=request.priority,
        tokens_estimate=request.tokens_estimate,
        max_latency_ms=request.max_latency_ms,
        max_cost_per_request=request.max_cost_per_request,
        min_quality_score=request.min_quality_score,
        prefer_provider=request.prefer_provider
    )
    
    # Get routing decision
    start_time = time.time()
    provider, info = router_instance.select_provider(context)
    routing_time_ms = (time.time() - start_time) * 1000
    
    return RoutingResponse(
        provider=provider,
        score=info.get("score", 0.0),
        reason=info.get("reason", ""),
        alternatives=info.get("alternatives", []),
        metadata={
            "routing_time_ms": round(routing_time_ms, 2),
            "specialty": specialty,
            "priority": request.priority
        }
    )


@router.get("/metrics", response_model=Dict[str, Any])
async def get_routing_metrics(
    provider: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get real-time routing metrics.
    
    Returns latency, success rate, cost, quality score, and availability
    for all providers or a specific provider.
    
    Query Parameters:
    - provider: Optional provider name to get specific metrics
    
    Returns:
    - For all providers: dict of provider metrics
    - For specific provider: detailed metrics including:
      - avg_latency_ms, min_latency_ms, max_latency_ms
      - success_rate
      - availability
      - cost_per_1k_tokens
      - quality_score
      - requests_per_minute
      - user_rating (if available)
      - last_used, last_error
    
    Example:
        curl http://127.0.0.1:8000/v1/routing/metrics
        curl http://127.0.0.1:8000/v1/routing/metrics?provider=ecc-code-specialist
    """
    router_instance = get_router()
    
    metrics = router_instance.get_metrics(provider)
    
    if provider and not metrics:
        raise HTTPException(
            status_code=404,
            detail=f"Provider not found: {provider}"
        )
    
    return metrics


@router.get("/cost", response_model=Dict[str, Any])
async def get_cost_estimate(
    provider: str,
    tokens: int = 1000
) -> Dict[str, Any]:
    """
    Get cost estimate for a provider.
    
    Calculates estimated cost in USD based on provider's pricing
    and token count.
    
    Query Parameters:
    - provider: Provider name
    - tokens: Token count (default: 1000)
    
    Returns:
    - provider: Provider name
    - tokens: Token count
    - cost_usd: Estimated cost in USD
    - cost_per_1k: Cost per 1000 tokens
    
    Example:
        curl http://127.0.0.1:8000/v1/routing/cost?provider=gemini-pro&tokens=5000
    """
    router_instance = get_router()
    
    result = router_instance.get_cost_estimate(provider, tokens)
    
    if "error" in result:
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )
    
    return result


@router.get("/stats", response_model=Dict[str, Any])
async def get_routing_statistics() -> Dict[str, Any]:
    """
    Get routing decision statistics.
    
    Returns aggregated statistics about all routing decisions made,
    including:
    - total_routing_decisions: Total number of routing decisions
    - provider_distribution: How many times each provider was selected
    - specialty_distribution: Distribution by specialty
    - priority_distribution: Distribution by priority
    - avg_candidates_per_decision: Average number of candidate providers
    - last_routed: Timestamp of last routing decision
    
    Returns:
    - Dict with routing statistics
    
    Example:
        curl http://127.0.0.1:8000/v1/routing/stats
    """
    router_instance = get_router()
    return router_instance.get_routing_stats()


@router.post("/feedback")
async def submit_feedback(
    feedback: UsageFeedback
) -> Dict[str, str]:
    """
    Submit feedback on provider usage.
    
    Records usage outcome (success/failure), latency, and optional
    user rating to improve future routing decisions.
    
    Request Body:
    - provider: Provider name
    - success: Whether the request succeeded
    - latency_ms: Actual latency in milliseconds
    - tokens_used: Optional token count used
    - user_rating: Optional user rating (1-5 stars)
    
    Returns:
    - Status message
    
    Example:
        curl -X POST http://127.0.0.1:8000/v1/routing/feedback \
          -H "Content-Type: application/json" \
          -d '{
            "provider": "ecc-code-specialist",
            "success": true,
            "latency_ms": 287,
            "tokens_used": 1500,
            "user_rating": 4.5
          }'
    """
    router_instance = get_router()
    
    # Record usage
    router_instance.record_usage(
        feedback.provider,
        feedback.success,
        feedback.latency_ms,
        feedback.tokens_used
    )
    
    # Record rating if provided
    if feedback.user_rating is not None:
        if not (1.0 <= feedback.user_rating <= 5.0):
            raise HTTPException(
                status_code=400,
                detail="user_rating must be between 1.0 and 5.0"
            )
        router_instance.record_user_feedback(
            feedback.provider,
            feedback.user_rating
        )
    
    return {
        "status": "success",
        "message": f"Feedback recorded for {feedback.provider}"
    }


@router.get("/providers", response_model=Dict[str, Any])
async def list_providers(
    specialty: Optional[str] = None
) -> Dict[str, Any]:
    """
    List all available providers.
    
    Optionally filter by specialty.
    
    Query Parameters:
    - specialty: Optional specialty filter (code, research, data, etc)
    
    Returns:
    - List of providers with their current metrics
    
    Example:
        curl http://127.0.0.1:8000/v1/routing/providers
        curl http://127.0.0.1:8000/v1/routing/providers?specialty=code
    """
    router_instance = get_router()
    
    if specialty:
        try:
            spec_enum = SpecialtyType[specialty.upper()]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid specialty: {specialty}"
            )
        
        providers = router_instance.registry.list_providers(spec_enum)
    else:
        providers = router_instance.registry.list_providers()
    
    return {
        "total": len(providers),
        "providers": [
            {
                "name": p.provider_name,
                "type": p.provider_type.value,
                "specialty": p.specialty.value,
                "quality_score": round(p.quality_score, 2),
                "cost_per_1k": p.cost_per_1k_tokens,
                "availability": round(p.availability, 2)
            }
            for p in providers
        ]
    }


@router.get("/health", response_model=Dict[str, str])
async def routing_health() -> Dict[str, str]:
    """
    Health check for routing service.
    
    Returns status of routing service and connected providers.
    
    Returns:
    - status: "healthy" or "degraded"
    - providers_available: Number of available providers
    - timestamp: Current timestamp
    
    Example:
        curl http://127.0.0.1:8000/v1/routing/health
    """
    router_instance = get_router()
    
    providers = router_instance.registry.list_providers()
    available = sum(1 for p in providers if p.availability > 0.5)
    
    status = "healthy" if available > 0 else "degraded"
    
    return {
        "status": status,
        "providers_available": str(available),
        "providers_total": str(len(providers))
    }


@router.get("/specialties", response_model=Dict[str, list])
async def list_specialties() -> Dict[str, list]:
    """
    List all available specialties and their best providers.
    
    Returns mapping of specialties to recommended providers ranked by quality.
    
    Returns:
    - Dict mapping specialty names to list of top providers
    
    Example:
        curl http://127.0.0.1:8000/v1/routing/specialties
    """
    router_instance = get_router()
    
    result = {}
    for specialty in SpecialtyType:
        providers = router_instance.registry.list_providers(specialty)
        sorted_providers = sorted(
            providers,
            key=lambda p: p.quality_score,
            reverse=True
        )
        result[specialty.value] = [
            {
                "name": p.provider_name,
                "quality": round(p.quality_score, 2),
                "latency_ms": round(p.avg_latency_ms, 0)
            }
            for p in sorted_providers[:5]
        ]
    
    return result


if __name__ == "__main__":
    # Test routing endpoints
    print("Routing API endpoints configured:")
    print("  POST   /v1/routing/select       - Select best provider")
    print("  GET    /v1/routing/metrics      - Get provider metrics")
    print("  GET    /v1/routing/cost         - Estimate cost")
    print("  GET    /v1/routing/stats        - Get routing statistics")
    print("  POST   /v1/routing/feedback     - Submit feedback")
    print("  GET    /v1/routing/providers    - List providers")
    print("  GET    /v1/routing/health       - Health check")
    print("  GET    /v1/routing/specialties  - List specialties")
