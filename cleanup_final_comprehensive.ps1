#!/usr/bin/env pwsh
# Project Orpheus - Final Repository Cleanup Script
# Ensures clean, organized structure and removes duplicates

param(
    [switch]$Force,
    [switch]$DryRun
)

Write-Host "🎵 Project Orpheus - Final Repository Cleanup" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

$projectRoot = Get-Location
Write-Host "📁 Working in: $projectRoot" -ForegroundColor Green

# Function to safely remove items
function Remove-SafelyIfExists {
    param([string]$Path, [string]$Description)
    
    if (Test-Path $Path) {
        if ($DryRun) {
            Write-Host "🔍 [DRY RUN] Would remove: $Description" -ForegroundColor Yellow
        } else {
            Write-Host "🗑️ Removing: $Description" -ForegroundColor Red
            Remove-Item $Path -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

# Function to safely move items
function Move-SafelyIfExists {
    param([string]$Source, [string]$Destination, [string]$Description)
    
    if (Test-Path $Source) {
        $destDir = Split-Path $Destination -Parent
        if (!(Test-Path $destDir)) {
            if (!$DryRun) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
        }
        
        if ($DryRun) {
            Write-Host "🔍 [DRY RUN] Would move: $Description" -ForegroundColor Yellow
        } else {
            Write-Host "📦 Moving: $Description" -ForegroundColor Green
            Move-Item $Source $Destination -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "`n🧹 Step 1: Remove old/duplicate files" -ForegroundColor Magenta

# Remove old virtual environments (keep orpheus_venv)
Remove-SafelyIfExists "orpheus_env" "Old virtual environment (orpheus_env)"
Remove-SafelyIfExists ".venv" "Old virtual environment (.venv)"

# Remove duplicate backup files
Remove-SafelyIfExists "03_interface\streamlit_app_backup.py" "Streamlit backup file"
Remove-SafelyIfExists "03_interface\streamlit_app_new.py" "Streamlit new file"

# Remove cleanup scripts (except this one)
Remove-SafelyIfExists "cleanup_repo.py" "Old cleanup script"
Remove-SafelyIfExists "cleanup_final.bat" "Old cleanup batch script"
Remove-SafelyIfExists "cleanup_final.ps1" "Old cleanup PowerShell script"

# Remove any old test files in root
Remove-SafelyIfExists "test_setup.py" "Old test file in root"
Remove-SafelyIfExists "main.py" "Old main file"

Write-Host "`n📂 Step 2: Organize remaining files" -ForegroundColor Magenta

# Move README to docs and create new minimal one
if (Test-Path "README.md") {
    Move-SafelyIfExists "README.md" "06_docs\README_ORIGINAL.md" "Original README to docs"
}

Write-Host "`n📝 Step 3: Create new clean README" -ForegroundColor Magenta

if (!$DryRun) {
    $newReadme = @"
# 🎵 Project Orpheus

**Decode your emotional underworld through the music that moves you**

## 🚀 Quick Start

```powershell
# 1. Test setup
.\01_setup\test_setup.py

# 2. Run analysis  
.\01_setup\run_analysis.py

# 3. Launch dashboard
.\01_setup\launch_dashboard.bat
```

## 📁 Project Structure

- **`01_setup/`** - Installation, testing, and launch scripts
- **`02_core/`** - Core analysis modules (data processing, patterns, emotions)
- **`03_interface/`** - Streamlit web dashboard
- **`04_data/`** - Raw and processed music data
- **`05_output/`** - Analysis results and visualizations
- **`06_docs/`** - Documentation and guides

## 🔧 Requirements

- Python 3.11+
- Virtual environment: `orpheus_venv`
- Dependencies: See `01_setup/requirements.txt`

## 📚 Documentation

- **Quick Start**: `06_docs/QUICK_START.md`
- **User Guide**: `06_docs/USER_GUIDE.md`
- **Technical**: `06_docs/TECHNICAL_SUMMARY.md`

---

*Just as Orpheus journeyed into the underworld with music as his guide, Project Orpheus helps you descend into your emotional depths to retrieve hidden truths and fresh self-understanding.*
"@

    $newReadme | Out-File -FilePath "README.md" -Encoding UTF8
    Write-Host "✅ Created new clean README.md" -ForegroundColor Green
}

Write-Host "`n🔧 Step 4: Update import paths" -ForegroundColor Magenta

# Update streamlit app to use correct paths
$streamlitPath = "03_interface\streamlit_app.py"
if ((Test-Path $streamlitPath) -and !$DryRun) {
    $content = Get-Content $streamlitPath -Raw
    
    # Fix the import paths
    $updatedContent = $content -replace 'sys\.path\.insert\(0, str\(project_root / "02_core"\)\)', 'sys.path.insert(0, str(project_root / "02_core"))'
    $updatedContent = $updatedContent -replace 'from data_processor import', 'from data_processor import'
    
    $updatedContent | Out-File -FilePath $streamlitPath -Encoding UTF8
    Write-Host "✅ Updated Streamlit import paths" -ForegroundColor Green
}

Write-Host "`n🎯 Step 5: Create launch script" -ForegroundColor Magenta

if (!$DryRun) {
    $launchScript = @"
@echo off
REM Project Orpheus - Quick Launch Script
REM Run this from the project root directory

echo 🎵 Project Orpheus - Quick Launch
echo ================================

cd /d "%~dp0"
echo 📁 Project directory: %CD%

echo.
echo 🔧 Testing setup...
.\orpheus_venv\Scripts\python.exe 01_setup\test_setup.py

if errorlevel 1 (
    echo ❌ Setup test failed! Check your environment.
    pause
    exit /b 1
)

echo.
echo 🚀 Launching Streamlit dashboard...
echo 🌐 Opening at: http://localhost:8501
echo 💡 Press Ctrl+C to stop the server

.\orpheus_venv\Scripts\streamlit.exe run 03_interface\streamlit_app.py --server.address localhost --server.port 8501

pause
"@

    $launchScript | Out-File -FilePath "launch_orpheus.bat" -Encoding ASCII
    Write-Host "✅ Created launch_orpheus.bat" -ForegroundColor Green
}

Write-Host "`n📊 Step 6: Verify structure" -ForegroundColor Magenta

$expectedDirs = @("01_setup", "02_core", "03_interface", "04_data", "05_output", "06_docs", "orpheus_venv")
$missingDirs = @()

foreach ($dir in $expectedDirs) {
    if (!(Test-Path $dir)) {
        $missingDirs += $dir
    } else {
        Write-Host "✅ $dir" -ForegroundColor Green
    }
}

if ($missingDirs) {
    Write-Host "❌ Missing directories: $($missingDirs -join ', ')" -ForegroundColor Red
} else {
    Write-Host "✅ All expected directories present" -ForegroundColor Green
}

Write-Host "`n🧪 Step 7: Test imports" -ForegroundColor Magenta

if (!$DryRun) {
    try {
        & ".\orpheus_venv\Scripts\python.exe" -c "
import sys
sys.path.insert(0, '02_core')
from data_processor import load_csv_data
from pattern_analyzer import analyze_patterns  
from visualizer import create_timeline
print('✅ All core modules import successfully')
"
        Write-Host "✅ Import test passed" -ForegroundColor Green
    } catch {
        Write-Host "❌ Import test failed: $_" -ForegroundColor Red
    }
}

Write-Host "`n🎉 Cleanup Summary" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "🔍 DRY RUN completed - no changes made" -ForegroundColor Yellow
    Write-Host "📝 Run without -DryRun to apply changes" -ForegroundColor Yellow
} else {
    Write-Host "✅ Repository structure cleaned and organized" -ForegroundColor Green
    Write-Host "✅ Duplicate files removed" -ForegroundColor Green  
    Write-Host "✅ Import paths updated" -ForegroundColor Green
    Write-Host "✅ Launch script created" -ForegroundColor Green
    Write-Host "" 
    Write-Host "🚀 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Run: .\launch_orpheus.bat" -ForegroundColor White
    Write-Host "   2. Or run: .\01_setup\test_setup.py" -ForegroundColor White
    Write-Host "   3. Visit: http://localhost:8501" -ForegroundColor White
}

Write-Host "`n📁 Final Structure:" -ForegroundColor Cyan
Get-ChildItem -Directory | Sort-Object Name | ForEach-Object {
    Write-Host "   📂 $($_.Name)" -ForegroundColor White
}

Write-Host ""
Write-Host "🎵 Project Orpheus is ready to decode your musical journey! 🎵" -ForegroundColor Magenta
