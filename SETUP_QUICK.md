# BoogPP Quick Setup Guide

## One-Command Setup

Run the automated setup script to verify Python, install dependencies, install LLVM, and test the compiler:

```powershell
cd C:\BoogPP-main
powershell -ExecutionPolicy Bypass -File boogpp\setup.ps1
```

This script performs all setup steps automatically:
1. ✓ Verifies Python 3.8+
2. ✓ Checks project structure
3. ✓ Installs/verifies Python dependencies
4. ✓ Runs unit tests (test_compiler.py, test_phase2.py)
5. ✓ Installs LLVM toolchain (automatic download if needed)
6. ✓ Tests compilation of boog.bpp to LLVM IR

## Setup Script Usage

### Run Full Setup (All Steps)

```powershell
powershell -ExecutionPolicy Bypass -File boogpp\setup.ps1
```

### Skip LLVM Installation

If you already have LLVM or want to install it manually:

```powershell
powershell -ExecutionPolicy Bypass -File boogpp\setup.ps1 -SkipLLVM
```

### Skip Test Compilation

To skip the test compilation step:

```powershell
powershell -ExecutionPolicy Bypass -File boogpp\setup.ps1 -SkipTest
```

### Skip Both

```powershell
powershell -ExecutionPolicy Bypass -File boogpp\setup.ps1 -SkipLLVM -SkipTest
```

## Expected Output

A successful setup run will show:

```
BoogPP Automated Setup

=== Step 1: Python Verification ===
[OK] Python found: Python 3.8.0

=== Step 2: Project Structure ===
[OK] Found: boogpp\compiler
[OK] Found: boogpp\examples
[OK] Found: boogpp\scripts

=== Step 3: Python Dependencies ===
[OK] llvmlite installed
[OK] colorama installed
[OK] rich installed
[OK] pyyaml installed
[OK] click installed

=== Step 4: Running Tests ===
Running test_compiler.py...
[OK] Compiler tests passed

Running test_phase2.py...
[OK] Phase 2 tests passed

=== Step 5: LLVM Toolchain ===
Running LLVM installer...
[Installer output...]

=== Step 6: Test Compilation ===
Compiling boog.bpp to LLVM IR...
[OK] Compilation successful
[OK] LLVM IR generated: test_output.ll (1234 bytes)

=== Setup Complete ===
```

## Troubleshooting

### "Python not found"
Install Python 3.8+ from https://www.python.org/downloads/ and add to PATH.

### "Project structure incomplete"
Ensure you're running the script from the project root (C:\BoogPP-main) or the boogpp directory.

### LLVM installation fails
The script tries automatic download. If that fails:
1. Download manually from https://github.com/llvm/llvm-project/releases
2. Extract to boogpp\tools\llvm
3. Add bin folder to PATH

For manual instructions, see [SETUP.md](./SETUP.md) → HowTo 3.

### Test compilation fails
Check that boog.bpp exists in the boogpp directory. If the error persists, run the compiler directly:

```powershell
python -m boogpp.compiler build boogpp\boog.bpp -o test_output.exe --verbose
```

## Next Steps After Setup

Once setup is complete:

1. **Compile your first program:**
   ```powershell
   python -m boogpp.compiler build yourfile.bpp -o output.exe
   ```

2. **Generate a native executable:**
   ```powershell
   python -m boogpp.compiler build yourfile.bpp -o output.exe --link
   ```

3. **Check syntax without compiling:**
   ```powershell
   python -m boogpp.compiler check yourfile.bpp
   ```

4. **View help:**
   ```powershell
   python -m boogpp.compiler --help
   ```

## Setup Script Features

| Feature | What It Does |
|---------|------------|
| Python Check | Verifies Python 3.8+ installed |
| Structure Verification | Checks for compiler, examples, scripts folders |
| Dependency Installation | Installs llvmlite, colorama, rich, pyyaml, click |
| Test Running | Runs test_compiler.py and test_phase2.py |
| LLVM Installation | Attempts automatic download and extraction |
| Test Compilation | Compiles boog.bpp to verify toolchain works |

## For More Information

- **Getting started:** See [SETUP.md](./SETUP.md)
- **Language syntax:** See [docs/LANGUAGE_SPEC.md](../docs/LANGUAGE_SPEC.md)
- **Runtime library:** See [docs/PHASE3_RUNTIME.md](../docs/PHASE3_RUNTIME.md)
- **Project overview:** See [README.md](./README.md)
