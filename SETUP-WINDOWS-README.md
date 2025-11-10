# Windows Setup Scripts

Two automated setup scripts are provided for Windows users to easily install all dependencies and build Boogpp.

## Quick Start

### Option 1: PowerShell Script (Recommended)

```powershell
# Run as Administrator (right-click PowerShell, "Run as Administrator")
Set-ExecutionPolicy Bypass -Scope Process -Force
.\setup-windows.ps1
```

### Option 2: Batch Script

```cmd
# Run as Administrator (right-click cmd, "Run as Administrator")
setup-windows.bat
```

## What These Scripts Do

Both scripts perform the following steps automatically:

1. **Check Python** - Verifies Python 3.8+ is installed
2. **Install Chocolatey** - Installs the Windows package manager (if needed)
3. **Install MinGW/GCC** - Installs the C compiler for building runtime
4. **Install Make** - Installs the build automation tool
5. **Check LLVM** - Checks for LLVM (optional, for native binaries)
6. **Build Boogpp** - Compiles runtime, stdlib, and verifies compiler

## Prerequisites

- **Windows 10/11** (64-bit)
- **Internet connection** (for downloading dependencies)
- **Administrator privileges** (for installing tools)

## What Gets Installed

### Via Chocolatey
- MinGW-w64 (GCC compiler)
- Make (build tool)

### Already Required
- Python 3.8+ (must be pre-installed)

### Optional
- LLVM 14+ (for compiling to native .exe files)

## After Installation

Once the script completes, you'll have:

1. **Built Libraries**:
   - `boogpp\runtime\lib\libboogpp_runtime.a`
   - `boogpp\stdlib\windows\lib\libboogpp_windows.a`

2. **Wrapper Scripts**:
   - `boogpp.bat` - Run Boogpp compiler from anywhere
   - `boogpp.psm1` - PowerShell module for Boogpp

3. **Ready to Use**:
   ```cmd
   python -m boogpp.compiler.cli build program.bpp -o program.ll
   ```

   Or with wrapper:
   ```cmd
   .\boogpp.bat build program.bpp -o program.ll
   ```

## Troubleshooting

### Script won't run (PowerShell)

**Error**: "Execution policy prevents running scripts"

**Solution**:
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
.\setup-windows.ps1
```

### Permission Denied

**Solution**: Run as Administrator
- Right-click PowerShell or Command Prompt
- Select "Run as Administrator"
- Run the script again

### Python not found

**Solution**: Install Python first
1. Download from https://www.python.org/downloads/
2. **Important**: Check "Add Python to PATH" during installation
3. Restart terminal and run script again

### Chocolatey installation fails

**Solution**: Install manually
1. Follow instructions at https://chocolatey.org/install
2. Run the setup script again

### MinGW installation fails

**Solution**: Install MinGW manually
1. Download from https://www.mingw-w64.org/
2. Add to PATH: `C:\mingw64\bin`
3. Run setup script again

### Build fails with "make: command not found"

**Solution**: Use mingw32-make
```cmd
# The script should auto-detect this
# If not, manually use:
cd boogpp\runtime
mingw32-make release
```

### LLVM not found (Optional)

This is optional. You can still use Boogpp to compile to LLVM IR.

**To install LLVM**:
1. Download from https://releases.llvm.org/download.html
2. Choose Windows installer (64-bit)
3. Add to PATH during installation
4. Restart terminal

## Manual Installation Alternative

If the automated scripts don't work, follow the manual steps in [INSTALL.md](INSTALL.md).

## Verification

After running the setup script, verify installation:

```cmd
# Check Python
python --version

# Check GCC
gcc --version

# Check Make
make --version
# OR
mingw32-make --version

# Check LLVM (optional)
llc --version

# Test Boogpp compiler
python -m boogpp.compiler.cli version
```

## Next Steps

1. **Try the examples**:
   ```cmd
   cd boogpp\examples
   python -m boogpp.compiler.cli build 01_hello_world.bpp -o hello.ll
   ```

2. **Run tests**:
   ```cmd
   cd boogpp\runtime
   mingw32-make test
   ```

3. **Read documentation**:
   - [README.md](README.md) - Project overview
   - [INSTALL.md](INSTALL.md) - Detailed installation guide
   - [boogpp/docs/LANGUAGE_SPEC.md](boogpp/docs/LANGUAGE_SPEC.md) - Language reference

## Uninstalling Dependencies

If you want to remove the installed tools:

```cmd
# Using Chocolatey
choco uninstall mingw -y
choco uninstall make -y
```

## Script Features

### PowerShell Script (`setup-windows.ps1`)
- ✅ Better error handling
- ✅ Colored output
- ✅ Creates PowerShell module
- ✅ More detailed progress messages
- ✅ Automatic environment refresh

### Batch Script (`setup-windows.bat`)
- ✅ Works on older Windows versions
- ✅ No execution policy issues
- ✅ Simple and straightforward
- ✅ Compatible with all cmd variants

## Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section above
2. See [INSTALL.md](INSTALL.md) for manual installation
3. Open an issue at: https://github.com/versix1337/BoogPP/issues

## License

These setup scripts are part of the Boogpp project and are licensed under the MIT License.
