#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎵 Project Orpheus - Repository Cleanup Script

Consolidates duplicate directories and files into the new organized structure.
Run this once to clean up the repository properly.
"""

import os
import shutil
import sys
from pathlib import Path

def main():
    """Clean up the repository structure"""
    
    print("🎵" * 50)
    print("PROJECT ORPHEUS - REPOSITORY CLEANUP")
    print("🎵" * 50)
    print()
    
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    print(f"📁 Working in: {project_root}")
    print()
    
    # Step 1: Ensure new directory structure exists
    print("📂 Creating new directory structure...")
    new_dirs = [
        "01_setup",
        "02_core", 
        "03_interface",
        "04_data/raw",
        "04_data/processed", 
        "04_data/temp",
        "05_output/visualizations",
        "05_output/reports",
        "05_output/exports",
        "06_docs"
    ]
    
    for dir_path in new_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ {dir_path}")
    
    print()
    
    # Step 2: Move core modules (preserve working src/ code)
    print("🔧 Moving core modules...")
    
    # Copy working modules from src/ to 02_core/
    src_files = {
        "src/config.py": "02_core/config.py",
        "src/data_processing.py": "02_core/data_processor.py", 
        "src/pattern_analysis.py": "02_core/pattern_analyzer.py",
        "src/emotion_analysis.py": "02_core/emotion_analyzer.py",
        "src/visualization.py": "02_core/visualizer.py"
    }
    
    for src_file, dest_file in src_files.items():
        if Path(src_file).exists():
            print(f"📄 {src_file} → {dest_file}")
            shutil.copy2(src_file, dest_file)
        else:
            print(f"⚠️  Missing: {src_file}")
    
    print()
    
    # Step 3: Consolidate data directories  
    print("📊 Consolidating data...")
    
    # Move all CSV files to 04_data/raw/
    data_sources = ["data/raw", "04_data/raw", "."]
    target_data_dir = Path("04_data/raw")
    
    for source_dir in data_sources:
        source_path = Path(source_dir)
        if source_path.exists():
            for csv_file in source_path.glob("*.csv"):
                dest_file = target_data_dir / csv_file.name
                if not dest_file.exists():
                    print(f"📄 {csv_file} → {dest_file}")
                    shutil.copy2(csv_file, dest_file)
                else:
                    print(f"⏭️  Already exists: {dest_file.name}")
    
    # Move processed data
    old_processed = Path("data/processed")
    new_processed = Path("04_data/processed")
    if old_processed.exists():
        for file in old_processed.glob("*"):
            dest_file = new_processed / file.name
            if not dest_file.exists() and file.is_file():
                print(f"📄 {file} → {dest_file}")
                shutil.copy2(file, dest_file)
    
    print()
    
    # Step 4: Move interface files
    print("🌐 Moving interface files...")
    
    interface_files = [
        ("ui/app.py", "03_interface/streamlit_app.py"),
        ("ui/app_fixed.py", "03_interface/streamlit_app_backup.py")
    ]
    
    for src_file, dest_file in interface_files:
        if Path(src_file).exists():
            print(f"📄 {src_file} → {dest_file}")
            shutil.copy2(src_file, dest_file)
    
    print()
    
    # Step 5: Move setup and utility files
    print("⚙️  Moving setup files...")
    
    setup_files = [
        ("main.py", "01_setup/run_analysis.py"),
        ("test_setup.py", "01_setup/test_setup.py"),
        ("test_imports.py", "01_setup/test_imports.py"),
        ("launch_streamlit.bat", "01_setup/launch_dashboard.bat"),
        ("run_streamlit.bat", "01_setup/launch_dashboard_simple.bat")
    ]
    
    for src_file, dest_file in setup_files:
        if Path(src_file).exists():
            print(f"📄 {src_file} → {dest_file}")
            shutil.copy2(src_file, dest_file)
    
    print()
    
    # Step 6: Move documentation
    print("📚 Moving documentation...")
    
    doc_files = [
        ("README.md", "06_docs/README_OLD.md"),
        ("README_NEW.md", "README.md"),
        ("USER_GUIDE.md", "06_docs/USER_GUIDE.md"),
        ("QUICK_START.md", "06_docs/QUICK_START_OLD.md"), 
        ("SETUP_COMPLETE.md", "06_docs/SETUP_COMPLETE.md"),
        ("CHANGELOG.md", "06_docs/CHANGELOG.md"),
        ("DOCUMENTATION_INDEX.md", "06_docs/DOCUMENTATION_INDEX.md")
    ]
    
    for src_file, dest_file in doc_files:
        if Path(src_file).exists():
            print(f"📄 {src_file} → {dest_file}")
            shutil.copy2(src_file, dest_file)
    
    # Move docs directory contents
    if Path("docs").exists():
        for file in Path("docs").glob("*"):
            if file.is_file():
                dest_file = Path("06_docs") / file.name
                if not dest_file.exists():
                    print(f"📄 {file} → {dest_file}")
                    shutil.copy2(file, dest_file)
    
    print()
    
    # Step 7: Move output files
    print("📈 Moving output files...")
    
    if Path("output").exists():
        for subdir in ["visualizations", "reports", "exports"]:
            old_dir = Path("output") / subdir
            new_dir = Path("05_output") / subdir
            if old_dir.exists():
                for file in old_dir.glob("*"):
                    if file.is_file():
                        dest_file = new_dir / file.name
                        if not dest_file.exists():
                            print(f"📄 {file} → {dest_file}")
                            shutil.copy2(file, dest_file)
    
    print()
    
    # Step 8: Create summary of what to remove
    print("🗑️  Files/directories that can be safely removed:")
    print("   (Review before deleting)")
    print()
    
    old_items = [
        "src/",
        "ui/", 
        "data/",
        "docs/",
        "output/",
        "notebooks/",
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
        "README_NEW.md"
    ]
    
    for item in old_items:
        if Path(item).exists():
            print(f"🗑️  {item}")
    
    print()
    print("✅ CLEANUP COMPLETE!")
    print()
    print("📋 Next steps:")
    print("1. Review the file moves above")
    print("2. Test the new structure: python 01_setup/test_setup.py")
    print("3. If working, remove old directories listed above")
    print("4. Update any remaining import paths")
    print()
    print("🎵 Your repository is now organized! 🎵")

if __name__ == "__main__":
    main()
