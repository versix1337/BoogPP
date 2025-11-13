# BoogPP - llvmlite Installation Diagnostic and Fix Script for Windows
# This script diagnoses and fixes common llvmlite installation issues on Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BoogPP llvmlite Installation Diagnostics" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if running as admin
function Test-Administrator {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Check Python installation
Write-Host "[1/6] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✓ Python found: $pythonVersion" -ForegroundColor Green

    # Extract version number
    if ($pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)") {
        $majorVersion = [int]$matches[1]
        $minorVersion = [int]$matches[2]

        # Check if version is supported (3.8-3.12)
        if ($majorVersion -eq 3 -and $minorVersion -ge 8 -and $minorVersion -le 12) {
            Write-Host "   ✓ Python version is compatible with llvmlite" -ForegroundColor Green
        } elseif ($majorVersion -eq 3 -and $minorVersion -gt 12) {
            Write-Host "   ✗ ERROR: Python $majorVersion.$minorVersion is too new!" -ForegroundColor Red
            Write-Host "   llvmlite requires Python 3.8-3.12" -ForegroundColor Red
            Write-Host "   Please install Python 3.11 or 3.12 from https://www.python.org/downloads/" -ForegroundColor Yellow
            exit 1
        } else {
            Write-Host "   ✗ ERROR: Python version not supported" -ForegroundColor Red
            Write-Host "   llvmlite requires Python 3.8-3.12" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "   ✗ Python not found in PATH!" -ForegroundColor Red
    Write-Host "   Please install Python 3.8-3.12 from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check Python architecture (32-bit vs 64-bit)
Write-Host ""
Write-Host "[2/6] Checking Python architecture..." -ForegroundColor Yellow
$pythonArch = python -c "import struct; print(struct.calcsize('P') * 8)" 2>&1
if ($pythonArch -match "64") {
    Write-Host "   ✓ 64-bit Python detected" -ForegroundColor Green
} elseif ($pythonArch -match "32") {
    Write-Host "   ✗ ERROR: 32-bit Python detected!" -ForegroundColor Red
    Write-Host "   llvmlite requires 64-bit Python on Windows" -ForegroundColor Red
    Write-Host "   Please install 64-bit Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "   Make sure to download the 'Windows installer (64-bit)' version" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "   ⚠ Could not determine Python architecture" -ForegroundColor Yellow
}

# Check pip version
Write-Host ""
Write-Host "[3/6] Checking pip version..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "   ✓ pip found: $pipVersion" -ForegroundColor Green

    # Extract pip version number
    if ($pipVersion -match "pip (\d+)\.(\d+)\.(\d+)") {
        $pipMajor = [int]$matches[1]
        $pipMinor = [int]$matches[2]

        if ($pipMajor -lt 21) {
            Write-Host "   ⚠ pip version is outdated (should be 21.0 or higher)" -ForegroundColor Yellow
            Write-Host "   Upgrading pip..." -ForegroundColor Yellow
            python -m pip install --upgrade pip
        } else {
            Write-Host "   ✓ pip version is up to date" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "   ✗ pip not found!" -ForegroundColor Red
    Write-Host "   Installing pip..." -ForegroundColor Yellow
    python -m ensurepip --upgrade
}

# Check internet connectivity to PyPI
Write-Host ""
Write-Host "[4/6] Checking connectivity to PyPI..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://pypi.org/simple/llvmlite/" -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
    Write-Host "   ✓ Can reach PyPI" -ForegroundColor Green
} catch {
    Write-Host "   ⚠ Cannot reach PyPI - you may be behind a proxy or firewall" -ForegroundColor Yellow
    Write-Host "   If you're behind a corporate proxy, configure pip with:" -ForegroundColor Yellow
    Write-Host "   pip config set global.proxy http://user:password@proxy:port" -ForegroundColor Yellow
}

# Try to check available llvmlite versions
Write-Host ""
Write-Host "[5/6] Checking llvmlite availability..." -ForegroundColor Yellow
$llvmliteCheck = pip index versions llvmlite 2>&1
if ($llvmliteCheck -match "0\.43\.0|0\.44\.0|0\.45\.") {
    Write-Host "   ✓ llvmlite is available on PyPI" -ForegroundColor Green
} else {
    Write-Host "   ⚠ Could not verify llvmlite availability" -ForegroundColor Yellow
}

# Attempt to install llvmlite
Write-Host ""
Write-Host "[6/6] Attempting to install llvmlite..." -ForegroundColor Yellow
Write-Host "   This may take a few minutes..." -ForegroundColor Cyan

# First upgrade pip, setuptools, and wheel
Write-Host "   Upgrading pip, setuptools, and wheel..." -ForegroundColor Cyan
python -m pip install --upgrade pip setuptools wheel 2>&1 | Out-Null

# Try installing llvmlite
Write-Host "   Installing llvmlite>=0.43.0..." -ForegroundColor Cyan
$installOutput = python -m pip install "llvmlite>=0.43.0" --prefer-binary 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✓ llvmlite installed successfully!" -ForegroundColor Green

    # Verify installation
    $verifyOutput = python -c "import llvmlite; print(f'llvmlite version: {llvmlite.__version__}')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✓ Verification: $verifyOutput" -ForegroundColor Green
    }
} else {
    Write-Host "   ✗ Failed to install llvmlite" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error output:" -ForegroundColor Red
    Write-Host $installOutput -ForegroundColor Red

    Write-Host ""
    Write-Host "Possible solutions:" -ForegroundColor Yellow
    Write-Host "1. Try installing a specific version:" -ForegroundColor Yellow
    Write-Host "   pip install llvmlite==0.43.0" -ForegroundColor White
    Write-Host ""
    Write-Host "2. If you see 'Microsoft Visual C++ 14.0 is required':" -ForegroundColor Yellow
    Write-Host "   Install Build Tools from: https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Try using a virtual environment:" -ForegroundColor Yellow
    Write-Host "   python -m venv boogpp_env" -ForegroundColor White
    Write-Host "   .\boogpp_env\Scripts\activate" -ForegroundColor White
    Write-Host "   pip install llvmlite>=0.43.0" -ForegroundColor White
    Write-Host ""
    Write-Host "4. Check if you're using 64-bit Python (not 32-bit)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "5. Ensure Python version is between 3.8 and 3.12" -ForegroundColor Yellow

    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Diagnostic Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now install BoogPP:" -ForegroundColor Green
Write-Host "  pip install -e ." -ForegroundColor White
Write-Host ""
Write-Host "Or with development dependencies:" -ForegroundColor Green
Write-Host "  pip install -e .[dev]" -ForegroundColor White
Write-Host ""
