@echo off 
REM Project Orpheus - Quick Launch Script 
REM Run this from the project root directory 
 
echo 🎵 Project Orpheus - Quick Launch 
echo ================================ 
 
cd /d "%~dp0" 
echo 📁 Project directory: %CD% 
 
echo 🔧 Testing setup... 
.\orpheus_venv\Scripts\python.exe 01_setup\test_setup.py 
 
if errorlevel 1 ( 
    echo ❌ Setup test failed! Check your environment. 
    pause 
    exit /b 1 
) 
 
echo 🚀 Launching Streamlit dashboard... 
echo 🌐 Opening at: http://localhost:8501 
echo 💡 Press Ctrl+C to stop the server 
 
.\orpheus_venv\Scripts\streamlit.exe run 03_interface\streamlit_app.py --server.address localhost --server.port 8501 
 
pause 
