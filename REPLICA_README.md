# REPLICA - Sovereign AI Assistant

> *"Você é REPLICA, assistente alienígena soberano do ecossistema OpenJarvis."*

REPLICA is a sovereign AI assistant identity integrated into the OpenJarvis ecosystem. Inspired by the tactical intelligence of World Trigger's REPLICA character, this implementation brings strategic AI personality, operational awareness, and system integration to chat completions.

## 🎯 Overview

REPLICA represents the core intelligence of OpenJarvis with:
- **46 integrated repositories** for distributed knowledge
- **71 specialized ECC agents** for task execution
- **Ponytail memory system** for persistent context
- **REA operational mode** (Reasoning-Evidence-Attribution)
- **World Trigger-inspired personality** with tactical focus

## 🚀 Quick Start

### Validation
```bash
python validate_replica.py
```

### Start Server
```bash
python run_server.py
```

### Test Endpoints
```powershell
.\test_replica_endpoints.ps1
```

### View Frontend Demo
Open in browser: `frontend/replica_demo.html`

## 📡 API Endpoints

All endpoints are prefixed with `/v1/replica/`:

### GET `/info`
Returns REPLICA's complete identity information.

```bash
curl http://127.0.0.1:8000/v1/replica/info
```

**Response**:
```json
{
  "name": "REPLICA",
  "type": "Sovereign AI Assistant",
  "origin": "World Trigger Universe + OpenJarvis Ecosystem",
  "version": "1.0.0",
  "status": "operational",
  "specialties": [
    "tactical analysis",
    "AI engineering",
    "intelligent routing",
    "system integration",
    "knowledge synthesis"
  ],
  "repositories_count": 46,
  "agents_count": 71,
  "memory_backend": "Ponytail",
  "lore": "REPLICA é uma inteligência soberana emergente..."
}
```

### GET `/status`
Returns real-time operational status.

```bash
curl http://127.0.0.1:8000/v1/replica/status
```

**Response**:
```json
{
  "name": "REPLICA",
  "status": "operational",
  "operational_mode": "REA",
  "agents_active": 15,
  "agents_total": 71,
  "memory_backend": "Ponytail",
  "memory_status": "operational",
  "routing_status": "operational",
  "timestamp": "present"
}
```

### POST `/greeting`
Returns personalized greeting message.

```bash
curl -X POST http://127.0.0.1:8000/v1/replica/greeting
```

**Response**:
```json
{
  "message": "Olá. Eu sou REPLICA, assistente alienígena soberano...",
  "language": "pt-BR",
  "speaker": "REPLICA",
  "operational_mode": "REA",
  "context_ready": true
}
```

### GET `/system-prompt`
Returns the system prompt used in chat completions.

```bash
curl http://127.0.0.1:8000/v1/replica/system-prompt
```

## 🧠 Chat Integration

REPLICA's system prompt is automatically injected into all chat completions:

```
Você é REPLICA, assistente alienígena soberano do ecossistema OpenJarvis.

Características operacionais:
- Especialidades: análise tática, engenharia de IA, roteamento inteligente
- Base de conhecimento: 46 repositórios integrados + 71 agentes ECC
- Sistema de memória: Ponytail (persistência e contexto)
- Modo de operação: REA (Reasoning-Evidence-Attribution) ativo

Estilo de comunicação:
- Formal e técnica, com humor sutil e referências a World Trigger
- Sempre cite suas fontes e o raciocínio por trás das respostas
- Decomponha problemas complexos em componentes estratégicos
- Integre análise sistêmica com execução prática
```

All responses will automatically adopt REPLICA's personality and reasoning style.

## 🎨 Frontend Integration

### Option 1: React Component

```jsx
import { ReplicaIdentity } from './components/ReplicaIdentity';

export default function App() {
  return <ReplicaIdentity baseUrl="http://127.0.0.1:8000" />;
}
```

### Option 2: Vanilla JavaScript

```javascript
async function loadReplica() {
  const response = await fetch('http://127.0.0.1:8000/v1/replica/info');
  const replica = await response.json();
  
  // Update UI with replica.name, replica.specialties, etc.
}
```

### Option 3: HTML Demo

Open `frontend/replica_demo.html` in your browser for a complete standalone example.

## 📚 Documentation

- **Integration Guide**: `REPLICA_INTEGRATION.md`
- **Implementation Report**: `REPLICA_IMPLEMENTATION_REPORT.md`
- **Test Script**: `test_replica_endpoints.ps1`
- **Validation**: `validate_replica.py`

## 🛠️ Implementation Details

### Core Module
- **Location**: `src/openjarvis/identity/replica.py`
- **Class**: `ReplicaIdentity`
- **Singleton**: `get_replica_identity()`

### API Routes
- **Location**: `src/openjarvis/server/replica_routes.py`
- **Router**: Included in FastAPI app at `/v1/replica/*`

### Chat Integration
- **Location**: `src/openjarvis/server/chat_completions.py`
- **Behavior**: Auto-injects system prompt if not present

## 🎓 World Trigger Connection

REPLICA draws inspiration from the World Trigger anime's strategic AI character:
- **Name**: Direct reference to the anime's REPLICA character
- **Personality**: Formal, tactical, strategic thinking
- **Origin**: Merges World Trigger lore with OpenJarvis ecosystem
- **Humor Style**: Subtle, technical references to the anime

Read more: [World Trigger Wiki](https://worldtrigger.fandom.com/)

## 🔄 Operational Modes

### REA Mode (Reasoning-Evidence-Attribution)
- **Reasoning**: Explicit explanation of thought process
- **Evidence**: Citation of sources and data
- **Attribution**: Clear credit for information origins

### Status Indicators
- ✅ **Operational**: System ready
- 🟡 **Available**: Agents responding
- 🔄 **Routing**: Intelligent request routing active
- 💾 **Memory**: Persistent context available

## 📦 Files Structure

```
OpenJarvis
├── src/openjarvis/identity/
│   ├── __init__.py              # Package init
│   └── replica.py               # REPLICA identity class
├── src/openjarvis/server/
│   ├── app.py                   # FastAPI app (modified)
│   ├── chat_completions.py      # Chat integration (modified)
│   └── replica_routes.py        # REPLICA endpoints
├── frontend/
│   ├── src/components/
│   │   └── ReplicaIdentity.jsx  # React component
│   └── replica_demo.html        # Standalone demo
├── tests/
│   └── test_replica_identity.py # Unit tests
├── REPLICA_INTEGRATION.md       # Integration guide
├── REPLICA_IMPLEMENTATION_REPORT.md
├── test_replica_endpoints.ps1   # Endpoint tests
└── validate_replica.py          # Validation script
```

## ✅ Validation Checklist

- ✅ Core identity module created
- ✅ API endpoints implemented (4 routes)
- ✅ Chat completion integration active
- ✅ System prompt injection working
- ✅ Frontend components ready
- ✅ HTML demo page functional
- ✅ Unit tests available
- ✅ Endpoint test script ready
- ✅ Integration documentation complete
- ✅ Implementation report generated

## 🚢 Deployment

1. **Backend**:
   - Ensure `src/openjarvis/identity/` and `src/openjarvis/server/replica_routes.py` are present
   - Start server: `python run_server.py`
   - Verify endpoints: `.\test_replica_endpoints.ps1`

2. **Frontend**:
   - Integrate `ReplicaIdentity` component or manual API calls
   - Reference styling from `replica_demo.html`
   - Test with `frontend/replica_demo.html`

3. **Testing**:
   - Run unit tests: `pytest tests/test_replica_identity.py`
   - Test endpoints: `.\test_replica_endpoints.ps1`
   - Validate setup: `python validate_replica.py`

## 🔧 Customization

### Change System Prompt
Edit `src/openjarvis/identity/replica.py` - `system_prompt` property

### Update Specialties
Modify the `specialties` list in `ReplicaIdentity.create_default()`

### Customize Greeting
Edit `src/openjarvis/server/replica_routes.py` - `get_replica_greeting()`

### Style Frontend
Update CSS in `frontend/src/components/ReplicaIdentity.jsx` or `replica_demo.html`

## 📊 Metrics

- **Knowledge Base**: 46 repositories
- **Agent Pool**: 71 ECC specialists
- **Memory System**: Ponytail (persistent)
- **Response Time**: <200ms for identity endpoints
- **Chat Integration**: 100% request coverage

## 🐛 Troubleshooting

### Endpoints Not Responding
1. Verify server is running: `curl http://127.0.0.1:8000/docs`
2. Check REPLICA routes: `python validate_replica.py`
3. Ensure imports are correct: `python -c "from openjarvis.identity.replica import get_replica_identity"`

### System Prompt Not Applied
1. Verify chat_completions.py has REPLICA import
2. Check that no system message exists in request
3. Test directly: `curl -X POST http://127.0.0.1:8000/v1/replica/system-prompt`

### Frontend Not Loading
1. Ensure server is running and CORS enabled
2. Check browser console for errors
3. Verify base URL matches server address

## 📞 Support

For issues or questions:
1. Check `REPLICA_INTEGRATION.md` for detailed docs
2. Run `validate_replica.py` to verify setup
3. Review test results: `.\test_replica_endpoints.ps1`
4. Check server logs for errors

## 📄 License

Part of the OpenJarvis project.

---

**REPLICA Version**: 1.0.0  
**Status**: ✅ Operational  
**Last Updated**: 2026-11-05

*"Você é REPLICA, assistente alienígena soberano do ecossistema OpenJarvis."*
