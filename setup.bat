@echo off
REM Setup script for Windows

echo Setting up OpenMetadata Polaris Connector...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -e ".[dev]"

REM Install pre-commit hooks
echo Setting up pre-commit hooks...
pre-commit install

echo.
echo Setup complete!
echo.
echo To activate the virtual environment, run:
echo   venv\Scripts\activate.bat
echo.
echo To start Polaris with Docker, run:
echo   docker-compose up -d polaris
echo.
echo To populate sample data, run:
echo   python scripts\setup_sample_data.py