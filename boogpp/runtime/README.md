# Boogpp Runtime Library

The Boogpp runtime library provides essential functionality for compiled Boogpp programs, including memory management, string operations, I/O, and Windows system integration.

## Architecture

The runtime is implemented in C for maximum performance and portability. It provides:

- **Memory Management**: Allocation, deallocation, and reference counting
- **String Operations**: UTF-8 string handling and manipulation
- **I/O Functions**: Console and file I/O
- **Type System Support**: Runtime type information and conversions
- **Array/Slice Operations**: Dynamic array and slice management
- **Windows Integration**: Direct Windows API access helpers
- **Error Handling**: Status code management and error reporting

## Components

### Core Runtime (`boogpp_runtime.h`)
- Initialization and cleanup
- Memory allocator interface
- Reference counting system
- Status code definitions

### Memory Management (`boogpp_memory.h`)
- `bpp_alloc()` - Allocate memory
- `bpp_free()` - Free memory
- `bpp_realloc()` - Reallocate memory
- `bpp_refcount_inc()` - Increment reference count
- `bpp_refcount_dec()` - Decrement reference count

### String Operations (`boogpp_string.h`)
- `bpp_string_new()` - Create new string
- `bpp_string_concat()` - Concatenate strings
- `bpp_string_length()` - Get string length
- `bpp_string_substring()` - Extract substring
- `bpp_string_compare()` - Compare strings

### I/O Operations (`boogpp_io.h`)
- `bpp_print()` - Print to stdout
- `bpp_println()` - Print with newline
- `bpp_read_line()` - Read line from stdin
- `bpp_log()` - Log message with timestamp

### Array/Slice Operations (`boogpp_array.h`)
- `bpp_array_new()` - Create new array
- `bpp_array_get()` - Get element
- `bpp_array_set()` - Set element
- `bpp_slice_new()` - Create slice from array

### Windows Support (`boogpp_windows.h`)
- Registry access helpers
- Process management
- Service utilities
- System hooks

## Building

The runtime library is built as a static library (`.lib`/`.a`) that is linked with compiled Boogpp programs.

```bash
# Build runtime library
cd boogpp/runtime
make

# Run tests
make test
```

## Integration with Compiler

The compiler automatically links against the runtime library during code generation. All Boogpp programs include:

```c
#include <boogpp_runtime.h>

int main(int argc, char** argv) {
    bpp_runtime_init();

    // User code here

    bpp_runtime_cleanup();
    return 0;
}
```

## Memory Model

Boogpp uses automatic reference counting for memory management in SAFE mode:

1. All heap allocations are tracked
2. Reference counts are maintained automatically
3. Objects are freed when reference count reaches 0
4. Cycle detection prevents memory leaks

In UNSAFE mode, manual memory management is available:
- Direct `alloc()` and `free()` calls
- No automatic reference counting
- Full control over memory lifetime

## Status Codes

The runtime uses standardized status codes:

```c
#define BPP_SUCCESS           0x000000
#define BPP_GENERIC_ERROR     0x000001
#define BPP_ACCESS_DENIED     0x000002
#define BPP_TIMEOUT           0x000003
#define BPP_NOT_FOUND         0x000004
#define BPP_INVALID_PARAMETER 0x000005
```

## Thread Safety

The runtime library is thread-safe by default. All public APIs use appropriate synchronization primitives for concurrent access.

## Performance

The runtime is optimized for:
- Minimal overhead (< 5% compared to C)
- Fast string operations
- Efficient memory allocation
- Zero-cost abstractions where possible

## Windows-Specific Features

The runtime provides direct access to Windows APIs without FFI overhead:
- Native Windows types (HANDLE, DWORD, etc.)
- Registry access
- Service management
- Process and thread creation
- System hooks and callbacks

## Future Enhancements

- JIT compilation support
- Garbage collection option (in addition to reference counting)
- SIMD optimizations for array operations
- Advanced memory profiling
- Cross-platform support (Linux, macOS)
