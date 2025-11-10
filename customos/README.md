# CustomOS Programming Language

**A Windows-centric systems programming language combining Python-like syntax with C++ performance.**

CustomOS is designed specifically for Windows system customization, with deep OS integration, built-in safety mechanisms, and automatic resilience features.

---

## Features

### 🎯 Core Features

- **Python-like Syntax** - Clean, readable, whitespace-based syntax
- **C++ Performance** - Compiles to native machine code via LLVM
- **Safety by Default** - Built-in safety checks with SAFE/UNSAFE/CUSTOM modes
- **Windows-Centric** - Deep OS integration with minimal boilerplate
- **Built-in Resilience** - `try_chain` for automatic failover and retry logic

### 🔒 Safety System

Three safety modes to balance security and flexibility:

- **SAFE Mode** (Default) - Blocks dangerous operations, auto-logs system calls
- **UNSAFE Mode** - Full system access for experts (process injection, memory access, kernel operations)
- **CUSTOM Mode** - User-defined safety rules with granular permissions

### 🔄 Resilience & Error Handling

```customos
return try_chain:
    primary:
        http.post(url, data)
    secondary:
        http.post(backup_url, data)
    fallback:
        cache.get(data)
```

- Automatic failover mechanism
- Built-in retry logic with exponential backoff
- Status code-based error handling (no exceptions)
- `@resilient` decorator for automatic retries

### 🪟 Windows Integration

Direct Windows API access without FFI boilerplate:

- Pre-built bindings for kernel32, user32, registry, WMI, etc.
- System hooks with `@hook` decorators
- Service creation with `@service` decorator
- Kernel driver support (compile to .sys files)
- Registry manipulation with safety checks
- Process injection (in UNSAFE mode)

---

## Quick Start

### Hello World

```customos
@safety_level(mode: SAFE)
module hello_world

import std.io

func main() -> i32:
    std.io.println("Hello from CustomOS!")
    return SUCCESS
```

### Registry Reader with Resilience

```customos
@safety_level(mode: SAFE)
import windows.registry

@resilient(max_attempts: 3, timeout: 2000ms)
func readRegistry(key: string, value: string) -> (i32, string):
    return try_chain:
        primary:
            windows.registry.read(key, value)
        secondary:
            cache.get(key + value)
        fallback:
            (SUCCESS, "DEFAULT")

func main() -> i32:
    status, version = readRegistry(
        "HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion",
        "ProductName"
    )

    if status == SUCCESS:
        print("Windows: " + version)

    return SUCCESS
```

### Process Monitor with Hooks

```customos
@safety_level(mode: SAFE)
import windows.processes
import std.io

@hook(event: PROCESS_CREATION)
func onProcessCreated(pid: u32, exe: string) -> i32:
    std.io.log("Process started: " + exe)

    if "malware" in exe.lower():
        std.io.log("BLOCKED: Suspicious process!")
        return BLOCK_PROCESS

    return ALLOW_PROCESS

func main() -> i32:
    std.io.println("Process Monitor Active")

    while true:
        sleep(1000)

    return SUCCESS
```

### Windows Service

```customos
@service(
    name: "CustomOSService",
    start_type: AUTO,
    run_as: SYSTEM
)
func mainService() -> i32:
    while isRunning():
        # Service logic here
        sleep(1000)
    return SUCCESS
```

---

## Installation

### Prerequisites

- Python 3.8+
- LLVM 14+ (for code generation)
- Windows 10/11 (primary target)

### Install CustomOS Compiler

```bash
# Clone the repository
git clone https://github.com/yourusername/customos.git
cd customos

# Install dependencies
pip install -r requirements.txt

# Install compiler
pip install -e .
```

---

## Compilation

### Basic Compilation

```bash
# Compile to executable
customos build main.cos -o output.exe

# Compile to DLL
customos build library.cos --type dll -o library.dll

# Compile to kernel driver
customos build driver.cos --type driver -o driver.sys
```

### Safety Mode Override

```bash
# Compile in UNSAFE mode
customos build main.cos --safety unsafe -o output.exe

# Compile in CUSTOM mode
customos build main.cos --safety custom -o output.exe
```

### Optimization Levels

```bash
customos build main.cos -O0  # No optimization
customos build main.cos -O1  # Basic optimization
customos build main.cos -O2  # Standard optimization (default)
customos build main.cos -O3  # Aggressive optimization
```

### Syntax Checking

```bash
# Check syntax and safety without compiling
customos check main.cos
```

---

## Language Syntax

### Types

**Primitive Types:**
- `i8`, `i16`, `i32`, `i64` - Signed integers
- `u8`, `u16`, `u32`, `u64` - Unsigned integers
- `f32`, `f64` - Floating point
- `bool` - Boolean
- `string` - UTF-8 strings
- `char` - Single character

**Compound Types:**
- `array[T, N]` - Fixed-size arrays
- `slice[T]` - Dynamic slices
- `ptr[T]` - Raw pointers (UNSAFE)
- `tuple(T1, T2, ...)` - Tuples
- `result[T]` - Result type (status, T)

### Variables

```customos
let x: i32 = 42          # Immutable
var y: string = "hello"  # Mutable

# Type inference
let z = 100              # Inferred as i32
```

### Functions

```customos
func add(a: i32, b: i32) -> i32:
    return a + b

func multiReturn() -> (i32, string):
    return 42, "hello"

func noReturn() -> void:
    print("No return value")
```

### Control Flow

```customos
# If statements
if condition:
    doSomething()
elif other:
    doOther()
else:
    doDefault()

# While loops
while condition:
    doWork()

# For loops
for i in range(0, 10):
    print(i)

# Match statements
match value:
    case 0:
        handleZero()
    case 1..10:
        handleSmall()
    case _:
        handleOther()
```

### Decorators

```customos
@hook(event: PROCESS_CREATION)
@resilient(max_attempts: 3, timeout: 5000ms)
@log_calls
func myFunction() -> i32:
    pass
```

---

## Windows API Modules

### Available Modules

- `windows.kernel32` - Core Windows operations
- `windows.user32` - UI and window management
- `windows.registry` - Registry access
- `windows.services` - Service management
- `windows.processes` - Process management
- `windows.network` - Network operations
- `windows.wmi` - WMI queries
- `windows.security` - Security APIs

See [Windows API Documentation](stdlib/windows/README.md) for complete API reference.

---

## Examples

The `examples/` directory contains complete working examples:

1. **01_hello_world.cos** - Basic syntax demonstration
2. **02_registry_reader.cos** - Registry access with resilience
3. **03_process_monitor.cos** - Process monitoring with hooks
4. **04_system_service.cos** - Windows service creation
5. **05_file_system_guard.cos** - File system protection
6. **06_network_monitor.cos** - Network connection monitoring
7. **07_registry_guard.cos** - Registry protection
8. **08_advanced_resilience.cos** - Complex failover scenarios

### Running Examples

```bash
# Compile and run an example
customos build examples/01_hello_world.cos -o hello.exe
./hello.exe

# Check example syntax
customos check examples/03_process_monitor.cos
```

---

## Project Structure

```
customos/
├── compiler/           # Compiler implementation
│   ├── lexer/         # Lexical analyzer
│   ├── parser/        # Parser and AST
│   ├── typechecker/   # Type system
│   ├── codegen/       # LLVM code generator
│   ├── safety/        # Safety checker
│   └── cli.py         # Command-line interface
├── runtime/           # Runtime library
├── stdlib/            # Standard library
│   └── windows/       # Windows API bindings
├── examples/          # Example programs
├── docs/              # Documentation
│   └── LANGUAGE_SPEC.md  # Language specification
└── tests/             # Test suite
```

---

## Safety System Details

### SAFE Mode (Default)

**Blocked Operations:**
- Raw pointer access
- Process injection
- Kernel operations
- Direct memory manipulation

**Logged Operations:**
- Registry writes
- Service creation
- Process termination
- Sensitive file operations

### UNSAFE Mode

Full system access. Use with caution.

```customos
@safety_level(mode: UNSAFE)
module dangerous_app

@unsafe
func inject_dll(pid: u32, dll_path: string) -> i32:
    # Process injection allowed in UNSAFE mode
    return windows.processes.inject_dll(pid, dll_path)
```

### CUSTOM Mode

Define your own safety rules:

```customos
@safety_level(mode: CUSTOM)
@allow_operations(["registry.write", "processes.kill"])
module custom_safety
```

---

## Status Codes

All operations return status codes:

- `0x000000` (SUCCESS) - Operation succeeded
- `0x000001` (GENERIC_ERROR) - Generic error
- `0x000002` (ACCESS_DENIED) - Access denied
- `0x000003` (TIMEOUT) - Operation timed out
- `0x000004` (NOT_FOUND) - Resource not found
- `0x000005` (INVALID_PARAMETER) - Invalid parameter

---

## Development Status

**Current Version:** 1.0.0 (Prototype)

**Implemented:**
- ✅ Lexer/Tokenizer
- ✅ Parser and AST
- ✅ Safety system
- ✅ Example programs
- ✅ CLI interface

**In Progress:**
- 🚧 Type checker
- 🚧 LLVM code generator
- 🚧 Runtime library
- 🚧 Windows API bindings

**Planned:**
- 📋 Standard library completion
- 📋 Debugger integration
- 📋 IDE support (VS Code extension)
- 📋 Package manager

---

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/customos.git
cd customos

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linter
pylint customos/compiler/
```

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- Inspired by Python's readability and Rust's safety
- LLVM for compilation backend
- Windows API for system integration

---

## Documentation

- [Language Specification](docs/LANGUAGE_SPEC.md) - Complete language reference
- [Windows API Reference](stdlib/windows/README.md) - Windows bindings documentation
- [Examples](examples/) - Working code examples

---

## Contact

- Issues: https://github.com/yourusername/customos/issues
- Discussions: https://github.com/yourusername/customos/discussions

---

**CustomOS** - Write Windows system tools with Python-like simplicity and C++ performance.
