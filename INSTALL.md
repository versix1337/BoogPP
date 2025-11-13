# BoogPP Installation Guide

This guide explains how to install BoogPP as a Python package for easy maintenance and updates.

## Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package installer)
- **Windows 10/11** (for full Windows API support)
- **LLVM 14+** (optional, required for native executable compilation)

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
