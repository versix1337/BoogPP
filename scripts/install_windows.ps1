# BoogPP Windows Installer
# Installs BoogPP compiler, runtime, and tools

param(
    [Parameter(Mandatory=$false)]
    [string]$InstallPath = "$env:ProgramFiles\BoogPP",

    [Parameter(Mandatory=$false)]
    [switch]$AddToPath,

    [Parameter(Mandatory=$false)]
    [switch]$InstallVSCodeExtension
)

$ErrorActionPreference = "Stop"

Write-Host @"
╔════════════════════════════════════════╗
║  BoogPP Windows Installer v3.0.0       ║
║  Systems Programming for Windows       ║
╚════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Check for administrator privileges
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Warning "Installer is not running with administrator privileges."
    Write-Warning "Some features may not be available."
    Write-Host ""
}

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green

    # Check Python version (3.8-3.12)
    if ($pythonVersion -match "Python 3\.([8-9]|1[0-2])\.") {
        Write-Host "  Python version compatible!" -ForegroundColor Green
    } else {
        Write-Error "Python 3.8-3.12 is required! Found: $pythonVersion"
        exit 1
    }
} catch {
    Write-Error "Python not found! Please install Python 3.8-3.12 from https://www.python.org"
    exit 1
}

# Check for LLVM (optional but recommended)
Write-Host "`nChecking for LLVM..." -ForegroundColor Yellow
try {
    $llvmVersion = llc --version 2>&1
    if ($llvmVersion -match "LLVM version") {
        Write-Host "  LLVM found!" -ForegroundColor Green
    }
} catch {
    Write-Warning "LLVM not found. Native compilation will not be available."
    Write-Host "  Install LLVM from: https://releases.llvm.org/" -ForegroundColor Yellow
}

# Create installation directory
Write-Host "`nCreating installation directory..." -ForegroundColor Yellow
if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
}

$BinPath = Join-Path $InstallPath "bin"
$LibPath = Join-Path $InstallPath "lib"
$IncludePath = Join-Path $InstallPath "include"
$ExamplesPath = Join-Path $InstallPath "examples"

New-Item -ItemType Directory -Path $BinPath -Force | Out-Null
New-Item -ItemType Directory -Path $LibPath -Force | Out-Null
New-Item -ItemType Directory -Path $IncludePath -Force | Out-Null
New-Item -ItemType Directory -Path $ExamplesPath -Force | Out-Null

# Install Python package
Write-Host "`nInstalling BoogPP compiler..." -ForegroundColor Yellow
pip install -e . --upgrade

# Build runtime and stdlib
Write-Host "`nBuilding runtime and standard library..." -ForegroundColor Yellow
& .\scripts\build_windows.ps1 -Configuration Release

# Copy runtime files
Write-Host "`nCopying runtime files..." -ForegroundColor Yellow
Copy-Item -Path "build\Release\*.dll" -Destination $BinPath -Force
Copy-Item -Path "build\Release\*.lib" -Destination $LibPath -Force
Copy-Item -Path "build\Release\include\*" -Destination $IncludePath -Force

# Copy examples
Write-Host "Copying example programs..." -ForegroundColor Yellow
Copy-Item -Path "examples\*" -Destination $ExamplesPath -Recurse -Force

# Add to PATH
if ($AddToPath) {
    Write-Host "`nAdding BoogPP to system PATH..." -ForegroundColor Yellow

    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($currentPath -notlike "*$BinPath*") {
        [Environment]::SetEnvironmentVariable(
            "Path",
            "$currentPath;$BinPath",
            "Machine"
        )
        Write-Host "  Added to PATH successfully!" -ForegroundColor Green
    } else {
        Write-Host "  Already in PATH" -ForegroundColor Yellow
    }

    # Set BOOGPP_HOME
    [Environment]::SetEnvironmentVariable("BOOGPP_HOME", $InstallPath, "Machine")
    Write-Host "  Set BOOGPP_HOME=$InstallPath" -ForegroundColor Green
}

# Install VS Code extension
if ($InstallVSCodeExtension) {
    Write-Host "`nInstalling VS Code extension..." -ForegroundColor Yellow

    $vscodePath = Get-Command code -ErrorAction SilentlyContinue
    if ($vscodePath) {
        Push-Location .vscode\extensions\boogpp
        npm install
        vsce package
        code --install-extension boogpp-3.0.0.vsix
        Pop-Location
        Write-Host "  VS Code extension installed!" -ForegroundColor Green
    } else {
        Write-Warning "VS Code not found. Skipping extension installation."
    }
}

# Create desktop shortcut
Write-Host "`nCreating shortcuts..." -ForegroundColor Yellow
$WshShell = New-Object -ComObject WScript.Shell

# BoogPP REPL shortcut
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\BoogPP REPL.lnk")
$Shortcut.TargetPath = "cmd.exe"
$Shortcut.Arguments = "/k boogpp repl"
$Shortcut.WorkingDirectory = $ExamplesPath
$Shortcut.Description = "BoogPP Interactive REPL"
$Shortcut.Save()

# Examples folder shortcut
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\BoogPP Examples.lnk")
$Shortcut.TargetPath = $ExamplesPath
$Shortcut.Description = "BoogPP Example Programs"
$Shortcut.Save()

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Yellow
try {
    $boogppVersion = boogpp --version
    Write-Host "  $boogppVersion" -ForegroundColor Green

    # Test compilation
    Write-Host "`nTesting compiler..." -ForegroundColor Yellow
    $testProgram = @"
module test
func main() -> i32:
    println("BoogPP is ready!")
    return 0
"@

    $testFile = Join-Path $env:TEMP "test.bpp"
    $testProgram | Out-File -FilePath $testFile -Encoding UTF8

    boogpp check $testFile
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Compiler test passed!" -ForegroundColor Green
    }

    Remove-Item $testFile -Force
} catch {
    Write-Error "Installation verification failed: $_"
    exit 1
}

# Installation complete
Write-Host @"

╔════════════════════════════════════════╗
║  Installation Complete! ✓              ║
╚════════════════════════════════════════╝

BoogPP has been installed to:
  $InstallPath

To get started:
  1. Open a new terminal (to refresh PATH)
  2. Run: boogpp --help
  3. Try the examples in: $ExamplesPath

Documentation:
  https://docs.boogpp.org

"@ -ForegroundColor Green

Write-Host "Quick Start:" -ForegroundColor Cyan
Write-Host "  boogpp repl                # Start interactive REPL" -ForegroundColor White
Write-Host "  boogpp build hello.bpp     # Compile a program" -ForegroundColor White
Write-Host "  boogpp check mycode.bpp    # Check syntax and safety" -ForegroundColor White

if (-not $AddToPath) {
    Write-Host "`nNote: Run installer with -AddToPath to add BoogPP to system PATH" -ForegroundColor Yellow
}

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
