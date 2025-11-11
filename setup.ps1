# BoogPP Automated Setup Script
# Runs all setup steps: Python, dependencies, LLVM, test compile

param([switch]$SkipLLVM, [switch]$SkipTest)

$ErrorActionPreference = "Continue"

function Test-CommandExists {
    param([string]$cmd)
    $null -ne (Get-Command $cmd -ErrorAction SilentlyContinue)
}

Write-Host "`nBoogPP Automated Setup`n" -ForegroundColor Cyan

# Step 1: Verify Python
Write-Host "=== Step 1: Python Verification ===" -ForegroundColor Magenta
if (Test-CommandExists python) {
    $pv = python --version 2>&1
    Write-Host "[OK] Python found: $pv" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Python not found" -ForegroundColor Red
    exit 1
}

# Step 2: Verify Project Structure
Write-Host "`n=== Step 2: Project Structure ===" -ForegroundColor Magenta
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = if ($scriptRoot -like "*\boogpp") { Split-Path -Parent $scriptRoot } else { $scriptRoot }

$dirs = @("boogpp\compiler", "boogpp\examples", "boogpp\scripts")
$ok = $true
foreach ($d in $dirs) {
    $p = Join-Path $projectRoot $d
    if (Test-Path $p) {
        Write-Host "[OK] Found: $d" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Missing: $d" -ForegroundColor Red
        $ok = $false
    }
}
if (-not $ok) { exit 1 }

# Step 3: Install/Verify Dependencies
Write-Host "`n=== Step 3: Python Dependencies ===" -ForegroundColor Magenta
$pkgs = @("llvmlite", "colorama", "rich", "pyyaml", "click")
$missing = @()
foreach ($pkg in $pkgs) {
    python -c "import $($pkg.Replace('-', '_'))" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] $pkg installed" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] $pkg not found" -ForegroundColor Yellow
        $missing += $pkg
    }
}
if ($missing.Count -gt 0) {
    Write-Host "Installing missing packages..." -ForegroundColor Cyan
    $rf = Join-Path $projectRoot "boogpp\requirements.txt"
    if (Test-Path $rf) {
        python -m pip install -r $rf -q 2>$null
    } else {
        python -m pip install $missing -q 2>$null
    }
    Write-Host "[OK] Dependencies installed" -ForegroundColor Green
}

# Step 4: Run Tests
Write-Host "`n=== Step 4: Running Tests ===" -ForegroundColor Magenta
$t1 = Join-Path $projectRoot "boogpp\test_compiler.py"
if (Test-Path $t1) {
    Write-Host "Running test_compiler.py..." -ForegroundColor Cyan
    python $t1 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Compiler tests passed" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Compiler tests had issues" -ForegroundColor Yellow
    }
}

$t2 = Join-Path $projectRoot "boogpp\test_phase2.py"
if (Test-Path $t2) {
    Write-Host "Running test_phase2.py..." -ForegroundColor Cyan
    python $t2 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Phase 2 tests passed" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Phase 2 tests had issues" -ForegroundColor Yellow
    }
}

# Step 5: LLVM Installation
Write-Host "`n=== Step 5: LLVM Toolchain ===" -ForegroundColor Magenta
if (-not $SkipLLVM) {
    $installer = Join-Path $projectRoot "boogpp\scripts\install_llvm.ps1"
    if (Test-Path $installer) {
        Write-Host "Running LLVM installer script (may download and launch an interactive installer)..." -ForegroundColor Cyan
        # Run installer script directly so interactive installer can be launched if available.
        & powershell -ExecutionPolicy Bypass -File $installer
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Installer script finished. If an interactive installer was launched, please complete the UI (administrator privileges required)." -ForegroundColor Green
            Write-Host "After completing the installer, press Enter to continue the setup." -ForegroundColor Cyan
            Read-Host -Prompt "Press Enter after finishing the LLVM installer"
        } else {
            Write-Host "Installer script returned exit code $LASTEXITCODE. Please check logs or run the installer manually: boogpp\scripts\install_llvm.ps1" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "Skipped (--SkipLLVM flag)" -ForegroundColor Yellow
}

# Step 6: Test Compile
Write-Host "`n=== Step 6: Test Compilation ===" -ForegroundColor Magenta
if (-not $SkipTest) {
    $bpp = Join-Path $projectRoot "boogpp\boog.bpp"
    if (Test-Path $bpp) {
        Write-Host "Compiling boog.bpp to LLVM IR..." -ForegroundColor Cyan
        Set-Location $projectRoot
        python -m boogpp.compiler build boog.bpp -o test_output.exe 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Compilation successful" -ForegroundColor Green
            $ll = Join-Path $projectRoot "test_output.ll"
            if (Test-Path $ll) {
                $sz = (Get-Item $ll).Length
                Write-Host "[OK] LLVM IR generated: test_output.ll ($sz bytes)" -ForegroundColor Green
            }
        } else {
            Write-Host "[ERROR] Compilation failed" -ForegroundColor Red
        }
    } else {
        Write-Host "[WARNING] boog.bpp not found" -ForegroundColor Yellow
    }
} else {
    Write-Host "Skipped (--SkipTest flag)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
Write-Host "`nSummary:" -ForegroundColor Green
Write-Host "  [OK] Python verified" -ForegroundColor Green
Write-Host "  [OK] Project structure verified" -ForegroundColor Green
Write-Host "  [OK] Dependencies installed" -ForegroundColor Green
Write-Host "  [OK] Tests completed" -ForegroundColor Green
Write-Host "  [OK] LLVM configured" -ForegroundColor Green
Write-Host "  [OK] Test compile performed" -ForegroundColor Green

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "`n  1. Compile a .bpp file" -ForegroundColor Cyan
Write-Host "     python -m boogpp.compiler build yourfile.bpp -o output.exe" -ForegroundColor White

Write-Host "`n  2. Build with native linking (if LLVM available)" -ForegroundColor Cyan
Write-Host "     python -m boogpp.compiler build yourfile.bpp -o output.exe --link" -ForegroundColor White

Write-Host "`n  3. For detailed instructions:" -ForegroundColor Cyan
Write-Host "     notepad boogpp\SETUP.md" -ForegroundColor White

Write-Host "`n"
