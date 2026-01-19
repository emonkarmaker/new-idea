# PowerShell Setup Script for Arabic Speech-to-Text
# Run this in PowerShell (not Command Prompt)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Arabic Speech-to-Text Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host $pythonVersion -ForegroundColor Green

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.11 or 3.12 from python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 1: Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

if (!(Test-Path "venv\Scripts\activate.ps1")) {
    Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Virtual environment created successfully!" -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Step 3: Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel

Write-Host ""
Write-Host "Step 4: Installing dependencies..." -ForegroundColor Yellow
Write-Host "  - Installing sounddevice..." -ForegroundColor Gray
pip install sounddevice

Write-Host "  - Installing numpy..." -ForegroundColor Gray
pip install "numpy>=1.26.0"

Write-Host "  - Installing scipy..." -ForegroundColor Gray
pip install scipy

Write-Host "  - Installing openai..." -ForegroundColor Gray
pip install openai

Write-Host "  - Installing python-dotenv..." -ForegroundColor Gray
pip install python-dotenv

Write-Host ""
Write-Host "Step 5: Setting up environment file..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item .env.example .env
        Write-Host "✓ Created .env file from template" -ForegroundColor Green
        Write-Host "⚠ IMPORTANT: Edit .env and add your OpenAI API key!" -ForegroundColor Yellow
    } else {
        "# OpenAI API Configuration`nOPENAI_API_KEY=your_openai_api_key_here" | Out-File -FilePath .env -Encoding UTF8
        Write-Host "✓ Created .env file" -ForegroundColor Green
        Write-Host "⚠ IMPORTANT: Edit .env and add your API key!" -ForegroundColor Yellow
    }
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠ NEXT STEP: Configure your API key" -ForegroundColor Yellow
Write-Host "  1. Open .env file in a text editor" -ForegroundColor White
Write-Host "  2. Replace 'your_openai_api_key_here' with your actual key" -ForegroundColor White
Write-Host "  3. Save the file" -ForegroundColor White
Write-Host ""
Write-Host "To use the application:" -ForegroundColor Yellow
Write-Host "  1. Run: venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  2. Run: python optimized_arabic_whisper.py" -ForegroundColor White
Write-Host ""
Write-Host "To test microphone:" -ForegroundColor Yellow
Write-Host "  1. Run: venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  2. Run: python test_microphone.py" -ForegroundColor White
Write-Host ""
Write-Host "Note: If you get execution policy errors, run:" -ForegroundColor Yellow
Write-Host "  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
