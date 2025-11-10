@echo off
REM ============================================================================
REM Boogpp Python-Only Setup Script for Windows
REM Sets up Python environment and validates compiler without C dependencies
REM ============================================================================

setlocal EnableDelayedExpansion

echo.
echo ========================================================================
echo                 Boogpp Python-Only Setup for Windows
echo ========================================================================
echo.

REM ============================================================================
REM Step 1: Check Python
REM ============================================================================

echo [1/5] Checking Python installation...

python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or later from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [OK] Python !PYTHON_VERSION! found
)

REM ============================================================================
REM Step 2: Create Virtual Environment
REM ============================================================================

echo [2/5] Setting up Python virtual environment...

if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %errorLevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

REM Activate virtual environment
call venv\Scripts\activate.bat
if %errorLevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment activated

REM ============================================================================
REM Step 3: Install Python Dependencies
REM ============================================================================

echo [3/5] Installing Python dependencies...

pip install --upgrade pip setuptools wheel >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] Failed to upgrade pip
)

REM Install optional dependencies
pip install llvmlite >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] LLVM bindings not available (optional - for native compilation)
)

echo [OK] Python dependencies ready

REM ============================================================================
REM Step 4: Validate Boogpp Compiler
REM ============================================================================

echo [4/5] Validating Boogpp compiler modules...

REM Set PYTHONPATH to include current directory
set PYTHONPATH=%CD%

REM Test compiler module from root
python -c "from boogpp.compiler import __version__; print('Boogpp version:', __version__)" 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Failed to import Boogpp compiler module
    echo [INFO] This might indicate missing dependencies or module issues
    pause
    exit /b 1
)

REM Test individual modules
echo [INFO] Testing Lexer module...
python -c "from boogpp.compiler.lexer import Lexer; print('  Lexer: OK')" 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Lexer module failed to load
    pause
    exit /b 1
)

echo [INFO] Testing Parser module...
python -c "from boogpp.compiler.parser import Parser; print('  Parser: OK')" 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Parser module failed to load
    pause
    exit /b 1
)

echo [INFO] Testing Type Checker module...
python -c "from boogpp.compiler.typechecker import TypeChecker; print('  Type Checker: OK')" 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Type Checker module failed to load
    pause
    exit /b 1
)

echo [INFO] Testing Safety Checker module...
python -c "from boogpp.compiler.safety import SafetyChecker; print('  Safety Checker: OK')" 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Safety Checker module failed to load
    pause
    exit /b 1
)

echo [INFO] Testing Code Generator module...
python -c "from boogpp.compiler.codegen import LLVMCodeGenerator; print('  Code Generator: OK')" 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Code Generator module failed to load
    pause
    exit /b 1
)

echo [OK] All compiler modules loaded successfully

REM ============================================================================
REM Step 5: Create Build Directories
REM ============================================================================

echo [5/5] Setting up build directories...

if not exist "build" mkdir build
if not exist "dist" mkdir dist
if not exist "bin" mkdir bin

echo [OK] Build directories created

echo.
echo ========================================================================
echo                    Setup Complete!
echo ========================================================================
echo.
echo [OK] Boogpp Python environment is ready for development!
echo.
echo Available modules:
echo   - Lexer:               boogpp.compiler.lexer
echo   - Parser:              boogpp.compiler.parser
echo   - Type Checker:        boogpp.compiler.typechecker
echo   - Safety Checker:      boogpp.compiler.safety
echo   - Code Generator:      boogpp.compiler.codegen
echo.
echo ========================================================================
echo                    Next Steps
echo ========================================================================
echo.
echo 1. Compile a Boogpp program to LLVM IR:
echo    python -m boogpp.compiler.cli build program.bpp -o program.ll
echo.
echo 2. Run compiler tests:
echo    python test_compiler.py
echo.
echo 3. To build C runtime library (requires Make/GCC):
echo    Run setup-windows.bat for full system setup
echo.
echo For more information, see README.md
echo.
echo ========================================================================
echo.

pause
exit /b 0
