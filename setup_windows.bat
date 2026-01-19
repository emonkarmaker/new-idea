@echo off
REM Windows Setup Script for Arabic Speech-to-Text
REM This script sets up a clean virtual environment

echo ========================================
echo Arabic Speech-to-Text Setup
echo ========================================
echo.

REM Check Python installation
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or 3.12 from python.org
    pause
    exit /b 1
)

echo.
echo Step 1: Creating virtual environment...
python -m venv venv

if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Virtual environment created successfully!
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 3: Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

echo.
echo Step 4: Installing dependencies...
pip install sounddevice>=0.4.6
pip install numpy>=1.26.0
pip install scipy>=1.11.4
pip install openai>=1.12.0
pip install python-dotenv>=1.0.0

echo.
echo Step 5: Setting up environment file...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo Created .env file from template
        echo IMPORTANT: Edit .env and add your OpenAI API key!
    ) else (
        echo # OpenAI API Configuration > .env
        echo OPENAI_API_KEY=your_openai_api_key_here >> .env
        echo Created .env file - IMPORTANT: Edit it and add your API key!
    )
) else (
    echo .env file already exists
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To use the application:
echo   1. Run: venv\Scripts\activate.bat
echo   2. Run: python optimized_arabic_whisper.py
echo.
echo To test microphone:
echo   1. Run: venv\Scripts\activate.bat
echo   2. Run: python test_microphone.py
echo.
pause
