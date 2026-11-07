"""Test knowledge base endpoints with curl commands."""

import subprocess
import json
import time
import sys

BASE_URL = "http://127.0.0.1:8001"


def run_curl(method: str, endpoint: str, data=None, query_params=None):
    """Execute curl command and return response."""
    url = f"{BASE_URL}{endpoint}"
    
    if query_params:
        params = "&".join([f"{k}={v}" for k, v in query_params.items()])
        url = f"{url}?{params}"
    
    cmd = ["curl", "-s", "-X", method]
    
    if method in ["POST", "PUT"]:
        cmd.extend(["-H", "Content-Type: application/json"])
        if data:
            cmd.extend(["-d", json.dumps(data)])
    
    cmd.append(url)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except Exception as e:
        return f"ERROR: {str(e)}"


def test_health():
    """Test server health."""
    print("\n=== Testing Server Health ===")
    response = run_curl("GET", "/health")
    print(f"GET /health: {response}")
    return "healthy" in response.lower()


def test_search_endpoint():
    """Test search endpoint."""
    print("\n=== Testing Search Endpoint ===")
    
    # Test search for ponytail
    response = run_curl(
        "GET",
        "/v1/knowledge/search",
        query_params={"q": "ponytail memory", "top_k": "3"}
    )
    print(f"Search 'ponytail memory':")
    try:
        data = json.loads(response)
        print(json.dumps(data, indent=2))
        assert "query" in data
        assert "results" in data
        assert "citations" in data
        return True
    except json.JSONDecodeError:
        print(f"ERROR: Could not parse JSON response: {response[:200]}")
        return False


def test_ingest_endpoint():
    """Test document ingest endpoint."""
    print("\n=== Testing Ingest Endpoint ===")
    
    doc_data = {
        "doc_id": "test-doc-1",
        "content": "This is a test document about FastAPI and Pydantic",
        "source": "test/README.md",
        "repo_url": "https://github.com/test/test-repo",
        "doc_type": "readme"
    }
    
    response = run_curl("POST", "/v1/knowledge/ingest", data=doc_data)
    print(f"POST /v1/knowledge/ingest:")
    try:
        data = json.loads(response)
        print(json.dumps(data, indent=2))
        assert data.get("success") is True
        return True
    except json.JSONDecodeError:
        print(f"ERROR: Could not parse JSON response: {response[:200]}")
        return False


def test_repos_endpoint():
    """Test repositories list endpoint."""
    print("\n=== Testing Repositories Endpoint ===")
    
    response = run_curl("GET", "/v1/knowledge/repos")
    print(f"GET /v1/knowledge/repos:")
    try:
        data = json.loads(response)
        if isinstance(data, list):
            print(f"Found {len(data)} repositories")
            print("Sample repos:")
            for repo in data[:3]:
                print(f"  - {repo.get('name')}: {repo.get('status')}")
            return True
        else:
            print(f"ERROR: Expected list, got: {type(data)}")
            return False
    except json.JSONDecodeError:
        print(f"ERROR: Could not parse JSON response: {response[:200]}")
        return False


def test_stats_endpoint():
    """Test statistics endpoint."""
    print("\n=== Testing Statistics Endpoint ===")
    
    response = run_curl("GET", "/v1/knowledge/stats")
    print(f"GET /v1/knowledge/stats:")
    try:
        data = json.loads(response)
        print(json.dumps(data, indent=2))
        assert "total_repositories" in data
        assert "total_documents" in data
        return True
    except json.JSONDecodeError:
        print(f"ERROR: Could not parse JSON response: {response[:200]}")
        return False


def main():
    """Run all tests."""
    print("Starting knowledge base endpoint tests...")
    print(f"Base URL: {BASE_URL}")
    
    # Wait for server to be ready
    print("\nWaiting for server to be ready...")
    for i in range(30):
        try:
            response = run_curl("GET", "/health")
            if "healthy" in response.lower():
                print("✓ Server is ready")
                break
        except:
            pass
        if i < 29:
            time.sleep(1)
    else:
        print("✗ Server did not become ready")
        return False
    
    # Run tests
    tests = [
        ("Health Check", test_health),
        ("Search Endpoint", test_search_endpoint),
        ("Ingest Endpoint", test_ingest_endpoint),
        ("Repositories Endpoint", test_repos_endpoint),
        ("Statistics Endpoint", test_stats_endpoint),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name} failed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*50)
    print("TEST RESULTS SUMMARY")
    print("="*50)
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
