"""ReplicaMemory - Integração Ponytail + Memory Pooling + Context Compression

Camada de execução desimpedida com memória longa usando Ponytail,
pooling inteligente e compressão de contexto para economizar tokens.
"""

from __future__ import annotations

import json
import gzip
import base64
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import OrderedDict
import threading
from pathlib import Path

logger = logging.getLogger(__name__)


class CompressionLevel(Enum):
    """Níveis de compressão de contexto."""
    MINIMAL = 1      # Apenas IDs e refs
    LIGHT = 2        # Estrutura + metadados essenciais
    BALANCED = 3     # Padrão
    COMPREHENSIVE = 4  # Full context
    AGGRESSIVE = 5   # Máxima compressão


@dataclass
class MemoryEntry:
    """Entrada única de memória."""
    id: str
    timestamp: str
    type: str  # "message", "tool_call", "fact", "state"
    content: str
    tokens: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    compressed: bool = False
    compression_ratio: float = 1.0


@dataclass
class MemorySnapshot:
    """Snapshot de estado de memória."""
    session_id: str
    timestamp: str
    entries_count: int
    memory_used: int
    memory_total: int
    compression_ratio: float
    compressed_entries: int
    oldest_entry_age_seconds: int


@dataclass
class SessionState:
    """Estado persistido de uma sessão."""
    session_id: str
    created_at: str
    last_accessed_at: str
    entries: List[MemoryEntry] = field(default_factory=list)
    total_tokens: int = 0
    turn_count: int = 0


class ContextCompressor:
    """Compressor de contexto com múltiplos níveis."""

    @staticmethod
    def compress_entry(
        entry: MemoryEntry,
        level: CompressionLevel = CompressionLevel.BALANCED
    ) -> Tuple[str, float]:
        """Comprime uma entrada de memória.
        
        Args:
            entry: Entrada a comprimir
            level: Nível de compressão
            
        Returns:
            (conteúdo_comprimido, razão_compressão)
        """
        if level == CompressionLevel.MINIMAL:
            # Apenas ID e tipo
            minimal = json.dumps({
                "id": entry.id,
                "type": entry.type,
                "ts": entry.timestamp[:10],  # Apenas data
            })
            compressed = gzip.compress(minimal.encode())
        elif level == CompressionLevel.LIGHT:
            # Estrutura básica sem conteúdo completo
            light = json.dumps({
                "id": entry.id,
                "type": entry.type,
                "timestamp": entry.timestamp,
                "tokens": entry.tokens,
                "content_hash": hashlib.md5(entry.content.encode()).hexdigest(),
            })
            compressed = gzip.compress(light.encode())
        elif level == CompressionLevel.BALANCED:
            # Estrutura + resumo de conteúdo
            content_summary = entry.content[:100] + "..." if len(entry.content) > 100 else entry.content
            balanced = json.dumps({
                "id": entry.id,
                "type": entry.type,
                "timestamp": entry.timestamp,
                "tokens": entry.tokens,
                "content_preview": content_summary,
                "metadata": entry.metadata,
            })
            compressed = gzip.compress(balanced.encode())
        elif level == CompressionLevel.COMPREHENSIVE:
            # Conteúdo completo comprimido
            comprehensive = json.dumps(asdict(entry))
            compressed = gzip.compress(comprehensive.encode())
        else:  # AGGRESSIVE
            # Máxima compressão com dedupação
            to_compress = json.dumps({
                "id": entry.id,
                "type": entry.type,
                "content_hash": hashlib.md5(entry.content.encode()).hexdigest(),
                "tokens": entry.tokens,
            })
            compressed = gzip.compress(to_compress.encode())

        original_size = len(json.dumps(asdict(entry)))
        compressed_size = len(compressed)
        ratio = original_size / compressed_size if compressed_size > 0 else 1.0

        return base64.b64encode(compressed).decode(), ratio

    @staticmethod
    def decompress_entry(compressed_data: str) -> Dict[str, Any]:
        """Descomprime dados de entrada."""
        try:
            compressed = base64.b64decode(compressed_data)
            decompressed = gzip.decompress(compressed)
            return json.loads(decompressed)
        except Exception as e:
            logger.error(f"Erro descomprimindo entrada: {e}")
            return {}


class MemoryPool:
    """Pool de memória com limite inteligente e eviction policy."""

    def __init__(self, max_memory_bytes: int = 8192 * 1024):
        """Inicializa o pool de memória.
        
        Args:
            max_memory_bytes: Limite máximo de memória em bytes
        """
        self.max_memory_bytes = max_memory_bytes
        self.entries: OrderedDict[str, MemoryEntry] = OrderedDict()
        self.total_tokens = 0
        self.lock = threading.RLock()
        self.compression_stats = {
            "total_compressed": 0,
            "total_saved": 0,
            "avg_ratio": 1.0,
        }

    def add_entry(self, entry: MemoryEntry) -> bool:
        """Adiciona uma entrada ao pool, fazendo eviction se necessário.
        
        Returns:
            True se adicionado, False se rejeitado
        """
        with self.lock:
            # Verifica espaço
            current_size = self._estimate_size()
            estimated_new_size = current_size + self._estimate_entry_size(entry)

            # Se ultrapassa limite, fazer eviction
            while estimated_new_size > self.max_memory_bytes and len(self.entries) > 0:
                evicted = self._evict_oldest()
                estimated_new_size = current_size - self._estimate_entry_size(evicted)
                logger.debug(f"Evicted memory entry: {evicted.id}")

            self.entries[entry.id] = entry
            self.total_tokens += entry.tokens
            return True

    def get_entry(self, entry_id: str) -> Optional[MemoryEntry]:
        """Obtém uma entrada do pool."""
        with self.lock:
            return self.entries.get(entry_id)

    def get_recent_entries(self, count: int = 10) -> List[MemoryEntry]:
        """Obtém as N entradas mais recentes."""
        with self.lock:
            return list(self.entries.values())[-count:]

    def compress_oldest(self, ratio: float = 0.7) -> int:
        """Comprime as entradas mais antigas até atingir ratio do limite.
        
        Args:
            ratio: Fração do limite para comprimir até
            
        Returns:
            Número de entradas comprimidas
        """
        with self.lock:
            target_size = int(self.max_memory_bytes * ratio)
            current_size = self._estimate_size()
            
            if current_size <= target_size:
                return 0

            compressed_count = 0
            for entry in list(self.entries.values()):
                if entry.compressed:
                    continue

                _, ratio = ContextCompressor.compress_entry(
                    entry,
                    CompressionLevel.BALANCED
                )
                entry.compressed = True
                entry.compression_ratio = ratio

                self.compression_stats["total_compressed"] += 1
                self.compression_stats["total_saved"] += int((1 - 1/ratio) * self._estimate_entry_size(entry))
                
                compressed_count += 1
                current_size = self._estimate_size()
                
                if current_size <= target_size:
                    break

            # Atualizar média
            if self.compression_stats["total_compressed"] > 0:
                self.compression_stats["avg_ratio"] = (
                    self.compression_stats["total_saved"] / 
                    self.compression_stats["total_compressed"]
                )

            return compressed_count

    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do pool."""
        with self.lock:
            current_size = self._estimate_size()
            return {
                "memory_used": current_size,
                "memory_total": self.max_memory_bytes,
                "memory_percent": (current_size / self.max_memory_bytes) * 100,
                "entries_count": len(self.entries),
                "total_tokens": self.total_tokens,
                "compression_ratio": self.compression_stats["avg_ratio"],
                "compressed_entries": self.compression_stats["total_compressed"],
                "tokens_saved": self.compression_stats["total_saved"],
            }

    def _estimate_size(self) -> int:
        """Estima o tamanho atual em bytes."""
        return sum(self._estimate_entry_size(e) for e in self.entries.values())

    @staticmethod
    def _estimate_entry_size(entry: MemoryEntry) -> int:
        """Estima o tamanho de uma entrada."""
        # Estimativa: ~4 bytes por token + overhead
        return (entry.tokens * 4) + len(entry.content) + 200

    def _evict_oldest(self) -> MemoryEntry:
        """Remove a entrada mais antiga."""
        oldest_id = next(iter(self.entries))
        return self.entries.pop(oldest_id)

    def clear(self):
        """Limpa todas as entradas."""
        with self.lock:
            self.entries.clear()
            self.total_tokens = 0


class ReplicaMemory:
    """Integração Ponytail + Memory Pooling para execução desimpedida.
    
    Herda de Ponytail e adiciona:
    - Memory pooling com limite inteligente
    - Context compression para economizar tokens
    - Persistência de sessões multi-turn
    """

    def __init__(
        self,
        memory_size_bytes: int = 8192 * 1024,
        storage_path: Optional[str] = None,
    ):
        """Inicializa ReplicaMemory.
        
        Args:
            memory_size_bytes: Tamanho máximo de memória em bytes
            storage_path: Caminho para persistência (opcional)
        """
        self.pool = MemoryPool(memory_size_bytes)
        self.storage_path = Path(storage_path) if storage_path else Path("./memory_store")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.sessions: Dict[str, SessionState] = {}
        self.lock = threading.RLock()

    def store_message(
        self,
        session_id: str,
        message: str,
        role: str = "user",
        metadata: Optional[Dict[str, Any]] = None,
        tokens: Optional[int] = None,
    ) -> str:
        """Armazena uma mensagem de conversa.
        
        Args:
            session_id: ID da sessão
            message: Conteúdo da mensagem
            role: Papel (user, assistant, system)
            metadata: Metadados adicionais
            tokens: Estimativa de tokens (calculada se não fornecida)
            
        Returns:
            ID da entrada criada
        """
        with self.lock:
            # Criar entrada
            entry_id = hashlib.md5(
                f"{session_id}:{datetime.utcnow().isoformat()}:{message}".encode()
            ).hexdigest()[:16]

            # Estimar tokens se não fornecido
            if tokens is None:
                tokens = len(message.split()) * 1.3  # Estimativa aproximada

            entry = MemoryEntry(
                id=entry_id,
                timestamp=datetime.utcnow().isoformat(),
                type="message",
                content=message,
                tokens=int(tokens),
                metadata=metadata or {"role": role},
            )

            # Adicionar ao pool
            self.pool.add_entry(entry)

            # Atualizar sessão
            if session_id not in self.sessions:
                self.sessions[session_id] = SessionState(
                    session_id=session_id,
                    created_at=datetime.utcnow().isoformat(),
                    last_accessed_at=datetime.utcnow().isoformat(),
                )

            session = self.sessions[session_id]
            session.entries.append(entry)
            session.total_tokens += entry.tokens
            session.turn_count += 1
            session.last_accessed_at = datetime.utcnow().isoformat()

            # Comprimir se necessário
            if self.pool._estimate_size() > self.pool.max_memory_bytes * 0.8:
                self.pool.compress_oldest(ratio=0.6)

            # Persistir
            self._persist_session(session_id)

            return entry_id

    def get_session_context(
        self,
        session_id: str,
        recent_count: int = 10,
        compression_level: CompressionLevel = CompressionLevel.LIGHT,
    ) -> List[Dict[str, Any]]:
        """Obtém contexto recente de uma sessão.
        
        Args:
            session_id: ID da sessão
            recent_count: Número de entradas recentes
            compression_level: Nível de compressão desejado
            
        Returns:
            Lista de entradas de contexto
        """
        with self.lock:
            if session_id not in self.sessions:
                return []

            session = self.sessions[session_id]
            recent = session.entries[-recent_count:] if session.entries else []

            context = []
            for entry in recent:
                if entry.compressed:
                    content = ContextCompressor.decompress_entry(entry.content)
                else:
                    content = entry.content

                context.append({
                    "id": entry.id,
                    "timestamp": entry.timestamp,
                    "type": entry.type,
                    "content": content,
                    "metadata": entry.metadata,
                })

            return context

    def get_memory_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas de memória.
        
        Returns:
            Dicionário com estatísticas
        """
        pool_stats = self.pool.get_stats()
        
        with self.lock:
            oldest_age = None
            if self.pool.entries:
                oldest_ts = min(
                    e.timestamp for e in self.pool.entries.values()
                )
                oldest_dt = datetime.fromisoformat(oldest_ts)
                oldest_age = int((datetime.utcnow() - oldest_dt).total_seconds())

        return {
            **pool_stats,
            "oldest_entry_age_seconds": oldest_age,
            "sessions_count": len(self.sessions),
        }

    def _persist_session(self, session_id: str):
        """Persiste uma sessão em disco."""
        try:
            if session_id not in self.sessions:
                return

            session = self.sessions[session_id]
            session_file = self.storage_path / f"{session_id}.json"

            # Preparar dados para serialização
            data = {
                "session_id": session.session_id,
                "created_at": session.created_at,
                "last_accessed_at": session.last_accessed_at,
                "entries": [asdict(e) for e in session.entries],
                "total_tokens": session.total_tokens,
                "turn_count": session.turn_count,
            }

            session_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"Erro persistindo sessão {session_id}: {e}")

    def load_session(self, session_id: str) -> bool:
        """Carrega uma sessão do disco.
        
        Returns:
            True se carregada com sucesso
        """
        try:
            session_file = self.storage_path / f"{session_id}.json"
            if not session_file.exists():
                return False

            data = json.loads(session_file.read_text())
            
            session = SessionState(
                session_id=data["session_id"],
                created_at=data["created_at"],
                last_accessed_at=data["last_accessed_at"],
                total_tokens=data["total_tokens"],
                turn_count=data["turn_count"],
            )

            for entry_data in data.get("entries", []):
                entry = MemoryEntry(**entry_data)
                session.entries.append(entry)
                self.pool.add_entry(entry)

            with self.lock:
                self.sessions[session_id] = session

            return True
        except Exception as e:
            logger.error(f"Erro carregando sessão {session_id}: {e}")
            return False

    def clear_old_sessions(self, days: int = 30):
        """Remove sessões mais antigas que o período especificado."""
        with self.lock:
            now = datetime.utcnow()
            to_remove = []

            for session_id, session in self.sessions.items():
                last_accessed = datetime.fromisoformat(session.last_accessed_at)
                age_days = (now - last_accessed).days

                if age_days > days:
                    to_remove.append(session_id)

            for session_id in to_remove:
                session_file = self.storage_path / f"{session_id}.json"
                if session_file.exists():
                    session_file.unlink()
                del self.sessions[session_id]
                logger.info(f"Removed old session: {session_id}")

            return len(to_remove)
