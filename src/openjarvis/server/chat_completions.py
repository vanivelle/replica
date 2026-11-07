"""
Chat Completions Pipeline - Integração Ollama + Grok + Gemini + Claude
com ReplicaRouter para roteamento inteligente multi-provider
"""
import os
import json
import asyncio
import time
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel
import httpx
import logging

from openjarvis.identity.replica import get_replica_identity
from openjarvis.routing import get_router, SpecialtyType, RoutingContext

logger = logging.getLogger(__name__)

# ============================================================================
# MODELOS DE REQUISIÇÃO/RESPOSTA
# ============================================================================

class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False


class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]


# ============================================================================
# CONFIGURAÇÃO DE MODELOS DISPONÍVEIS
# ============================================================================

MODELS_CONFIG = {
    # Local - Ollama
    "ollama": {
        "url": "http://localhost:11434/api/chat",
        "models": ["gemma2:latest", "mistral:latest", "neural-chat"],
        "type": "local",
        "priority": 1
    },
    # Cloud - Grok
    "grok": {
        "url": "https://api.x.ai/v1/chat/completions",
        "models": ["grok-beta", "grok-vision-beta"],
        "type": "cloud",
        "priority": 2,
        "api_key_env": "XAI_API_KEY"
    },
    # Cloud - Gemini
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "models": ["gemini-pro", "gemini-pro-vision"],
        "type": "cloud",
        "priority": 3,
        "api_key_env": "GEMINI_API_KEY"
    },
    # Cloud - Claude (via Anthropic)
    "claude": {
        "url": "https://api.anthropic.com/v1/messages",
        "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
        "type": "cloud",
        "priority": 4,
        "api_key_env": "ANTHROPIC_API_KEY"
    }
}


# ============================================================================
# ROTEADOR INTELIGENTE
# ============================================================================

class SmartRouter:
    """Roteia requisições para o melhor modelo disponível"""
    
    def __init__(self):
        self.model_status = {}
        self.update_status()
    
    def update_status(self):
        """Verifica status de cada modelo"""
        for provider, config in MODELS_CONFIG.items():
            if config["type"] == "local":
                self.model_status[provider] = self._check_local(provider)
            else:
                api_key = os.getenv(config.get("api_key_env"))
                self.model_status[provider] = api_key is not None
    
    def _check_local(self, provider: str) -> bool:
        """Verifica se provider local está disponível"""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def route(self, model_name: Optional[str] = None) -> tuple[str, str]:
        """
        Roteia para o melhor provider disponível
        Retorna: (provider, actual_model_name)
        """
        # Se modelo específico solicitado
        if model_name:
            for provider, config in MODELS_CONFIG.items():
                if model_name in config.get("models", []):
                    if self.model_status.get(provider):
                        return provider, model_name
        
        # Fallback: próximo disponível por prioridade
        sorted_providers = sorted(
            MODELS_CONFIG.items(),
            key=lambda x: x[1]["priority"]
        )
        
        for provider, config in sorted_providers:
            if self.model_status.get(provider):
                return provider, config["models"][0]
        
        # Emergency fallback para Ollama
        return "ollama", "gemma2:latest"


router = APIRouter(prefix="/v1", tags=["chat"])
smart_router = SmartRouter()


# ============================================================================
# HANDLERS DE CADA PROVIDER
# ============================================================================

async def call_ollama(messages: List[Message], model: str, **kwargs) -> str:
    """Chama Ollama local"""
    payload = {
        "model": model,
        "messages": [{"role": m.role, "content": m.content} for m in messages],
        "stream": False,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                MODELS_CONFIG["ollama"]["url"],
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            raise HTTPException(status_code=503, detail="Ollama unavailable")


async def call_grok(messages: List[Message], model: str, **kwargs) -> str:
    """Chama Grok via X.AI API"""
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="Grok API key not configured")
    
    payload = {
        "model": model,
        "messages": [{"role": m.role, "content": m.content} for m in messages],
        "temperature": kwargs.get("temperature", 0.7),
        "max_tokens": kwargs.get("max_tokens", 2048),
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                MODELS_CONFIG["grok"]["url"],
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Grok error: {e}")
            raise HTTPException(status_code=503, detail="Grok API unavailable")


async def call_gemini(messages: List[Message], model: str, **kwargs) -> str:
    """Chama Gemini via Google API"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="Gemini API key not configured")
    
    # Converter mensagens para formato Gemini
    contents = []
    for msg in messages:
        contents.append({
            "role": "user" if msg.role == "user" else "model",
            "parts": [{"text": msg.content}]
        })
    
    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": kwargs.get("temperature", 0.7),
            "maxOutputTokens": kwargs.get("max_tokens", 2048),
        }
    }
    
    url = f"{MODELS_CONFIG['gemini']['url']}chat/completions?key={api_key}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            raise HTTPException(status_code=503, detail="Gemini API unavailable")


async def call_claude(messages: List[Message], model: str, **kwargs) -> str:
    """Chama Claude via Anthropic API"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="Claude API key not configured")
    
    payload = {
        "model": model,
        "max_tokens": kwargs.get("max_tokens", 2048),
        "messages": [{"role": m.role, "content": m.content} for m in messages],
    }
    
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                MODELS_CONFIG["claude"]["url"],
                json=payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data.get("content", [{}])[0].get("text", "")
        except Exception as e:
            logger.error(f"Claude error: {e}")
            raise HTTPException(status_code=503, detail="Claude API unavailable")


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    request_obj: Request,
    x_replica_specialty: Optional[str] = Header(None)
):
    """
    OpenAI-compatible chat completions endpoint
    Roteia automaticamente para o melhor provider disponível
    Suporta roteamento inteligente via ReplicaRouter quando model="auto"
    Injeta system prompt REPLICA para personalidade soberana
    
    Suporte X-Replica-Specialty header:
    - code: Codigo, debugging, análise (ECC agents)
    - research: Pesquisa, RAGFlow, análise de conhecimento
    - data: Processamento de dados
    - general: Chat geral, propósito geral
    - reasoning: Raciocínio complexo
    - creative: Criação, brainstorm
    
    Exemplo com roteamento automático:
        curl -X POST http://127.0.0.1:8000/v1/chat/completions \
          -H "X-Replica-Specialty: code" \
          -d '{"model": "auto", "messages": [...], "max_tokens": 2048}'
    """
    
    # Injetar system prompt REPLICA se não existir
    replica = get_replica_identity()
    messages_with_replica = list(request.messages)
    
    # Verificar se já existe system message
    has_system = any(msg.role == "system" for msg in messages_with_replica)
    if not has_system:
        # Injetar REPLICA system prompt no início
        system_msg = Message(
            role="system",
            content=replica.system_prompt
        )
        messages_with_replica.insert(0, system_msg)
    
    # Se modelo é "auto", usar ReplicaRouter
    if request.model.lower() == "auto":
        replica_router = get_router()
        
        # Mapear specialty header para enum
        specialty = SpecialtyType.GENERAL
        if x_replica_specialty:
            try:
                specialty = SpecialtyType[x_replica_specialty.upper()]
            except KeyError:
                logger.warning(f"Invalid specialty: {x_replica_specialty}, using GENERAL")
        
        # Criar contexto de roteamento
        routing_context = RoutingContext(
            specialty=specialty,
            tokens_estimate=request.max_tokens,
            priority="balanced"
        )
        
        # Obter provider recomendado
        start_routing = time.time()
        provider_name, routing_info = replica_router.select_provider(routing_context)
        routing_time = time.time() - start_routing
        
        logger.info(
            f"ReplicaRouter: {x_replica_specialty or 'general'} -> {provider_name} "
            f"(score: {routing_info.get('score'):.3f}, time: {routing_time*1000:.1f}ms)"
        )
        
        # Mapear provider ReplicaRouter para SmartRouter
        # ecc-code-specialist -> usa orchestração especial
        if provider_name.startswith("ecc-"):
            provider = "ollama"  # ECC roda localmente
        else:
            # Extrair primeiro nome: "gemini-pro" -> "gemini"
            provider = provider_name.split("-")[0].lower()
        
        actual_model = request.model  # Usa o padrão do provider
    else:
        # Roteamento clássico
        provider, actual_model = smart_router.route(request.model)
    
    logger.info(f"Routing {request.model} -> {provider}:{actual_model}")
    
    # Executar requisição
    try:
        start_call = time.time()
        
        if provider == "ollama":
            content = await call_ollama(
                messages_with_replica,
                actual_model,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
        elif provider == "grok":
            content = await call_grok(
                messages_with_replica,
                actual_model,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
        elif provider == "gemini":
            content = await call_gemini(
                messages_with_replica,
                actual_model,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
        elif provider == "claude":
            content = await call_claude(
                messages_with_replica,
                actual_model,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
        else:
            raise HTTPException(status_code=500, detail="No valid provider found")
        
        # Registrar uso no ReplicaRouter se foi usado "auto"
        if request.model.lower() == "auto":
            actual_call_time = (time.time() - start_call) * 1000
            replica_router.record_usage(
                provider_name,
                success=True,
                latency_ms=actual_call_time,
                tokens_used=request.max_tokens
            )
        
        return {
            "id": "chatcmpl-" + os.urandom(12).hex(),
            "object": "chat.completion",
            "created": int(time.time()),
            "model": actual_model,
            "provider": provider,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": len(str(request.messages)),
                "completion_tokens": len(content.split()),
                "total_tokens": len(str(request.messages)) + len(content.split())
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/models")
async def list_chat_models():
    """Lista todos os modelos de chat disponíveis"""
    smart_router.update_status()
    
    available = {}
    for provider, config in MODELS_CONFIG.items():
        if smart_router.model_status.get(provider):
            available[provider] = {
                "models": config["models"],
                "type": config["type"],
                "priority": config["priority"]
            }
    
    return {
        "available_providers": list(available.keys()),
        "models": available,
        "routing_policy": "automatic with fallback"
    }


@router.post("/chat/models/refresh")
async def refresh_models():
    """Atualiza status dos modelos"""
    smart_router.update_status()
    return {
        "status": "refreshed",
        "models": smart_router.model_status
    }
