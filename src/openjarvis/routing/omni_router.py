"""
OmniRoute - Intelligent Model Selection & Cost Optimization
Roteia requisições para o melhor modelo baseado em custo, latência, qualidade e confiabilidade
"""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class ModelType(Enum):
    """Tipos de modelos disponíveis"""
    LOCAL_LLAMACPP = "local_llamacpp"
    LOCAL_OLLAMA = "local_ollama"
    LOCAL_SGLANG = "local_sglang"
    CLOUD_CLAUDE = "cloud_claude"
    CLOUD_GEMINI = "cloud_gemini"
    CLOUD_VERTEX = "cloud_vertex"
    EXO_NETWORK = "exo_network"
    APPLE_FM = "apple_fm"


@dataclass
class ModelMetrics:
    """Métricas de performance de um modelo"""
    model_name: str
    model_type: ModelType
    avg_latency_ms: float = 0.0
    success_rate: float = 1.0  # 0-1
    cost_per_1k_tokens: float = 0.0
    quality_score: float = 0.8  # 0-1
    availability: float = 1.0  # 0-1
    last_used: Optional[datetime] = None
    total_requests: int = 0
    failed_requests: int = 0
    

@dataclass
class RoutingWeights:
    """Pesos para cálculo de score de roteamento"""
    quality_weight: float = 0.30
    cost_weight: float = 0.25
    latency_weight: float = 0.25
    reliability_weight: float = 0.15
    availability_weight: float = 0.05
    
    def normalize(self) -> None:
        """Normaliza pesos para somar 1.0"""
        total = sum([
            self.quality_weight,
            self.cost_weight,
            self.latency_weight,
            self.reliability_weight,
            self.availability_weight
        ])
        if total > 0:
            self.quality_weight /= total
            self.cost_weight /= total
            self.latency_weight /= total
            self.reliability_weight /= total
            self.availability_weight /= total


@dataclass
class RoutingContext:
    """Contexto para decisão de roteamento"""
    task_type: str  # "chat", "code_review", "analysis", etc
    max_latency_ms: int = 5000
    min_quality_score: float = 0.7
    max_cost_per_request: float = 0.10
    prefer_local: bool = False
    require_reasoning: bool = False
    streaming_required: bool = False
    multi_turn: bool = False
    priority: str = "balanced"  # "cost", "speed", "quality", "balanced"
    tokens_estimate: int = 1000


class ModelRegistry:
    """Registro de modelos disponíveis"""
    
    def __init__(self):
        self.models: Dict[str, ModelMetrics] = {}
        self._init_default_models()
    
    def _init_default_models(self) -> None:
        """Inicializa modelos padrão"""
        defaults = [
            ModelMetrics(
                model_name="gemma2:latest",
                model_type=ModelType.LOCAL_OLLAMA,
                avg_latency_ms=150,
                success_rate=0.98,
                cost_per_1k_tokens=0.0,
                quality_score=0.75
            ),
            ModelMetrics(
                model_name="llama2:latest",
                model_type=ModelType.LOCAL_OLLAMA,
                avg_latency_ms=200,
                success_rate=0.97,
                cost_per_1k_tokens=0.0,
                quality_score=0.70
            ),
            ModelMetrics(
                model_name="claude-opus",
                model_type=ModelType.CLOUD_CLAUDE,
                avg_latency_ms=800,
                success_rate=0.99,
                cost_per_1k_tokens=0.015,
                quality_score=0.95
            ),
            ModelMetrics(
                model_name="claude-sonnet",
                model_type=ModelType.CLOUD_CLAUDE,
                avg_latency_ms=400,
                success_rate=0.98,
                cost_per_1k_tokens=0.003,
                quality_score=0.90
            ),
            ModelMetrics(
                model_name="gemini-pro",
                model_type=ModelType.CLOUD_GEMINI,
                avg_latency_ms=500,
                success_rate=0.96,
                cost_per_1k_tokens=0.001,
                quality_score=0.85
            ),
            ModelMetrics(
                model_name="gpt-4",
                model_type=ModelType.CLOUD_CLAUDE,
                avg_latency_ms=1000,
                success_rate=0.99,
                cost_per_1k_tokens=0.03,
                quality_score=0.98
            )
        ]
        
        for model in defaults:
            self.register_model(model)
    
    def register_model(self, metrics: ModelMetrics) -> None:
        """Registra novo modelo"""
        self.models[metrics.model_name] = metrics
    
    def get_model(self, name: str) -> Optional[ModelMetrics]:
        """Obtém métricas de um modelo"""
        return self.models.get(name)
    
    def list_models(self, model_type: Optional[ModelType] = None) -> List[ModelMetrics]:
        """Lista modelos, opcionalmente filtrados por tipo"""
        if model_type:
            return [m for m in self.models.values() if m.model_type == model_type]
        return list(self.models.values())
    
    def update_metrics(self, model_name: str, success: bool, latency_ms: float, cost: float = 0.0) -> None:
        """Atualiza métricas após uso"""
        if model_name not in self.models:
            return
        
        model = self.models[model_name]
        model.total_requests += 1
        model.last_used = datetime.now()
        
        if success:
            model.avg_latency_ms = (model.avg_latency_ms * 0.9) + (latency_ms * 0.1)
        else:
            model.failed_requests += 1
        
        # Atualiza taxa de sucesso
        model.success_rate = 1.0 - (model.failed_requests / model.total_requests)


class OmniRouter:
    """Roteador inteligente de modelos"""
    
    def __init__(self):
        self.registry = ModelRegistry()
        self.weights = RoutingWeights()
        self.weights.normalize()
        self.fallback_chain: List[str] = [
            "claude-opus",
            "claude-sonnet",
            "gemini-pro",
            "gpt-4",
            "gemma2:latest",
            "llama2:latest"
        ]
        self.routing_history: List[Dict] = []
    
    def select_model(self, context: RoutingContext) -> Tuple[str, Dict]:
        """Seleciona melhor modelo para contexto"""
        
        # Filtra candidatos
        candidates = self._filter_candidates(context)
        
        if not candidates:
            return self.fallback_chain[0], {"reason": "Fallback: sem candidatos"}
        
        # Calcula scores
        scores = self._calculate_scores(candidates, context)
        
        # Seleciona melhor
        best_model = max(scores, key=scores.get)
        
        # Log
        self.routing_history.append({
            "timestamp": datetime.now().isoformat(),
            "context": context.task_type,
            "selected": best_model,
            "score": scores[best_model],
            "candidates": len(candidates)
        })
        
        return best_model, {
            "score": scores[best_model],
            "reason": "Primary selection",
            "fallbacks": [m for m in self.fallback_chain if m != best_model][:3]
        }
    
    def _filter_candidates(self, context: RoutingContext) -> List[str]:
        """Filtra modelos que atendem critérios"""
        candidates = []
        
        all_models = self.registry.list_models()
        
        for model in all_models:
            # Aplica filtros
            if model.avg_latency_ms > context.max_latency_ms:
                continue
            
            if model.quality_score < context.min_quality_score:
                continue
            
            if model.cost_per_1k_tokens > context.max_cost_per_request / (context.tokens_estimate / 1000):
                continue
            
            if context.prefer_local and model.model_type not in [
                ModelType.LOCAL_LLAMACPP,
                ModelType.LOCAL_OLLAMA,
                ModelType.LOCAL_SGLANG,
                ModelType.APPLE_FM
            ]:
                continue
            
            if model.availability < 0.8:
                continue
            
            candidates.append(model.model_name)
        
        return candidates
    
    def _calculate_scores(self, candidates: List[str], context: RoutingContext) -> Dict[str, float]:
        """Calcula scores de roteamento"""
        scores = {}
        
        for model_name in candidates:
            model = self.registry.get_model(model_name)
            if not model:
                continue
            
            # Normaliza métricas para 0-1
            latency_score = 1.0 - min(model.avg_latency_ms / 5000, 1.0)
            cost_score = 1.0 - min(model.cost_per_1k_tokens / 0.05, 1.0)
            quality_score = model.quality_score
            reliability_score = model.success_rate
            availability_score = model.availability
            
            # Aplica pesos
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
            
            scores[model_name] = base_score
        
        return scores
    
    def set_weights(self, weights: RoutingWeights) -> None:
        """Define pesos de roteamento"""
        weights.normalize()
        self.weights = weights
    
    def set_fallback_chain(self, chain: List[str]) -> None:
        """Define cadeia de fallback"""
        self.fallback_chain = chain
    
    def add_fallback_model(self, model_name: str, position: int = -1) -> None:
        """Adiciona modelo à cadeia de fallback"""
        if position < 0:
            self.fallback_chain.append(model_name)
        else:
            self.fallback_chain.insert(position, model_name)
    
    def get_routing_stats(self) -> Dict:
        """Retorna estatísticas de roteamento"""
        if not self.routing_history:
            return {}
        
        model_counts = {}
        for entry in self.routing_history:
            model = entry["selected"]
            model_counts[model] = model_counts.get(model, 0) + 1
        
        return {
            "total_routing_decisions": len(self.routing_history),
            "model_distribution": model_counts,
            "avg_score": sum(e["score"] for e in self.routing_history) / len(self.routing_history),
            "last_routed": self.routing_history[-1]["timestamp"] if self.routing_history else None
        }
    
    def simulate_failure(self, model_name: str) -> None:
        """Simula falha de modelo"""
        model = self.registry.get_model(model_name)
        if model:
            model.availability = max(0.0, model.availability - 0.2)
            model.failed_requests += 1


class AdaptiveRouter:
    """Router adaptativo que aprende de padrões de uso"""
    
    def __init__(self):
        self.router = OmniRouter()
        self.task_patterns: Dict[str, Dict] = {}
        self.learning_enabled = True
    
    def route(self, context: RoutingContext) -> Tuple[str, Dict]:
        """Roteia com aprendizado"""
        
        # Consulta padrões aprendidos
        if context.task_type in self.task_patterns:
            preferred = self.task_patterns[context.task_type].get("preferred_model")
            if preferred:
                context.prefer_local = self.task_patterns[context.task_type].get("prefer_local", False)
        
        model, info = self.router.select_model(context)
        return model, info
    
    def record_outcome(self, model_name: str, context: RoutingContext, success: bool, latency_ms: float) -> None:
        """Registra resultado para aprendizado"""
        
        if not self.learning_enabled:
            return
        
        self.router.registry.update_metrics(model_name, success, latency_ms)
        
        # Atualiza padrões
        if context.task_type not in self.task_patterns:
            self.task_patterns[context.task_type] = {
                "preferred_model": model_name,
                "success_count": 0,
                "fail_count": 0
            }
        
        pattern = self.task_patterns[context.task_type]
        if success:
            pattern["success_count"] += 1
            if pattern["success_count"] > 5:
                pattern["preferred_model"] = model_name
        else:
            pattern["fail_count"] += 1


if __name__ == "__main__":
    router = OmniRouter()
    
    # Exemplo de contexto de roteamento
    context = RoutingContext(
        task_type="code_review",
        max_latency_ms=2000,
        min_quality_score=0.85,
        prefer_local=False,
        priority="quality",
        tokens_estimate=1500
    )
    
    model, info = router.select_model(context)
    print(f"✓ Modelo selecionado: {model}")
    print(f"  Score: {info.get('score'):.3f}")
    print(f"  Fallbacks: {info.get('fallbacks')}")
