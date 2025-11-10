@echo off
REM ============================================================================
REM boogpp Setup Script for Windows
REM Automatically checks and installs dependencies, then builds the project
REM ============================================================================

setlocal EnableDelayedExpansion

echo.
echo ========================================================================
echo                    boogpp Setup for Windows
echo ========================================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] Not running as administrator.
    echo           Some installations may fail. Consider running as admin.
    echo.
    timeout /t 3 >nul
)

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
pip install llvmlite llvm >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] LLVM bindings not available (optional - for native compilation)
)

echo [OK] Python dependencies ready

REM ============================================================================
REM Step 4: Build boogpp Components
REM ============================================================================

echo [4/5] Building boogpp compiler...

REM Test lexer
python -c "from lexer import Lexer; print('Lexer module loaded')" >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Lexer module failed to load
    pause
    exit /b 1
)

REM Test parser
python -c "from parser import Parser; print('Parser module loaded')" >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Parser module failed to load
    pause
    exit /b 1
)

echo [OK] Compiler modules loaded successfully

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
echo [OK] boogpp v0.1.0 is now ready for development!
echo.
echo Built components:
echo   - Lexer:               lexer.py
echo   - Parser:              parser.py
echo   - AST Nodes:           ast_nodes.py
echo   - Test Framework:      test_lexer_parser.py
echo.
echo ========================================================================
echo                    Next Steps
echo ========================================================================
echo.
echo 1. Run tests to verify setup:
echo    python test_lexer_parser.py
echo.
echo 2. Start developing:
echo    - Type checker: type_checker.py
echo    - Safety system: safety.py
echo    - Code generator: codegen.py
echo.
echo 3. Compile boogpp programs:
echo    python -m boogpp build program.os -o program.exe
echo.
echo For more information, see README.md
echo.
echo ========================================================================
echo.

pause
exit /b 0
