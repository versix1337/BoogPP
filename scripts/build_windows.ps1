# BoogPP Windows Build Script
# Compiles runtime library and standard library for Windows

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Release",

    [Parameter(Mandatory=$false)]
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BoogPP Windows Build System" -ForegroundColor Cyan
Write-Host "  Configuration: $Configuration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Paths
$RootDir = Split-Path -Parent $PSScriptRoot
$BuildDir = Join-Path $RootDir "build"
$RuntimeDir = Join-Path $RootDir "runtime"
$StdlibDir = Join-Path $RootDir "stdlib\windows"
$OutputDir = Join-Path $BuildDir $Configuration

# Create directories
if ($Clean -and (Test-Path $BuildDir)) {
    Write-Host "`nCleaning build directory..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $BuildDir
}

if (-not (Test-Path $BuildDir)) {
    New-Item -ItemType Directory -Path $BuildDir | Out-Null
}

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

# Check for Visual Studio Build Tools
Write-Host "`nChecking for Visual Studio Build Tools..." -ForegroundColor Yellow

$VsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
if (-not (Test-Path $VsWhere)) {
    Write-Error "Visual Studio Build Tools not found! Please install Visual Studio 2019 or later."
    exit 1
}

$VsPath = & $VsWhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath
if (-not $VsPath) {
    Write-Error "Visual C++ Build Tools not found!"
    exit 1
}

Write-Host "Found Visual Studio at: $VsPath" -ForegroundColor Green

# Import Visual Studio environment
$VcVarsAll = Join-Path $VsPath "VC\Auxiliary\Build\vcvarsall.bat"
if (-not (Test-Path $VcVarsAll)) {
    Write-Error "vcvarsall.bat not found!"
    exit 1
}

Write-Host "`nInitializing Visual Studio environment..." -ForegroundColor Yellow
cmd /c "`"$VcVarsAll`" x64 && set" | ForEach-Object {
    if ($_ -match "=") {
        $v = $_.split("=")
        Set-Item -Force -Path "ENV:\$($v[0])" -Value "$($v[1])"
    }
}

# Compiler flags
$CFlags = @(
    "/nologo",
    "/W3",
    "/c",
    "/D_CRT_SECURE_NO_WARNINGS",
    "/DBPP_VERSION=`"3.0.0`""
)

$CxxFlags = @(
    "/EHsc",
    "/std:c++17"
)

$LinkFlags = @(
    "/nologo",
    "/DLL"
)

if ($Configuration -eq "Debug") {
    $CFlags += @("/Od", "/Zi", "/DBPP_DEBUG")
    $LinkFlags += @("/DEBUG")
} else {
    $CFlags += @("/O2", "/GL")
    $LinkFlags += @("/LTCG")
}

# Build Runtime Library
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Building Runtime Library" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$RuntimeSrc = Join-Path $RuntimeDir "src\boogpp_runtime.c"
$RuntimeObj = Join-Path $OutputDir "boogpp_runtime.obj"
$RuntimeLib = Join-Path $OutputDir "boogpp_runtime.lib"
$RuntimeDll = Join-Path $OutputDir "boogpp_runtime.dll"

Write-Host "`nCompiling runtime..." -ForegroundColor Yellow
$RuntimeInclude = Join-Path $RuntimeDir "include"

& cl.exe $CFlags /I"$RuntimeInclude" /Fo"$RuntimeObj" "$RuntimeSrc"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Runtime compilation failed!"
    exit 1
}

Write-Host "Linking runtime library..." -ForegroundColor Yellow
& link.exe $LinkFlags /OUT:"$RuntimeDll" "$RuntimeObj"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Runtime linking failed!"
    exit 1
}

& lib.exe /nologo /OUT:"$RuntimeLib" "$RuntimeObj"

Write-Host "Runtime library built successfully!" -ForegroundColor Green

# Build Windows Standard Library
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Building Windows Standard Library" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$WindowsSrc = Join-Path $StdlibDir "src\boogpp_windows.c"
$WindowsAdvSrc = Join-Path $StdlibDir "src\boogpp_windows_advanced.c"
$WindowsObj = Join-Path $OutputDir "boogpp_windows.obj"
$WindowsAdvObj = Join-Path $OutputDir "boogpp_windows_advanced.obj"
$WindowsLib = Join-Path $OutputDir "boogpp_windows.lib"
$WindowsDll = Join-Path $OutputDir "boogpp_windows.dll"

Write-Host "`nCompiling Windows API bindings..." -ForegroundColor Yellow
$StdlibInclude = Join-Path $StdlibDir "include"

& cl.exe $CFlags /I"$RuntimeInclude" /I"$StdlibInclude" /Fo"$WindowsObj" "$WindowsSrc"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Windows stdlib compilation failed!"
    exit 1
}

Write-Host "Compiling advanced Windows API bindings..." -ForegroundColor Yellow
& cl.exe $CFlags /I"$RuntimeInclude" /I"$StdlibInclude" /Fo"$WindowsAdvObj" "$WindowsAdvSrc"
if ($LASTEXITCODE -ne 0) {
    Write-Error "Advanced Windows stdlib compilation failed!"
    exit 1
}

Write-Host "Linking Windows stdlib..." -ForegroundColor Yellow
& link.exe $LinkFlags /OUT:"$WindowsDll" "$WindowsObj" "$WindowsAdvObj" "$RuntimeLib" `
    kernel32.lib user32.lib advapi32.lib psapi.lib ntdll.lib
if ($LASTEXITCODE -ne 0) {
    Write-Error "Windows stdlib linking failed!"
    exit 1
}

& lib.exe /nologo /OUT:"$WindowsLib" "$WindowsObj" "$WindowsAdvObj"

Write-Host "Windows standard library built successfully!" -ForegroundColor Green

# Copy headers
Write-Host "`nCopying headers..." -ForegroundColor Yellow
$IncludeOutputDir = Join-Path $OutputDir "include"
if (-not (Test-Path $IncludeOutputDir)) {
    New-Item -ItemType Directory -Path $IncludeOutputDir | Out-Null
}

Copy-Item -Path (Join-Path $RuntimeDir "include\*.h") -Destination $IncludeOutputDir -Force
Copy-Item -Path (Join-Path $StdlibDir "include\*.h") -Destination $IncludeOutputDir -Force

# Build complete
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Build Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nOutput directory: $OutputDir" -ForegroundColor Cyan
Write-Host "`nBuilt libraries:" -ForegroundColor Cyan
Write-Host "  - boogpp_runtime.dll" -ForegroundColor White
Write-Host "  - boogpp_runtime.lib" -ForegroundColor White
Write-Host "  - boogpp_windows.dll" -ForegroundColor White
Write-Host "  - boogpp_windows.lib" -ForegroundColor White

# Create package
Write-Host "`nCreating distribution package..." -ForegroundColor Yellow
$PackageDir = Join-Path $BuildDir "package"
if (Test-Path $PackageDir) {
    Remove-Item -Recurse -Force $PackageDir
}

New-Item -ItemType Directory -Path $PackageDir | Out-Null
New-Item -ItemType Directory -Path (Join-Path $PackageDir "bin") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $PackageDir "lib") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $PackageDir "include") | Out-Null

Copy-Item -Path (Join-Path $OutputDir "*.dll") -Destination (Join-Path $PackageDir "bin") -Force
Copy-Item -Path (Join-Path $OutputDir "*.lib") -Destination (Join-Path $PackageDir "lib") -Force
Copy-Item -Path (Join-Path $OutputDir "include\*") -Destination (Join-Path $PackageDir "include") -Force

Write-Host "Package created at: $PackageDir" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  All tasks completed successfully!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
