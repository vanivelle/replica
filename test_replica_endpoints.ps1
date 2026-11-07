#!/usr/bin/env pwsh
<#
    .SYNOPSIS
    Test REPLICA identity endpoints
    
    .DESCRIPTION
    Tests all REPLICA endpoints to verify they are working correctly
#>

param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [int]$Timeout = 30
)

$ErrorActionPreference = "Stop"

function Test-Endpoint {
    param(
        [string]$Method,
        [string]$Path,
        [string]$Description
    )
    
    $url = "$BaseUrl$Path"
    Write-Host "Testing: $Description"
    Write-Host "  URL: $url"
    
    try {
        $params = @{
            Uri = $url
            Method = $Method
            TimeoutSec = $Timeout
            ContentType = "application/json"
        }
        
        if ($Method -eq "POST") {
            $params["Body"] = "{}"
        }
        
        $response = Invoke-RestMethod @params
        
        Write-Host "  ✓ Status: Success" -ForegroundColor Green
        Write-Host "  Response: $($response | ConvertTo-Json -Depth 2)" -ForegroundColor Cyan
        return $true
    }
    catch {
        Write-Host "  ✗ Status: Failed" -ForegroundColor Red
        Write-Host "  Error: $_" -ForegroundColor Red
        return $false
    }
}

Write-Host "================================"
Write-Host "REPLICA Identity Endpoint Tests"
Write-Host "================================"
Write-Host ""

$results = @()

# Test /v1/replica/info
$results += Test-Endpoint -Method "GET" -Path "/v1/replica/info" -Description "GET /v1/replica/info - REPLICA Identity"
Write-Host ""

# Test /v1/replica/status
$results += Test-Endpoint -Method "GET" -Path "/v1/replica/status" -Description "GET /v1/replica/status - Operational Status"
Write-Host ""

# Test /v1/replica/greeting
$results += Test-Endpoint -Method "POST" -Path "/v1/replica/greeting" -Description "POST /v1/replica/greeting - Initial Greeting"
Write-Host ""

# Test /v1/replica/system-prompt
$results += Test-Endpoint -Method "GET" -Path "/v1/replica/system-prompt" -Description "GET /v1/replica/system-prompt - System Prompt"
Write-Host ""

# Summary
Write-Host "================================"
Write-Host "Test Summary"
Write-Host "================================"
$passed = ($results | Where-Object { $_ -eq $true }).Count
$total = $results.Count
Write-Host "Passed: $passed/$total"

if ($passed -eq $total) {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "✗ Some tests failed" -ForegroundColor Red
    exit 1
}
