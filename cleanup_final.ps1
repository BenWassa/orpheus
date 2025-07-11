#!/usr/bin/env powershell
# Project Orpheus - Repository Cleanup (PowerShell)
# Removes old directories and files after consolidation

Write-Host "🎵 Project Orpheus - Final Cleanup" -ForegroundColor Cyan
Write-Host "Removing old directories and files..." -ForegroundColor Yellow
Write-Host ""

# Change to project directory
Set-Location "c:\Users\benjamin.haddon\Documents\orpheus"

# Define items to remove
$itemsToRemove = @(
    "src",
    "ui", 
    "data",
    "docs",
    "output",
    "notebooks",
    "main.py",
    "test_setup.py", 
    "test_imports.py",
    "launch_streamlit.bat",
    "run_streamlit.bat",
    "USER_GUIDE.md",
    "QUICK_START.md",
    "SETUP_COMPLETE.md",
    "CHANGELOG.md",
    "DOCUMENTATION_INDEX.md",
    "README_NEW.md",
    "cleanup_repo.py"
)

# Remove each item
foreach ($item in $itemsToRemove) {
    if (Test-Path $item) {
        Write-Host "🗑️  Removing: $item" -ForegroundColor Red
        Remove-Item $item -Recurse -Force
    } else {
        Write-Host "⏭️  Not found: $item" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "✅ Cleanup complete!" -ForegroundColor Green
Write-Host ""

# Show final structure
Write-Host "📁 Final repository structure:" -ForegroundColor Cyan
Get-ChildItem -Directory | Sort-Object Name | ForEach-Object {
    Write-Host "   📂 $($_.Name)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎵 Repository is now clean and organized! 🎵" -ForegroundColor Green
