@echo off
REM Streamlit launcher for Project Orpheus
REM Updated for new organized structure

cd /d "c:\Users\benjamin.haddon\Documents\orpheus"
echo Starting Project Orpheus Streamlit Dashboard...
echo Current directory: %CD%
echo.
echo 🔧 Running quick health check...
.\orpheus_venv\Scripts\python.exe 01_setup\test_setup.py

if errorlevel 1 (
    echo ❌ Health check failed! See errors above.
    pause
    exit /b 1
)

echo.
echo 🚀 Launching dashboard...
.\orpheus_venv\Scripts\streamlit.exe run 03_interface\streamlit_app.py --server.address localhost --server.port 8501
