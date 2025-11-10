# CustomOS

A Windows-centric systems programming language combining Python-like syntax with C++ performance.

## Overview

CustomOS is designed specifically for Windows system customization, featuring:

- **Python-like Syntax** - Clean, readable, whitespace-based
- **C++ Performance** - Compiles to native machine code via LLVM
- **Safety by Default** - SAFE/UNSAFE/CUSTOM modes with compile-time checks
- **Windows Integration** - Deep OS integration with minimal boilerplate
- **Built-in Resilience** - `try_chain` for automatic failover

## Quick Start

```customos
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
```customos
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

Full documentation is available in the [`customos/`](customos/) directory:

- [Language Specification](customos/docs/LANGUAGE_SPEC.md)
- [Windows API Reference](customos/stdlib/windows/README.md)
- [Examples](customos/examples/)
- [Getting Started](customos/README.md)

## Installation

```bash
# Clone the repository
git clone https://github.com/versix1337/CehSim.git
cd CehSim/customos

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_compiler.py
```

## Examples

See the [examples directory](customos/examples/) for complete working examples including:

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
customos build main.cos -o output.exe

# Compile with specific safety mode
customos build main.cos --safety unsafe -o output.exe

# Compile to Windows service
customos build service.cos --type service -o service.exe

# Check syntax without compiling
customos check main.cos
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

Contributions are welcome! Please see the [CustomOS directory](customos/) for development guidelines.

---

**CustomOS** - Write Windows system tools with Python-like simplicity and C++ performance.
