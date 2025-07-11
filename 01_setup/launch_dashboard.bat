@echo off
REM ========================================
REM 🎵 Project Orpheus - PowerShell Launcher
REM ========================================

cd /d "c:\Users\benjamin.haddon\Documents\orpheus"

echo.
echo ========================================
echo 🎵 Project Orpheus Dashboard Launcher
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "orpheus_venv\Scripts\streamlit.exe" (
    echo ❌ Virtual environment not found!
    echo Please run setup first.
    pause
    exit /b 1
)

REM Check if core modules exist
if not exist "02_core\data_processor.py" (
    echo ❌ Core modules not found!
    echo Please ensure project structure is correct.
    pause
    exit /b 1
)

echo ✅ Environment check passed
echo 🚀 Starting Streamlit dashboard...
echo.
echo 📍 Dashboard will open at: http://localhost:8501
echo 🔧 Press Ctrl+C to stop the server
echo.

REM Start Streamlit with proper error handling
.\orpheus_venv\Scripts\streamlit.exe run 03_interface\streamlit_app.py --server.address localhost --server.port 8501

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ Error starting dashboard!
    echo 💡 Try these troubleshooting steps:
    echo 1. Ensure you're in the project root directory
    echo 2. Check that all dependencies are installed
    echo 3. Verify the virtual environment is working
    echo.
    pause
)

echo.
echo 👋 Dashboard closed. Thanks for using Project Orpheus!
pause
