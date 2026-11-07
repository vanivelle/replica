# REPLICA Identity Integration Guide

## Overview

REPLICA is a sovereign AI assistant for the OpenJarvis ecosystem, inspired by the tactical intelligence from World Trigger. This document guides frontend integration of REPLICA's identity, status, and personality.

## Backend Implementation ✓

### 1. Core Identity Module
**File**: `src/openjarvis/identity/replica.py`

```python
from openjarvis.identity.replica import ReplicaIdentity, get_replica_identity

replica = get_replica_identity()
print(replica.name)  # "REPLICA"
print(replica.system_prompt)  # Full system prompt
print(replica.lore)  # Background story
```

**Key Features**:
- Sovereign AI identity with World Trigger inspiration
- 46 repositories + 71 agents ECC
- Ponytail memory backend
- System prompt with tactical analysis focus
- REA (Reasoning-Evidence-Attribution) mode

### 2. API Endpoints
**File**: `src/openjarvis/server/replica_routes.py`

#### GET `/v1/replica/info`
Returns REPLICA's identity information including specialties and lore.

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
  "lore": "REPLICA é uma inteligência soberana..."
}
```

#### GET `/v1/replica/status`
Returns real-time operational status.

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

#### POST `/v1/replica/greeting`
Returns initial greeting message in Portuguese-Brazilian.

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

#### GET `/v1/replica/system-prompt`
Returns the system prompt for chat completions.

**Response**:
```json
{
  "system_prompt": "Você é REPLICA, assistente alienígena soberano..."
}
```

### 3. Chat Completions Integration
**File**: `src/openjarvis/server/chat_completions.py`

The REPLICA system prompt is automatically injected into all chat completion requests:
- If no system message exists, REPLICA's system prompt is prepended
- All chat responses will adopt REPLICA's personality
- REA mode ensures reasoning, evidence, and attribution

## Frontend Integration

### Step 1: Update Logo/Branding
Replace "OpenJarvis" with "REPLICA" in the UI:

```html
<!-- Update header/nav -->
<div class="app-header">
  <h1>REPLICA</h1>
  <span class="subtitle">Sovereign AI Assistant</span>
</div>
```

### Step 2: Fetch REPLICA Info on Load
```javascript
async function initializeReplica() {
  const response = await fetch('http://127.0.0.1:8000/v1/replica/info');
  const replica = await response.json();
  
  // Update UI with REPLICA identity
  updateLogo(replica.name);
  updateSubtitle(replica.type);
  displayLore(replica.lore);
  updateSpecialties(replica.specialties);
}

// Call on app startup
initializeReplica();
```

### Step 3: Display Status Panel
Create a real-time status indicator:

```javascript
async function updateStatus() {
  const response = await fetch('http://127.0.0.1:8000/v1/replica/status');
  const status = await response.json();
  
  // Update UI elements
  updateOperationalMode(status.operational_mode);
  updateAgentCount(`${status.agents_active}/${status.agents_total}`);
  updateMemoryStatus(status.memory_status);
  updateRoutingStatus(status.routing_status);
}

// Refresh every 5 seconds
setInterval(updateStatus, 5000);
```

### Step 4: Show Greeting on Startup
```javascript
async function showGreeting() {
  const response = await fetch(
    'http://127.0.0.1:8000/v1/replica/greeting',
    { method: 'POST' }
  );
  const greeting = await response.json();
  
  // Display greeting message
  displayMessage(greeting.message, 'assistant');
}

// Call once on first user interaction
showGreeting();
```

### Step 5: Update Chat UI Styling
Add REPLICA-themed styling:

```css
/* REPLICA branding */
.chat-header {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: #00d4ff;
  border-left: 4px solid #00d4ff;
}

.replica-badge {
  background: #00d4ff;
  color: #1a1a2e;
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 4px;
}

.operational-status {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
  font-size: 12px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00d4ff;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

### Step 6: Example React Component
```jsx
import React, { useState, useEffect } from 'react';

function ReplicaIdentity() {
  const [replica, setReplica] = useState(null);
  const [status, setStatus] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      const infoRes = await fetch('http://127.0.0.1:8000/v1/replica/info');
      const statusRes = await fetch('http://127.0.0.1:8000/v1/replica/status');
      
      setReplica(await infoRes.json());
      setStatus(await statusRes.json());
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (!replica || !status) return <div>Loading REPLICA...</div>;

  return (
    <div className="replica-panel">
      <h1>{replica.name}</h1>
      <p>{replica.type}</p>
      
      <div className="status-section">
        <h3>Operational Status</h3>
        <div className="status-grid">
          <div>Mode: {status.operational_mode}</div>
          <div>Agents: {status.agents_active}/{status.agents_total}</div>
          <div>Memory: {status.memory_status}</div>
          <div>Routing: {status.routing_status}</div>
        </div>
      </div>

      <div className="specialties-section">
        <h3>Specialties</h3>
        <ul>
          {replica.specialties.map(s => <li key={s}>{s}</li>)}
        </ul>
      </div>

      <div className="lore-section">
        <p>{replica.lore}</p>
      </div>
    </div>
  );
}

export default ReplicaIdentity;
```

## Testing

### Test REPLICA Endpoints
```bash
# Get REPLICA identity
curl http://127.0.0.1:8000/v1/replica/info

# Get operational status
curl http://127.0.0.1:8000/v1/replica/status

# Get greeting
curl -X POST http://127.0.0.1:8000/v1/replica/greeting

# Get system prompt
curl http://127.0.0.1:8000/v1/replica/system-prompt
```

### Test with PowerShell
```powershell
.\test_replica_endpoints.ps1
```

## System Prompt Injection

The REPLICA system prompt is automatically injected into chat completions. The prompt includes:

- **Personality**: Formal, technical with subtle World Trigger humor
- **Specialties**: Tactical analysis, AI engineering, intelligent routing
- **Mode**: REA (Reasoning-Evidence-Attribution) active
- **Behavior**: Always cite sources and reasoning
- **Integration**: System decomposition and strategic analysis

Example injected system message:
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

## Next Steps

1. **Deploy**: Ensure server with REPLICA routes is running
2. **Frontend**: Integrate React/Vue component or vanilla JS
3. **Testing**: Verify all endpoints respond correctly
4. **Styling**: Apply REPLICA-themed CSS
5. **Customization**: Adjust colors, fonts, and layouts per branding
6. **Documentation**: Update user docs with REPLICA identity

## References

- World Trigger Anime: https://worldtrigger.fandom.com/
- OpenJarvis Repository: https://github.com/openjarvis
- REPLICA Backend: `src/openjarvis/identity/replica.py`
- REPLICA Routes: `src/openjarvis/server/replica_routes.py`
