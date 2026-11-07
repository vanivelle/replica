"""Demo of ReplicaKnowledgeBase functionality."""

import asyncio
import sys
sys.path.insert(0, "J:\\tasksorobon\\jarvis\\src")

from openjarvis.knowledge.replica_kb import ReplicaKnowledgeBase


async def main():
    print("\n=== REPLICA KNOWLEDGE BASE DEMO ===\n")
    
    # Initialize KB
    kb = ReplicaKnowledgeBase()
    print(f"[1] Initialized KB with {len(kb.scrapling.repositories)} repositories")
    
    # Ingest test document
    result = await kb.ingest_document(
        doc_id="test-doc-1",
        content="FastAPI is a modern framework for building APIs with Python",
        source="fastapi/README.md",
        repo_url="https://github.com/tiangolo/fastapi"
    )
    print(f"[2] Ingested document: {result['success']}")
    
    # Ingest another doc
    result2 = await kb.ingest_document(
        doc_id="test-doc-2",
        content="Ponytail memory system for maintaining long-term context in AI agents",
        source="ponytail/README.md",
        repo_url="https://github.com/dietrichgebert/ponytail"
    )
    print(f"[3] Ingested second document: {result2['success']}")
    
    # Search for FastAPI
    search_result = await kb.search("FastAPI framework", top_k=2)
    print(f"[4] Search 'FastAPI framework' found {search_result['total_results']} result(s)")
    if search_result['results']:
        for i, result in enumerate(search_result['results'], 1):
            print(f"    [{i}] Score: {result['score']:.2f}")
            print(f"        Source: {result['source']}")
            print(f"        Repo: {result['repo']}")
    
    # Search for ponytail
    search_result2 = await kb.search("ponytail memory", top_k=2)
    print(f"\n[5] Search 'ponytail memory' found {search_result2['total_results']} result(s)")
    if search_result2['results']:
        for i, result in enumerate(search_result2['results'], 1):
            print(f"    [{i}] Score: {result['score']:.2f}")
            print(f"        Source: {result['source']}")
    
    # Get stats
    stats = await kb.get_repository_stats()
    print(f"\n[6] Knowledge Base Statistics:")
    print(f"    - Total repositories tracked: {stats['total_repositories']}")
    print(f"    - Total documents indexed: {stats['total_documents']}")
    print(f"    - Auto-update interval: {stats['auto_update_interval']} seconds (24 hours)")
    print(f"    - Initialized: {stats['initialized']}")
    
    # List first 5 repos
    repos = await kb.list_repositories()
    print(f"\n[7] Sample of {len(repos)} tracked repositories:")
    for repo in repos[:5]:
        print(f"    - {repo['name']}: status={repo['status']}")
    
    # Test citations
    print(f"\n[8] Testing citations for 'FastAPI':")
    search_with_citations = await kb.search("FastAPI", top_k=1)
    if search_with_citations['citations']:
        for i, citation in enumerate(search_with_citations['citations'], 1):
            print(f"    Citation {i}:")
            print(f"      Text preview: {citation['text'][:60]}...")
            print(f"      Source: {citation['source']}")
            print(f"      Repo: {citation['repo']}")
            print(f"      Score: {citation['score']:.2f}")
    
    await kb.close()
    print("\n[SUCCESS] Demo completed successfully!\n")


if __name__ == "__main__":
    asyncio.run(main())
