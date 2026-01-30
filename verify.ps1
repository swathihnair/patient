# System Verification Script
# Checks if all components are properly set up

Write-Host "🏥 Patient Monitoring System - Setup Verification" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

$allGood = $true

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.([9]|1[0-9])") {
        Write-Host "  ✓ $pythonVersion" -ForegroundColor Green
    }
    else {
        Write-Host "  ✗ Python 3.9+ required, found: $pythonVersion" -ForegroundColor Red
        $allGood = $false
    }
}
catch {
    Write-Host "  ✗ Python not found" -ForegroundColor Red
    $allGood = $false
}

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    if ($nodeVersion -match "v(1[6-9]|[2-9][0-9])") {
        Write-Host "  ✓ Node.js $nodeVersion" -ForegroundColor Green
    }
    else {
        Write-Host "  ✗ Node.js 16+ required, found: $nodeVersion" -ForegroundColor Red
        $allGood = $false
    }
}
catch {
    Write-Host "  ✗ Node.js not found" -ForegroundColor Red
    $allGood = $false
}

# Check npm
Write-Host "Checking npm..." -ForegroundColor Yellow
try {
    $npmVersion = npm --version 2>&1
    Write-Host "  ✓ npm $npmVersion" -ForegroundColor Green
}
catch {
    Write-Host "  ✗ npm not found" -ForegroundColor Red
    $allGood = $false
}

Write-Host ""
Write-Host "Checking Project Structure..." -ForegroundColor Yellow

# Check backend files
$backendFiles = @(
    "backend\main.py",
    "backend\requirements.txt",
    "backend\generate_test_video.py",
    "backend\README.md"
)

foreach ($file in $backendFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    }
    else {
        Write-Host "  ✗ Missing: $file" -ForegroundColor Red
        $allGood = $false
    }
}

# Check frontend files
$frontendFiles = @(
    "frontend\package.json",
    "frontend\src\App.jsx",
    "frontend\src\index.css",
    "frontend\README.md"
)

foreach ($file in $frontendFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    }
    else {
        Write-Host "  ✗ Missing: $file" -ForegroundColor Red
        $allGood = $false
    }
}

# Check documentation
$docFiles = @(
    "README.md",
    "QUICKSTART.md",
    "DOCUMENTATION.md",
    "PROJECT_SUMMARY.md"
)

foreach ($file in $docFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    }
    else {
        Write-Host "  ✗ Missing: $file" -ForegroundColor Red
        $allGood = $false
    }
}

Write-Host ""
Write-Host "Checking Dependencies..." -ForegroundColor Yellow

# Check if backend venv exists
if (Test-Path "backend\venv") {
    Write-Host "  ✓ Backend virtual environment exists" -ForegroundColor Green
}
else {
    Write-Host "  ⚠ Backend virtual environment not created yet" -ForegroundColor Yellow
    Write-Host "    Run: cd backend; python -m venv venv" -ForegroundColor Gray
}

# Check if frontend node_modules exists
if (Test-Path "frontend\node_modules") {
    Write-Host "  ✓ Frontend dependencies installed" -ForegroundColor Green
}
else {
    Write-Host "  ⚠ Frontend dependencies not installed yet" -ForegroundColor Yellow
    Write-Host "    Run: cd frontend; npm install" -ForegroundColor Gray
}

# Check if uploads directory exists
if (Test-Path "backend\uploads") {
    Write-Host "  ✓ Uploads directory exists" -ForegroundColor Green
}
else {
    Write-Host "  ✗ Uploads directory missing" -ForegroundColor Red
    $allGood = $false
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

if ($allGood) {
    Write-Host "✓ All core components verified!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Install dependencies (if not done):" -ForegroundColor White
    Write-Host "     Backend:  cd backend; python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt" -ForegroundColor Gray
    Write-Host "     Frontend: cd frontend; npm install" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Start the system:" -ForegroundColor White
    Write-Host "     Quick:  .\start.ps1" -ForegroundColor Gray
    Write-Host "     Manual: See QUICKSTART.md" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  3. Generate test video:" -ForegroundColor White
    Write-Host "     cd backend; python generate_test_video.py" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  4. Open dashboard:" -ForegroundColor White
    Write-Host "     http://localhost:5173" -ForegroundColor Gray
}
else {
    Write-Host "✗ Some components are missing or incorrect" -ForegroundColor Red
    Write-Host "Please check the errors above and fix them" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "  README.md          - Project overview" -ForegroundColor Gray
Write-Host "  QUICKSTART.md      - Quick setup guide" -ForegroundColor Gray
Write-Host "  DOCUMENTATION.md   - Technical details" -ForegroundColor Gray
Write-Host "  PROJECT_SUMMARY.md - Complete summary" -ForegroundColor Gray
Write-Host ""
