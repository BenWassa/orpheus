@echo off
cd /d "c:\Users\benjamin.haddon\Documents\orpheus"
echo Starting Project Orpheus Streamlit Dashboard...
echo Current directory: %CD%
echo.
.\orpheus_venv\Scripts\streamlit.exe run ui/app.py
pause
