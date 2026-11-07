"""
ReplicaRouter - Intelligent Multi-Provider Routing with Real-time Metrics
Integrates OmniRoute + 9Router patterns for specialty-based provider selection
"""

import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import asyncio
import threading


class ProviderType(Enum):
    """Tipos de providers disponíveis"""
    GEMINI = "gemini"          # $$$  - High quality, moderate cost
    OLLAMA = "ollama"          # $$   - Free local model
    GROK = "grok"              # $$$ - Real-time knowledge
    ECC_AGENT = "ecc_agent"    # $$$ - Specialized code/analysis
    CLAUDE = "claude"          # $$$ - High quality reasoning
    VERTEX = "vertex"          # $$  - Google enterprise
    MINIMAX = "minimax"        # $   - Budget model
    KIRO = "kiro"              # FREE - Free tier model


class SpecialtyType(Enum):
    """Especialidades de roteamento"""
    CODE = "code"              # Código, debugging, análise
    RESEARCH = "research"      # Pesquisa, análise, RAGFlow
    DATA = "data"              # Processamento, análise de dados
    GENERAL = "general"        # Texto, chat, propósito geral
    REASONING = "reasoning"    # Raciocínio complexo
    CREATIVE = "creative"      # Criação, brainstorm


@dataclass
class ProviderMetrics:
    """Métricas de performance de um provider"""
    provider_name: str
    provider_type: ProviderType
    specialty: SpecialtyType
    
    # Métricas em tempo real
    avg_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    max_latency_ms: float = 0.0
    latency_history: deque = field(default_factory=lambda: deque(maxlen=100))
    
    success_rate: float = 1.0
    total_requests: int = 0
    failed_requests: int = 0
    
    # Custo por 1k tokens (em USD)
    cost_per_1k_tokens: float = 0.0
    
    # Qualidade (0-1)
    quality_score: float = 0.8
    
    # Disponibilidade (0-1)
    availability: float = 1.0
    last_availability_check: Optional[datetime] = None
    
    last_used: Optional[datetime] = None
    last_error: Optional[str] = None
    
    # Rastreamento de throughput
    requests_per_minute: float = 0.0
    request_times: deque = field(default_factory=lambda: deque(maxlen=60))
    
    # Rating do usuário agregado
    user_rating: float = 0.0
    user_rating_count: int = 0


@dataclass
class RoutingWeights:
    """Pesos para cálculo de score de roteamento"""
    latency_weight: float = 0.25
    cost_weight: float = 0.20
    quality_weight: float = 0.30
    reliability_weight: float = 0.15
    availability_weight: float = 0.10
    
    def normalize(self) -> None:
        """Normaliza pesos para somar 1.0"""
        total = sum([
            self.latency_weight,
            self.cost_weight,
            self.quality_weight,
            self.reliability_weight,
            self.availability_weight
        ])
        if total > 0:
            self.latency_weight /= total
            self.cost_weight /= total
            self.quality_weight /= total
            self.reliability_weight /= total
            self.availability_weight /= total


@dataclass
class RoutingContext:
    """Contexto para decisão de roteamento"""
    specialty: SpecialtyType = SpecialtyType.GENERAL
    max_latency_ms: int = 5000
    min_quality_score: float = 0.7
    max_cost_per_request: float = 0.10
    priority: str = "balanced"  # "cost", "speed", "quality", "balanced"
    tokens_estimate: int = 1000
    require_stream: bool = False
    prefer_provider: Optional[str] = None


class ProviderRegistry:
    """Registro de providers e suas métricas"""
    
    def __init__(self):
        self.providers: Dict[str, ProviderMetrics] = {}
        self._lock = threading.RLock()
        self._init_default_providers()
    
    def _init_default_providers(self) -> None:
        """Inicializa providers padrão com custos realistas"""
        defaults = [
            # ECC Agents - Especialização em código
            ProviderMetrics(
                provider_name="ecc-code-specialist",
                provider_type=ProviderType.ECC_AGENT,
                specialty=SpecialtyType.CODE,
                avg_latency_ms=300,
                success_rate=0.98,
                cost_per_1k_tokens=0.003,  # $$
                quality_score=0.95
            ),
            
            # Gemini - Propósito geral, bom custo
            ProviderMetrics(
                provider_name="gemini-pro",
                provider_type=ProviderType.GEMINI,
                specialty=SpecialtyType.GENERAL,
                avg_latency_ms=400,
                success_rate=0.96,
                cost_per_1k_tokens=0.001,
                quality_score=0.85
            ),
            
            # Ollama - Local, grátis
            ProviderMetrics(
                provider_name="ollama-llama2",
                provider_type=ProviderType.OLLAMA,
                specialty=SpecialtyType.GENERAL,
                avg_latency_ms=200,
                success_rate=0.95,
                cost_per_1k_tokens=0.0,
                quality_score=0.75
            ),
            
            # Grok - Real-time knowledge
            ProviderMetrics(
                provider_name="grok-api",
                provider_type=ProviderType.GROK,
                specialty=SpecialtyType.RESEARCH,
                avg_latency_ms=600,
                success_rate=0.94,
                cost_per_1k_tokens=0.002,
                quality_score=0.88
            ),
            
            # Claude - Alta qualidade reasoning
            ProviderMetrics(
                provider_name="claude-sonnet",
                provider_type=ProviderType.CLAUDE,
                specialty=SpecialtyType.REASONING,
                avg_latency_ms=500,
                success_rate=0.99,
                cost_per_1k_tokens=0.003,
                quality_score=0.92
            ),
            
            # Vertex - Google enterprise
            ProviderMetrics(
                provider_name="vertex-bison",
                provider_type=ProviderType.VERTEX,
                specialty=SpecialtyType.GENERAL,
                avg_latency_ms=450,
                success_rate=0.97,
                cost_per_1k_tokens=0.0005,
                quality_score=0.80
            ),
            
            # MiniMax - Budget
            ProviderMetrics(
                provider_name="minimax-budget",
                provider_type=ProviderType.MINIMAX,
                specialty=SpecialtyType.GENERAL,
                avg_latency_ms=350,
                success_rate=0.90,
                cost_per_1k_tokens=0.0002,
                quality_score=0.65
            ),
            
            # Kiro - Free tier
            ProviderMetrics(
                provider_name="kiro-free",
                provider_type=ProviderType.KIRO,
                specialty=SpecialtyType.GENERAL,
                avg_latency_ms=800,
                success_rate=0.85,
                cost_per_1k_tokens=0.0,
                quality_score=0.60
            )
        ]
        
        for provider in defaults:
            self.register_provider(provider)
    
    def register_provider(self, metrics: ProviderMetrics) -> None:
        """Registra novo provider"""
        with self._lock:
            self.providers[metrics.provider_name] = metrics
    
    def get_provider(self, name: str) -> Optional[ProviderMetrics]:
        """Obtém métricas de um provider"""
        with self._lock:
            return self.providers.get(name)
    
    def list_providers(self, specialty: Optional[SpecialtyType] = None) -> List[ProviderMetrics]:
        """Lista providers, opcionalmente filtrados por especialidade"""
        with self._lock:
            if specialty:
                return [p for p in self.providers.values() if p.specialty == specialty]
            return list(self.providers.values())
    
    def update_metrics(
        self,
        provider_name: str,
        success: bool,
        latency_ms: float,
        cost: float = 0.0
    ) -> None:
        """Atualiza métricas após uso"""
        with self._lock:
            if provider_name not in self.providers:
                return
            
            provider = self.providers[provider_name]
            provider.total_requests += 1
            provider.last_used = datetime.now()
            
            # Atualiza latência
            provider.latency_history.append(latency_ms)
            provider.avg_latency_ms = sum(provider.latency_history) / len(provider.latency_history)
            provider.min_latency_ms = min(provider.min_latency_ms, latency_ms)
            provider.max_latency_ms = max(provider.max_latency_ms, latency_ms)
            
            # Atualiza requisições por minuto
            now = time.time()
            provider.request_times.append(now)
            if len(provider.request_times) > 1:
                time_span = provider.request_times[-1] - provider.request_times[0]
                if time_span > 0:
                    provider.requests_per_minute = (len(provider.request_times) - 1) / (time_span / 60.0)
            
            if not success:
                provider.failed_requests += 1
            
            # Atualiza taxa de sucesso
            if provider.total_requests > 0:
                provider.success_rate = 1.0 - (provider.failed_requests / provider.total_requests)
    
    def record_error(self, provider_name: str, error: str) -> None:
        """Registra erro de provider"""
        with self._lock:
            if provider_name not in self.providers:
                return
            provider = self.providers[provider_name]
            provider.last_error = error
            provider.availability = max(0.5, provider.availability - 0.1)
    
    def record_availability(self, provider_name: str, available: bool) -> None:
        """Registra check de disponibilidade"""
        with self._lock:
            if provider_name not in self.providers:
                return
            provider = self.providers[provider_name]
            provider.last_availability_check = datetime.now()
            if available:
                provider.availability = min(1.0, provider.availability + 0.05)
            else:
                provider.availability = max(0.0, provider.availability - 0.1)


class ReplicaRouter:
    """Roteador inteligente multi-provider com métricas em tempo real"""
    
    def __init__(self):
        self.registry = ProviderRegistry()
        self.weights = RoutingWeights()
        self.weights.normalize()
        
        # Histórico de roteamento
        self.routing_history: List[Dict] = []
        self.routing_history_max = 10000
        
        # Especialidade -> providers preferidos
        self.specialty_preferences: Dict[SpecialtyType, List[str]] = {
            SpecialtyType.CODE: [
                "ecc-code-specialist",
                "claude-sonnet",
                "gemini-pro"
            ],
            SpecialtyType.RESEARCH: [
                "grok-api",
                "claude-sonnet",
                "gemini-pro"
            ],
            SpecialtyType.DATA: [
                "ecc-code-specialist",
                "vertex-bison",
                "gemini-pro"
            ],
            SpecialtyType.REASONING: [
                "claude-sonnet",
                "ecc-code-specialist",
                "gemini-pro"
            ],
            SpecialtyType.CREATIVE: [
                "claude-sonnet",
                "gemini-pro",
                "grok-api"
            ],
            SpecialtyType.GENERAL: [
                "gemini-pro",
                "claudie-sonnet",
                "ollama-llama2"
            ]
        }
        
        self._lock = threading.RLock()
    
    def select_provider(self, context: RoutingContext) -> Tuple[str, Dict]:
        """Seleciona melhor provider para contexto"""
        
        # Filtra candidatos
        candidates = self._filter_candidates(context)
        
        if not candidates:
            return self._fallback_provider(context), {
                "reason": "Fallback: sem candidatos"
            }
        
        # Calcula scores
        scores = self._calculate_scores(candidates, context)
        
        # Seleciona melhor
        best_provider = max(scores, key=scores.get)
        
        # Log
        with self._lock:
            self.routing_history.append({
                "timestamp": datetime.now().isoformat(),
                "specialty": context.specialty.value,
                "selected": best_provider,
                "score": scores[best_provider],
                "candidates": len(candidates),
                "priority": context.priority
            })
            
            if len(self.routing_history) > self.routing_history_max:
                self.routing_history = self.routing_history[-self.routing_history_max:]
        
        return best_provider, {
            "score": scores[best_provider],
            "reason": "Primary selection",
            "alternatives": sorted(
                [(p, scores[p]) for p in candidates if p != best_provider],
                key=lambda x: x[1],
                reverse=True
            )[:3]
        }
    
    def _filter_candidates(self, context: RoutingContext) -> List[str]:
        """Filtra providers que atendem critérios"""
        candidates = []
        
        # Começa com preferências de especialidade
        preferred_list = self.specialty_preferences.get(
            context.specialty,
            self.specialty_preferences[SpecialtyType.GENERAL]
        )
        
        # Filtra por critérios
        for provider_name in preferred_list:
            provider = self.registry.get_provider(provider_name)
            if not provider:
                continue
            
            # Verifica critérios obrigatórios
            if provider.avg_latency_ms > context.max_latency_ms:
                continue
            
            if provider.quality_score < context.min_quality_score:
                continue
            
            if provider.availability < 0.5:
                continue
            
            # Verifica custo
            estimated_cost = (provider.cost_per_1k_tokens * context.tokens_estimate) / 1000
            if estimated_cost > context.max_cost_per_request:
                continue
            
            candidates.append(provider_name)
        
        # Se nenhum candidato preferido, expande busca
        if not candidates:
            all_providers = self.registry.list_providers()
            for provider in all_providers:
                if (provider.avg_latency_ms <= context.max_latency_ms and
                    provider.quality_score >= (context.min_quality_score - 0.1) and
                    provider.availability >= 0.5):
                    candidates.append(provider.provider_name)
        
        return candidates
    
    def _calculate_scores(self, candidates: List[str], context: RoutingContext) -> Dict[str, float]:
        """Calcula scores de roteamento"""
        scores = {}
        
        for provider_name in candidates:
            provider = self.registry.get_provider(provider_name)
            if not provider:
                continue
            
            # Normaliza métricas para 0-1
            latency_score = 1.0 - min(provider.avg_latency_ms / 5000.0, 1.0)
            cost_score = 1.0 - min((provider.cost_per_1k_tokens * 10000), 1.0)  # Normaliza para 0-1
            quality_score = provider.quality_score
            reliability_score = provider.success_rate
            availability_score = provider.availability
            
            # Aplicabased score
            base_score = (
                quality_score * self.weights.quality_weight +
                cost_score * self.weights.cost_weight +
                latency_score * self.weights.latency_weight +
                reliability_score * self.weights.reliability_weight +
                availability_score * self.weights.availability_weight
            )
            
            # Ajusta por prioridade do contexto
            if context.priority == "cost":
                base_score *= (1.0 + (cost_score * 0.5))
            elif context.priority == "speed":
                base_score *= (1.0 + (latency_score * 0.5))
            elif context.priority == "quality":
                base_score *= (1.0 + (quality_score * 0.5))
            
            # Bonus para user rating
            if provider.user_rating > 0:
                base_score *= (1.0 + (provider.user_rating / 5.0 * 0.2))
            
            scores[provider_name] = base_score
        
        return scores
    
    def _fallback_provider(self, context: RoutingContext) -> str:
        """Retorna provider de fallback"""
        # Tenta fallback por especialidade
        all_providers = self.registry.list_providers()
        for provider in sorted(
            all_providers,
            key=lambda p: p.quality_score,
            reverse=True
        )[:5]:
            if provider.availability >= 0.5:
                return provider.provider_name
        
        # Último recurso
        return "kiro-free"
    
    def record_usage(
        self,
        provider_name: str,
        success: bool,
        latency_ms: float,
        tokens_used: int = 0
    ) -> None:
        """Registra uso de provider"""
        provider = self.registry.get_provider(provider_name)
        if provider:
            cost = (provider.cost_per_1k_tokens * tokens_used) / 1000.0
            self.registry.update_metrics(provider_name, success, latency_ms, cost)
    
    def record_user_feedback(self, provider_name: str, rating: float) -> None:
        """Registra feedback de usuário (1-5)"""
        provider = self.registry.get_provider(provider_name)
        if provider:
            with self._lock:
                provider.user_rating_count += 1
                provider.user_rating = (
                    (provider.user_rating * (provider.user_rating_count - 1) + rating) /
                    provider.user_rating_count
                )
    
    def get_metrics(self, provider_name: Optional[str] = None) -> Dict[str, Any]:
        """Retorna métricas de providers"""
        if provider_name:
            provider = self.registry.get_provider(provider_name)
            if not provider:
                return {}
            
            return {
                "provider": provider.provider_name,
                "type": provider.provider_type.value,
                "specialty": provider.specialty.value,
                "avg_latency_ms": round(provider.avg_latency_ms, 2),
                "min_latency_ms": round(provider.min_latency_ms, 2),
                "max_latency_ms": round(provider.max_latency_ms, 2),
                "success_rate": round(provider.success_rate, 4),
                "availability": round(provider.availability, 2),
                "total_requests": provider.total_requests,
                "cost_per_1k_tokens": provider.cost_per_1k_tokens,
                "quality_score": round(provider.quality_score, 2),
                "requests_per_minute": round(provider.requests_per_minute, 2),
                "user_rating": round(provider.user_rating, 2) if provider.user_rating > 0 else None,
                "last_used": provider.last_used.isoformat() if provider.last_used else None,
                "last_error": provider.last_error
            }
        else:
            # Retorna métricas de todos
            all_providers = self.registry.list_providers()
            return {
                p.provider_name: self.get_metrics(p.provider_name)
                for p in all_providers
            }
    
    def get_cost_estimate(self, provider_name: str, tokens: int) -> Dict[str, float]:
        """Estima custo para um provider"""
        provider = self.registry.get_provider(provider_name)
        if not provider:
            return {"error": "Provider not found"}
        
        cost = (provider.cost_per_1k_tokens * tokens) / 1000.0
        return {
            "provider": provider_name,
            "tokens": tokens,
            "cost_usd": round(cost, 6),
            "cost_per_1k": provider.cost_per_1k_tokens
        }
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de roteamento"""
        with self._lock:
            if not self.routing_history:
                return {"total_decisions": 0}
            
            provider_counts = defaultdict(int)
            specialty_counts = defaultdict(int)
            priority_counts = defaultdict(int)
            
            for entry in self.routing_history:
                provider_counts[entry["selected"]] += 1
                specialty_counts[entry["specialty"]] += 1
                priority_counts[entry["priority"]] += 1
            
            return {
                "total_routing_decisions": len(self.routing_history),
                "provider_distribution": dict(provider_counts),
                "specialty_distribution": dict(specialty_counts),
                "priority_distribution": dict(priority_counts),
                "avg_candidates_per_decision": sum(
                    e["candidates"] for e in self.routing_history
                ) / len(self.routing_history),
                "last_routed": self.routing_history[-1]["timestamp"] if self.routing_history else None
            }


# Singleton global
_router_instance: Optional[ReplicaRouter] = None
_router_lock = threading.Lock()


def get_router() -> ReplicaRouter:
    """Obtém instância global do router"""
    global _router_instance
    if _router_instance is None:
        with _router_lock:
            if _router_instance is None:
                _router_instance = ReplicaRouter()
    return _router_instance


if __name__ == "__main__":
    router = get_router()
    
    # Exemplo de roteamento por especialidade
    context = RoutingContext(
        specialty=SpecialtyType.CODE,
        priority="quality",
        max_latency_ms=1000,
        tokens_estimate=2000
    )
    
    provider, info = router.select_provider(context)
    print(f"✓ Provider selecionado: {provider}")
    print(f"  Score: {info.get('score'):.3f}")
    print(f"  Alternativas: {info.get('alternatives')}")
    
    # Simula uso
    router.record_usage(provider, success=True, latency_ms=250)
    
    # Métricas
    print("\n📊 Métricas do Provider:")
    metrics = router.get_metrics(provider)
    for key, value in metrics.items():
        print(f"  {key}: {value}")
