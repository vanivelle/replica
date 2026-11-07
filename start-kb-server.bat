@echo off
REM Start OpenJarvis Knowledge Base Server
REM This batch file keeps the server running 24/7

cd /d J:\tasksorobon\jarvis

REM Set Python path
set PYTHONPATH=J:\tasksorobon\jarvis\src

REM Start the server
echo [%date% %time%] Starting OpenJarvis Knowledge Base Server...
echo Listening on http://127.0.0.1:8001
echo.
echo Endpoints:
echo   POST   /v1/knowledge/ingest     - Index document
echo   GET    /v1/knowledge/search     - Search with citations
echo   GET    /v1/knowledge/repos      - List repositories  
echo   GET    /v1/knowledge/stats      - Statistics
echo   POST   /v1/knowledge/repositories - Add repository
echo   DELETE /v1/knowledge/clear      - Clear index
echo.
echo Press CTRL+C to stop the server
echo.

.venv\Scripts\python -m uvicorn openjarvis.server.main:app --port 8001 --host 127.0.0.1

REM If server crashes, restart automatically
echo [%date% %time%] Server stopped. Restarting in 5 seconds...
timeout /t 5
goto :start
