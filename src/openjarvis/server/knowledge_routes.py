"""Knowledge base API endpoints for OpenJarvis."""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

from openjarvis.knowledge.replica_kb import ReplicaKnowledgeBase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/knowledge", tags=["knowledge"])

# Global knowledge base instance
_knowledge_base: Optional[ReplicaKnowledgeBase] = None


async def get_knowledge_base() -> ReplicaKnowledgeBase:
    """Get or create knowledge base instance."""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = ReplicaKnowledgeBase()
        await _knowledge_base.initialize()
    return _knowledge_base


# Request/Response Models
class DocumentIngestRequest(BaseModel):
    """Document ingestion request."""
    doc_id: str = Field(..., description="Unique document ID")
    content: str = Field(..., description="Document content to index")
    source: str = Field(..., description="Source file/location")
    repo_url: str = Field(..., description="Repository URL")
    doc_type: str = Field(default="custom", description="Document type (readme/docs/code/custom)")


class DocumentIngestResponse(BaseModel):
    """Document ingestion response."""
    success: bool
    doc_id: str
    source: str
    indexed_at: str


class SearchRequest(BaseModel):
    """Search request."""
    query: str = Field(..., description="Search query")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results")
    similarity_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Similarity threshold")


class Citation(BaseModel):
    """Citation source."""
    text: str
    source: str
    repo: str
    url: str
    score: float
    updated_at: str


class SearchResult(BaseModel):
    """Search result."""
    text: str
    source: str
    repo: str
    url: str
    score: float
    chunk_id: str


class SearchResponse(BaseModel):
    """Search response with citations."""
    query: str
    results: List[SearchResult]
    citations: List[Citation]
    total_results: int
    timestamp: str


class RepositoryInfo(BaseModel):
    """Repository information."""
    url: str
    name: str
    status: str
    last_scraped: Optional[str] = None
    document_count: int


class KnowledgeBaseStats(BaseModel):
    """Knowledge base statistics."""
    total_repositories: int
    indexed_repositories: int
    failed_repositories: int
    total_documents: int
    last_update: str
    auto_update_interval: int
    initialized: bool


# Endpoints
@router.post("/ingest", response_model=DocumentIngestResponse, summary="Ingest document")
async def ingest_document(request: DocumentIngestRequest) -> DocumentIngestResponse:
    """Ingest a document into the knowledge base."""
    try:
        kb = await get_knowledge_base()
        result = await kb.ingest_document(
            doc_id=request.doc_id,
            content=request.content,
            source=request.source,
            repo_url=request.repo_url,
            doc_type=request.doc_type
        )
        return DocumentIngestResponse(**result)
    except Exception as e:
        logger.error(f"Document ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=SearchResponse, summary="Search knowledge base")
async def search_knowledge(
    q: str = Query(..., description="Search query"),
    top_k: int = Query(5, ge=1, le=50, description="Number of results"),
    threshold: float = Query(0.5, ge=0.0, le=1.0, description="Similarity threshold")
) -> SearchResponse:
    """Search the knowledge base with citations."""
    try:
        if not q or len(q.strip()) < 2:
            raise HTTPException(status_code=400, detail="Query too short (minimum 2 characters)")
        
        kb = await get_knowledge_base()
        result = await kb.search(
            query=q,
            top_k=top_k,
            similarity_threshold=threshold
        )
        return SearchResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/repos", response_model=List[RepositoryInfo], summary="List repositories")
async def list_repositories() -> List[RepositoryInfo]:
    """List all tracked repositories."""
    try:
        kb = await get_knowledge_base()
        repos = await kb.list_repositories()
        return [RepositoryInfo(**r) for r in repos]
    except Exception as e:
        logger.error(f"Failed to list repositories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=KnowledgeBaseStats, summary="Knowledge base statistics")
async def get_stats() -> KnowledgeBaseStats:
    """Get knowledge base statistics."""
    try:
        kb = await get_knowledge_base()
        stats = await kb.get_repository_stats()
        return KnowledgeBaseStats(**stats)
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/repositories", summary="Add repository to monitoring")
async def add_repository(
    repo_url: str = Body(..., embed=True, description="Repository URL")
) -> Dict[str, Any]:
    """Add a repository to the monitoring list."""
    try:
        kb = await get_knowledge_base()
        if repo_url not in kb.scrapling.repositories:
            kb.scrapling.repositories.append(repo_url)
            kb.scrapling._init_metadata()
            # Trigger immediate scraping
            repo_content = await kb.scrapling.scrape_repository(repo_url)
            if repo_content["readme"]:
                doc_id = kb.scrapling._generate_doc_id(repo_url, "readme")
                metadata = {
                    "source": f"{repo_url.split('/')[-1]}/README.md",
                    "repo": repo_url,
                    "url": repo_url,
                    "type": "readme",
                }
                await kb.ragflow.index_document(doc_id, repo_content["readme"], metadata)
        
        return {
            "success": True,
            "message": f"Repository {repo_url} added and indexed",
            "repository": repo_url
        }
    except Exception as e:
        logger.error(f"Failed to add repository: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear", summary="Clear knowledge base")
async def clear_knowledge_base() -> Dict[str, str]:
    """Clear all indexed documents."""
    try:
        kb = await get_knowledge_base()
        await kb.ragflow.delete_dataset("default")
        return {"success": True, "message": "Knowledge base cleared"}
    except Exception as e:
        logger.error(f"Failed to clear knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))
