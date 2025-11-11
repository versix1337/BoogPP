# Installer script for LLVM on Windows (PowerShell)
# - Checks for llc/clang on PATH
# - If missing, tries to install via winget or chocolatey
# - Does NOT require repository modifications

param(
    [switch]$Force,
    [string]$Version = "17.0.6"
)

function Test-HasCmd {
    param([string]$cmd)
    return (Get-Command $cmd -ErrorAction SilentlyContinue) -ne $null
}

Write-Host "== Boogpp LLVM Installer (with portable fallback) =="

$hasLlc = Test-HasCmd -cmd 'llc'
$hasClang = Test-HasCmd -cmd 'clang'

if ($hasLlc -and $hasClang -and -not $Force) {
    Write-Host "llc and clang are already available on PATH."
    try { llc --version 2>$null | ForEach-Object { Write-Host "llc: $_" } } catch {}
    try { clang --version 2>$null | Select-Object -First 1 | ForEach-Object { Write-Host "clang: $_" } } catch {}
    exit 0
}

# Resolve repo paths and check for pre-bundled assets
try {
    $scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
    $repoRoot = Resolve-Path (Join-Path $scriptRoot "..")
    $installDir = Join-Path $repoRoot 'tools\llvm'
} catch {}

if (-not $Force) {
    # 1) If an extracted toolchain is already present under tools/llvm, use it
    try {
        if (Test-Path $installDir) {
            $existingLlc = Get-ChildItem -Path $installDir -Filter 'llc.exe' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
            $existingClang = Get-ChildItem -Path $installDir -Filter 'clang.exe' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($existingLlc -and $existingClang) {
                $binPath = Split-Path -Parent $existingLlc.FullName
                Write-Host "Found existing LLVM tools under: $binPath"
                $env:Path = "$binPath;$env:Path"
                try { llc --version 2>$null | ForEach-Object { Write-Host "llc: $_" } } catch {}
                try { clang --version 2>$null | Select-Object -First 1 | ForEach-Object { Write-Host "clang: $_" } } catch {}
                exit 0
            }
        }
    } catch {}

    # 2) If a pre-bundled zip exists, extract it
    try {
        if (Test-Path $installDir) {
            $zipCandidate = Get-ChildItem -Path $installDir -Filter '*.zip' -File -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($zipCandidate) {
                Write-Host "Extracting pre-bundled archive: $($zipCandidate.Name)"
                Expand-Archive -Path $zipCandidate.FullName -DestinationPath $installDir -Force
                $llcFile = Get-ChildItem -Path $installDir -Filter 'llc.exe' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
                if ($llcFile) {
                    $binPath = Split-Path -Parent $llcFile.FullName
                    Write-Host "Found LLVM tools in: $binPath"
                    $env:Path = "$binPath;$env:Path"
                    try { llc --version 2>$null | ForEach-Object { Write-Host "llc: $_" } } catch {}
                    try { clang --version 2>$null | Select-Object -First 1 | ForEach-Object { Write-Host "clang: $_" } } catch {}
                    exit 0
                } else {
                    Write-Host "Archive extracted but did not contain llc.exe" -ForegroundColor Yellow
                }
            }
        }
    } catch {}

    # 3) If a pre-bundled installer exe exists, launch it interactively
    try {
        if (Test-Path $installDir) {
            $exeCandidate = Get-ChildItem -Path $installDir -Filter '*.exe' -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'LLVM-*.exe' } | Select-Object -First 1
            if ($exeCandidate) {
                Write-Host "Launching pre-bundled LLVM installer: $($exeCandidate.Name)" -ForegroundColor Cyan
                try {
                    Start-Process -FilePath $exeCandidate.FullName -Verb RunAs
                    Write-Host "Installer launched. Complete the installer UI, then re-run this script or continue setup." -ForegroundColor Green
                    # Try to hint PATH for current session if standard location exists
                    $defaultBin = 'C:\\Program Files\\LLVM\\bin'
                    if (Test-Path $defaultBin) {
                        $env:Path = "$defaultBin;$env:Path"
                    }
                    exit 0
                } catch {
                    Write-Host "Failed to launch the pre-bundled installer: $_" -ForegroundColor Yellow
                }
            }
        }
    } catch {}
}

# Try package managers first
if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "winget detected — attempting to install LLVM using winget..."
    try {
        winget install --id LLVM.LLVM -e --accept-package-agreements --accept-source-agreements
    } catch {
        Write-Host "winget install failed: $_" -ForegroundColor Yellow
    }
} elseif (Get-Command choco -ErrorAction SilentlyContinue) {
    Write-Host "Chocolatey detected — attempting to install llvm via choco..."
    try {
        choco install llvm -y
    } catch {
        Write-Host "choco install failed: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "No supported package manager found (winget or choco). Will attempt portable download fallback."
}

# Re-check availability
$hasLlc = Test-HasCmd -cmd 'llc'
$hasClang = Test-HasCmd -cmd 'clang'
if ($hasLlc -and $hasClang -and -not $Force) {
    Write-Host "Installation successful via package manager. Tools are available on PATH."
    try { llc --version 2>$null | ForEach-Object { Write-Host "llc: $_" } } catch {}
    try { clang --version 2>$null | Select-Object -First 1 | ForEach-Object { Write-Host "clang: $_" } } catch {}
    exit 0
}

# Portable download fallback: try multiple known release filenames and extract into boogpp/tools/llvm
try {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null


    # Try a list of candidate version strings and filename patterns
    $versions = @($Version, '17.0.5', '17.0.4', '16.0.6')
    $patterns = @("LLVM-{0}-win64.zip", "LLVM-{0}-win64.exe", "llvm-{0}-win64.zip")
    $downloaded = $false
    foreach ($ver in $versions) {
        foreach ($pat in $patterns) {
            $fileName = $pat -f $ver
            $url = "https://github.com/llvm/llvm-project/releases/download/llvmorg-$ver/$fileName"
            $zipPath = Join-Path $installDir $fileName
            Write-Host "Attempting to download $url"
            try {
                Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing -ErrorAction Stop
                $downloaded = $true
                Write-Host "Downloaded $fileName"
                break
            } catch {
                # Try next candidate
                Write-Host "Not available: $url" -ForegroundColor DarkGray
                if (Test-Path $zipPath) { Remove-Item $zipPath -ErrorAction SilentlyContinue }
            }
        }
        if ($downloaded) { break }
    }
    if (-not $downloaded) {
        throw "Could not download any known LLVM release archive for versions: $($versions -join ', ')"
    }

    Write-Host "Downloaded candidate: $fileName"

    # If we downloaded an .exe installer, launch it elevated and ask the user to complete the install interactively.
    if ($fileName -like '*.exe') {
        Write-Host "Launching downloaded installer: $zipPath" -ForegroundColor Cyan
        try {
            # Start the installer with elevation. This will prompt for UAC and require user interaction.
            Start-Process -FilePath $zipPath -Verb RunAs
            Write-Host "Installer process launched. Please complete the installer UI and then re-run this script or restart the setup." -ForegroundColor Green
            exit 0
        } catch {
            Write-Host "Failed to launch the installer executable: $_" -ForegroundColor Yellow
            # Fall through and try other candidates
            if (Test-Path $zipPath) { Remove-Item $zipPath -ErrorAction SilentlyContinue }
            continue
        }
    }

    Write-Host "Extracting to $installDir"
    Expand-Archive -Path $zipPath -DestinationPath $installDir -Force

    # Find the bin directory (search for llc.exe)
    $llcFile = Get-ChildItem -Path $installDir -Filter 'llc.exe' -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -eq $llcFile) {
        Write-Host "Downloaded archive but could not find llc.exe inside it." -ForegroundColor Yellow
        exit 4
    }

    $binPath = Split-Path -Parent $llcFile.FullName
    Write-Host "Found LLVM tools in: $binPath"

    # Add to PATH for current session
    $env:Path = "$binPath;$env:Path"

    # Verify
    $hasLlc = Test-HasCmd -cmd 'llc'
    $hasClang = Test-HasCmd -cmd 'clang'
    if ($hasLlc -and $hasClang) {
        Write-Host "Portable LLVM installation successful and available in this session PATH."
        try { llc --version 2>$null | ForEach-Object { Write-Host "llc: $_" } } catch {}
        try { clang --version 2>$null | Select-Object -First 1 | ForEach-Object { Write-Host "clang: $_" } } catch {}
        exit 0
    } else {
        Write-Host "Portable extraction completed but tools not found after updating PATH." -ForegroundColor Yellow
        exit 5
    }

} catch {
    Write-Host "Automatic portable installation failed: $_" -ForegroundColor Yellow
    Write-Host "You can manually download LLVM from https://llvm.org/releases/ and place the bin/ directory under boogpp/tools/llvm or install via winget/choco."
    exit 6
}
