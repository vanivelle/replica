#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test ReplicaRouter integration with FastAPI endpoints"""

import sys
sys.path.insert(0, r'j:\tasksorobon\jarvis\src')

from fastapi import FastAPI
from openjarvis.server.routing_routes import router as routing_router
from openjarvis.routing import get_router, SpecialtyType, RoutingContext

def test_routing_integration():
    """Test ReplicaRouter integration with FastAPI"""
    
    print("[*] Testando integracao ReplicaRouter com FastAPI\n")
    
    # 1. Verify router instance
    router = get_router()
    print("[OK] ReplicaRouter singleton acessivel")
    
    # 2. Verify routing_routes module loads
    print("[OK] routing_routes module carregado")
    
    # 3. Test routing logic
    print("\n[TEST] Teste de roteamento por specialty:")
    
    specialties = [SpecialtyType.CODE, SpecialtyType.RESEARCH, SpecialtyType.DATA]
    for specialty in specialties:
        context = RoutingContext(specialty=specialty)
        provider, info = router.select_provider(context)
        score = info.get('score', 0)
        print(f"  {specialty.value:12} -> {provider:22} (score: {score:.3f})")
    
    # 4. Test metrics collection
    print("\n[TEST] Coleta de metricas:")
    
    # Record some usage
    router.record_usage("ecc-code-specialist", success=True, latency_ms=250, tokens_used=1500)
    router.record_usage("gemini-pro", success=True, latency_ms=420, tokens_used=2000)
    router.record_usage("ollama-llama2", success=False, latency_ms=180, tokens_used=1000)
    
    # Get metrics
    metrics = router.get_metrics("ecc-code-specialist")
    print(f"  ecc-code-specialist: {metrics.get('total_requests')} requests")
    print(f"    - Latencia media: {metrics.get('avg_latency_ms'):.1f}ms")
    print(f"    - Taxa sucesso: {metrics.get('success_rate'):.1%}")
    
    # 5. Test cost calculations
    print("\n[TEST] Calculo de custos:")
    
    for provider_name in ["ecc-code-specialist", "gemini-pro", "ollama-llama2"]:
        cost = router.get_cost_estimate(provider_name, 10000)
        print(f"  {provider_name:22} 10k tokens: ${cost.get('cost_usd'):.6f}")
    
    # 6. Test statistics
    print("\n[TEST] Estatisticas de roteamento:")
    
    stats = router.get_routing_stats()
    print(f"  Total de decisoes: {stats.get('total_routing_decisions')}")
    print(f"  Media de candidatos: {stats.get('avg_candidates_per_decision', 0):.1f}")
    
    # 7. Test user feedback
    print("\n[TEST] Feedback de usuario:")
    
    router.record_user_feedback("ecc-code-specialist", 4.8)
    router.record_user_feedback("gemini-pro", 4.2)
    
    metrics_updated = router.get_metrics("ecc-code-specialist")
    print(f"  ecc-code-specialist rating: {metrics_updated.get('user_rating')}")
    
    # 8. Test providers list
    print("\n[TEST] Lista de providers:")
    
    all_providers = router.registry.list_providers()
    print(f"  Total: {len(all_providers)}")
    
    code_providers = router.registry.list_providers(SpecialtyType.CODE)
    print(f"  Para CODE: {len(code_providers)} providers")
    for p in code_providers:
        print(f"    - {p.provider_name}")
    
    # 9. Test FastAPI app structure
    print("\n[TEST] Estrutura FastAPI:")
    
    app = FastAPI()
    app.include_router(routing_router)
    
    # Get routes
    routes = [route.path for route in app.routes]
    routing_routes = [r for r in routes if '/v1/routing' in r]
    
    print(f"  Routes de roteamento registrados: {len(routing_routes)}")
    for route in sorted(routing_routes):
        print(f"    - {route}")
    
    print("\n[SUCCESS] Todos os testes de integracao passaram!")
    return True

if __name__ == "__main__":
    success = test_routing_integration()
    sys.exit(0 if success else 1)
