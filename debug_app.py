#!/usr/bin/env python3
"""Debug app creation."""

import sys
sys.path.insert(0, 'src')

try:
    from openjarvis.server.app import create_app
    app = create_app()
    print("App created successfully")
    print(f"Total routes: {len(app.routes)}")
    
    # Test memory router
    from openjarvis.server.api_routes import memory_router
    print(f"Memory router routes: {len(memory_router.routes)}")
    
    # Check if replica endpoints are there
    replica_routes = [r for r in memory_router.routes if "/replica" in r.path]
    print(f"Replica routes: {len(replica_routes)}")
    
    for route in replica_routes:
        print(f"  - {route.path}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
