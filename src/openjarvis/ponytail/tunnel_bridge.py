"""
Ponytail Bridge - CLI Tunneling & Context Compression
Integra CLI tunelado com compressão de contexto leve
"""

import json
import gzip
import base64
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class ContextCompressionLevel(Enum):
    """Níveis de compressão de contexto"""
    MINIMAL = 1      # Apenas IDs e refs
    LIGHT = 2        # Estrutura + metadados essenciais
    BALANCED = 3     # Padrão
    COMPREHENSIVE = 4  # Full context
    AGGRESSIVE = 5   # Máxima compressão


@dataclass
class CLICommand:
    """Comando CLI capturado"""
    id: str
    timestamp: str
    user: str
    command: str
    cwd: str
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int


@dataclass
class ContextSnapshot:
    """Snapshot comprimido de contexto"""
    session_id: str
    timestamp: str
    compression_level: str
    compressed_size: int
    original_size: int
    compression_ratio: float
    components: List[str]


class ContextCompressor:
    """Compressor de contexto para transferência eficiente"""
    
    def __init__(self, compression_level: ContextCompressionLevel = ContextCompressionLevel.BALANCED):
        self.level = compression_level
    
    def compress_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Comprime contexto baseado no nível selecionado"""
        if self.level == ContextCompressionLevel.MINIMAL:
            return self._compress_minimal(context)
        elif self.level == ContextCompressionLevel.LIGHT:
            return self._compress_light(context)
        elif self.level == ContextCompressionLevel.BALANCED:
            return self._compress_balanced(context)
        elif self.level == ContextCompressionLevel.COMPREHENSIVE:
            return self._compress_comprehensive(context)
        elif self.level == ContextCompressionLevel.AGGRESSIVE:
            return self._compress_aggressive(context)
    
    def _compress_minimal(self, context: Dict) -> Dict:
        """Apenas IDs e referências críticas"""
        return {
            "session": context.get("session_id"),
            "agent_ids": [a.get("id") for a in context.get("agents", [])],
            "skill_ids": [s.get("id") for s in context.get("skills", [])],
            "timestamp": context.get("timestamp")
        }
    
    def _compress_light(self, context: Dict) -> Dict:
        """Estrutura + metadados essenciais"""
        return {
            "session": context.get("session_id"),
            "agents": [
                {
                    "id": a.get("id"),
                    "name": a.get("name"),
                    "category": a.get("category"),
                    "status": a.get("status", "idle")
                }
                for a in context.get("agents", [])[:10]  # Top 10
            ],
            "active_skills": [s.get("id") for s in context.get("skills", [])],
            "memory_refs": context.get("memory_refs", []),
            "timestamp": context.get("timestamp")
        }
    
    def _compress_balanced(self, context: Dict) -> Dict:
        """Padrão: estrutura + metadados + estado essencial"""
        return {
            "session": context.get("session_id"),
            "agents": context.get("agents", []),
            "skills": [
                {
                    "id": s.get("id"),
                    "name": s.get("name"),
                    "category": s.get("category"),
                    "version": s.get("version", "1.0.0")
                }
                for s in context.get("skills", [])
            ],
            "memory": {
                "total_tokens": context.get("memory", {}).get("total_tokens"),
                "used_tokens": context.get("memory", {}).get("used_tokens"),
                "refs": context.get("memory_refs", [])[:50]  # Top 50 refs
            },
            "recent_tasks": context.get("recent_tasks", [])[:20],
            "timestamp": context.get("timestamp")
        }
    
    def _compress_comprehensive(self, context: Dict) -> Dict:
        """Full context sem compressão agressiva"""
        return context
    
    def _compress_aggressive(self, context: Dict) -> Dict:
        """Máxima compressão - remove redundância"""
        compressed = self._compress_balanced(context)
        
        # Remove duplicatas
        agents_map = {}
        for agent in compressed.get("agents", []):
            agents_map[agent.get("id")] = agent
        compressed["agents"] = list(agents_map.values())
        
        # Deduplica skills
        skills_ids = set(s.get("id") for s in compressed.get("skills", []))
        compressed["skills"] = [s for s in compressed.get("skills", []) if s.get("id") in skills_ids]
        
        return compressed
    
    def serialize_compressed(self, compressed: Dict) -> str:
        """Serializa contexto comprimido em base64"""
        json_str = json.dumps(compressed, separators=(',', ':'))
        gzip_bytes = gzip.compress(json_str.encode('utf-8'))
        base64_str = base64.b64encode(gzip_bytes).decode('utf-8')
        return base64_str
    
    def deserialize_compressed(self, base64_str: str) -> Dict:
        """Deserializa contexto comprimido"""
        gzip_bytes = base64.b64decode(base64_str.encode('utf-8'))
        json_str = gzip.decompress(gzip_bytes).decode('utf-8')
        return json.loads(json_str)


class CLITunnelBridge:
    """Bridge entre CLI e API via contexto tunelado"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.cli_history: List[CLICommand] = []
        self.compressor = ContextCompressor()
        self.sessions: Dict[str, Dict] = {}
    
    def capture_cli_command(self, command: CLICommand) -> str:
        """Captura comando CLI para envio"""
        self.cli_history.append(command)
        return command.id
    
    def create_tunnel_session(self, session_id: str, context: Dict) -> Dict:
        """Cria sessão tunelada com contexto comprimido"""
        compressed = self.compressor.compress_context(context)
        serialized = self.compressor.serialize_compressed(compressed)
        
        self.sessions[session_id] = {
            "id": session_id,
            "created": datetime.now().isoformat(),
            "compressed_context": serialized,
            "compression_level": self.compressor.level.name,
            "cli_commands": []
        }
        
        return {
            "session_id": session_id,
            "tunnel_url": f"{self.base_url}/v1/tunnel/{session_id}",
            "context_size": len(serialized),
            "ready": True
        }
    
    def send_cli_output_via_tunnel(self, session_id: str, command: CLICommand) -> Dict:
        """Envia saída CLI através do túnel"""
        if session_id not in self.sessions:
            return {"error": f"Sessão {session_id} não encontrada"}
        
        self.sessions[session_id]["cli_commands"].append({
            "id": command.id,
            "command": command.command,
            "exit_code": command.exit_code,
            "output_size": len(command.stdout) + len(command.stderr),
            "timestamp": command.timestamp
        })
        
        return {
            "session_id": session_id,
            "command_id": command.id,
            "status": "queued",
            "tunnel_ready": True
        }
    
    def build_cli_payload(self, session_id: str) -> Dict:
        """Constrói payload para envio via CLI tunnel"""
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        return {
            "type": "cli_tunnel",
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "context": session["compressed_context"],
            "cli_commands": session["cli_commands"],
            "compression_level": session["compression_level"]
        }
    
    def get_session_stats(self, session_id: str) -> Dict:
        """Retorna estatísticas da sessão"""
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "total_commands": len(session["cli_commands"]),
            "compressed_size": len(session["compressed_context"]),
            "compression_level": session["compression_level"],
            "uptime": (datetime.now().isoformat())
        }


class PonytailCLIConfig:
    """Configuração do Ponytail CLI"""
    
    def __init__(self):
        self.endpoints = {
            "chat": "/v1/chat/completions",
            "agents": "/v1/agents",
            "skills": "/v1/skills",
            "tunnel": "/v1/tunnel",
            "archive": "/v1/archive"
        }
        
        self.options = {
            "model": "gemma2:latest",
            "max_tokens": 2000,
            "temperature": 0.7,
            "compression_level": "balanced",
            "verbose": False,
            "timeout": 30
        }
    
    def get_command_template(self, endpoint: str) -> str:
        """Retorna template de comando para CLI"""
        templates = {
            "chat": "ponytail chat --model {model} --compressed",
            "agents": "ponytail agents list --graphify",
            "skills": "ponytail skills search --catalog",
            "tunnel": "ponytail tunnel create --session-id {session_id}",
            "archive": "ponytail archive export --format json"
        }
        return templates.get(endpoint, "")


class PonytailIntegration:
    """Integração completa do Ponytail com OpenJarvis"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.bridge = CLITunnelBridge(base_url)
        self.config = PonytailCLIConfig()
        self.active_tunnels = {}
    
    def init_tunnel(self, session_id: str, context: Dict) -> Dict:
        """Inicializa túnel CLI"""
        tunnel_info = self.bridge.create_tunnel_session(session_id, context)
        self.active_tunnels[session_id] = tunnel_info
        
        return {
            "status": "tunnel_ready",
            "session": tunnel_info,
            "cli_command": self._build_cli_command(session_id),
            "estimated_compression": f"{self.bridge.compressor.level.name}"
        }
    
    def _build_cli_command(self, session_id: str) -> str:
        """Constrói comando CLI para usuario"""
        return f"""
        # Tunnel de contexto criado para sessão {session_id}
        ponytail --tunnel {session_id} \\
            --model gemma2:latest \\
            --compression balanced \\
            --api http://127.0.0.1:8000
        """
    
    def send_command(self, session_id: str, cmd: CLICommand) -> Dict:
        """Envia comando via túnel"""
        return self.bridge.send_cli_output_via_tunnel(session_id, cmd)
    
    def list_active_tunnels(self) -> List[Dict]:
        """Lista túneis ativos"""
        return [
            {
                "session_id": sid,
                "status": "active",
                "commands": len(tunnel.get("cli_commands", [])),
                "compressed_size": tunnel.get("context_size", 0)
            }
            for sid, tunnel in self.bridge.sessions.items()
        ]
    
    def close_tunnel(self, session_id: str) -> Dict:
        """Fecha túnel e retorna resumo"""
        if session_id not in self.bridge.sessions:
            return {"error": "Túnel não encontrado"}
        
        session = self.bridge.sessions[session_id]
        stats = self.bridge.get_session_stats(session_id)
        
        del self.bridge.sessions[session_id]
        if session_id in self.active_tunnels:
            del self.active_tunnels[session_id]
        
        return {
            "status": "tunnel_closed",
            "session_id": session_id,
            "stats": stats
        }


if __name__ == "__main__":
    # Exemplo de uso
    integration = PonytailIntegration()
    
    sample_context = {
        "session_id": "sess_001",
        "timestamp": datetime.now().isoformat(),
        "agents": [
            {"id": "agent_1", "name": "Code Reviewer", "category": "CODE_REVIEW", "status": "active"},
            {"id": "agent_2", "name": "DevOps Agent", "category": "DEVOPS", "status": "idle"}
        ],
        "skills": [
            {"id": "skill_1", "name": "Pylance", "category": "analysis"},
            {"id": "skill_2", "name": "Security Scan", "category": "security"}
        ],
        "memory_refs": ["ctx_1", "ctx_2", "ctx_3"],
        "recent_tasks": ["task_1", "task_2"]
    }
    
    result = integration.init_tunnel("session_123", sample_context)
    print("✓ Ponytail Integration Ready")
    print(json.dumps(result, indent=2, default=str))
