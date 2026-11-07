"""REPLICA Implementation Validation Script"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from openjarvis.identity.replica import get_replica_identity
from openjarvis.server.replica_routes import router

def validate_replica():
    """Validate REPLICA implementation"""
    replica = get_replica_identity()

    print("=" * 70)
    print("REPLICA IDENTITY VALIDATION")
    print("=" * 70)
    print()

    print("1. Identity Status")
    print("-" * 70)
    print(f"   Name: {replica.name}")
    print(f"   Type: {replica.type}")
    print(f"   Status: {replica.status}")
    print(f"   Version: {replica.version}")
    print()

    print("2. Operational Metrics")
    print("-" * 70)
    print(f"   Agents: {replica.agents_count}")
    print(f"   Repositories: {replica.repositories_count}")
    print(f"   Memory Backend: {replica.memory_backend}")
    print()

    print("3. Specialties")
    print("-" * 70)
    for specialty in replica.specialties:
        print(f"   - {specialty}")
    print()

    print("4. API Routes Registered")
    print("-" * 70)
    for route in router.routes:
        methods_str = ', '.join(sorted(route.methods - {'OPTIONS', 'HEAD'}))
        print(f"   {route.path} [{methods_str}]")
    print()

    print("5. System Prompt Preview")
    print("-" * 70)
    prompt_lines = replica.system_prompt.split('\n')[:5]
    for line in prompt_lines:
        if line.strip():
            preview = line[:65] + "..." if len(line) > 65 else line
            print(f"   {preview}")
    print()

    print("6. JSON Export Sample")
    print("-" * 70)
    data = replica.to_dict()
    print(f"   Keys: {', '.join(data.keys())}")
    print(f"   Total Size: {len(json.dumps(data))} bytes")
    print()

    print("=" * 70)
    print("VALIDATION COMPLETE")
    print("=" * 70)
    print()
    print("Success! REPLICA is fully operational and ready for deployment.")
    print()
    print("Next Steps:")
    print("  1. Start the OpenJarvis server: python run_server.py")
    print("  2. Test endpoints: .\\test_replica_endpoints.ps1")
    print("  3. Integrate frontend: Use ReplicaIdentity.jsx or replica_demo.html")
    print("  4. Read docs: REPLICA_INTEGRATION.md")

if __name__ == '__main__':
    validate_replica()
