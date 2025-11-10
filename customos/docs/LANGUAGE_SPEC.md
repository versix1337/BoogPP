# CustomOS Language Specification v1.0

## Overview
CustomOS is a Windows-centric systems programming language that combines Python-like syntax with C++ performance, compiled to native machine code via LLVM.

## Core Principles
1. **Safety by Default**: Operations are checked and logged by default
2. **Performance**: Compiles to native machine code via LLVM
3. **Windows Integration**: Deep OS integration with minimal boilerplate
4. **Resilience**: Built-in failover and retry mechanisms
5. **Readability**: Python-inspired syntax with whitespace-based structure

---

## 1. Type System

### Primitive Types
- `i8`, `i16`, `i32`, `i64` - Signed integers
- `u8`, `u16`, `u32`, `u64` - Unsigned integers
- `f32`, `f64` - Floating point numbers
- `bool` - Boolean (true/false)
- `string` - UTF-8 encoded strings
- `char` - Single character

### Compound Types
- `array[T, N]` - Fixed-size arrays
- `slice[T]` - Dynamic-size slices
- `ptr[T]` - Raw pointers (UNSAFE mode only)
- `tuple(T1, T2, ...)` - Tuples

### Special Types
- `status` - Status code (alias for i32)
- `handle` - Windows handle (alias for u64)
- `result[T]` - Result type (status, T)

---

## 2. Safety System

### Safety Modes

#### SAFE Mode (Default)
- Blocks dangerous operations
- Auto-logs all system calls
- Bounds checking on arrays
- No raw pointer access
- No process injection
- No kernel operations

#### UNSAFE Mode
- Full system access
- Process injection allowed
- Raw memory access
- Kernel driver operations
- Direct syscalls

#### CUSTOM Mode
- User-defined safety rules
- Granular permissions
- Custom validation functions

### Syntax
```customos
@safety_level(mode: SAFE)  # File-level

@unsafe  # Function-level override
func dangerousOperation() -> i32:
    # unsafe operations allowed here
    pass
```

---

## 3. Resilience System

### try_chain
Automatic fallback mechanism that tries multiple strategies:

```customos
return try_chain:
    primary:
        operation1()
    secondary:
        operation2()
    fallback:
        defaultValue
```

### Resilient Decorator
```customos
@resilient(max_attempts: 3, timeout: 2000ms, backoff: EXPONENTIAL)
func unstableOperation() -> result[string]:
    # Automatically retried on failure
    pass
```

### Status Codes
- `0x000000` - SUCCESS
- `0x000001` - GENERIC_ERROR
- `0x000002` - ACCESS_DENIED
- `0x000003` - TIMEOUT
- `0x000004` - NOT_FOUND
- `0x000005` - INVALID_PARAMETER

---

## 4. Windows Integration

### API Access
Direct Windows API access without FFI boilerplate:

```customos
import windows.kernel32
import windows.user32
import windows.registry

# Direct API calls
kernel32.CreateProcess(...)
user32.MessageBoxW(...)
registry.RegSetValueEx(...)
```

### System Hooks
```customos
@hook(event: PROCESS_CREATION)
func onProcessCreated(pid: u32, exe: string) -> i32:
    if suspicious(exe):
        return BLOCK_PROCESS
    return ALLOW_PROCESS

@hook(event: FILE_WRITE, path: "C:\Windows\System32\*")
func onSystemFileWrite(path: string) -> i32:
    log("Attempt to write: " + path)
    return ALLOW_OPERATION
```

### Supported Hook Events
- `PROCESS_CREATION`
- `PROCESS_TERMINATION`
- `FILE_WRITE`
- `FILE_READ`
- `FILE_DELETE`
- `REGISTRY_WRITE`
- `REGISTRY_READ`
- `NETWORK_CONNECTION`
- `DRIVER_LOAD`

### Service Decorator
```customos
@service(
    name: "CustomOSService",
    start_type: AUTO,
    run_as: SYSTEM,
    description: "CustomOS background service"
)
func mainService() -> i32:
    while isRunning():
        doWork()
        sleep(1000)
    return SUCCESS
```

---

## 5. Syntax

### Module Declaration
```customos
@safety_level(mode: SAFE)
@version("1.0.0")
module my_module
```

### Imports
```customos
import windows.registry
import windows.kernel32 as k32
from windows.user32 import MessageBoxW, FindWindowA
```

### Function Declaration
```customos
func add(a: i32, b: i32) -> i32:
    return a + b

func multiReturn() -> (i32, string):
    return 42, "hello"

func noReturn() -> void:
    print("No return value")
```

### Variables
```customos
let x: i32 = 42          # Immutable
var y: string = "hello"  # Mutable

# Type inference
let z = 100              # Inferred as i32
var name = "CustomOS"    # Inferred as string
```

### Control Flow
```customos
# If statements
if condition:
    doSomething()
elif otherCondition:
    doOther()
else:
    doDefault()

# While loops
while condition:
    doWork()

# For loops
for i in range(0, 10):
    print(i)

for item in collection:
    process(item)

# Pattern matching
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
@resilient(max_attempts: 3)
@log_calls
func myFunction() -> i32:
    pass
```

---

## 6. Memory Management

### Automatic Memory Management (SAFE mode)
Reference counted by default, with cycle detection.

### Manual Memory Management (UNSAFE mode)
```customos
@unsafe
func manualAlloc() -> ptr[u8]:
    let size = 1024
    let buffer = alloc(size)  # Manual allocation
    defer free(buffer)        # Automatic cleanup on scope exit
    return buffer
```

---

## 7. Interoperability

### C/C++ Integration
```customos
@extern("C")
func external_function(x: i32) -> i32

@export
func customos_function(x: i32) -> i32:
    return x * 2
```

### DLL Loading
```customos
import dll

let lib = dll.load("my_library.dll")
let func = lib.getFunction("MyFunction")
let result = func(arg1, arg2)
```

---

## 8. Kernel Driver Support

Compile to .sys files for kernel-mode drivers:

```customos
@safety_level(mode: UNSAFE)
@driver(
    name: "CustomDriver",
    type: KERNEL_MODE,
    entry_point: "DriverEntry"
)
module my_driver

import windows.kernel

func DriverEntry(driver: ptr[DRIVER_OBJECT], registry: ptr[UNICODE_STRING]) -> NTSTATUS:
    driver.DriverUnload = DriverUnload
    return STATUS_SUCCESS

func DriverUnload(driver: ptr[DRIVER_OBJECT]) -> void:
    # Cleanup
    pass
```

---

## 9. Standard Library

### Core Modules
- `std.io` - Input/output operations
- `std.fs` - File system operations
- `std.net` - Networking
- `std.time` - Time and date
- `std.thread` - Threading
- `std.sync` - Synchronization primitives

### Windows Modules
- `windows.kernel32` - Kernel32 API
- `windows.user32` - User32 API
- `windows.registry` - Registry access
- `windows.wmi` - WMI queries
- `windows.services` - Service management
- `windows.processes` - Process management
- `windows.network` - Network operations
- `windows.security` - Security APIs

---

## 10. Compilation

### Command Line
```bash
# Compile to executable
customos build main.cos -o output.exe

# Compile to DLL
customos build lib.cos --type dll -o library.dll

# Compile to kernel driver
customos build driver.cos --type driver -o driver.sys

# Safety mode override
customos build main.cos --safety unsafe -o output.exe

# Optimization levels
customos build main.cos -O0  # No optimization
customos build main.cos -O1  # Basic optimization
customos build main.cos -O2  # Standard optimization
customos build main.cos -O3  # Aggressive optimization
```

---

## 11. Example Programs

### Registry Monitor
```customos
@safety_level(mode: SAFE)
import windows.registry
import std.io

@resilient(max_attempts: 3, timeout: 5000ms)
func readRegistryKey(key: string, value: string) -> result[string]:
    status, data = windows.registry.read(key, value)
    return (status, data)

@hook(event: REGISTRY_WRITE, key: "HKLM\Software\*")
func onRegistryWrite(key: string, value: string, data: string) -> i32:
    std.io.log("Registry write: " + key + " = " + data)
    return ALLOW_OPERATION

func main() -> i32:
    result = try_chain:
        primary:
            readRegistryKey("HKLM\Software\Microsoft", "Version")
        secondary:
            ("SUCCESS", "DefaultVersion")
        fallback:
            ("ERROR", "Unknown")

    status, value = result
    print("Result: " + value)
    return SUCCESS
```

### Process Monitor Service
```customos
@safety_level(mode: SAFE)
import windows.processes
import std.io

@hook(event: PROCESS_CREATION)
func onProcessCreated(pid: u32, exe: string) -> i32:
    std.io.log("Process started: " + exe + " (PID: " + string(pid) + ")")

    if "malware" in exe.lower():
        std.io.log("BLOCKED: Suspicious process detected!")
        return BLOCK_PROCESS

    return ALLOW_PROCESS

@service(name: "ProcessMonitor", start_type: AUTO, run_as: SYSTEM)
func mainService() -> i32:
    std.io.log("Process Monitor Service started")

    while isRunning():
        sleep(1000)

    return SUCCESS

func main() -> i32:
    return mainService()
```

---

## 12. File Extension
- Source files: `.cos`
- Header files: `.cosh`
- Compiled binaries: `.exe`, `.dll`, `.sys`

---

## 13. Keywords
- `func` - Function declaration
- `let` - Immutable variable
- `var` - Mutable variable
- `if`, `elif`, `else` - Conditionals
- `while`, `for` - Loops
- `match`, `case` - Pattern matching
- `return` - Return from function
- `import`, `from` - Module imports
- `module` - Module declaration
- `struct` - Structure definition
- `enum` - Enumeration
- `trait` - Trait definition
- `impl` - Implementation
- `defer` - Deferred execution
- `try_chain` - Resilience mechanism
- `primary`, `secondary`, `fallback` - try_chain keywords
- `true`, `false` - Boolean literals

---

## 14. Operators

### Arithmetic
`+`, `-`, `*`, `/`, `%`, `**` (power)

### Comparison
`==`, `!=`, `<`, `>`, `<=`, `>=`

### Logical
`and`, `or`, `not`

### Bitwise
`&`, `|`, `^`, `~`, `<<`, `>>`

### Assignment
`=`, `+=`, `-=`, `*=`, `/=`, `%=`, `&=`, `|=`, `^=`

---

## 15. Comments
```customos
# Single line comment

###
Multi-line comment
block
###
```

---

This specification provides the foundation for CustomOS. Implementation details and runtime behavior are defined in the compiler and runtime documentation.
