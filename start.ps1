# Patient Monitoring System - Quick Start Script
# This script starts both backend and frontend servers

Write-Host "Patient Monitoring System - Starting..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "OK $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Check if Node is installed
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "OK Node.js $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Node.js not found. Please install Node.js 16+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray

# Start backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
    cd '$PSScriptRoot\backend'
    Write-Host 'Activating Python virtual environment...' -ForegroundColor Cyan
    if (Test-Path 'venv\Scripts\Activate.ps1') {
        .\venv\Scripts\Activate.ps1
    } else {
        Write-Host 'Creating virtual environment...' -ForegroundColor Yellow
        python -m venv venv
        .\venv\Scripts\Activate.ps1
        Write-Host 'Installing dependencies...' -ForegroundColor Yellow
        pip install -r requirements.txt
    }
    Write-Host 'Starting FastAPI server...' -ForegroundColor Green
    python main.py
"@

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray

# Start frontend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", @"
    cd '$PSScriptRoot\frontend'
    Write-Host 'Checking Node modules...' -ForegroundColor Cyan
    if (-not (Test-Path 'node_modules')) {
        Write-Host 'Installing dependencies...' -ForegroundColor Yellow
        npm install
    }
    Write-Host 'Starting Vite dev server...' -ForegroundColor Green
    npm run dev
"@

Write-Host ""
Write-Host "========================================" -ForegroundColor Gray
Write-Host "Servers starting in separate windows" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop the servers" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Gray
