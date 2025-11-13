# BoogPP Scripts

This directory contains utility scripts for BoogPP installation and setup.

## Available Scripts

### fix_llvmlite_windows.ps1

**Purpose:** Diagnoses and fixes common llvmlite installation issues on Windows.

**Usage:**
```powershell
powershell -ExecutionPolicy Bypass -File scripts\fix_llvmlite_windows.ps1
```

**What it checks:**
1. Python version (must be 3.8-3.12)
2. Python architecture (must be 64-bit)
3. pip version (upgrades if needed)
4. PyPI connectivity
5. llvmlite availability
6. Attempts installation with proper settings

**Common issues it solves:**
- ✓ Detects 32-bit Python (not compatible with llvmlite on Windows)
- ✓ Detects Python 3.13+ (not yet supported by llvmlite)
- ✓ Upgrades outdated pip versions
- ✓ Uses `--prefer-binary` flag to avoid source builds
- ✓ Provides specific error messages and solutions

### install_llvm.ps1

**Purpose:** Automates LLVM installation on Windows for native executable compilation.

**Usage:**
```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_llvm.ps1
```

This script downloads and installs LLVM 14+ with the correct PATH configuration.

## Troubleshooting

If scripts fail to run due to execution policy, use:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Or run with bypass (one-time):
```powershell
powershell -ExecutionPolicy Bypass -File scripts\scriptname.ps1
```
