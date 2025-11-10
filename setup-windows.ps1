# ============================================================================
# Boogpp Setup Script for Windows (PowerShell)
# Automatically checks and installs dependencies, then builds the project
# ============================================================================

# Require PowerShell 5.1 or later
#Requires -Version 5.1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================================================"
Write-Host "                    Boogpp Setup for Windows"
Write-Host "========================================================================"
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[WARNING] Not running as administrator." -ForegroundColor Yellow
    Write-Host "          Some installations may fail. Consider running as admin." -ForegroundColor Yellow
    Write-Host ""
    Start-Sleep -Seconds 2
}

# ============================================================================
# Helper Functions
# ============================================================================

function Test-CommandExists {
    param($command)
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

function Install-Chocolatey {
    Write-Host "[INFO] Installing Chocolatey package manager..." -ForegroundColor Cyan

    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072

    try {
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        Write-Host "[OK] Chocolatey installed successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "[ERROR] Chocolatey installation failed: $_" -ForegroundColor Red
        return $false
    }
}

# ============================================================================
# Step 1: Check Python
# ============================================================================

Write-Host "[1/6] Checking Python installation..." -ForegroundColor Cyan

if (Test-CommandExists python) {
    $pythonVersion = python --version 2>&1 | Out-String
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green

    # Check Python version
    $version = (python --version 2>&1 | Select-String -Pattern "(\d+)\.(\d+)" | ForEach-Object { $_.Matches.Groups[1].Value + "." + $_.Matches.Groups[2].Value })
    $versionNum = [double]$version

    if ($versionNum -lt 3.8) {
        Write-Host "[ERROR] Python 3.8 or later required. Current: $pythonVersion" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.8 or later from:" -ForegroundColor Yellow
    Write-Host "https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Make sure to check 'Add Python to PATH' during installation!" -ForegroundColor Yellow
    pause
    exit 1
}

# ============================================================================
# Step 2: Check/Install Chocolatey
# ============================================================================

Write-Host "[2/6] Checking Chocolatey package manager..." -ForegroundColor Cyan

if (-not (Test-CommandExists choco)) {
    if (-not (Install-Chocolatey)) {
        Write-Host "[WARNING] Continuing without Chocolatey" -ForegroundColor Yellow
        Write-Host "          You may need to install dependencies manually" -ForegroundColor Yellow
        $hasChoco = $false
    }
    else {
        $hasChoco = $true
    }
}
else {
    Write-Host "[OK] Chocolatey already installed" -ForegroundColor Green
    $hasChoco = $true
}

# ============================================================================
# Step 3: Check/Install MinGW (GCC)
# ============================================================================

Write-Host "[3/6] Checking GCC/MinGW installation..." -ForegroundColor Cyan

if (-not (Test-CommandExists gcc)) {
    Write-Host "[INFO] GCC not found. Installing MinGW..." -ForegroundColor Cyan

    if ($hasChoco) {
        try {
            choco install mingw -y
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            Write-Host "[OK] MinGW installed successfully" -ForegroundColor Green
        }
        catch {
            Write-Host "[ERROR] MinGW installation failed" -ForegroundColor Red
            Write-Host "Please install MinGW manually from: https://www.mingw-w64.org/" -ForegroundColor Yellow
            pause
            exit 1
        }
    }
    else {
        Write-Host "[ERROR] Cannot install MinGW without Chocolatey" -ForegroundColor Red
        Write-Host "Please install MinGW manually from: https://www.mingw-w64.org/" -ForegroundColor Yellow
        pause
        exit 1
    }
}
else {
    $gccVersion = gcc --version | Select-Object -First 1
    Write-Host "[OK] $gccVersion" -ForegroundColor Green
}

# ============================================================================
# Step 4: Check/Install Make
# ============================================================================

Write-Host "[4/6] Checking Make installation..." -ForegroundColor Cyan

$makeCmd = $null

if (Test-CommandExists mingw32-make) {
    $makeCmd = "mingw32-make"
    Write-Host "[OK] MinGW Make found" -ForegroundColor Green
}
elseif (Test-CommandExists make) {
    $makeCmd = "make"
    Write-Host "[OK] Make found" -ForegroundColor Green
}
else {
    Write-Host "[INFO] Make not found. Installing..." -ForegroundColor Cyan

    if ($hasChoco) {
        try {
            choco install make -y
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            $makeCmd = "make"
            Write-Host "[OK] Make installed successfully" -ForegroundColor Green
        }
        catch {
            if (Test-CommandExists mingw32-make) {
                $makeCmd = "mingw32-make"
                Write-Host "[WARNING] Using mingw32-make instead" -ForegroundColor Yellow
            }
            else {
                Write-Host "[ERROR] Make installation failed and no alternative found" -ForegroundColor Red
                pause
                exit 1
            }
        }
    }
    else {
        Write-Host "[ERROR] No Make utility found and cannot install without Chocolatey!" -ForegroundColor Red
        pause
        exit 1
    }
}

Write-Host "[INFO] Using make command: $makeCmd" -ForegroundColor Cyan

# ============================================================================
# Step 5: Optional - Check LLVM
# ============================================================================

Write-Host "[5/6] Checking LLVM installation (optional for native binaries)..." -ForegroundColor Cyan

$hasLLVM = $false

if (Test-CommandExists llc) {
    $llvmVersion = llc --version | Select-String -Pattern "version" | Select-Object -First 1
    Write-Host "[OK] LLVM found - $llvmVersion" -ForegroundColor Green
    $hasLLVM = $true
}
else {
    Write-Host "[INFO] LLVM not found (optional)" -ForegroundColor Yellow
    Write-Host "       You can compile to LLVM IR, but not native binaries" -ForegroundColor Yellow
    Write-Host "       Install LLVM from: https://releases.llvm.org/download.html" -ForegroundColor Yellow
}

# ============================================================================
# Step 6: Build Boogpp
# ============================================================================

Write-Host "[6/6] Building Boogpp..." -ForegroundColor Cyan
Write-Host ""

try {
    # Build runtime library
    Write-Host "Building runtime library..." -ForegroundColor Cyan
    Push-Location boogpp\runtime
    & $makeCmd release
    if ($LASTEXITCODE -ne 0) { throw "Runtime build failed" }
    Pop-Location
    Write-Host "[OK] Runtime library built" -ForegroundColor Green

    # Build Windows standard library
    Write-Host "Building Windows standard library..." -ForegroundColor Cyan
    Push-Location boogpp\stdlib\windows
    & $makeCmd -f ..\..\Makefile.stdlib release
    if ($LASTEXITCODE -ne 0) { throw "Standard library build failed" }
    Pop-Location
    Write-Host "[OK] Standard library built" -ForegroundColor Green

    # Test compiler
    Write-Host "Testing compiler..." -ForegroundColor Cyan
    Push-Location boogpp
    $compilerVersion = python -c "from compiler import __version__; print(__version__)"
    if ($LASTEXITCODE -ne 0) { throw "Compiler test failed" }
    Pop-Location
    Write-Host "[OK] Compiler version: $compilerVersion" -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "[ERROR] Build failed: $_" -ForegroundColor Red
    pause
    exit 1
}

# ============================================================================
# Success Summary
# ============================================================================

Write-Host ""
Write-Host "========================================================================"
Write-Host "                    Build Complete!"
Write-Host "========================================================================"
Write-Host ""
Write-Host "[OK] Boogpp v$compilerVersion is now built and ready to use!" -ForegroundColor Green
Write-Host ""
Write-Host "Built components:" -ForegroundColor Cyan
Write-Host "  - Runtime library:     boogpp\runtime\lib\libboogpp_runtime.a"
Write-Host "  - Windows stdlib:      boogpp\stdlib\windows\lib\libboogpp_windows.a"
Write-Host "  - Boogpp compiler:     boogpp\compiler\"
Write-Host ""
Write-Host "========================================================================"
Write-Host "                    Usage Instructions"
Write-Host "========================================================================"
Write-Host ""
Write-Host "To compile a Boogpp program:" -ForegroundColor Cyan
Write-Host "  python -m boogpp.compiler.cli build program.bpp -o program.ll"
Write-Host ""
Write-Host "To run tests:" -ForegroundColor Cyan
Write-Host "  cd boogpp\runtime"
Write-Host "  $makeCmd test"
Write-Host ""
Write-Host "To create a native binary (requires LLVM):" -ForegroundColor Cyan

if ($hasLLVM) {
    Write-Host "  llc -filetype=obj program.ll -o program.o"
    Write-Host "  clang program.o boogpp\runtime\lib\libboogpp_runtime.a -o program.exe"
}
else {
    Write-Host "  [Install LLVM first from https://releases.llvm.org/]" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "For more information, see INSTALL.md and README.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================================================"
Write-Host ""

# Create convenience PowerShell function
$boogppWrapper = @"
# Boogpp wrapper function
function boogpp {
    python -m boogpp.compiler.cli `$args
}

# Export function
Export-ModuleMember -Function boogpp
"@

$boogppWrapper | Out-File -FilePath "boogpp.psm1" -Encoding UTF8

Write-Host "[INFO] Created boogpp.psm1 PowerShell module" -ForegroundColor Cyan
Write-Host "       To use globally, add to your PowerShell profile:" -ForegroundColor Yellow
Write-Host "       Import-Module $PWD\boogpp.psm1" -ForegroundColor Yellow
Write-Host ""

# Create batch wrapper
@"
@echo off
python -m boogpp.compiler.cli %*
"@ | Out-File -FilePath "boogpp.bat" -Encoding ASCII

Write-Host "[INFO] Created boogpp.bat wrapper script" -ForegroundColor Cyan
Write-Host "       You can now use: .\boogpp.bat build program.bpp" -ForegroundColor Yellow
Write-Host ""

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
