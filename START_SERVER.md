# 🚀 Initiate Phase 2 - Quick Start Guide

## Status: ✅ PRODUCTION READY

All Phase 2 components are implemented, tested, and validated. Ready to start the FastAPI server!

---

## 1️⃣ Start the Server

Open PowerShell in the project root and run:

```powershell
cd J:\tasksorobon\jarvis
.\.venv\Scripts\python -m uvicorn openjarvis.server.app:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete
```

---

## 2️⃣ Validate Health Check

In a new PowerShell window:

```powershell
# Option A: Direct HTTP request
Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/health" | ConvertTo-Json

# Option B: Using curl (if installed)
curl http://127.0.0.1:8000/v1/health

# Option C: Browser
# Navigate to: http://127.0.0.1:8000/v1/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-04T11:30:00.123456",
  "components": {
    "ecc_parser": "ok",
    "omni_router": "ok",
    "graphify": "ok",
    "ponytail": "ok",
    "archify": "ok"
  }
}
```

---

## 3️⃣ Access Swagger UI (Interactive Documentation)

Open your browser and navigate to:

```
http://127.0.0.1:8000/docs
```

You'll see the interactive Swagger UI with all 17 endpoints documented and testable!

---

## 4️⃣ Test Key Endpoints

### Option A: Using PowerShell Invoke-RestMethod

```powershell
# 1. List all ECC agents
Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/agents/ecc?limit=5" | ConvertTo-Json

# 2. Select optimal model
Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/routing/select-model?task_type=code_review&priority=quality" -Method Post | ConvertTo-Json

# 3. Create an agent instance
$body = @{
    agent_id = "ecc_code_reviewer_python"
    session_id = "test_session_001"
}
Invoke-RestMethod -Uri "http://127.0.0.1:8000/v1/agents/create?agent_id=ecc_code_reviewer_python&session_id=test_001" -Method Post | ConvertTo-Json
```

### Option B: Using Swagger UI
1. Navigate to http://127.0.0.1:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Enter parameters and click "Execute"

---

## 5️⃣ Run Integration Tests

```powershell
cd J:\tasksorobon\jarvis

# Run all tests
pytest tests/test_layer_a_integration.py -v

# Run specific test
pytest tests/test_layer_a_integration.py::test_ecc_parser_loads_agents -v

# Run with coverage
pytest tests/test_layer_a_integration.py --cov=src/openjarvis
```

---

## 6️⃣ Validate All Components

```powershell
cd J:\tasksorobon\jarvis
python validate_phase2.py
```

**Expected Output:**
```
======================================================================
  FASE 2 - FINAL VALIDATION
======================================================================

[OK] ECC Parser                     OK         Loaded 42 agents
[OK] Agent Factory                  OK         Created: Python Code Reviewer
[OK] OmniRouter                     OK         Model: claude-sonnet
[OK] Graphify                       OK         Manager initialized
[OK] Ponytail                       OK         Tunnel created successfully
[OK] Layer A Routes                 OK         17 endpoints available
[OK] App Integration                OK         Routes integrated in app.py
[OK] Integration Tests              OK         36 tests available

Total: 8/8 components validated
Success Rate: 100.0%

[OK] PHASE 2 COMPLETE - PRODUCTION READY
```

---

## 📝 API Examples

### Create an Agent

```powershell
$response = Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/v1/agents/create" `
  -Method Post `
  -Body @"
{
  "agent_id": "ecc_code_reviewer_python",
  "session_id": "my_session_123"
}
"@ `
  -ContentType "application/json"

$response | ConvertTo-Json -Depth 10
```

### Select Optimal Model

```powershell
$response = Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/v1/routing/select-model?task_type=code_review&priority=quality" `
  -Method Post

$response
# Returns: selected_model, score, fallbacks, reason
```

### Get Agent Dependencies

```powershell
$response = Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/v1/graph/dependencies/ecc_code_reviewer_python"

$response | ConvertTo-Json -Depth 5
```

### Get Architecture Diagram

```powershell
# Mermaid format
$response = Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/v1/archify/diagram?format=mermaid"

# JSON format
$response = Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/v1/archify/diagram?format=json"

# Export to file
$response = Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/v1/archify/diagram?format=mermaid"

$response.diagram | Out-File -Path "architecture.mmd"
```

---

## 🔍 Troubleshooting

### Server won't start on port 8000

**Error:** `Address already in use`

**Solution:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Try again
.\.venv\Scripts\python -m uvicorn openjarvis.server.app:app --reload
```

### Import errors

**Error:** `ModuleNotFoundError`

**Solution:**
```powershell
# Reinstall in development mode
cd J:\tasksorobon\jarvis
.\.venv\Scripts\python -m pip install -e .
```

### Tests failing

**Solution:**
```powershell
# Run with verbose output
pytest tests/test_layer_a_integration.py -v -s

# Check Python version
python --version  # Should be 3.12

# Check if all dependencies installed
pip list | findstr pytest
```

### Unicode encoding errors (Windows)

**Note:** Windows PowerShell may have encoding issues with special characters.

**Solution:**
```powershell
# Add to profile or script
$OutputEncoding = [System.Text.UTF8Encoding]::UTF8
```

---

## 📊 Files Reference

### Core Implementation
- `src/openjarvis/server/layer_a_routes.py` - 17 FastAPI endpoints
- `src/openjarvis/agents/agent_factory.py` - Dynamic agent instantiation
- `tests/test_layer_a_integration.py` - 36 integration tests

### Documentation
- `PHASE_2_EXECUTIVE_SUMMARY.md` - Executive summary
- `FASE_2_COMPLETION.md` - Technical completion report
- `PHASE_2_SUMMARY.txt` - Quick reference
- `validate_phase2.py` - Validation script

### App Integration
- `src/openjarvis/server/app.py` - Modified with layer_a_router

---

## 🎯 Next Steps

1. ✅ Start server: `python -m uvicorn openjarvis.server.app:app --reload`
2. ✅ Test endpoints: Visit http://127.0.0.1:8000/docs
3. ✅ Run tests: `pytest tests/test_layer_a_integration.py -v`
4. ✅ Validate: `python validate_phase2.py`
5. ⏳ **Phase 3**: Implement Skills Layer (Camada B) with 1900+ templates

---

## 📞 Support

For issues or questions:
1. Check error messages carefully
2. Review logs in the terminal
3. Check `PHASE_2_EXECUTIVE_SUMMARY.md` for troubleshooting
4. Run validation script: `python validate_phase2.py`

---

**Phase 2 is PRODUCTION READY! 🚀**

Server ready to accept requests via FastAPI endpoints!
