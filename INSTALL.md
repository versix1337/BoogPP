# Boogpp Installation Guide

Complete installation guide for the Boogpp Programming Language.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Install](#quick-install)
- [Manual Installation](#manual-installation)
- [Verification](#verification)
- [IDE Setup](#ide-setup)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required
- **Python 3.8+** - For the compiler
- **GCC or Clang** - For building runtime and standard library
- **Make** - For build automation

### Optional
- **LLVM 14+** - For compiling to native binaries (llc, clang)
- **Git** - For cloning the repository
- **VS Code** - For IDE integration (future)

### Platform Support
- **Primary**: Windows 10/11 (x64)
- **Secondary**: Linux, macOS (runtime/compiler only)

## Quick Install

### Linux/macOS

```bash
# Clone repository
git clone https://github.com/versix1337/BoogPP.git
cd BoogPP

# Build and install
make
sudo make install

# Verify installation
boogpp version
```

### Windows

```powershell
# Clone repository
git clone https://github.com/versix1337/BoogPP.git
cd BoogPP

# Build (requires MinGW or WSL)
make

# Add to PATH or use directly
python -m boogpp.compiler.cli version
```

## Manual Installation

### Step 1: Build Runtime Library

```bash
cd boogpp/runtime
make release
```

Output: `lib/libboogpp_runtime.a`

### Step 2: Build Standard Library

```bash
cd ../stdlib/windows
make -f ../../Makefile.stdlib release
```

Output: `lib/libboogpp_windows.a`

### Step 3: Setup Compiler

```bash
cd ../../..
export PYTHONPATH="$PWD:$PYTHONPATH"
python3 -m boogpp.compiler.cli version
```

### Step 4: Install System-Wide (Optional)

```bash
sudo make install
```

This installs:
- Libraries to `/usr/local/lib/`
- Headers to `/usr/local/include/boogpp/`
- Compiler wrapper to `/usr/local/bin/boogpp`

## Directory Structure After Installation

```
/usr/local/
├── bin/
│   └── boogpp                      # Compiler wrapper
├── lib/
│   ├── libboogpp_runtime.a         # Runtime library
│   └── libboogpp_windows.a         # Windows stdlib
└── include/boogpp/
    ├── boogpp_runtime.h            # Runtime header
    └── boogpp_windows.h            # Windows header
```

## Verification

### Check Installation

```bash
# Check compiler version
boogpp version

# Should output: Boogpp Compiler v3.0.0

# Check libraries
ls -l /usr/local/lib/libboogpp_*

# Check headers
ls -l /usr/local/include/boogpp/
```

### Build Test Program

Create `hello.bpp`:
```boogpp
@safety_level(mode: SAFE)
module hello_world

import std.io

func main() -> i32:
    std.io.println("Hello from Boogpp!")
    return SUCCESS
```

Compile and check:
```bash
# Compile to LLVM IR
boogpp build hello.bpp -o hello.ll

# Check output
cat hello.ll
```

### Run Tests

```bash
# Run all tests
make test

# Run specific tests
cd boogpp/runtime && make test
cd boogpp && python test_compiler.py
cd boogpp && python test_phase2.py
```

## IDE Setup

### VS Code (Recommended)

1. Install VS Code
2. Install Python extension
3. Open BoogPP directory
4. Add to `settings.json`:

```json
{
    "python.analysis.extraPaths": [
        "${workspaceFolder}"
    ],
    "files.associations": {
        "*.bpp": "python"
    }
}
```

### Vim/Neovim

Add to `.vimrc` or `init.vim`:
```vim
au BufRead,BufNewFile *.bpp set filetype=python
```

### Emacs

Add to `.emacs`:
```elisp
(add-to-list 'auto-mode-alist '("\\.bpp\\'" . python-mode))
```

## Compiling to Native Binaries

### Requirements
- LLVM toolchain (`llc`, `clang`)

### Compilation Steps

```bash
# 1. Compile Boogpp to LLVM IR
boogpp build program.bpp -o program.ll

# 2. Compile LLVM IR to object file
llc -filetype=obj program.ll -o program.o

# 3. Link with runtime and stdlib
clang program.o \
    /usr/local/lib/libboogpp_runtime.a \
    /usr/local/lib/libboogpp_windows.a \
    -o program.exe

# 4. Run
./program.exe
```

### Automated Script

Create `bppcompile.sh`:
```bash
#!/bin/bash
PROG=$1
BASE=$(basename "$PROG" .bpp)

boogpp build "$PROG" -o "$BASE.ll" && \
llc -filetype=obj "$BASE.ll" -o "$BASE.o" && \
clang "$BASE.o" \
    /usr/local/lib/libboogpp_runtime.a \
    /usr/local/lib/libboogpp_windows.a \
    -o "$BASE.exe"

echo "Compiled: $BASE.exe"
```

Usage:
```bash
chmod +x bppcompile.sh
./bppcompile.sh program.bpp
```

## Environment Variables

### Optional Configuration

```bash
# Add to ~/.bashrc or ~/.zshrc

# Boogpp installation path
export BOOGPP_HOME=/usr/local

# Runtime library path
export BOOGPP_RUNTIME_LIB=$BOOGPP_HOME/lib/libboogpp_runtime.a

# Windows stdlib path
export BOOGPP_WINDOWS_LIB=$BOOGPP_HOME/lib/libboogpp_windows.a

# Include path
export BOOGPP_INCLUDE=$BOOGPP_HOME/include/boogpp
```

## Troubleshooting

### Common Issues

#### 1. "boogpp: command not found"

**Solution**: Add to PATH or use full path
```bash
export PATH="/usr/local/bin:$PATH"
# Or use: python3 -m boogpp.compiler.cli
```

#### 2. "No module named 'boogpp'"

**Solution**: Set PYTHONPATH
```bash
export PYTHONPATH="/path/to/BoogPP:$PYTHONPATH"
```

#### 3. Build fails on Windows

**Solution**: Use WSL or MinGW
```bash
# Install WSL2
wsl --install

# Or use MinGW-w64
# Install from https://www.mingw-w64.org/
```

#### 4. "Permission denied" during install

**Solution**: Use sudo
```bash
sudo make install
```

#### 5. Runtime tests fail

**Solution**: Check GCC version
```bash
gcc --version  # Should be 7.0+
make -C boogpp/runtime clean
make -C boogpp/runtime test
```

#### 6. Link errors when compiling to binary

**Solution**: Ensure LLVM installed
```bash
# Ubuntu/Debian
sudo apt install llvm clang

# macOS
brew install llvm

# Check versions
llc --version
clang --version
```

### Getting Help

- **Documentation**: See [README.md](README.md)
- **Issues**: https://github.com/versix1337/BoogPP/issues
- **Discussions**: https://github.com/versix1337/BoogPP/discussions

## Uninstallation

```bash
# Remove system installation
sudo make uninstall

# Remove build artifacts
make clean

# Remove repository
cd ..
rm -rf BoogPP
```

## Development Installation

For contributors and developers:

```bash
# Clone repository
git clone https://github.com/versix1337/BoogPP.git
cd BoogPP

# Setup development environment
make dev-setup

# Build in debug mode
cd boogpp/runtime && make debug
cd ../stdlib/windows && make -f ../../Makefile.stdlib debug

# Run tests
make test

# Build examples
make examples
```

## Docker Installation (Future)

Coming soon:
```bash
docker pull boogpp/boogpp:latest
docker run -it boogpp/boogpp boogpp version
```

## Platform-Specific Notes

### Windows
- Requires MinGW-w64 or WSL for building C components
- Native Windows build support coming soon
- Windows API bindings only work on Windows platform

### Linux
- Full support for all features
- Windows API functions return BPP_NOT_IMPLEMENTED

### macOS
- Full support for runtime and compiler
- Windows API functions return BPP_NOT_IMPLEMENTED

## Next Steps

After installation:

1. **Read the tutorial**: [docs/TUTORIAL.md](docs/TUTORIAL.md) (coming soon)
2. **Try examples**: `ls boogpp/examples/*.bpp`
3. **Read language spec**: [docs/LANGUAGE_SPEC.md](boogpp/docs/LANGUAGE_SPEC.md)
4. **Build something**: Start coding in Boogpp!

## License

MIT License - See [LICENSE](LICENSE) for details.
