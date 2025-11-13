# BoogPP Installation Guide

This guide explains how to install BoogPP as a Python package for easy maintenance and updates.

## Prerequisites

- **Python 3.8-3.12** (64-bit) - **Important:** Python 3.13+ is not yet supported by llvmlite
- **pip** (Python package installer)
- **Windows 10/11** (for full Windows API support)
- **LLVM 14+** (optional, required for native executable compilation)

## ⚠️ Important for Windows Users

**Before installing, please verify:**

1. **You have 64-bit Python installed** (not 32-bit)
   - llvmlite does NOT work with 32-bit Python on Windows
   - Check with: `python -c "import struct; print(struct.calcsize('P') * 8)"`
   - Should output `64`

2. **You're using Python 3.8-3.12** (not 3.13 or newer)
   - llvmlite doesn't support Python 3.13 yet
   - Check with: `python --version`
   - Recommended: Python 3.11 or 3.12

3. **Your pip is up to date**
   - Run: `python -m pip install --upgrade pip setuptools wheel`

### Quick Fix for Windows llvmlite Issues

If you encounter "No matching distribution found for llvmlite", run our diagnostic script:

```powershell
# From the BoogPP directory
powershell -ExecutionPolicy Bypass -File scripts\fix_llvmlite_windows.ps1
```

This script will:
- Check your Python version and architecture
- Verify pip is up to date
- Test PyPI connectivity
- Attempt to install llvmlite with the correct settings
- Provide specific solutions if issues are found

## Installation Methods

### Method 1: Install from Source (Development Mode)

This is recommended for development and allows you to edit the code while having it available system-wide.

```powershell
# Clone the repository
git clone https://github.com/versix1337/BoogPP.git
cd BoogPP

# Install in editable/development mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

**Benefits of `-e` (editable install):**
- Changes to the source code are immediately reflected
- No need to reinstall after making changes
- Perfect for development and testing

### Method 2: Regular Installation from Source

For regular use without development:

```powershell
# Clone the repository
git clone https://github.com/versix1337/BoogPP.git
cd BoogPP

# Install the package
pip install .
```

### Method 3: Install from GitHub Directly

```powershell
pip install git+https://github.com/versix1337/BoogPP.git
```

### Method 4: Install from PyPI (Future)

Once published to PyPI:

```powershell
pip install boogpp
```

## Verifying Installation

After installation, verify that BoogPP is installed correctly:

```powershell
# Check if boogpp command is available
boogpp --version

# Or use Python module syntax
python -m boogpp.compiler --version
```

You should see output similar to:
```
BoogPP Compiler v3.0.0
```

## Installing LLVM (Optional but Recommended)

To compile BoogPP programs to native executables, you need LLVM installed:

### Automated LLVM Installation

```powershell
# Run the automated LLVM installer script
powershell -ExecutionPolicy Bypass -File scripts/install_llvm.ps1
```

### Manual LLVM Installation

1. Download LLVM 14+ from https://releases.llvm.org/
2. Install to a directory (e.g., `C:\Program Files\LLVM`)
3. Add LLVM bin directory to your PATH:
   ```powershell
   $env:Path += ";C:\Program Files\LLVM\bin"
   ```

4. Verify installation:
   ```powershell
   llc --version
   clang --version
   ```

## Post-Installation Setup

### 1. Compile Runtime Library

The BoogPP runtime library needs to be compiled once:

```powershell
cd stdlib
nmake /f Makefile.stdlib
# Or on Linux/WSL:
make -f Makefile.stdlib
```

This creates the runtime library files needed for linking.

### 2. Run Tests (Optional)

Verify everything works by running the test suite:

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=boogpp
```

### 3. Try Example Programs

Compile and run a simple example:

```powershell
# Compile to LLVM IR
boogpp build examples/01_hello_world.bpp -o hello.exe

# Compile and link to native executable (requires LLVM)
boogpp build examples/01_hello_world.bpp -o hello.exe --link

# Run the program
.\hello.exe
```

## Using BoogPP

### Command-Line Interface

After installation, you can use `boogpp` command anywhere:

```powershell
# Compile a BoogPP program
boogpp build myprogram.bpp -o myprogram.exe

# Compile with linking
boogpp build myprogram.bpp -o myprogram.exe --link

# Check syntax and safety
boogpp check myprogram.bpp

# Compile with specific safety mode
boogpp build myprogram.bpp --safety unsafe -o myprogram.exe

# Compile a DLL
boogpp build mylib.bpp --type dll -o mylib.dll --link

# Show help
boogpp --help
```

### Python Module Usage

You can also use BoogPP as a Python module:

```python
from boogpp.compiler import Lexer, Parser, TypeChecker, LLVMCodeGenerator
from boogpp.compiler.safety import SafetyChecker, SafetyMode

# Tokenize source code
lexer = Lexer(source_code)
tokens = lexer.tokenize()

# Parse tokens
parser = Parser(tokens)
ast = parser.parse()

# Type checking
type_checker = TypeChecker()
type_checker.check(ast)

# Safety checking
safety_checker = SafetyChecker(SafetyMode.SAFE)
safety_checker.check(ast)

# Code generation
codegen = LLVMCodeGenerator()
llvm_ir = codegen.generate(ast)
```

## Updating BoogPP

### Development Mode Installation

If installed with `pip install -e .`, just pull the latest changes:

```powershell
git pull origin main
# Changes are automatically available
```

### Regular Installation

For regular installations, reinstall:

```powershell
git pull origin main
pip install --upgrade .
```

### From PyPI (Future)

```powershell
pip install --upgrade boogpp
```

## Uninstalling

To uninstall BoogPP:

```powershell
pip uninstall boogpp
```

## Troubleshooting

### "No matching distribution found for llvmlite>=0.43.0"

This is a common issue with llvmlite installation. Try these solutions in order:

#### Solution 1: Upgrade pip, setuptools, and wheel

```bash
# Upgrade pip and build tools
pip install --upgrade pip setuptools wheel
```

Then retry the installation:
```bash
pip install -e .
```

#### Solution 2: Install llvmlite separately first

```bash
# Install llvmlite explicitly
pip install llvmlite>=0.43.0

# Then install BoogPP
pip install -e .
```

#### Solution 3: Use a compatible Python version

llvmlite requires Python 3.8-3.12. Check your Python version:

```bash
python --version
```

If you're using an unsupported version, install Python 3.11 (recommended):
- Download from https://www.python.org/downloads/
- Or use pyenv/conda to manage multiple Python versions

#### Solution 4: Platform-specific issues

**On Windows:**
- Install Microsoft Visual C++ 14.0 or greater from:
  https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Or use pre-built wheels by upgrading pip (Solution 1)

**On Linux:**
- Install LLVM development libraries:
  ```bash
  # Ubuntu/Debian
  sudo apt-get update
  sudo apt-get install llvm-14-dev

  # Fedora/RHEL
  sudo dnf install llvm-devel

  # Arch Linux
  sudo pacman -S llvm
  ```

**On macOS:**
- Install LLVM via Homebrew:
  ```bash
  brew install llvm@14
  ```

#### Solution 5: Use a virtual environment

Sometimes system-wide installations have conflicts. Use a virtual environment:

```bash
# Create a fresh virtual environment
python -m venv boogpp_env

# Activate it
# Windows:
boogpp_env\Scripts\activate
# Linux/macOS:
source boogpp_env/bin/activate

# Upgrade pip in the virtual environment
pip install --upgrade pip setuptools wheel

# Install BoogPP
pip install -e .
```

#### Solution 6: Install a specific version

If the latest llvmlite version has issues, try a specific version:

```bash
pip install llvmlite==0.43.0
pip install -e .
```

#### Solution 7: Check network and proxy settings

If you're behind a corporate proxy or firewall:

```bash
# Use a different PyPI mirror
pip install --index-url https://pypi.org/simple/ llvmlite>=0.43.0

# Or configure proxy
pip install --proxy http://user:password@proxy:port llvmlite>=0.43.0
```

### Command 'boogpp' not found

Make sure Python's Scripts directory is in your PATH:

```powershell
# Windows
$env:Path += ";$env:LOCALAPPDATA\Programs\Python\Python3X\Scripts"

# Or if using Python from Microsoft Store
$env:Path += ";$env:LOCALAPPDATA\Packages\PythonSoftwareFoundation.Python.3.X_qbz5n2kfra8p0\LocalCache\local-packages\Python3X\Scripts"
```

### Import errors after installation

Try reinstalling:
```powershell
pip uninstall boogpp
pip install -e .
```

### LLVM not found during linking

Ensure LLVM is installed and in your PATH:
```powershell
# Check if LLVM tools are available
llc --version
clang --version

# Add to PATH if needed
$env:Path += ";C:\Program Files\LLVM\bin"
```

### Permission errors during installation

Run as administrator or use a virtual environment:

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Install in the virtual environment
pip install -e .
```

## Development Setup

For contributors and developers:

```powershell
# Clone the repository
git clone https://github.com/versix1337/BoogPP.git
cd BoogPP

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
pylint boogpp

# Format code
black boogpp

# Type checking
mypy boogpp
```

## Next Steps

- Read the [Language Specification](docs/LANGUAGE_SPEC.md)
- Explore [Examples](examples/)
- Check out [Setup Guide](SETUP.md) for detailed LLVM setup
- Join discussions at https://github.com/versix1337/BoogPP/discussions

## Getting Help

- **Documentation**: See [docs/](docs/) directory
- **Issues**: Report bugs at https://github.com/versix1337/BoogPP/issues
- **Discussions**: Ask questions at https://github.com/versix1337/BoogPP/discussions

## License

BoogPP is licensed under the MIT License. See [LICENSE](LICENSE) file for details.
