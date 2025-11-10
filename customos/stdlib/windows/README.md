# CustomOS Windows API Bindings

This directory contains Windows API bindings for CustomOS, providing direct access to Windows system calls with minimal boilerplate.

## Available Modules

### windows.kernel32
Core Windows kernel operations.

**Functions:**
- `CreateProcess(app_name, cmd_line, ...) -> (status, handle)`
- `TerminateProcess(handle, exit_code) -> status`
- `OpenProcess(desired_access, inherit_handle, pid) -> (status, handle)`
- `CloseHandle(handle) -> status`
- `GetCurrentProcess() -> handle`
- `GetCurrentProcessId() -> u32`
- `GetModuleHandle(module_name) -> (status, handle)`
- `GetProcAddress(module, proc_name) -> (status, ptr[void])`
- `VirtualAlloc(address, size, alloc_type, protect) -> (status, ptr[void])`
- `VirtualFree(address, size, free_type) -> status`
- `WriteProcessMemory(process, address, buffer, size) -> (status, u64)` [UNSAFE]
- `ReadProcessMemory(process, address, buffer, size) -> (status, u64)` [UNSAFE]
- `CreateRemoteThread(process, security, stack_size, start_addr, param, flags) -> (status, handle)` [UNSAFE]
- `Sleep(milliseconds) -> void`
- `GetLastError() -> u32`

### windows.user32
User interface and window management.

**Functions:**
- `MessageBoxW(hwnd, text, caption, type) -> i32`
- `FindWindowA(class_name, window_name) -> (status, handle)`
- `FindWindowExA(parent, child_after, class_name, window_name) -> (status, handle)`
- `GetWindowTextA(hwnd, buffer, max_count) -> (status, i32)`
- `SetWindowTextA(hwnd, text) -> status`
- `ShowWindow(hwnd, cmd_show) -> status`
- `SendMessageA(hwnd, msg, wparam, lparam) -> i64`
- `PostMessageA(hwnd, msg, wparam, lparam) -> status`
- `GetForegroundWindow() -> handle`
- `SetForegroundWindow(hwnd) -> status`

### windows.registry
Windows Registry access with safety checks.

**Functions:**
- `read(key_path, value_name) -> (status, string)` [LOGGED IN SAFE MODE]
- `write(key_path, value_name, value, value_type) -> status` [LOGGED IN SAFE MODE]
- `create_key(key_path) -> status` [LOGGED IN SAFE MODE]
- `delete_key(key_path) -> status` [LOGGED IN SAFE MODE]
- `delete_value(key_path, value_name) -> status` [LOGGED IN SAFE MODE]
- `enumerate_keys(key_path) -> (status, array[string])`
- `enumerate_values(key_path) -> (status, array[string])`
- `key_exists(key_path) -> bool`
- `value_exists(key_path, value_name) -> bool`

**Registry Key Constants:**
- `HKEY_CLASSES_ROOT` / `HKCR`
- `HKEY_CURRENT_USER` / `HKCU`
- `HKEY_LOCAL_MACHINE` / `HKLM`
- `HKEY_USERS` / `HKU`
- `HKEY_CURRENT_CONFIG` / `HKCC`

### windows.services
Windows service management.

**Functions:**
- `create(name, display_name, binary_path, start_type, run_as) -> status`
- `delete(name) -> status`
- `start(name) -> status`
- `stop(name) -> status`
- `query_status(name) -> (status, ServiceStatus)`
- `enum_services() -> (status, array[ServiceInfo])`

**Service Start Types:**
- `AUTO` - Automatic start
- `MANUAL` - Manual start
- `DISABLED` - Disabled

**Run As Options:**
- `SYSTEM` - LocalSystem account
- `NETWORK_SERVICE` - NetworkService account
- `LOCAL_SERVICE` - LocalService account
- Custom user: `"DOMAIN\\Username"`

### windows.processes
Process management and monitoring.

**Functions:**
- `enumerate() -> (status, array[ProcessInfo])`
- `get_info(pid) -> (status, ProcessInfo)`
- `kill(pid, exit_code) -> status`
- `suspend(pid) -> status` [UNSAFE]
- `resume(pid) -> status` [UNSAFE]
- `get_modules(pid) -> (status, array[ModuleInfo])`
- `inject_dll(pid, dll_path) -> status` [UNSAFE]

**ProcessInfo Structure:**
```customos
struct ProcessInfo:
    pid: u32
    parent_pid: u32
    name: string
    path: string
    command_line: string
    creation_time: u64
    user_name: string
```

### windows.network
Network operations and monitoring.

**Functions:**
- `get_connections() -> (status, array[ConnectionInfo])`
- `resolve_hostname(hostname) -> (status, string)`
- `http_get(url) -> (status, string)`
- `http_post(url, data) -> (status, string)`
- `download_file(url, dest_path) -> status`

### windows.wmi
WMI (Windows Management Instrumentation) queries.

**Functions:**
- `query(wmi_query) -> (status, array[dict])`
- `get_os_info() -> (status, OSInfo)`
- `get_cpu_info() -> (status, CPUInfo)`
- `get_memory_info() -> (status, MemoryInfo)`
- `get_disk_info() -> (status, array[DiskInfo])`

### windows.security
Security and privilege management.

**Functions:**
- `elevate() -> status` [UNSAFE]
- `is_admin() -> bool`
- `enable_privilege(privilege_name) -> status` [UNSAFE]
- `disable_privilege(privilege_name) -> status`
- `get_current_user() -> (status, string)`
- `impersonate_user(username, password) -> status` [UNSAFE]

**Common Privileges:**
- `SE_DEBUG_PRIVILEGE` - Debug programs
- `SE_BACKUP_PRIVILEGE` - Backup files
- `SE_RESTORE_PRIVILEGE` - Restore files
- `SE_SHUTDOWN_PRIVILEGE` - Shutdown system
- `SE_LOAD_DRIVER_PRIVILEGE` - Load drivers

## Hook Events

CustomOS provides system hooks that intercept Windows events:

### Process Hooks
```customos
@hook(event: PROCESS_CREATION)
func on_process_created(pid: u32, exe_path: string) -> i32:
    # Return ALLOW_PROCESS or BLOCK_PROCESS
    pass

@hook(event: PROCESS_TERMINATION)
func on_process_terminated(pid: u32, exit_code: i32) -> void:
    pass
```

### File System Hooks
```customos
@hook(event: FILE_WRITE, path: "C:\\Windows\\System32\\*")
func on_system_file_write(path: string, pid: u32) -> i32:
    # Return ALLOW_OPERATION or BLOCK_OPERATION
    pass

@hook(event: FILE_DELETE)
func on_file_delete(path: string, pid: u32) -> i32:
    pass
```

### Registry Hooks
```customos
@hook(event: REGISTRY_WRITE, key: "HKLM\\Software\\*")
func on_registry_write(key: string, value: string, data: string) -> i32:
    # Return ALLOW_OPERATION or BLOCK_OPERATION
    pass
```

### Network Hooks
```customos
@hook(event: NETWORK_CONNECTION)
func on_network_connection(pid: u32, remote_addr: string, remote_port: u16) -> i32:
    # Return ALLOW_CONNECTION or BLOCK_CONNECTION
    pass
```

## Hook Return Values
- `ALLOW_PROCESS` (0x0000) - Allow process creation
- `BLOCK_PROCESS` (0x0001) - Block process creation
- `ALLOW_OPERATION` (0x0000) - Allow file/registry operation
- `BLOCK_OPERATION` (0x0001) - Block file/registry operation
- `ALLOW_CONNECTION` (0x0000) - Allow network connection
- `BLOCK_CONNECTION` (0x0001) - Block network connection

## Service Decorator

Create Windows services directly with the `@service` decorator:

```customos
@service(
    name: "MyService",
    display_name: "My CustomOS Service",
    description: "A service written in CustomOS",
    start_type: AUTO,
    run_as: SYSTEM
)
func main_service() -> i32:
    while isRunning():
        # Service logic
        sleep(1000)
    return SUCCESS
```

## Safety Considerations

### Operations requiring UNSAFE mode:
- Raw memory access (`ptr[T]` operations)
- Process injection (`inject_dll`, `CreateRemoteThread`)
- Direct memory read/write (`ReadProcessMemory`, `WriteProcessMemory`)
- Kernel operations
- Process suspension/resumption
- Privilege escalation

### Operations logged in SAFE mode:
- Registry writes
- Service creation/deletion
- Process termination
- Sensitive file operations

### Example with Safety:
```customos
@safety_level(mode: SAFE)
import windows.registry

func safe_read() -> (status, string):
    # This is safe - registry reads are allowed
    return windows.registry.read("HKLM\\Software\\Test", "Value")

@unsafe
func unsafe_write() -> status:
    # This requires @unsafe decorator in SAFE mode
    return windows.registry.write("HKLM\\Software\\Test", "Value", "Data", REG_SZ)
```

## Error Handling

All Windows API functions return status codes:
- `0x000000` (SUCCESS) - Operation succeeded
- `0x000001` (GENERIC_ERROR) - Generic error
- `0x000002` (ACCESS_DENIED) - Access denied
- `0x000003` (TIMEOUT) - Operation timed out
- `0x000004` (NOT_FOUND) - Resource not found
- `0x000005` (INVALID_PARAMETER) - Invalid parameter

Use `try_chain` for automatic error handling:
```customos
result = try_chain:
    primary:
        windows.registry.read("HKLM\\Software\\Key", "Value")
    secondary:
        ("SUCCESS", "DefaultValue")
    fallback:
        ("ERROR", "")
```

## Compilation

### Compile to executable:
```bash
customos build myapp.cos -o myapp.exe
```

### Compile to Windows service:
```bash
customos build myservice.cos --type service -o myservice.exe
```

### Compile to kernel driver:
```bash
customos build mydriver.cos --type driver -o mydriver.sys --safety unsafe
```

## Notes

- All Windows API bindings are automatically available when you `import windows.*`
- No FFI declarations needed - bindings are built into the language
- Safety checks are enforced at compile-time
- UNSAFE operations require explicit opt-in
- All operations support the resilience system (`try_chain`, `@resilient`)
