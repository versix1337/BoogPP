# Boog++

A Windows-centric systems programming language combining Python-like syntax with C++ performance.

## Overview

Boog++ is designed specifically for Windows system customization, featuring:

- **Python-like Syntax** - Clean, readable, whitespace-based
- **C++ Performance** - Compiles to native machine code via LLVM
- **Safety by Default** - SAFE/UNSAFE/CUSTOM modes with compile-time checks
- **Windows Integration** - Deep OS integration with minimal boilerplate
- **Built-in Resilience** - `try_chain` for automatic failover

## Quick Start

```boogpp
@safety_level(mode: SAFE)
import windows.registry

func main() -> i32:
    status, version = windows.registry.read(
        "HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion",
        "ProductName"
    )

    if status == SUCCESS:
        print("Windows: " + version)

    return SUCCESS
```

## Features

### Safety System
- **SAFE Mode** (Default) - Blocks dangerous operations, auto-logs everything
- **UNSAFE Mode** - Full access for experts (process injection, memory access, kernel ops)
- **CUSTOM Mode** - User-defined safety rules

### Resilience
```boogpp
return try_chain:
    primary:
        http.post(url, data)
    secondary:
        http.post(backup_url, data)
    fallback:
        cache.get(data)
```

### Windows Integration
- Direct API access (kernel32, user32, registry, WMI)
- System hooks (`@hook` decorator)
- Service creation (`@service` decorator)
- Kernel driver support
- Process monitoring and injection

## Documentation

Full documentation is available in the [`boogpp/`](boogpp/) directory:

- [Language Specification](boogpp/docs/LANGUAGE_SPEC.md)
- [Windows API Reference](boogpp/stdlib/windows/README.md)
- [Examples](boogpp/examples/)
- [Getting Started](boogpp/README.md)

## Installation

```bash
# Clone the repository
git clone https://github.com/versix1337/CehSim.git
cd CehSim/boogpp

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_compiler.py
```

## Examples

See the [examples directory](boogpp/examples/) for complete working examples including:

1. Registry access with resilience
2. Process monitoring with hooks
3. Windows service creation
4. File system protection
5. Network monitoring
6. Registry protection
7. Advanced failover scenarios

## Compilation

```bash
# Compile to executable
boogpp build main.bpp -o output.exe

# Compile with specific safety mode
boogpp build main.bpp --safety unsafe -o output.exe

# Compile to Windows service
boogpp build service.bpp --type service -o service.exe

# Check syntax without compiling
boogpp check main.bpp
```

## Status

**Current Version:** 1.0.0 (Prototype)

**Implemented:**
- ✅ Lexer/Tokenizer
- ✅ Parser and AST
- ✅ Safety system
- ✅ CLI interface
- ✅ Example programs

**In Progress:**
- 🚧 Type checker
- 🚧 LLVM code generator
- 🚧 Runtime library

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please see the [Boog++ directory](boogpp/) for development guidelines.

---

**Boog++** - Write Windows system tools with Python-like simplicity and C++ performance.
