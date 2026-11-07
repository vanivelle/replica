"""Entry point for uvicorn to run the OpenJarvis API server."""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from openjarvis.server.app import create_app
from datetime import datetime

class MockEngine:
    """Mock inference engine for development/testing."""
    
    def __init__(self):
        self._model = "gpt-4"
    
    def list_models(self):
        """Return a list of available models."""
        return ["llama2", "mistral", "neural-chat", "starling-lm", "orca-mini"]
    
    def health(self):
        """Health check status."""
        return {"status": "ok", "model": self._model}
    
    async def agenerate(self, *args, **kwargs):
        """Mock async generation."""
        return {
            "content": "Sistema operacional normalmente. Todos os agentes estão online e prontos para ação!",
            "model": kwargs.get("model", "gpt-4"),
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        }
    
    def generate(self, *args, **kwargs):
        """Mock generation."""
        return {
            "content": "Sistema operacional normalmente. Todos os agentes estão online e prontos para ação!",
            "model": kwargs.get("model", "gpt-4"),
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        }
    
    async def stream(self, *args, **kwargs):
        """Mock streaming generation."""
        yield {
            "type": "content_block_delta",
            "delta": {"type": "text_delta", "text": "Jarvis operacional e pronto para ação! "},
            "index": 0
        }
        yield {
            "type": "message_stop",
            "delta": {}
        }


# Create the app instance with mock engine for development
app = create_app(
    engine=MockEngine(),
    model="gpt-4",
)


# Add home/status endpoint
@app.get("/", response_class=HTMLResponse)
async def home():
    """Home page with API status and documentation."""
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OpenJarvis API - Status</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                color: white;
                margin-bottom: 40px;
            }
            .header h1 {
                font-size: 3em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .status-card {
                background: white;
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                border-left: 5px solid #10b981;
            }
            .status-card h3 {
                color: #333;
                margin-bottom: 10px;
            }
            .status-badge {
                display: inline-block;
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 0.9em;
                font-weight: bold;
                background: #d1fae5;
                color: #065f46;
            }
            .endpoints-section {
                background: white;
                border-radius: 10px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .endpoints-section h2 {
                color: #333;
                margin-bottom: 20px;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }
            .endpoint {
                background: #f5f5f5;
                border-left: 3px solid #667eea;
                padding: 15px;
                margin-bottom: 15px;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
                font-size: 0.95em;
            }
            .method {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 3px;
                font-weight: bold;
                margin-right: 10px;
                font-size: 0.9em;
                background: #3b82f6;
                color: white;
            }
            .method.post {
                background: #10b981;
            }
            .buttons {
                display: flex;
                gap: 10px;
                justify-content: center;
            }
            .btn {
                padding: 12px 24px;
                border-radius: 5px;
                text-decoration: none;
                font-weight: bold;
                background: #667eea;
                color: white;
                transition: all 0.3s;
            }
            .btn:hover {
                background: #5568d3;
            }
            .footer {
                text-align: center;
                color: white;
                margin-top: 40px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 OpenJarvis API</h1>
                <p>Modular AI Assistant Backend</p>
            </div>
            <div class="status-grid">
                <div class="status-card">
                    <h3>Server Status</h3>
                    <span class="status-badge">🟢 ONLINE</span>
                </div>
            </div>
            <div class="endpoints-section">
                <h2>📡 Endpoints</h2>
                <div class="endpoint"><span class="method">GET</span> /v1/models</div>
                <div class="endpoint"><span class="method post">POST</span> /v1/chat/completions</div>
                <div class="endpoint"><span class="method">GET</span> /docs</div>
            </div>
            <div class="buttons">
                <a href="/docs" class="btn">📖 API Docs (Swagger)</a>
            </div>
            <div class="footer">
                <p>✨ OpenJarvis v1.0.5.dev | Python • FastAPI • Uvicorn</p>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/status")
async def status():
    """API status endpoint (JSON)."""
    return {
        "status": "online",
        "version": "1.0.5.dev",
        "timestamp": datetime.utcnow().isoformat()
    }