# BoogPP Setup & HowTo Guide

This guide covers environment setup, compilation, LLVM installation, and native binary generation for the BoogPP compiler.

---

## Quick Start

### Prerequisites

- Python 3.8+ (verify with `python --version`)
- Windows PowerShell or Command Prompt

### Basic Compilation (LLVM IR only)

From the project root directory:

```powershell
cd C:\BoogPP-main
python -m boogpp.compiler build boogpp\boog.bpp -o output.exe
```

This produces:
- `output.ll` — LLVM Intermediate Representation (text format)

---

## HowTo 1: Set Up Your Environment

### Step 1: Verify Python Installation

```powershell
python --version
# Expected: Python 3.8 or higher
```

If Python is not found, [install Python 3.8+](https://www.python.org/downloads/).

### Step 2: Verify Project Structure

Ensure the project is at `C:\BoogPP-main` with these subdirectories:

```
C:\BoogPP-main\
  boogpp\
    compiler\          # compiler source
    examples\          # example .bpp files
    scripts\           # build scripts
    boog.bpp           # test file
  README.md
  requirements.txt
```

### Step 3: Verify Dependencies Are Installed

```powershell
cd C:\BoogPP-main\boogpp
python -m pip list | findstr -i "llvmlite colorama rich"
```

Expected output includes:
- `llvmlite`
- `colorama`
- `rich`

If any are missing, install them:

```powershell
pip install -r requirements.txt
```

---

## HowTo 2: Compile a .bpp File to LLVM IR

### Basic Syntax

```powershell
python -m boogpp.compiler build <input.bpp> -o <output.exe>
```

### Examples

#### Compile from project root, specifying full path:

```powershell
cd C:\BoogPP-main
python -m boogpp.compiler build boogpp\examples\01_hello_world.bpp -o hello_world.exe
```

Output:
- `hello_world.ll` — LLVM IR file (in current directory)

#### Compile from project root, using short name (auto-resolved to boogpp folder):

```powershell
cd C:\BoogPP-main
python -m boogpp.compiler build boog.bpp -o output.exe
```

Output:
- `output.ll` — LLVM IR file

#### Compile with verbose output:

```powershell
python -m boogpp.compiler build boog.bpp -o output.exe --verbose
```

#### Check syntax and safety without compiling:

```powershell
python -m boogpp.compiler check boog.bpp --safety safe
```

---

## HowTo 3: Install LLVM Toolchain

The BoogPP project includes an automatic installer script for the LLVM toolchain (llc and clang). This is required to produce native Windows executables.

### Automatic Installation (Recommended)

Run the installer script:

```powershell
cd C:\BoogPP-main
powershell -ExecutionPolicy Bypass -File boogpp\scripts\install_llvm.ps1
```

**What it does:**

1. Checks if `llc` and `clang` are already available on PATH.
2. If not found, tries to install via `winget` (Windows Package Manager) or `choco` (Chocolatey).
3. If package managers are unavailable, attempts to download a portable LLVM ZIP from GitHub releases and extracts it to `boogpp\tools\llvm`.
4. Updates the current PowerShell session PATH to include the LLVM tools.

**Output:**

- Success: "Portable LLVM installation successful and available in this session PATH."
- Partial: "Linking requested but llc/clang not found on PATH" — the tools were not found (see Troubleshooting below).

Note about interactive installers
-------------------------------

On Windows some LLVM release assets are provided as an installer executable (e.g. `LLVM-17.0.6-win64.exe`). When the automatic installer detects such an asset it will download the `.exe` and launch it elevated using the OS UAC prompt. This is interactive and requires an administrator to approve the install and follow the installer UI. The `setup.ps1` script has been updated to pause after launching the installer so you can finish the installation and then return to complete setup.

### Force Reinstall

To force reinstall even if LLVM is already available:

```powershell
powershell -ExecutionPolicy Bypass -File boogpp\scripts\install_llvm.ps1 -Force
```

### Specify a Different LLVM Version

By default, the installer tries version 17.0.6. To specify a different version:

```powershell
powershell -ExecutionPolicy Bypass -File boogpp\scripts\install_llvm.ps1 -Version 17.0.5
```

The installer will try multiple known release patterns for that version.

### Manual Installation

If the automatic installer fails:

1. Download a portable LLVM release for Windows:
   - Visit [LLVM Releases](https://github.com/llvm/llvm-project/releases)
   - Download a file named like `LLVM-17.0.6-win64.zip` (or latest win64 release)

2. Extract the ZIP:

```powershell
cd C:\BoogPP-main\boogpp
mkdir -Force tools\llvm
Expand-Archive -Path "C:\path\to\LLVM-17.0.6-win64.zip" -DestinationPath "tools\llvm"
```

3. Find the bin folder and add it to PATH for the current session:

```powershell
$llcFile = Get-ChildItem -Path tools\llvm -Filter llc.exe -Recurse | Select-Object -First 1
$binPath = Split-Path -Parent $llcFile.FullName
$env:Path = "$binPath;$env:Path"
```

4. Verify:

```powershell
llc --version
clang --version
```

---

## HowTo 4: Produce a Native Windows Executable (.exe)

After LLVM is installed, you can use the `--link` flag to automatically produce a native binary.

### Basic Syntax

```powershell
python -m boogpp.compiler build <input.bpp> -o <output.exe> --link
```

### Step-by-Step Example

```powershell
cd C:\BoogPP-main

# 1. Install LLVM (if not already done)
powershell -ExecutionPolicy Bypass -File boogpp\scripts\install_llvm.ps1

# 2. Compile with linking
python -m boogpp.compiler build boog.bpp -o output.exe --link
```

**Output:**

- `output.ll` — LLVM Intermediate Representation
- `output.obj` — Compiled object file (intermediate)
- `output.exe` — Native Windows executable

### With Verbose Output

```powershell
python -m boogpp.compiler build boog.bpp -o output.exe --link --verbose
```

Shows each compilation step (lexing, parsing, type checking, code generation, linking).

### What Happens During Linking

1. `llc` compiles `output.ll` → `output.obj` (object file)
2. `clang` links `output.obj` → `output.exe` (native executable)

If either step fails, an error message is printed and the partial outputs remain (for debugging).

---

## HowTo 5: Run Your Compiled Executable

After producing a native `.exe`:

```powershell
cd C:\BoogPP-main
.\output.exe
```

Expected output depends on your `.bpp` program. For example, if compiling `boog.bpp` (which likely contains a hello-world program), you should see output printed to the console.

---

## HowTo 6: Troubleshooting

### Issue: "File not found: boog.bpp"

**Cause:** The input file path doesn't exist relative to the current directory.

**Solution:**

- Ensure you're running from the project root (`C:\BoogPP-main`).
- Provide the full relative path: `python -m boogpp.compiler build boogpp\boog.bpp`
- Or provide an absolute path: `python -m boogpp.compiler build "C:\BoogPP-main\boogpp\boog.bpp"`

The CLI now has automatic fallback: if a short filename like `boog.bpp` is not found, it will search inside `boogpp/`, `boogpp/examples/`, and `boogpp/tests/`.

### Issue: "Linking requested but llc/clang not found on PATH"

**Cause:** LLVM toolchain (llc and clang) is not installed or not accessible on PATH.

**Solution:**

1. Run the automatic installer:
   ```powershell
   powershell -ExecutionPolicy Bypass -File boogpp\scripts\install_llvm.ps1
   ```

2. Verify installation:
   ```powershell
   llc --version
   clang --version
   ```

3. If still not found, check PATH manually:
   ```powershell
   $env:Path -split ';' | findstr llvm
   ```

4. If LLVM is installed but not on PATH, add it manually:
   ```powershell
   $env:Path = "C:\path\to\llvm\bin;$env:Path"
   llc --version  # Verify
   ```

### Issue: LLVM Download Failed ("Not Found" or network error)

**Cause:** The GitHub release URL for the specified version doesn't exist, or network access is blocked.

**Solution:**

1. Try with a different version:
   ```powershell
   powershell -ExecutionPolicy Bypass -File boogpp\scripts\install_llvm.ps1 -Version 17.0.5
   ```

2. If all downloads fail, download manually from [LLVM Releases](https://github.com/llvm/llvm-project/releases) and extract (see HowTo 3, "Manual Installation").

### Issue: Type Errors or Syntax Errors in Compilation

**Cause:** Your `.bpp` file contains invalid BoogPP code.

**Solution:**

1. Check your code syntax by running:
   ```powershell
   python -m boogpp.compiler check your_file.bpp
   ```

2. Review the error messages and fix the `.bpp` file.

3. Refer to [LANGUAGE_SPEC.md](../docs/LANGUAGE_SPEC.md) for language syntax.

---

## HowTo 7: Run Tests

### Run Unit Tests

```powershell
cd C:\BoogPP-main\boogpp
python test_compiler.py
```

Expected output: "All tests passed!"

### Run Integration Tests (Phase 2)

```powershell
python test_phase2.py
```

Expected output: "8/8 tests passed"

---

## HowTo 8: Compiler Command Reference

### Show Help

```powershell
python -m boogpp.compiler --help
```

### Show Version

```powershell
python -m boogpp.compiler version
```

### Build Command (Full Reference)

```powershell
python -m boogpp.compiler build INPUT [OPTIONS]
```

**Options:**

- `-o OUTPUT.exe` — Specify output file (default: input name with .exe)
- `--type {exe|dll|service|driver}` — Output type (default: exe)
  - `exe` — Standalone executable
  - `dll` — Dynamic Link Library (requires additional toolchain)
  - `service` — Windows Service binary (advanced)
  - `driver` — Kernel Driver (.sys, advanced)
- `--safety {safe|unsafe|custom}` — Safety mode (default: safe)
  - `safe` — Blocks dangerous operations
  - `unsafe` — Allows all operations (expert mode)
  - `custom` — User-defined rules (advanced)
- `-O {0|1|2|3}` — Optimization level (default: 0)
  - `0` — No optimization
  - `1, 2, 3` — Increasing optimization (passed to llc)
- `-v, --verbose` — Verbose output
- `--link` — Automatically run llc + clang to produce native executable

**Examples:**

```powershell
# Basic build to LLVM IR
python -m boogpp.compiler build main.bpp -o app.exe

# Build with linking to native executable
python -m boogpp.compiler build main.bpp -o app.exe --link

# Build with optimization
python -m boogpp.compiler build main.bpp -o app.exe --link -O2

# Build with unsafe mode (expert)
python -m boogpp.compiler build driver.bpp --safety unsafe --link -o mydriver.exe

# Build and get verbose output
python -m boogpp.compiler build main.bpp -o app.exe --link --verbose
```

### Check Command (Full Reference)

```powershell
python -m boogpp.compiler check INPUT [OPTIONS]
```

**Options:**

- `--safety {safe|unsafe|custom}` — Safety mode (default: safe)
- `-v, --verbose` — Verbose output

**Examples:**

```powershell
# Check for syntax and safety issues
python -m boogpp.compiler check main.bpp

# Check with unsafe mode
python -m boogpp.compiler check main.bpp --safety unsafe
```

---

## Next Steps

- Read [LANGUAGE_SPEC.md](../docs/LANGUAGE_SPEC.md) to learn the BoogPP language syntax.
- Explore example programs in `boogpp/examples/`.
- Review [PHASE3_RUNTIME.md](../docs/PHASE3_RUNTIME.md) for runtime library documentation.

---

## Support & Troubleshooting

For additional help:

1. Check the [main README.md](../README.md) for project overview.
2. Run `python -m boogpp.compiler check <file>` to validate syntax.
3. Run tests with `python test_compiler.py` and `python test_phase2.py`.
4. Review error messages — they include file and line information.
