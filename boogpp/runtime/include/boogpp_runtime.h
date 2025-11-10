#ifndef BOOGPP_RUNTIME_H
#define BOOGPP_RUNTIME_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================================
 * Version Information
 * ========================================================================= */
#define BPP_VERSION_MAJOR 3
#define BPP_VERSION_MINOR 0
#define BPP_VERSION_PATCH 0
#define BPP_VERSION "3.0.0"

/* ============================================================================
 * Status Codes
 * ========================================================================= */
typedef int32_t bpp_status_t;

#define BPP_SUCCESS           0x000000
#define BPP_GENERIC_ERROR     0x000001
#define BPP_ACCESS_DENIED     0x000002
#define BPP_TIMEOUT           0x000003
#define BPP_NOT_FOUND         0x000004
#define BPP_INVALID_PARAMETER 0x000005
#define BPP_OUT_OF_MEMORY     0x000006
#define BPP_BUFFER_TOO_SMALL  0x000007
#define BPP_NOT_IMPLEMENTED   0x000008

/* ============================================================================
 * Type Definitions
 * ========================================================================= */
typedef int8_t   bpp_i8;
typedef int16_t  bpp_i16;
typedef int32_t  bpp_i32;
typedef int64_t  bpp_i64;

typedef uint8_t  bpp_u8;
typedef uint16_t bpp_u16;
typedef uint32_t bpp_u32;
typedef uint64_t bpp_u64;

typedef float    bpp_f32;
typedef double   bpp_f64;

typedef bool     bpp_bool;
typedef char     bpp_char;

/* ============================================================================
 * String Type
 * ========================================================================= */
typedef struct bpp_string {
    char* data;
    size_t length;
    size_t capacity;
    size_t refcount;
} bpp_string_t;

/* ============================================================================
 * Array Type
 * ========================================================================= */
typedef struct bpp_array {
    void* data;
    size_t length;
    size_t capacity;
    size_t element_size;
    size_t refcount;
} bpp_array_t;

/* ============================================================================
 * Slice Type
 * ========================================================================= */
typedef struct bpp_slice {
    void* data;
    size_t length;
    size_t element_size;
} bpp_slice_t;

/* ============================================================================
 * Runtime Initialization
 * ========================================================================= */

/**
 * Initialize the Boogpp runtime.
 * Must be called before any other runtime functions.
 *
 * @return BPP_SUCCESS on success, error code otherwise
 */
bpp_status_t bpp_runtime_init(void);

/**
 * Cleanup the Boogpp runtime.
 * Should be called before program exit.
 */
void bpp_runtime_cleanup(void);

/**
 * Get runtime version string.
 *
 * @return Version string (e.g., "3.0.0")
 */
const char* bpp_runtime_version(void);

/* ============================================================================
 * Memory Management
 * ========================================================================= */

/**
 * Allocate memory.
 *
 * @param size Size in bytes to allocate
 * @return Pointer to allocated memory, or NULL on failure
 */
void* bpp_alloc(size_t size);

/**
 * Free memory.
 *
 * @param ptr Pointer to memory to free
 */
void bpp_free(void* ptr);

/**
 * Reallocate memory.
 *
 * @param ptr Pointer to existing memory
 * @param size New size in bytes
 * @return Pointer to reallocated memory, or NULL on failure
 */
void* bpp_realloc(void* ptr, size_t size);

/**
 * Increment reference count.
 *
 * @param ptr Pointer to reference-counted object
 */
void bpp_refcount_inc(void* ptr);

/**
 * Decrement reference count and free if zero.
 *
 * @param ptr Pointer to reference-counted object
 */
void bpp_refcount_dec(void* ptr);

/* ============================================================================
 * String Operations
 * ========================================================================= */

/**
 * Create new string from C string.
 *
 * @param cstr C string (null-terminated)
 * @return New Boogpp string
 */
bpp_string_t* bpp_string_new(const char* cstr);

/**
 * Create new string with specific capacity.
 *
 * @param capacity Initial capacity
 * @return New Boogpp string
 */
bpp_string_t* bpp_string_with_capacity(size_t capacity);

/**
 * Free string.
 *
 * @param str String to free
 */
void bpp_string_free(bpp_string_t* str);

/**
 * Concatenate two strings.
 *
 * @param s1 First string
 * @param s2 Second string
 * @return New concatenated string
 */
bpp_string_t* bpp_string_concat(const bpp_string_t* s1, const bpp_string_t* s2);

/**
 * Get string length.
 *
 * @param str String
 * @return Length in bytes
 */
size_t bpp_string_length(const bpp_string_t* str);

/**
 * Compare two strings.
 *
 * @param s1 First string
 * @param s2 Second string
 * @return 0 if equal, < 0 if s1 < s2, > 0 if s1 > s2
 */
int bpp_string_compare(const bpp_string_t* s1, const bpp_string_t* s2);

/* ============================================================================
 * I/O Operations
 * ========================================================================= */

/**
 * Print string to stdout.
 *
 * @param str String to print
 * @return BPP_SUCCESS on success, error code otherwise
 */
bpp_status_t bpp_print(const bpp_string_t* str);

/**
 * Print string to stdout with newline.
 *
 * @param str String to print
 * @return BPP_SUCCESS on success, error code otherwise
 */
bpp_status_t bpp_println(const bpp_string_t* str);

/**
 * Log message with timestamp.
 *
 * @param message Message to log
 * @return BPP_SUCCESS on success, error code otherwise
 */
bpp_status_t bpp_log(const bpp_string_t* message);

/**
 * Read line from stdin.
 *
 * @return New string with input, or NULL on error
 */
bpp_string_t* bpp_read_line(void);

/* ============================================================================
 * Array Operations
 * ========================================================================= */

/**
 * Create new array.
 *
 * @param capacity Initial capacity
 * @param element_size Size of each element
 * @return New array
 */
bpp_array_t* bpp_array_new(size_t capacity, size_t element_size);

/**
 * Free array.
 *
 * @param array Array to free
 */
void bpp_array_free(bpp_array_t* array);

/**
 * Get array element.
 *
 * @param array Array
 * @param index Element index
 * @return Pointer to element, or NULL if out of bounds
 */
void* bpp_array_get(const bpp_array_t* array, size_t index);

/**
 * Set array element.
 *
 * @param array Array
 * @param index Element index
 * @param value Pointer to value to set
 * @return BPP_SUCCESS on success, error code otherwise
 */
bpp_status_t bpp_array_set(bpp_array_t* array, size_t index, const void* value);

/**
 * Create slice from array.
 *
 * @param array Source array
 * @param start Start index
 * @param end End index (exclusive)
 * @return New slice
 */
bpp_slice_t* bpp_slice_new(const bpp_array_t* array, size_t start, size_t end);

/**
 * Free slice.
 *
 * @param slice Slice to free
 */
void bpp_slice_free(bpp_slice_t* slice);

/* ============================================================================
 * Utility Functions
 * ========================================================================= */

/**
 * Sleep for specified milliseconds.
 *
 * @param milliseconds Milliseconds to sleep
 */
void bpp_sleep(uint32_t milliseconds);

/**
 * Get current timestamp in milliseconds.
 *
 * @return Timestamp in milliseconds
 */
uint64_t bpp_timestamp_ms(void);

/**
 * Convert status code to string.
 *
 * @param status Status code
 * @return String description of status code
 */
const char* bpp_status_string(bpp_status_t status);

#ifdef __cplusplus
}
#endif

#endif /* BOOGPP_RUNTIME_H */
