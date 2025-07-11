@echo off
REM Project Orpheus - Final Repository Cleanup
REM Removes duplicates and organizes structure

echo 🎵 Project Orpheus - Final Repository Cleanup
echo =============================================

cd /d "%~dp0"
echo 📁 Working in: %CD%

echo.
echo 🧹 Step 1: Remove old/duplicate files
echo =====================================

REM Remove old virtual environments (keep orpheus_venv)
if exist "orpheus_env" (
    echo 🗑️ Removing: orpheus_env
    rmdir /s /q "orpheus_env"
)

if exist ".venv" (
    echo 🗑️ Removing: .venv
    rmdir /s /q ".venv"
)

REM Remove duplicate backup files
if exist "03_interface\streamlit_app_backup.py" (
    echo 🗑️ Removing: streamlit_app_backup.py
    del "03_interface\streamlit_app_backup.py"
)

if exist "03_interface\streamlit_app_new.py" (
    echo 🗑️ Removing: streamlit_app_new.py
    del "03_interface\streamlit_app_new.py"
)

REM Remove old cleanup scripts
if exist "cleanup_repo.py" (
    echo 🗑️ Removing: cleanup_repo.py
    del "cleanup_repo.py"
)

if exist "cleanup_final.bat" (
    echo 🗑️ Removing: cleanup_final.bat
    del "cleanup_final.bat"
)

if exist "cleanup_final.ps1" (
    echo 🗑️ Removing: cleanup_final.ps1
    del "cleanup_final.ps1"
)

REM Remove any old test files in root
if exist "test_setup.py" (
    echo 🗑️ Removing: old test_setup.py
    del "test_setup.py"
)

if exist "main.py" (
    echo 🗑️ Removing: old main.py
    del "main.py"
)

echo.
echo 📂 Step 2: Organize files
echo =========================

REM Move original README to docs
if exist "README.md" (
    echo 📦 Moving: README.md to docs
    move "README.md" "06_docs\README_ORIGINAL.md"
)

echo.
echo 📝 Step 3: Create new README
echo ============================

echo # 🎵 Project Orpheus > README.md
echo. >> README.md
echo **Decode your emotional underworld through the music that moves you** >> README.md
echo. >> README.md
echo ## 🚀 Quick Start >> README.md
echo. >> README.md
echo ```powershell >> README.md
echo # 1. Test setup >> README.md
echo .\01_setup\test_setup.py >> README.md
echo. >> README.md
echo # 2. Run analysis >> README.md
echo .\01_setup\run_analysis.py >> README.md
echo. >> README.md
echo # 3. Launch dashboard >> README.md
echo .\launch_orpheus.bat >> README.md
echo ``` >> README.md
echo. >> README.md
echo ## 📁 Project Structure >> README.md
echo. >> README.md
echo - **`01_setup/`** - Installation, testing, and launch scripts >> README.md
echo - **`02_core/`** - Core analysis modules (data processing, patterns, emotions) >> README.md
echo - **`03_interface/`** - Streamlit web dashboard >> README.md
echo - **`04_data/`** - Raw and processed music data >> README.md
echo - **`05_output/`** - Analysis results and visualizations >> README.md
echo - **`06_docs/`** - Documentation and guides >> README.md

echo.
echo 🚀 Step 4: Create launch script
echo ===============================

echo @echo off > launch_orpheus.bat
echo REM Project Orpheus - Quick Launch Script >> launch_orpheus.bat
echo REM Run this from the project root directory >> launch_orpheus.bat
echo. >> launch_orpheus.bat
echo echo 🎵 Project Orpheus - Quick Launch >> launch_orpheus.bat
echo echo ================================ >> launch_orpheus.bat
echo. >> launch_orpheus.bat
echo cd /d "%%~dp0" >> launch_orpheus.bat
echo echo 📁 Project directory: %%CD%% >> launch_orpheus.bat
echo. >> launch_orpheus.bat
echo echo 🔧 Testing setup... >> launch_orpheus.bat
echo .\orpheus_venv\Scripts\python.exe 01_setup\test_setup.py >> launch_orpheus.bat
echo. >> launch_orpheus.bat
echo if errorlevel 1 ( >> launch_orpheus.bat
echo     echo ❌ Setup test failed! Check your environment. >> launch_orpheus.bat
echo     pause >> launch_orpheus.bat
echo     exit /b 1 >> launch_orpheus.bat
echo ^) >> launch_orpheus.bat
echo. >> launch_orpheus.bat
echo echo 🚀 Launching Streamlit dashboard... >> launch_orpheus.bat
echo echo 🌐 Opening at: http://localhost:8501 >> launch_orpheus.bat
echo echo 💡 Press Ctrl+C to stop the server >> launch_orpheus.bat
echo. >> launch_orpheus.bat
echo .\orpheus_venv\Scripts\streamlit.exe run 03_interface\streamlit_app.py --server.address localhost --server.port 8501 >> launch_orpheus.bat
echo. >> launch_orpheus.bat
echo pause >> launch_orpheus.bat

echo.
echo 📊 Step 5: Verify structure
echo ===========================

echo ✅ Checking directories:
if exist "01_setup" echo   ✅ 01_setup
if exist "02_core" echo   ✅ 02_core
if exist "03_interface" echo   ✅ 03_interface
if exist "04_data" echo   ✅ 04_data
if exist "05_output" echo   ✅ 05_output
if exist "06_docs" echo   ✅ 06_docs
if exist "orpheus_venv" echo   ✅ orpheus_venv

echo.
echo 🧪 Step 6: Test imports
echo =======================

echo Testing core module imports...
.\orpheus_venv\Scripts\python.exe -c "import sys; sys.path.insert(0, '02_core'); from data_processor import load_csv_data; from pattern_analyzer import analyze_patterns; from visualizer import create_timeline; print('✅ All core modules import successfully')"

if errorlevel 1 (
    echo ❌ Import test failed
) else (
    echo ✅ Import test passed
)

echo.
echo 🎉 Cleanup Complete!
echo ===================
echo ✅ Repository structure cleaned and organized
echo ✅ Duplicate files removed
echo ✅ Launch script created
echo.
echo 🚀 Next steps:
echo    1. Run: .\launch_orpheus.bat
echo    2. Or run: .\01_setup\test_setup.py  
echo    3. Visit: http://localhost:8501
echo.
echo 📁 Final Structure:
dir /ad /b | findstr /v "__pycache__"

echo.
echo 🎵 Project Orpheus is ready to decode your musical journey! 🎵

REM Clean up this script
del "%~f0"
