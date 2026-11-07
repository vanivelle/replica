#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick test of ReplicaRouter functionality"""

import sys
import os
sys.path.insert(0, r'j:\tasksorobon\jarvis\src')

# Set encoding to UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

from openjarvis.routing import get_router, SpecialtyType, RoutingContext

def test_replica_router():
    """Test ReplicaRouter basic functionality"""
    
    print("[*] Testando ReplicaRouter...\n")
    
    # Get router instance
    router = get_router()
    print("[OK] ReplicaRouter importado com sucesso")
    
    # Test for CODE specialty
    print("\n[TEST 1] Roteamento para CODE")
    context = RoutingContext(specialty=SpecialtyType.CODE)
    provider, info = router.select_provider(context)
    print(f"  Provider selecionado: {provider}")
    print(f"  Score: {info.get('score'):.3f}")
    print(f"  Razao: {info.get('reason')}")
    
    # Test for RESEARCH specialty
    print("\n[TEST 2] Roteamento para RESEARCH")
    context = RoutingContext(specialty=SpecialtyType.RESEARCH)
    provider, info = router.select_provider(context)
    print(f"  Provider selecionado: {provider}")
    print(f"  Score: {info.get('score'):.3f}")
    
    # Test metrics
    print("\n[TEST 3] Metricas")
    metrics = router.get_metrics("ecc-code-specialist")
    print(f"  Provider: {metrics.get('provider')}")
    print(f"  Specialty: {metrics.get('specialty')}")
    print(f"  Quality: {metrics.get('quality_score')}")
    print(f"  Latencia: {metrics.get('avg_latency_ms'):.1f}ms")
    
    # Test cost estimate
    print("\n[TEST 4] Estimativa de Custo")
    cost = router.get_cost_estimate("gemini-pro", 5000)
    print(f"  Provider: {cost.get('provider')}")
    print(f"  Tokens: {cost.get('tokens')}")
    print(f"  Custo: ${cost.get('cost_usd'):.6f}")
    
    # Test recording usage
    print("\n[TEST 5] Registrar Uso")
    router.record_usage("ecc-code-specialist", success=True, latency_ms=287, tokens_used=1500)
    router.record_usage("gemini-pro", success=True, latency_ms=450, tokens_used=2000)
    print("  [OK] Uso registrado")
    
    # Test user feedback
    print("\n[TEST 6] Feedback do Usuario")
    router.record_user_feedback("ecc-code-specialist", 4.8)
    router.record_user_feedback("gemini-pro", 4.2)
    print("  [OK] Feedback registrado")
    
    # Test routing stats
    print("\n[TEST 7] Estatisticas de Roteamento")
    stats = router.get_routing_stats()
    print(f"  Total de decisoes: {stats.get('total_routing_decisions')}")
    print(f"  Media de candidatos: {stats.get('avg_candidates_per_decision', 0):.1f}")
    
    # Test list providers
    print("\n[TEST 8] Listar Providers")
    all_providers = router.registry.list_providers()
    print(f"  Total de providers: {len(all_providers)}")
    
    code_providers = router.registry.list_providers(SpecialtyType.CODE)
    print(f"  Providers para CODE: {len(code_providers)}")
    for p in code_providers:
        print(f"    - {p.provider_name}")
    
    print("\n[SUCCESS] Todos os testes passaram!")

if __name__ == "__main__":
    test_replica_router()
