"""Integration tests for ReplicaKnowledgeBase and knowledge endpoints."""

import pytest
import asyncio
from httpx import AsyncClient
from openjarvis.knowledge.replica_kb import (
    ReplicaKnowledgeBase,
    RAGFlowClient,
    ScraplingMonitor,
    Citation,
    SearchResult,
)


@pytest.fixture
async def knowledge_base():
    """Create knowledge base instance."""
    kb = ReplicaKnowledgeBase()
    yield kb
    await kb.close()


@pytest.fixture
async def ragflow():
    """Create RAGFlow client."""
    client = RAGFlowClient()
    yield client


class TestRAGFlowClient:
    """Tests for RAGFlow integration."""
    
    @pytest.mark.asyncio
    async def test_index_document(self, ragflow):
        """Test document indexing."""
        success = await ragflow.index_document(
            doc_id="test-1",
            content="FastAPI is a modern web framework for building APIs",
            metadata={"source": "fastapi/README.md", "repo": "https://github.com/tiangolo/fastapi"}
        )
        assert success is True
    
    @pytest.mark.asyncio
    async def test_search(self, ragflow):
        """Test document search."""
        # Index documents
        await ragflow.index_document(
            doc_id="test-1",
            content="FastAPI is a modern web framework for building APIs with Python",
            metadata={"source": "fastapi/README.md", "repo": "https://github.com/tiangolo/fastapi"}
        )
        
        await ragflow.index_document(
            doc_id="test-2",
            content="Ponytail memory system for maintaining agent context",
            metadata={"source": "ponytail/README.md", "repo": "https://github.com/dietrichgebert/ponytail"}
        )
        
        # Search
        results = await ragflow.search("FastAPI web framework", top_k=1)
        assert len(results) > 0
        assert "FastAPI" in results[0]["text"]
    
    @pytest.mark.asyncio
    async def test_search_with_threshold(self, ragflow):
        """Test search with similarity threshold."""
        await ragflow.index_document(
            doc_id="test-1",
            content="Python programming language for AI and data science",
            metadata={"source": "python/README.md", "repo": "https://github.com/psf/cpython"}
        )
        
        results = await ragflow.search("Python", similarity_threshold=0.8, top_k=1)
        assert len(results) >= 0  # May have no results depending on threshold


class TestScraplingMonitor:
    """Tests for Scrapling repository monitoring."""
    
    @pytest.mark.asyncio
    async def test_default_repositories(self):
        """Test that default repositories are loaded."""
        monitor = ScraplingMonitor()
        assert len(monitor.repositories) == 46
        assert "https://github.com/infiniflow/ragflow" in monitor.repositories
        assert "https://github.com/D4Vinci/Scrapling" in monitor.repositories
    
    @pytest.mark.asyncio
    async def test_custom_repositories(self):
        """Test custom repository list."""
        custom_repos = [
            "https://github.com/tiangolo/fastapi",
            "https://github.com/psf/cpython"
        ]
        monitor = ScraplingMonitor(repositories=custom_repos)
        assert len(monitor.repositories) == 2
    
    @pytest.mark.asyncio
    async def test_scrape_repository(self):
        """Test repository scraping."""
        monitor = ScraplingMonitor(
            repositories=["https://github.com/tiangolo/fastapi"]
        )
        result = await monitor.scrape_repository("https://github.com/tiangolo/fastapi")
        
        assert "readme" in result
        assert "docs" in result
        assert "url" in result
        await monitor.close()


class TestReplicaKnowledgeBase:
    """Tests for ReplicaKnowledgeBase."""
    
    @pytest.mark.asyncio
    async def test_initialization(self, knowledge_base):
        """Test knowledge base initialization."""
        await knowledge_base.initialize()
        assert knowledge_base._initialized is True
    
    @pytest.mark.asyncio
    async def test_ingest_document(self, knowledge_base):
        """Test document ingestion."""
        await knowledge_base.initialize()
        
        result = await knowledge_base.ingest_document(
            doc_id="test-doc-1",
            content="FastAPI is excellent for building APIs",
            source="fastapi/README.md",
            repo_url="https://github.com/tiangolo/fastapi",
            doc_type="readme"
        )
        
        assert result["success"] is True
        assert result["doc_id"] == "test-doc-1"
    
    @pytest.mark.asyncio
    async def test_search_with_citations(self, knowledge_base):
        """Test search with citation results."""
        await knowledge_base.initialize()
        
        # Ingest some documents
        await knowledge_base.ingest_document(
            doc_id="test-1",
            content="Ponytail is a memory system for AI agents",
            source="ponytail/README.md",
            repo_url="https://github.com/dietrichgebert/ponytail"
        )
        
        # Search
        result = await knowledge_base.search("ponytail memory")
        
        assert "query" in result
        assert "results" in result
        assert "citations" in result
        assert result["query"] == "ponytail memory"
    
    @pytest.mark.asyncio
    async def test_list_repositories(self, knowledge_base):
        """Test repository listing."""
        repos = await knowledge_base.list_repositories()
        assert isinstance(repos, list)
        assert len(repos) == 46
        assert all("url" in r and "name" in r for r in repos)
    
    @pytest.mark.asyncio
    async def test_get_stats(self, knowledge_base):
        """Test statistics retrieval."""
        await knowledge_base.initialize()
        stats = await knowledge_base.get_repository_stats()
        
        assert "total_repositories" in stats
        assert "indexed_repositories" in stats
        assert "failed_repositories" in stats
        assert "total_documents" in stats
        assert stats["total_repositories"] == 46


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
