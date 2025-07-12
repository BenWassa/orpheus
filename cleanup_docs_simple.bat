@echo off
REM Project Orpheus - Documentation Cleanup Script
REM Consolidates multiple guide versions into clean structure

echo 📚 Project Orpheus - Documentation Cleanup
echo ===========================================

cd /d "%~dp0\06_docs"
echo 📁 Working in: %CD%

echo.
echo 🧹 Step 1: Create archive directory
if not exist "archive" mkdir "archive"

echo.
echo 📦 Step 2: Archive legacy versions
if exist "QUICK_START_OLD.md" (
    echo   📦 Archiving: QUICK_START_OLD.md
    move "QUICK_START_OLD.md" "archive\"
)

if exist "QUICK_START_NEW.md" (
    echo   📦 Archiving: QUICK_START_NEW.md
    move "QUICK_START_NEW.md" "archive\"
)

if exist "README_OLD.md" (
    echo   📦 Archiving: README_OLD.md
    move "README_OLD.md" "archive\"
)

if exist "README_ORIGINAL.md" (
    echo   📦 Archiving: README_ORIGINAL.md
    move "README_ORIGINAL.md" "archive\"
)

if exist "SETUP_COMPLETE.md" (
    echo   📦 Archiving: SETUP_COMPLETE.md
    move "SETUP_COMPLETE.md" "archive\"
)

if exist "DOCUMENTATION_INDEX.md" (
    echo   📦 Archiving: DOCUMENTATION_INDEX.md (original)
    move "DOCUMENTATION_INDEX.md" "archive\DOCUMENTATION_INDEX_ORIGINAL.md"
)

echo.
echo 🗑️ Step 3: Remove temporary files
if exist "REPOSITORY_STATUS_FINAL.md" (
    echo   🗑️ Removing: REPOSITORY_STATUS_FINAL.md
    del "REPOSITORY_STATUS_FINAL.md"
)

echo.
echo 🔄 Step 4: Rename final versions to clean names
if exist "QUICK_START_FINAL.md" (
    if exist "QUICK_START.md" del "QUICK_START.md"
    echo   ✅ Renaming: QUICK_START_FINAL.md → QUICK_START.md
    move "QUICK_START_FINAL.md" "QUICK_START.md"
)

if exist "DOCUMENTATION_INDEX_UPDATED.md" (
    echo   ✅ Renaming: DOCUMENTATION_INDEX_UPDATED.md → DOCUMENTATION_INDEX.md
    move "DOCUMENTATION_INDEX_UPDATED.md" "DOCUMENTATION_INDEX.md"
)

echo.
echo 📄 Step 5: Create docs README
echo # 📚 Project Orpheus - Documentation > README.md
echo. >> README.md
echo **Complete guide to your organized music analysis system** >> README.md
echo. >> README.md
echo ## 🎯 **Start Here** >> README.md
echo. >> README.md
echo ### **🚀 QUICK_START.md** - Your Main Guide >> README.md
echo **Everything you need in one place:** >> README.md
echo - ⚡ 30-second setup commands >> README.md
echo - 📁 Complete structure explanation >> README.md
echo - 🔧 Troubleshooting solutions >> README.md
echo - 💡 All features explained >> README.md
echo. >> README.md
echo ## 📖 **Core Documentation** >> README.md
echo. >> README.md
echo ### **Essential Guides** >> README.md
echo - **📋 DOCUMENTATION_INDEX.md** - Navigation guide >> README.md
echo - **📚 USER_GUIDE.md** - Complete user manual >> README.md
echo - **🔧 TECHNICAL_SUMMARY.md** - Architecture ^& technical details >> README.md
echo - **📊 exportify_data_dictionary.md** - Data format reference >> README.md
echo. >> README.md
echo ### **Reference** >> README.md
echo - **📋 CHANGELOG.md** - Version history and updates >> README.md
echo - **🔄 PROCESS_FLOWS.md** - System architecture flows >> README.md
echo. >> README.md
echo ## 📁 **Final Clean Structure** >> README.md
echo. >> README.md
echo ``` >> README.md
echo 06_docs/ >> README.md
echo ├── 📄 README.md                    # Documentation overview >> README.md
echo ├── 📄 QUICK_START.md               # 👈 MAIN GUIDE >> README.md
echo ├── 📄 DOCUMENTATION_INDEX.md       # Navigation guide >> README.md
echo ├── 📄 USER_GUIDE.md                # Complete manual >> README.md
echo ├── 📄 TECHNICAL_SUMMARY.md         # Technical details >> README.md
echo ├── 📄 CHANGELOG.md                 # Version history >> README.md
echo ├── 📄 exportify_data_dictionary.md # Data reference >> README.md
echo ├── 📄 PROCESS_FLOWS.md             # Architecture flows >> README.md
echo └── 📁 archive/                     # Historical versions >> README.md
echo ``` >> README.md
echo. >> README.md
echo **🎉 Ready to decode your musical journey? Start with QUICK_START.md! 🎉** >> README.md

echo.
echo 📊 Final clean structure:
dir /b
echo.
echo 📁 archive/:
dir /b archive

echo.
echo ✅ Documentation cleanup complete!
echo 📚 Clean, organized documentation structure created
echo 🎯 Primary guide: QUICK_START.md
echo 📁 Legacy files preserved in archive/ folder

echo.
echo 🎵 Documentation is now rock solid! 🎵

cd /d "%~dp0"
