@echo off
REM Project Orpheus - Final Cleanup
REM Removes old directories and files after consolidation

echo 🎵 Project Orpheus - Final Cleanup
echo Removing old directories and files...
echo.

cd /d "c:\Users\benjamin.haddon\Documents\orpheus"

REM Remove old directories
if exist "src" (
    echo 🗑️ Removing: src
    rmdir /s /q "src"
)

if exist "ui" (
    echo 🗑️ Removing: ui  
    rmdir /s /q "ui"
)

if exist "data" (
    echo 🗑️ Removing: data
    rmdir /s /q "data"
)

if exist "docs" (
    echo 🗑️ Removing: docs
    rmdir /s /q "docs"
)

if exist "output" (
    echo 🗑️ Removing: output
    rmdir /s /q "output"
)

if exist "notebooks" (
    echo 🗑️ Removing: notebooks
    rmdir /s /q "notebooks"
)

REM Remove old files
if exist "main.py" (
    echo 🗑️ Removing: main.py
    del "main.py"
)

if exist "test_setup.py" (
    echo 🗑️ Removing: test_setup.py
    del "test_setup.py"
)

if exist "test_imports.py" (
    echo 🗑️ Removing: test_imports.py
    del "test_imports.py"
)

if exist "launch_streamlit.bat" (
    echo 🗑️ Removing: launch_streamlit.bat
    del "launch_streamlit.bat"
)

if exist "run_streamlit.bat" (
    echo 🗑️ Removing: run_streamlit.bat
    del "run_streamlit.bat"
)

if exist "USER_GUIDE.md" (
    echo 🗑️ Removing: USER_GUIDE.md
    del "USER_GUIDE.md"
)

if exist "QUICK_START.md" (
    echo 🗑️ Removing: QUICK_START.md
    del "QUICK_START.md"
)

if exist "SETUP_COMPLETE.md" (
    echo 🗑️ Removing: SETUP_COMPLETE.md
    del "SETUP_COMPLETE.md"
)

if exist "CHANGELOG.md" (
    echo 🗑️ Removing: CHANGELOG.md
    del "CHANGELOG.md"
)

if exist "DOCUMENTATION_INDEX.md" (
    echo 🗑️ Removing: DOCUMENTATION_INDEX.md
    del "DOCUMENTATION_INDEX.md"
)

if exist "README_NEW.md" (
    echo 🗑️ Removing: README_NEW.md
    del "README_NEW.md"
)

if exist "cleanup_repo.py" (
    echo 🗑️ Removing: cleanup_repo.py
    del "cleanup_repo.py"
)

echo.
echo ✅ Cleanup complete!
echo.
echo 📁 Final repository structure:
dir /ad /b | sort

echo.
echo 🎵 Repository is now clean and organized! 🎵
