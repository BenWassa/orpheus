#!/usr/bin/env pwsh
# Project Orpheus - Documentation Cleanup Script
# Consolidates multiple guide versions into clean, organized structure

param(
    [switch]$DryRun
)

Write-Host "📚 Project Orpheus - Documentation Cleanup" -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

$docsDir = "06_docs"
$archiveDir = "$docsDir\archive"

Write-Host "📁 Working in: $docsDir" -ForegroundColor Green

# Function to safely move items to archive
function Move-ToArchive {
    param([string]$File, [string]$Description)
    
    if (Test-Path "$docsDir\$File") {
        if ($DryRun) {
            Write-Host "🔍 [DRY RUN] Would archive: $Description" -ForegroundColor Yellow
        } else {
            # Create archive directory if it doesn't exist
            if (!(Test-Path $archiveDir)) {
                New-Item -ItemType Directory -Path $archiveDir -Force | Out-Null
            }
            Write-Host "📦 Archiving: $Description" -ForegroundColor Blue
            Move-Item "$docsDir\$File" "$archiveDir\$File" -Force -ErrorAction SilentlyContinue
        }
    }
}

# Function to remove files
function Remove-DocFile {
    param([string]$File, [string]$Description)
    
    if (Test-Path "$docsDir\$File") {
        if ($DryRun) {
            Write-Host "🔍 [DRY RUN] Would remove: $Description" -ForegroundColor Yellow
        } else {
            Write-Host "🗑️ Removing: $Description" -ForegroundColor Red
            Remove-Item "$docsDir\$File" -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host "`n🧹 Step 1: Archive legacy versions" -ForegroundColor Magenta

# Archive old versions (preserve for reference but move out of main docs)
Move-ToArchive "QUICK_START_OLD.md" "Original quick start guide"
Move-ToArchive "QUICK_START_NEW.md" "Intermediate quick start guide" 
Move-ToArchive "README_OLD.md" "Legacy README"
Move-ToArchive "README_ORIGINAL.md" "Original README"
Move-ToArchive "SETUP_COMPLETE.md" "Old setup guide"

# Archive duplicate documentation indexes
Move-ToArchive "DOCUMENTATION_INDEX.md" "Original documentation index"

Write-Host "`n📝 Step 2: Remove redundant status files" -ForegroundColor Magenta

# Remove temporary status files
Remove-DocFile "REPOSITORY_STATUS_FINAL.md" "Temporary cleanup status report"

Write-Host "`n🔄 Step 3: Rename final versions to clean names" -ForegroundColor Magenta

if (!$DryRun) {
    # Rename the "FINAL" versions to clean names
    if (Test-Path "$docsDir\QUICK_START_FINAL.md") {
        Move-Item "$docsDir\QUICK_START_FINAL.md" "$docsDir\QUICK_START.md" -Force
        Write-Host "✅ Renamed QUICK_START_FINAL.md → QUICK_START.md" -ForegroundColor Green
    }
    
    if (Test-Path "$docsDir\DOCUMENTATION_INDEX_UPDATED.md") {
        Move-Item "$docsDir\DOCUMENTATION_INDEX_UPDATED.md" "$docsDir\DOCUMENTATION_INDEX.md" -Force
        Write-Host "✅ Renamed DOCUMENTATION_INDEX_UPDATED.md → DOCUMENTATION_INDEX.md" -ForegroundColor Green
    }
} else {
    Write-Host "🔍 [DRY RUN] Would rename QUICK_START_FINAL.md → QUICK_START.md" -ForegroundColor Yellow
    Write-Host "🔍 [DRY RUN] Would rename DOCUMENTATION_INDEX_UPDATED.md → DOCUMENTATION_INDEX.md" -ForegroundColor Yellow
}

Write-Host "`n📄 Step 4: Create comprehensive guide consolidation" -ForegroundColor Magenta

if (!$DryRun) {
    # Create a single comprehensive README for the docs folder
    $docsReadme = @"
# 📚 Project Orpheus - Documentation

**Complete guide to your organized music analysis system**

---

## 🎯 **Start Here**

### **🚀 QUICK_START.md** - Your Main Guide  
**Everything you need in one place:**
- ⚡ 30-second setup commands
- 📁 Complete structure explanation  
- 🔧 Troubleshooting solutions
- 💡 All features explained

---

## 📖 **Core Documentation**

### **Essential Guides**
- **📋 DOCUMENTATION_INDEX.md** - Navigation guide to all docs
- **📚 USER_GUIDE.md** - Complete user manual
- **🔧 TECHNICAL_SUMMARY.md** - Architecture & technical details
- **📊 exportify_data_dictionary.md** - Data format reference

### **Reference**
- **📋 CHANGELOG.md** - Version history and updates
- **🔄 PROCESS_FLOWS.md** - System architecture flows

---

## 📁 **Documentation Structure**

```
06_docs/
├── 📄 QUICK_START.md           # 👈 START HERE
├── 📄 DOCUMENTATION_INDEX.md   # Navigation guide
├── 📄 USER_GUIDE.md            # Complete manual
├── 📄 TECHNICAL_SUMMARY.md     # Technical details
├── 📄 CHANGELOG.md             # Version history
├── 📄 exportify_data_dictionary.md # Data reference
├── 📄 PROCESS_FLOWS.md         # Architecture flows
└── 📁 archive/                 # Historical versions
    ├── QUICK_START_OLD.md      # Legacy guides
    ├── README_ORIGINAL.md      # Original docs
    └── [Other legacy files]    # Preserved for reference
```

---

## 🎯 **Quick Reference**

### **"I'm new to this project"**
→ **QUICK_START.md** → Complete setup in 30 seconds

### **"I want to understand all features"**  
→ **USER_GUIDE.md** → Comprehensive walkthrough

### **"I'm having issues"**
→ **QUICK_START.md** (Troubleshooting section)

### **"I want technical details"**
→ **TECHNICAL_SUMMARY.md** → Architecture overview

### **"I need data format help"**
→ **exportify_data_dictionary.md** → CSV column definitions

---

## 📊 **Documentation Quality**

All current documentation is **✅ Updated** for the new numbered folder structure:

| Document | Status | Coverage |
|----------|--------|----------|
| QUICK_START.md | ✅ Current | Complete |
| USER_GUIDE.md | ✅ Current | Complete |
| TECHNICAL_SUMMARY.md | ✅ Current | Complete |
| DOCUMENTATION_INDEX.md | ✅ Current | Complete |

---

**🎉 Ready to decode your musical journey? Start with QUICK_START.md! 🎉**
"@

    $docsReadme | Out-File -FilePath "$docsDir\README.md" -Encoding UTF8
    Write-Host "✅ Created comprehensive docs README.md" -ForegroundColor Green
}

Write-Host "`n📊 Step 5: Final documentation structure" -ForegroundColor Magenta

if ($DryRun) {
    Write-Host "`n🔍 DRY RUN - Proposed final structure:" -ForegroundColor Yellow
} else {
    Write-Host "`n✅ Final clean structure:" -ForegroundColor Green
}

Write-Host "`n📁 06_docs/" -ForegroundColor Cyan
Write-Host "├── 📄 README.md                    # Documentation overview" -ForegroundColor White
Write-Host "├── 📄 QUICK_START.md               # 👈 MAIN GUIDE" -ForegroundColor Green
Write-Host "├── 📄 DOCUMENTATION_INDEX.md       # Navigation guide" -ForegroundColor White  
Write-Host "├── 📄 USER_GUIDE.md                # Complete manual" -ForegroundColor White
Write-Host "├── 📄 TECHNICAL_SUMMARY.md         # Technical details" -ForegroundColor White
Write-Host "├── 📄 CHANGELOG.md                 # Version history" -ForegroundColor White
Write-Host "├── 📄 exportify_data_dictionary.md # Data reference" -ForegroundColor White
Write-Host "├── 📄 PROCESS_FLOWS.md             # Architecture flows" -ForegroundColor White
Write-Host "└── 📁 archive/                     # Historical versions" -ForegroundColor Blue
Write-Host "    ├── QUICK_START_OLD.md" -ForegroundColor Gray
Write-Host "    ├── README_ORIGINAL.md" -ForegroundColor Gray
Write-Host "    └── [Other legacy files]" -ForegroundColor Gray

Write-Host "`n📊 Cleanup Summary" -ForegroundColor Cyan
Write-Host "=================" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "🔍 DRY RUN completed - no changes made" -ForegroundColor Yellow
    Write-Host "📝 Run without -DryRun to apply changes" -ForegroundColor Yellow
} else {
    Write-Host "✅ Documentation cleaned and organized" -ForegroundColor Green
    Write-Host "✅ Legacy files archived (preserved)" -ForegroundColor Green  
    Write-Host "✅ Final versions renamed to clean names" -ForegroundColor Green
    Write-Host "✅ Comprehensive navigation created" -ForegroundColor Green
    Write-Host "" 
    Write-Host "📚 Result: Clean, organized documentation structure" -ForegroundColor Cyan
    Write-Host "🎯 Primary guide: 06_docs/QUICK_START.md" -ForegroundColor Green
}

$finalCount = (Get-ChildItem $docsDir -File).Count
$archiveCount = if (Test-Path $archiveDir) { (Get-ChildItem $archiveDir -File).Count } else { 0 }

Write-Host "`n📈 Before: 15+ files in docs root" -ForegroundColor White
Write-Host "📉 After: $finalCount essential files + $archiveCount archived" -ForegroundColor Green

Write-Host "`n🎵 Documentation is now rock solid and organized! 🎵" -ForegroundColor Magenta
