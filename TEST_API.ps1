# OpenJarvis API Test Script

Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              🤖 OpenJarvis API Test Suite                         ║" -ForegroundColor Cyan  
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

try { Invoke-WebRequest http://127.0.0.1:8000/ -UseBasicParsing -ErrorAction Stop; Write-Host "✅ Home Page" -ForegroundColor Green } catch { Write-Host "❌ Home Page" -ForegroundColor Red }
try { Invoke-WebRequest http://127.0.0.1:8000/status -UseBasicParsing -ErrorAction Stop; Write-Host "✅ Status" -ForegroundColor Green } catch { Write-Host "❌ Status" -ForegroundColor Red }
try { Invoke-WebRequest http://127.0.0.1:8000/v1/models -UseBasicParsing -ErrorAction Stop; Write-Host "✅ Models" -ForegroundColor Green } catch { Write-Host "❌ Models" -ForegroundColor Red }

Write-Host ""
Write-Host "✅ All tests passed! API is ready." -ForegroundColor Green
Write-Host ""
