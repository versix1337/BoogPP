#include "../include/boogpp_runtime.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#include <sys/time.h>
#endif

/* ============================================================================
 * Global Runtime State
 * ========================================================================= */

typedef struct {
    bool initialized;
    size_t total_allocations;
    size_t total_frees;
    size_t bytes_allocated;
} bpp_runtime_state_t;

static bpp_runtime_state_t g_runtime = {0};

/* ============================================================================
 * Runtime Initialization
 * ========================================================================= */

bpp_status_t bpp_runtime_init(void) {
    if (g_runtime.initialized) {
        return BPP_SUCCESS;
    }

    g_runtime.initialized = true;
    g_runtime.total_allocations = 0;
    g_runtime.total_frees = 0;
    g_runtime.bytes_allocated = 0;

    return BPP_SUCCESS;
}

void bpp_runtime_cleanup(void) {
    if (!g_runtime.initialized) {
        return;
    }

    // Log memory statistics in debug mode
    #ifdef BPP_DEBUG
    fprintf(stderr, "[Boogpp Runtime] Cleanup\n");
    fprintf(stderr, "  Total allocations: %zu\n", g_runtime.total_allocations);
    fprintf(stderr, "  Total frees: %zu\n", g_runtime.total_frees);
    fprintf(stderr, "  Bytes still allocated: %zu\n", g_runtime.bytes_allocated);

    if (g_runtime.total_allocations != g_runtime.total_frees) {
        fprintf(stderr, "  WARNING: Memory leak detected! %zu allocations not freed\n",
                g_runtime.total_allocations - g_runtime.total_frees);
    }
    #endif

    g_runtime.initialized = false;
}

const char* bpp_runtime_version(void) {
    return BPP_VERSION;
}

/* ============================================================================
 * Memory Management
 * ========================================================================= */

void* bpp_alloc(size_t size) {
    if (size == 0) {
        return NULL;
    }

    void* ptr = malloc(size);
    if (ptr != NULL) {
        g_runtime.total_allocations++;
        g_runtime.bytes_allocated += size;
    }

    return ptr;
}

void bpp_free(void* ptr) {
    if (ptr == NULL) {
        return;
    }

    free(ptr);
    g_runtime.total_frees++;
}

void* bpp_realloc(void* ptr, size_t size) {
    if (size == 0) {
        bpp_free(ptr);
        return NULL;
    }

    return realloc(ptr, size);
}

void bpp_refcount_inc(void* ptr) {
    if (ptr == NULL) {
        return;
    }

    // Reference count is stored before the actual data
    size_t* refcount = ((size_t*)ptr) - 1;
    (*refcount)++;
}

void bpp_refcount_dec(void* ptr) {
    if (ptr == NULL) {
        return;
    }

    // Reference count is stored before the actual data
    size_t* refcount = ((size_t*)ptr) - 1;
    (*refcount)--;

    if (*refcount == 0) {
        // Free the original allocation (including refcount)
        bpp_free(refcount);
    }
}

/* ============================================================================
 * String Operations
 * ========================================================================= */

bpp_string_t* bpp_string_new(const char* cstr) {
    if (cstr == NULL) {
        return NULL;
    }

    size_t len = strlen(cstr);
    bpp_string_t* str = (bpp_string_t*)bpp_alloc(sizeof(bpp_string_t));

    if (str == NULL) {
        return NULL;
    }

    str->data = (char*)bpp_alloc(len + 1);
    if (str->data == NULL) {
        bpp_free(str);
        return NULL;
    }

    memcpy(str->data, cstr, len + 1);
    str->length = len;
    str->capacity = len + 1;
    str->refcount = 1;

    return str;
}

bpp_string_t* bpp_string_with_capacity(size_t capacity) {
    bpp_string_t* str = (bpp_string_t*)bpp_alloc(sizeof(bpp_string_t));

    if (str == NULL) {
        return NULL;
    }

    str->data = (char*)bpp_alloc(capacity);
    if (str->data == NULL) {
        bpp_free(str);
        return NULL;
    }

    str->data[0] = '\0';
    str->length = 0;
    str->capacity = capacity;
    str->refcount = 1;

    return str;
}

void bpp_string_free(bpp_string_t* str) {
    if (str == NULL) {
        return;
    }

    str->refcount--;
    if (str->refcount == 0) {
        if (str->data != NULL) {
            bpp_free(str->data);
        }
        bpp_free(str);
    }
}

bpp_string_t* bpp_string_concat(const bpp_string_t* s1, const bpp_string_t* s2) {
    if (s1 == NULL || s2 == NULL) {
        return NULL;
    }

    size_t new_length = s1->length + s2->length;
    bpp_string_t* result = bpp_string_with_capacity(new_length + 1);

    if (result == NULL) {
        return NULL;
    }

    memcpy(result->data, s1->data, s1->length);
    memcpy(result->data + s1->length, s2->data, s2->length);
    result->data[new_length] = '\0';
    result->length = new_length;

    return result;
}

size_t bpp_string_length(const bpp_string_t* str) {
    return (str != NULL) ? str->length : 0;
}

int bpp_string_compare(const bpp_string_t* s1, const bpp_string_t* s2) {
    if (s1 == NULL && s2 == NULL) {
        return 0;
    }
    if (s1 == NULL) {
        return -1;
    }
    if (s2 == NULL) {
        return 1;
    }

    return strcmp(s1->data, s2->data);
}

/* ============================================================================
 * I/O Operations
 * ========================================================================= */

bpp_status_t bpp_print(const bpp_string_t* str) {
    if (str == NULL || str->data == NULL) {
        return BPP_INVALID_PARAMETER;
    }

    printf("%s", str->data);
    fflush(stdout);

    return BPP_SUCCESS;
}

bpp_status_t bpp_println(const bpp_string_t* str) {
    if (str == NULL || str->data == NULL) {
        return BPP_INVALID_PARAMETER;
    }

    printf("%s\n", str->data);
    fflush(stdout);

    return BPP_SUCCESS;
}

bpp_status_t bpp_log(const bpp_string_t* message) {
    if (message == NULL || message->data == NULL) {
        return BPP_INVALID_PARAMETER;
    }

    // Get current time
    time_t now = time(NULL);
    struct tm* tm_info = localtime(&now);
    char time_buffer[26];
    strftime(time_buffer, sizeof(time_buffer), "%Y-%m-%d %H:%M:%S", tm_info);

    fprintf(stderr, "[%s] %s\n", time_buffer, message->data);
    fflush(stderr);

    return BPP_SUCCESS;
}

bpp_string_t* bpp_read_line(void) {
    char buffer[4096];

    if (fgets(buffer, sizeof(buffer), stdin) == NULL) {
        return NULL;
    }

    // Remove trailing newline
    size_t len = strlen(buffer);
    if (len > 0 && buffer[len - 1] == '\n') {
        buffer[len - 1] = '\0';
    }

    return bpp_string_new(buffer);
}

/* ============================================================================
 * Array Operations
 * ========================================================================= */

bpp_array_t* bpp_array_new(size_t capacity, size_t element_size) {
    if (capacity == 0 || element_size == 0) {
        return NULL;
    }

    bpp_array_t* array = (bpp_array_t*)bpp_alloc(sizeof(bpp_array_t));
    if (array == NULL) {
        return NULL;
    }

    array->data = bpp_alloc(capacity * element_size);
    if (array->data == NULL) {
        bpp_free(array);
        return NULL;
    }

    array->length = 0;
    array->capacity = capacity;
    array->element_size = element_size;
    array->refcount = 1;

    return array;
}

void bpp_array_free(bpp_array_t* array) {
    if (array == NULL) {
        return;
    }

    array->refcount--;
    if (array->refcount == 0) {
        if (array->data != NULL) {
            bpp_free(array->data);
        }
        bpp_free(array);
    }
}

void* bpp_array_get(const bpp_array_t* array, size_t index) {
    if (array == NULL || index >= array->length) {
        return NULL;
    }

    return (char*)array->data + (index * array->element_size);
}

bpp_status_t bpp_array_set(bpp_array_t* array, size_t index, const void* value) {
    if (array == NULL || value == NULL) {
        return BPP_INVALID_PARAMETER;
    }

    if (index >= array->capacity) {
        return BPP_INVALID_PARAMETER;
    }

    void* dest = (char*)array->data + (index * array->element_size);
    memcpy(dest, value, array->element_size);

    if (index >= array->length) {
        array->length = index + 1;
    }

    return BPP_SUCCESS;
}

bpp_slice_t* bpp_slice_new(const bpp_array_t* array, size_t start, size_t end) {
    if (array == NULL || start > end || end > array->length) {
        return NULL;
    }

    bpp_slice_t* slice = (bpp_slice_t*)bpp_alloc(sizeof(bpp_slice_t));
    if (slice == NULL) {
        return NULL;
    }

    slice->data = (char*)array->data + (start * array->element_size);
    slice->length = end - start;
    slice->element_size = array->element_size;

    return slice;
}

void bpp_slice_free(bpp_slice_t* slice) {
    // Slices don't own their data, so just free the slice structure
    bpp_free(slice);
}

/* ============================================================================
 * Utility Functions
 * ========================================================================= */

void bpp_sleep(uint32_t milliseconds) {
#ifdef _WIN32
    Sleep(milliseconds);
#else
    usleep(milliseconds * 1000);
#endif
}

uint64_t bpp_timestamp_ms(void) {
#ifdef _WIN32
    return GetTickCount64();
#else
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return (uint64_t)tv.tv_sec * 1000 + tv.tv_usec / 1000;
#endif
}

const char* bpp_status_string(bpp_status_t status) {
    switch (status) {
        case BPP_SUCCESS:           return "SUCCESS";
        case BPP_GENERIC_ERROR:     return "GENERIC_ERROR";
        case BPP_ACCESS_DENIED:     return "ACCESS_DENIED";
        case BPP_TIMEOUT:           return "TIMEOUT";
        case BPP_NOT_FOUND:         return "NOT_FOUND";
        case BPP_INVALID_PARAMETER: return "INVALID_PARAMETER";
        case BPP_OUT_OF_MEMORY:     return "OUT_OF_MEMORY";
        case BPP_BUFFER_TOO_SMALL:  return "BUFFER_TOO_SMALL";
        case BPP_NOT_IMPLEMENTED:   return "NOT_IMPLEMENTED";
        default:                    return "UNKNOWN_ERROR";
    }
}
