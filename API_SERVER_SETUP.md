# OpenJarvis API Server - Setup e Configuração

## ✅ Status: Servidor Funcionando

O servidor FastAPI do OpenJarvis está rodando com sucesso em `http://127.0.0.1:8000`

---

## 📋 O Que Foi Feito

### Passo 1: Verificação da Instância FastAPI ✓
- **Localização:** `src/openjarvis/server/app.py`
- **Resultado:** A instância é criada dinamicamente pela função `create_app()`
- **Solução:** Criado arquivo `src/openjarvis/server/main.py` que exporta a instância `app`

### Passo 2: Inicialização do Servidor ✓
- **Comando executado:**
  ```powershell
  .\.venv\Scripts\python -m uvicorn openjarvis.server.main:app --host 127.0.0.1 --port 8000 --reload
  ```
- **Status:** ✅ Servidor rodando com reload automático

### Passo 3: Documentação Acessível ✓
- **OpenAPI JSON:** http://127.0.0.1:8000/openapi.json
- **Swagger UI:** http://127.0.0.1:8000/docs (com CSP)
- **ReDoc:** http://127.0.0.1:8000/redoc (com CSP)

---

## 🧪 Testes Realizados

### 1. Listar Modelos Disponíveis
```bash
curl http://127.0.0.1:8000/v1/models
```

**Resposta:**
```json
{
  "object": "list",
  "data": [
    {"id": "concursos-elite:latest", "object": "model", "created": 1793774282, "owned_by": "openjarvis"},
    {"id": "gemma2:latest", "object": "model", "created": 1793774282, "owned_by": "openjarvis"},
    {"id": "gemma2:2b", "object": "model", "created": 1793774282, "owned_by": "openjarvis"},
    {"id": "gemma4:latest", "object": "model", "created": 1793774282, "owned_by": "openjarvis"}
  ]
}
```

**Status:** ✅ 200 OK

---

## 📝 Arquivos Criados/Modificados

### 1. `src/openjarvis/server/main.py` (NOVO)
**Propósito:** Entry point para uvicorn

```python
"""Entry point for uvicorn to run the OpenJarvis API server."""

from openjarvis.server.app import create_app


class MockEngine:
    """Mock inference engine for development/testing."""
    
    def __init__(self):
        self._model = "gpt-4"
    
    def list_models(self):
        """Return a list of available models."""
        return ["gpt-4", "gpt-3.5-turbo", "claude-3-opus"]
    
    async def agenerate(self, *args, **kwargs):
        """Mock async generation."""
        return "This is a mock response"
    
    def generate(self, *args, **kwargs):
        """Mock generation."""
        return "This is a mock response"


# Create the app instance with mock engine for development
app = create_app(
    engine=MockEngine(),
    model="gpt-4",
)
```

---

## 🚀 Como Usar

### Iniciar o Servidor

```powershell
cd J:\tasksorobon\jarvis
.\.venv\Scripts\python -m uvicorn openjarvis.server.main:app --host 127.0.0.1 --port 8000 --reload
```

### Endpoints Disponíveis

- **Base URL:** http://127.0.0.1:8000
- **OpenAPI Spec:** http://127.0.0.1:8000/openapi.json
- **List Models:** http://127.0.0.1:8000/v1/models
- **Chat Completions:** POST http://127.0.0.1:8000/v1/chat/completions
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

### Exemplo com Python

```python
import requests

# Listar modelos
response = requests.get("http://127.0.0.1:8000/v1/models")
print(response.json())

# Chat completion
data = {
    "model": "gpt-4",
    "messages": [
        {"role": "user", "content": "Olá!"}
    ]
}
response = requests.post("http://127.0.0.1:8000/v1/chat/completions", json=data)
print(response.json())
```

### Exemplo com cURL

```bash
# Listar modelos
curl http://127.0.0.1:8000/v1/models

# Chat completion
curl -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Olá!"}]
  }'
```

---

## 🔧 Configuração de Produção

Para usar com um motor de inferência real (não mock), atualize `src/openjarvis/server/main.py`:

```python
from openjarvis.inference import create_engine  # ou seu engine real

# Criar engine real
engine = create_engine(
    provider="litellm",
    model="gpt-4",
    api_key="sua-chave-api"
)

app = create_app(
    engine=engine,
    model="gpt-4",
)
```

---

## 📊 Informações da Configuração

- **Python:** 3.12.16
- **FastAPI:** 0.136.3
- **Uvicorn:** 0.54.0
- **Starlette:** 1.6.0
- **Pydantic:** 2.14.0
- **Host:** 127.0.0.1
- **Port:** 8000
- **Modo:** Development (reload ativo)

---

## ⚠️ Notas

1. O engine mock retorna dados fictícios - não faça requisições reais de chat completions
2. A documentação Swagger/ReDoc pode ter problemas de CSP em navegadores em sandbox
3. Use o OpenAPI JSON diretamente ou ferramentas como Postman para testar
4. Para produção, configure um motor de inferência real (LiteLLM, Ollama, etc)

---

## ✨ Próximos Passos

1. ✅ Servidor FastAPI funcionando
2. ✅ Documentação OpenAPI disponível
3. 🔜 Integrar motor de inferência real
4. 🔜 Configurar autenticação/autorização
5. 🔜 Deploy em produção
