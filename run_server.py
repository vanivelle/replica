#!/usr/bin/env python
"""Run the OpenJarvis server."""
import sys
from openjarvis.server.app import create_app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
