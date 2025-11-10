@echo off
REM ============================================================================
REM Boogpp Setup Script for Windows
REM Automatically checks and installs dependencies, then builds the project
REM ============================================================================

setlocal EnableDelayedExpansion

echo.
echo ========================================================================
echo                    Boogpp Setup for Windows
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

echo [1/6] Checking Python installation...

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
REM Step 2: Check/Install Chocolatey (Package Manager)
REM ============================================================================

echo [2/6] Checking Chocolatey package manager...

where choco >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Chocolatey not found. Installing Chocolatey...
    echo        This will take a moment...

    powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"

    if %errorLevel% neq 0 (
        echo [WARNING] Chocolatey installation failed.
        echo           You may need to install dependencies manually.
    ) else (
        echo [OK] Chocolatey installed successfully
        REM Refresh environment
        call refreshenv
    )
) else (
    echo [OK] Chocolatey already installed
)

REM ============================================================================
REM Step 3: Check/Install MinGW (GCC for Windows)
REM ============================================================================

echo [3/6] Checking GCC/MinGW installation...

where gcc >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] GCC not found. Installing MinGW...

    where choco >nul 2>&1
    if %errorLevel% equ 0 (
        choco install mingw -y
        if %errorLevel% neq 0 (
            echo [ERROR] MinGW installation failed
            echo Please install MinGW manually from: https://www.mingw-w64.org/
            pause
            exit /b 1
        )
        REM Refresh environment
        call refreshenv
    ) else (
        echo [ERROR] Cannot install MinGW without Chocolatey
        echo Please install MinGW manually from: https://www.mingw-w64.org/
        pause
        exit /b 1
    )
) else (
    for /f "tokens=3" %%i in ('gcc --version 2^>^&1 ^| findstr /C:"gcc"') do set GCC_VERSION=%%i
    echo [OK] GCC found (version !GCC_VERSION!)
)

REM ============================================================================
REM Step 4: Check/Install Make
REM ============================================================================

echo [4/6] Checking Make installation...

where mingw32-make >nul 2>&1
if %errorLevel% neq 0 (
    where make >nul 2>&1
    if %errorLevel% neq 0 (
        echo [INFO] Make not found. Installing...

        where choco >nul 2>&1
        if %errorLevel% equ 0 (
            choco install make -y
            if %errorLevel% neq 0 (
                echo [WARNING] Make installation failed
                echo Will try to use mingw32-make instead
            )
        )
    ) else (
        echo [OK] Make found
    )
) else (
    echo [OK] MinGW Make found
    set MAKE_CMD=mingw32-make
)

REM Set make command
where make >nul 2>&1
if %errorLevel% equ 0 (
    set MAKE_CMD=make
) else (
    where mingw32-make >nul 2>&1
    if %errorLevel% equ 0 (
        set MAKE_CMD=mingw32-make
    ) else (
        echo [ERROR] No Make utility found!
        echo Please install Make or MinGW
        pause
        exit /b 1
    )
)

echo [INFO] Using make command: !MAKE_CMD!

REM ============================================================================
REM Step 5: Optional - Check LLVM
REM ============================================================================

echo [5/6] Checking LLVM installation (optional for native binaries)...

where llc >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] LLVM not found (optional)
    echo       You can compile to LLVM IR, but not native binaries
    echo       Install LLVM from: https://releases.llvm.org/download.html
    set HAS_LLVM=0
) else (
    for /f "tokens=3" %%i in ('llc --version 2^>^&1 ^| findstr /C:"version"') do set LLVM_VERSION=%%i
    echo [OK] LLVM found (version !LLVM_VERSION!)
    set HAS_LLVM=1
)

REM ============================================================================
REM Step 6: Build Boogpp
REM ============================================================================

echo [6/6] Building Boogpp...
echo.

REM Build runtime library
echo Building runtime library...
cd boogpp\runtime
!MAKE_CMD! release
if %errorLevel% neq 0 (
    echo [ERROR] Runtime build failed!
    cd ..\..
    pause
    exit /b 1
)
cd ..\..

REM Build Windows standard library
echo Building Windows standard library...
cd boogpp\stdlib\windows
!MAKE_CMD! -f ..\..\Makefile.stdlib release
if %errorLevel% neq 0 (
    echo [ERROR] Standard library build failed!
    cd ..\..\..
    pause
    exit /b 1
)
cd ..\..\..

REM Test compiler
echo Testing compiler...
cd boogpp
python -c "from compiler import __version__; print('Compiler version:', __version__)"
if %errorLevel% neq 0 (
    echo [ERROR] Compiler test failed!
    cd ..
    pause
    exit /b 1
)
cd ..

echo.
echo ========================================================================
echo                    Build Complete!
echo ========================================================================
echo.
echo [OK] Boogpp v3.0.0 is now built and ready to use!
echo.
echo Built components:
echo   - Runtime library:     boogpp\runtime\lib\libboogpp_runtime.a
echo   - Windows stdlib:      boogpp\stdlib\windows\lib\libboogpp_windows.a
echo   - Boogpp compiler:     boogpp\compiler\
echo.
echo ========================================================================
echo                    Usage Instructions
echo ========================================================================
echo.
echo To compile a Boogpp program:
echo   python -m boogpp.compiler.cli build program.bpp -o program.ll
echo.
echo To run tests:
echo   cd boogpp\runtime
echo   !MAKE_CMD! test
echo.
echo To create a native binary (requires LLVM):

if !HAS_LLVM! equ 1 (
    echo   llc -filetype=obj program.ll -o program.o
    echo   clang program.o boogpp\runtime\lib\libboogpp_runtime.a -o program.exe
) else (
    echo   [Install LLVM first from https://releases.llvm.org/]
)

echo.
echo For more information, see INSTALL.md and README.md
echo.
echo ========================================================================
echo.

REM Create convenience batch file for boogpp command
echo @echo off > boogpp.bat
echo python -m boogpp.compiler.cli %%* >> boogpp.bat

echo [INFO] Created boogpp.bat wrapper script
echo       You can now use: boogpp.bat build program.bpp
echo.

pause
exit /b 0
