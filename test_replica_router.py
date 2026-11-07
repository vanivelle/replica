"""
Teste completo do ReplicaRouter + endpoints de roteamento
"""

import subprocess
import time
import requests
import json
import sys
from typing import Dict, Any, Optional


class RoutingTester:
    """Tester para ReplicaRouter e endpoints de roteamento"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.test_results = []
    
    def wait_for_server(self, timeout: int = 30) -> bool:
        """Aguarda servidor iniciar"""
        print(f"🔄 Aguardando servidor em {self.base_url}...")
        start = time.time()
        
        while time.time() - start < timeout:
            try:
                response = requests.get(f"{self.base_url}/v1/routing/health", timeout=2)
                if response.status_code == 200:
                    print("✓ Servidor online!")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
        
        print("✗ Timeout aguardando servidor")
        return False
    
    def test_routing_health(self) -> bool:
        """Testa health check de roteamento"""
        print("\n📋 TEST 1: Routing Health Check")
        try:
            response = requests.get(f"{self.base_url}/v1/routing/health")
            result = response.json()
            
            print(f"  Status: {result.get('status')}")
            print(f"  Providers disponíveis: {result.get('providers_available')}/{result.get('providers_total')}")
            
            self.test_results.append(("health_check", True, response.status_code))
            return True
        except Exception as e:
            print(f"  ✗ Erro: {e}")
            self.test_results.append(("health_check", False, str(e)))
            return False
    
    def test_providers_list(self) -> bool:
        """Testa listagem de providers"""
        print("\n📋 TEST 2: List Providers")
        try:
            response = requests.get(f"{self.base_url}/v1/routing/providers")
            result = response.json()
            
            print(f"  Total de providers: {result.get('total')}")
            if result.get('providers'):
                for p in result.get('providers', [])[:3]:
                    print(f"    - {p['name']}: {p['specialty']} (quality: {p['quality_score']})")
            
            self.test_results.append(("list_providers", True, response.status_code))
            return True
        except Exception as e:
            print(f"  ✗ Erro: {e}")
            self.test_results.append(("list_providers", False, str(e)))
            return False
    
    def test_specialties(self) -> bool:
        """Testa listagem de especialidades"""
        print("\n📋 TEST 3: List Specialties")
        try:
            response = requests.get(f"{self.base_url}/v1/routing/specialties")
            result = response.json()
            
            for specialty, providers in list(result.items())[:3]:
                print(f"  {specialty}:")
                for p in providers[:2]:
                    print(f"    - {p['name']} (quality: {p['quality']}ms latência: {p['latency_ms']}ms)")
            
            self.test_results.append(("specialties", True, response.status_code))
            return True
        except Exception as e:
            print(f"  ✗ Erro: {e}")
            self.test_results.append(("specialties", False, str(e)))
            return False
    
    def test_select_provider(self, specialty: str = "general") -> Optional[Dict[str, Any]]:
        """Testa seleção de provider"""
        print(f"\n📋 TEST 4: Select Provider ({specialty})")
        try:
            payload = {
                "specialty": specialty,
                "priority": "balanced",
                "tokens_estimate": 1000
            }
            
            response = requests.post(
                f"{self.base_url}/v1/routing/select",
                json=payload
            )
            result = response.json()
            
            print(f"  Provider: {result.get('provider')}")
            print(f"  Score: {result.get('score'):.3f}")
            print(f"  Motivo: {result.get('reason')}")
            if result.get('alternatives'):
                print(f"  Alternativas:")
                for alt in result.get('alternatives', [])[:2]:
                    print(f"    - {alt[0]}: {alt[1]:.3f}")
            
            self.test_results.append(("select_provider", True, response.status_code))
            return result
        except Exception as e:
            print(f"  ✗ Erro: {e}")
            self.test_results.append(("select_provider", False, str(e)))
            return None
    
    def test_metrics(self, provider: Optional[str] = None) -> bool:
        """Testa métricas de provider"""
        print(f"\n📋 TEST 5: Get Metrics{f' ({provider})' if provider else ' (all)'}")
        try:
            url = f"{self.base_url}/v1/routing/metrics"
            if provider:
                url += f"?provider={provider}"
            
            response = requests.get(url)
            result = response.json()
            
            if provider:
                print(f"  Provider: {result.get('provider')}")
                print(f"  Tipo: {result.get('type')}")
                print(f"  Specialty: {result.get('specialty')}")
                print(f"  Latência média: {result.get('avg_latency_ms'):.1f}ms")
                print(f"  Taxa de sucesso: {result.get('success_rate'):.1%}")
                print(f"  Disponibilidade: {result.get('availability'):.1%}")
                print(f"  Custo/1k tokens: ${result.get('cost_per_1k_tokens'):.6f}")
                print(f"  Total requisições: {result.get('total_requests')}")
            else:
                print(f"  Total de providers com métricas: {len(result)}")
            
            self.test_results.append(("metrics", True, response.status_code))
            return True
        except Exception as e:
            print(f"  ✗ Erro: {e}")
            self.test_results.append(("metrics", False, str(e)))
            return False
    
    def test_cost_estimate(self, provider: str = "gemini-pro", tokens: int = 5000) -> bool:
        """Testa estimativa de custo"""
        print(f"\n📋 TEST 6: Cost Estimate ({provider}, {tokens} tokens)")
        try:
            response = requests.get(
                f"{self.base_url}/v1/routing/cost",
                params={"provider": provider, "tokens": tokens}
            )
            result = response.json()
            
            print(f"  Provider: {result.get('provider')}")
            print(f"  Tokens: {result.get('tokens')}")
            print(f"  Custo: ${result.get('cost_usd'):.6f}")
            print(f"  Preço/1k: ${result.get('cost_per_1k'):.6f}")
            
            self.test_results.append(("cost_estimate", True, response.status_code))
            return True
        except Exception as e:
            print(f"  ✗ Erro: {e}")
            self.test_results.append(("cost_estimate", False, str(e)))
            return False
    
    def test_feedback(self, provider: str = "gemini-pro") -> bool:
        """Testa submissão de feedback"""
        print(f"\n📋 TEST 7: Submit Feedback ({provider})")
        try:
            payload = {
                "provider": provider,
                "success": True,
                "latency_ms": 245.5,
                "tokens_used": 1500,
                "user_rating": 4.5
            }
            
            response = requests.post(
                f"{self.base_url}/v1/routing/feedback",
                json=payload
            )
            result = response.json()
            
            print(f"  Status: {result.get('status')}")
            print(f"  Mensagem: {result.get('message')}")
            
            self.test_results.append(("feedback", True, response.status_code))
            return True
        except Exception as e:
            print(f"  ✗ Erro: {e}")
            self.test_results.append(("feedback", False, str(e)))
            return False
    
    def test_routing_stats(self) -> bool:
        """Testa estatísticas de roteamento"""
        print(f"\n📋 TEST 8: Routing Statistics")
        try:
            response = requests.get(f"{self.base_url}/v1/routing/stats")
            result = response.json()
            
            print(f"  Total de decisões: {result.get('total_routing_decisions')}")
            print(f"  Média de candidatos: {result.get('avg_candidates_per_decision', 0):.1f}")
            if result.get('provider_distribution'):
                print(f"  Top providers:")
                for p, count in sorted(
                    result.get('provider_distribution', {}).items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]:
                    print(f"    - {p}: {count} vezes")
            
            self.test_results.append(("stats", True, response.status_code))
            return True
        except Exception as e:
            print(f"  ✗ Erro: {e}")
            self.test_results.append(("stats", False, str(e)))
            return False
    
    def test_chat_completions_auto(self) -> bool:
        """Testa chat completions com roteamento automático"""
        print(f"\n📋 TEST 9: Chat Completions com model='auto'")
        try:
            payload = {
                "model": "auto",
                "messages": [
                    {"role": "user", "content": "Olá! Como você está?"}
                ],
                "max_tokens": 100
            }
            
            headers = {
                "X-Replica-Specialty": "general"
            }
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  Provider selecionado: {result.get('provider')}")
                print(f"  Modelo: {result.get('model')}")
                if result.get('choices'):
                    content = result['choices'][0].get('message', {}).get('content', '')
                    print(f"  Resposta (primeiros 100 chars): {content[:100]}...")
                
                self.test_results.append(("chat_auto", True, response.status_code))
                return True
            else:
                print(f"  ✗ Status code: {response.status_code}")
                print(f"  Resposta: {response.text[:200]}")
                self.test_results.append(("chat_auto", False, response.status_code))
                return False
        except Exception as e:
            print(f"  ✗ Erro: {e}")
            self.test_results.append(("chat_auto", False, str(e)))
            return False
    
    def print_summary(self):
        """Imprime resumo dos testes"""
        print("\n" + "="*60)
        print("📊 RESUMO DOS TESTES")
        print("="*60)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        for test_name, success, detail in self.test_results:
            status = "✓" if success else "✗"
            print(f"{status} {test_name}: {detail}")
        
        print(f"\n✅ Testes aprovados: {passed}/{total}")
        print("="*60)
        
        return passed == total


def main():
    """Função principal"""
    print("🚀 Iniciando testes do ReplicaRouter\n")
    
    tester = RoutingTester()
    
    # Aguarda servidor
    if not tester.wait_for_server():
        print("❌ Não foi possível conectar ao servidor")
        sys.exit(1)
    
    # Executa testes
    tester.test_routing_health()
    tester.test_providers_list()
    tester.test_specialties()
    tester.test_select_provider("code")
    tester.test_select_provider("research")
    tester.test_select_provider("data")
    tester.test_metrics()
    provider_result = tester.test_select_provider("general")
    if provider_result:
        tester.test_metrics(provider_result.get('provider'))
    tester.test_cost_estimate()
    tester.test_feedback()
    tester.test_routing_stats()
    # tester.test_chat_completions_auto()  # Descomentado se o servidor está rodando
    
    # Resumo
    success = tester.print_summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
