# BoogPP API Reference

Complete reference for BoogPP standard library and Windows API bindings.

## Table of Contents

- [Runtime API](#runtime-api)
- [Standard Library](#standard-library)
- [Windows API Bindings](#windows-api-bindings)
- [Type System](#type-system)
- [Status Codes](#status-codes)

---

## Runtime API

### Memory Management

#### `bpp_alloc(size: u64) -> ptr[u8]`

Allocates memory from the heap.

**Parameters:**
- `size`: Number of bytes to allocate

**Returns:**
- Pointer to allocated memory, or `null` on failure

**Example:**
```boogpp
buffer: ptr[u8] = bpp_alloc(1024)
if buffer == null:
    return OUT_OF_MEMORY
```

#### `bpp_free(ptr: ptr[u8]) -> void`

Frees previously allocated memory.

**Parameters:**
- `ptr`: Pointer to memory to free

**Example:**
```boogpp
bpp_free(buffer)
```

#### `bpp_realloc(ptr: ptr[u8], size: u64) -> ptr[u8]`

Reallocates memory to a different size.

**Parameters:**
- `ptr`: Pointer to existing allocation
- `size`: New size in bytes

**Returns:**
- Pointer to reallocated memory

**Example:**
```boogpp
buffer = bpp_realloc(buffer, 2048)
```

### String Operations

#### `bpp_string_new(cstr: ptr[char]) -> ptr[bpp_string_t]`

Creates a new BoogPP string from a C string.

**Parameters:**
- `cstr`: Null-terminated C string

**Returns:**
- New string object

**Example:**
```boogpp
str: ptr[bpp_string_t] = bpp_string_new("Hello")
```

#### `bpp_string_concat(s1: ptr[bpp_string_t], s2: ptr[bpp_string_t]) -> ptr[bpp_string_t]`

Concatenates two strings.

**Parameters:**
- `s1`: First string
- `s2`: Second string

**Returns:**
- New concatenated string

**Example:**
```boogpp
result: ptr[bpp_string_t] = bpp_string_concat(hello, world)
```

#### `bpp_string_length(str: ptr[bpp_string_t]) -> u64`

Gets the length of a string in bytes.

**Parameters:**
- `str`: String to measure

**Returns:**
- Length in bytes

**Example:**
```boogpp
length: u64 = bpp_string_length(str)
```

### I/O Operations

#### `println(str: string) -> status`

Prints a string to stdout with a newline.

**Parameters:**
- `str`: String to print

**Returns:**
- `SUCCESS` on success, error code on failure

**Example:**
```boogpp
println("Hello, World!")
```

#### `print(str: string) -> status`

Prints a string to stdout without a newline.

#### `log(message: string) -> status`

Logs a message with timestamp to stderr.

#### `read_line() -> string`

Reads a line from stdin.

**Returns:**
- String containing the input line

**Example:**
```boogpp
name: string = read_line()
println(f"Hello, {name}!")
```

---

## Standard Library

### std.io

#### File Operations

```boogpp
import std.io

# Open file
file: handle = std.io.open("file.txt", "r")

# Read file
content: string = std.io.read_file("file.txt")

# Write file
std.io.write_file("output.txt", "data")

# Close file
std.io.close(file)
```

### std.fs

#### File System Operations

```boogpp
import std.fs

# Create directory
std.fs.create_directory("mydir")

# Delete file
std.fs.delete("file.txt")

# Copy file
std.fs.copy("source.txt", "dest.txt")

# Move file
std.fs.move("old.txt", "new.txt")

# Check if file exists
if std.fs.exists("file.txt"):
    println("File exists")

# Get file size
size: u64 = std.fs.get_size("file.txt")
```

### std.net

#### Network Operations

```boogpp
import std.net

# HTTP GET request
response: string = std.net.http_get("https://api.example.com/data")

# HTTP POST request
response: string = std.net.http_post("https://api.example.com/submit", data)

# TCP client
socket: handle = std.net.tcp_connect("127.0.0.1", 8080)
std.net.send(socket, data, data_size)
std.net.close(socket)
```

### std.time

#### Time Operations

```boogpp
import std.time

# Get current timestamp
timestamp: u64 = std.time.now()

# Sleep
std.time.sleep(1000)  # milliseconds

# Format time
time_str: string = std.time.format(timestamp, "%Y-%m-%d %H:%M:%S")
```

---

## Windows API Bindings

### windows.registry

#### Registry Read/Write

```boogpp
import windows.registry

# Read string value
value: array[char, 256]
status: status = windows.registry.read(
    "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",
    "ProductName",
    value,
    256
)

# Write string value
windows.registry.write(
    "HKCU\\SOFTWARE\\MyApp",
    "Setting",
    "Value"
)

# Delete value
windows.registry.delete(
    "HKCU\\SOFTWARE\\MyApp",
    "OldSetting"
)

# Read DWORD
dword_value: u32
windows.registry.read_dword(key, value_name, &dword_value)

# Write DWORD
windows.registry.write_dword(key, value_name, 42)
```

#### Registry Enumeration

```boogpp
# Enumerate subkeys
subkeys: array[ptr[char], 128]
count: u64
windows.registry.enum_keys(key_path, subkeys, 128, &count)

for i in range(count):
    println(f"Subkey: {subkeys[i]}")

# Enumerate values
value_names: array[ptr[char], 256]
value_count: u64
windows.registry.enum_values(key_path, value_names, 256, &value_count)
```

#### Registry Watching

```boogpp
# Watch for changes
watch_handle: handle
windows.registry.watch(
    "HKCU\\SOFTWARE\\MyApp",
    NOTIFY_CHANGE_LAST_SET,
    on_change_callback,
    user_data,
    &watch_handle
)

# Unwatch
windows.registry.unwatch(watch_handle)
```

### windows.process

#### Process Management

```boogpp
import windows.process

# List processes
processes: array[PROCESS_INFO, 512]
count: u64
windows.process.list(processes, 512, &count)

for i in range(count):
    println(f"PID: {processes[i].pid}, Name: {processes[i].name}")

# Start process
pid: u32
windows.process.start("notepad.exe", "", &pid)

# Terminate process
windows.process.terminate(pid)

# Check if process is running
if windows.process.is_running(pid):
    println("Process is running")
```

#### Process Memory Operations

```boogpp
# Read process memory
buffer: array[u8, 256]
bytes_read: u64
windows.process.read_memory(pid, address, buffer, 256, &bytes_read)

# Write process memory
data: array[u8, 64]
bytes_written: u64
windows.process.write_memory(pid, address, data, 64, &bytes_written)

# Allocate memory in remote process
remote_addr: u64
windows.process.alloc_memory(pid, 4096, PAGE_EXECUTE_READWRITE, &remote_addr)

# Free remote memory
windows.process.free_memory(pid, remote_addr)
```

#### Process Injection

```boogpp
@safety_level(mode: UNSAFE)

# DLL injection
windows.process.inject_dll(
    pid,
    "C:\\tools\\injected.dll",
    INJECT_CREATEREMOTETHREAD
)

# Shellcode injection
shellcode: array[u8, 256] = [...]
windows.process.inject_shellcode(
    pid,
    shellcode,
    256,
    INJECT_CREATEREMOTETHREAD
)
```

### windows.pe

#### PE File Operations

```boogpp
import windows.pe

# Load PE file
pe_data: ptr[u8]
pe_size: u64
windows.pe.load("program.exe", &pe_data, &pe_size)

# Get PE information
info: PE_INFO
windows.pe.get_info(pe_data, &info)

println(f"Machine: {info.machine}")
println(f"Image Base: 0x{info.image_base:X}")
println(f"Entry Point: 0x{info.entry_point:X}")

# Get sections
sections: array[PE_SECTION, 32]
section_count: u64
windows.pe.get_sections(pe_data, sections, 32, &section_count)

for i in range(section_count):
    println(f"Section: {sections[i].name}")
    println(f"  RVA: 0x{sections[i].virtual_address:X}")
    println(f"  Size: {sections[i].virtual_size}")

# Patch bytes
patch_data: array[u8, 16] = [0x90, 0x90, ...]
windows.pe.patch_bytes(pe_data, 0x1000, patch_data, 16)

# Save modified PE
windows.pe.save("program_patched.exe", pe_data, pe_size)

# Cleanup
free(pe_data)
```

#### PE Import/Export

```boogpp
# Get imports
imports: array[PE_IMPORT, 512]
import_count: u64
windows.pe.get_imports(pe_data, imports, 512, &import_count)

for i in range(import_count):
    println(f"Import: {imports[i].dll_name}!{imports[i].function_name}")
```

### windows.service

#### Service Management

```boogpp
import windows.service

# Create service
windows.service.create(
    "MyService",
    "My Windows Service",
    "C:\\services\\myservice.exe"
)

# Start service
windows.service.start("MyService")

# Stop service
windows.service.stop("MyService")

# Get service state
state: SERVICE_STATE
windows.service.get_state("MyService", &state)

match state:
    RUNNING:
        println("Service is running")
    STOPPED:
        println("Service is stopped")
    _:
        println(f"Service state: {state}")

# Delete service
windows.service.delete("MyService")
```

#### Service Development

```boogpp
@service(
    name: "MonitorService",
    display_name: "System Monitor Service",
    start_type: AUTO
)
func service_main() -> i32:
    log("Service started")

    while service_running():
        # Service logic here
        perform_monitoring()
        sleep(5000)

    log("Service stopped")
    return SUCCESS
```

### windows.driver

#### Driver Operations

```boogpp
@safety_level(mode: UNSAFE)
import windows.driver
import windows.token

# Enable privilege
windows.token.enable_privilege(PRIVILEGE_LOAD_DRIVER)

# Load driver
windows.driver.load("C:\\drivers\\mydriver.sys", "MyDriver")

# Send IOCTL
output_buffer: array[u8, 256]
bytes_returned: u64
windows.driver.ioctl(
    "\\\\.\\MyDriver",
    0x222000,  # IOCTL_CODE
    input_buffer, input_size,
    output_buffer, 256,
    &bytes_returned
)

# Unload driver
windows.driver.unload("MyDriver")
```

### windows.token

#### Token and Privilege Management

```boogpp
import windows.token

# Enable privilege
windows.token.enable_privilege(PRIVILEGE_DEBUG)
windows.token.enable_privilege(PRIVILEGE_LOAD_DRIVER)
windows.token.enable_privilege(PRIVILEGE_BACKUP)

# Disable privilege
windows.token.disable_privilege(PRIVILEGE_DEBUG)

# Get current user SID
sid: array[char, 256]
windows.token.get_user_sid(sid, 256)

# Elevate to SYSTEM
windows.token.elevate_to_system()

# Impersonate process
windows.token.impersonate_process(target_pid)

# Revert to self
windows.token.revert_to_self()
```

### windows.hook

#### API Hooking

```boogpp
@safety_level(mode: UNSAFE)
import windows.hook

# Install Windows hook
hook_handle: handle
windows.hook.install(
    HOOK_KEYBOARD,
    on_keyboard_event,
    user_data,
    &hook_handle
)

func on_keyboard_event(code: i32, wparam: u64, lparam: u64, user_data: ptr[void]) -> void:
    println(f"Key pressed: {wparam}")

# Uninstall hook
windows.hook.uninstall(hook_handle)

# Inline hook (function detour)
original_func: ptr[void]
windows.hook.inline_install(
    target_function,
    hook_function,
    &original_func
)

# IAT hook
windows.hook.iat(
    module_handle,
    "kernel32.dll",
    "CreateFileW",
    hooked_createfile,
    &original_createfile
)
```

---

## Type System

### Primitive Types

| Type | Description | Size |
|------|-------------|------|
| `i8` | Signed 8-bit integer | 1 byte |
| `i16` | Signed 16-bit integer | 2 bytes |
| `i32` | Signed 32-bit integer | 4 bytes |
| `i64` | Signed 64-bit integer | 8 bytes |
| `u8` | Unsigned 8-bit integer | 1 byte |
| `u16` | Unsigned 16-bit integer | 2 bytes |
| `u32` | Unsigned 32-bit integer | 4 bytes |
| `u64` | Unsigned 64-bit integer | 8 bytes |
| `f32` | 32-bit floating point | 4 bytes |
| `f64` | 64-bit floating point | 8 bytes |
| `bool` | Boolean | 1 byte |
| `char` | Character | 1 byte |
| `string` | UTF-8 string | Variable |
| `status` | Status code (i32) | 4 bytes |
| `handle` | OS handle (u64) | 8 bytes |

### Composite Types

```boogpp
# Pointers
ptr[i32]           # Pointer to i32
ptr[ptr[u8]]       # Pointer to pointer to u8

# Arrays
array[i32, 100]    # Fixed-size array of 100 i32s

# Slices
slice[u8]          # Dynamic slice of u8

# Tuples
tuple(i32, string) # Tuple of i32 and string

# Results
result[string]     # Result type holding string or error
```

---

## Status Codes

### Standard Status Codes

| Code | Value | Description |
|------|-------|-------------|
| `SUCCESS` | 0x000000 | Operation succeeded |
| `GENERIC_ERROR` | 0x000001 | Generic error occurred |
| `ACCESS_DENIED` | 0x000002 | Access was denied |
| `TIMEOUT` | 0x000003 | Operation timed out |
| `NOT_FOUND` | 0x000004 | Resource not found |
| `INVALID_PARAMETER` | 0x000005 | Invalid parameter |
| `OUT_OF_MEMORY` | 0x000006 | Out of memory |
| `BUFFER_TOO_SMALL` | 0x000007 | Buffer too small |
| `NOT_IMPLEMENTED` | 0x000008 | Not implemented |

### Usage

```boogpp
func do_something() -> status:
    if condition_failed:
        return GENERIC_ERROR

    return SUCCESS

# Check status
result: status = do_something()
if result != SUCCESS:
    log(f"Error: {bpp_status_string(result)}")
```

---

## Error Handling

### try_chain

```boogpp
result: status = try_chain {
    primary_operation()
} or {
    secondary_operation()
} else {
    log("All operations failed")
    return GENERIC_ERROR
}
```

### @resilient Decorator

```boogpp
@resilient(max_retries: 3, timeout: 5000)
func unreliable_operation() -> status:
    # Will automatically retry up to 3 times with timeout
    return perform_operation()
```

---

## Constants

### Safety Modes

```boogpp
SAFE       # Safe mode (default)
UNSAFE     # Unsafe mode
CUSTOM     # Custom safety rules
```

### Memory Protection

```boogpp
PAGE_EXECUTE            # Execute access
PAGE_EXECUTE_READ       # Execute and read
PAGE_EXECUTE_READWRITE  # Execute, read, write
PAGE_READONLY           # Read-only
PAGE_READWRITE          # Read and write
```

### Injection Methods

```boogpp
INJECT_CREATEREMOTETHREAD   # CreateRemoteThread
INJECT_QUEUEUSERAPC         # QueueUserAPC
INJECT_SETWINDOWSHOOKEX     # SetWindowsHookEx
INJECT_THREAD_HIJACKING     # Thread hijacking
INJECT_PROCESS_HOLLOWING    # Process hollowing
```

---

For more information, see the [Language Specification](LANGUAGE_SPEC.md) and [Standard Library Guide](STDLIB.md).
