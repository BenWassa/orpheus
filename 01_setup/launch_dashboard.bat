@echo off
REM Streamlit launcher for Project Orpheus
REM Ensures we're in the correct directory and uses the right Python environment

cd /d "c:\Users\benjamin.haddon\Documents\orpheus"
echo Starting Project Orpheus Streamlit Dashboard...
echo Current directory: %CD%
.\orpheus_venv\Scripts\streamlit.exe run ui/app.py --server.address localhost --server.port 8501
