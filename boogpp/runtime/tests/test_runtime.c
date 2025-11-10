#include "../include/boogpp_runtime.h"
#include <stdio.h>
#include <assert.h>
#include <string.h>

/* Test helper macros */
#define TEST(name) \
    static void test_##name(void); \
    static void test_##name(void)

#define RUN_TEST(name) \
    do { \
        printf("Running test: %s...", #name); \
        test_##name(); \
        printf(" PASSED\n"); \
    } while(0)

#define ASSERT(condition) \
    do { \
        if (!(condition)) { \
            fprintf(stderr, "\nAssertion failed: %s\n", #condition); \
            fprintf(stderr, "  File: %s\n", __FILE__); \
            fprintf(stderr, "  Line: %d\n", __LINE__); \
            exit(1); \
        } \
    } while(0)

/* ============================================================================
 * Runtime Initialization Tests
 * ========================================================================= */

TEST(runtime_init) {
    bpp_status_t status = bpp_runtime_init();
    ASSERT(status == BPP_SUCCESS);

    const char* version = bpp_runtime_version();
    ASSERT(version != NULL);
    ASSERT(strcmp(version, "3.0.0") == 0);
}

TEST(runtime_cleanup) {
    bpp_runtime_init();
    bpp_runtime_cleanup();
    // No assertion needed, just testing it doesn't crash
}

/* ============================================================================
 * Memory Management Tests
 * ========================================================================= */

TEST(memory_alloc) {
    void* ptr = bpp_alloc(100);
    ASSERT(ptr != NULL);
    bpp_free(ptr);
}

TEST(memory_alloc_zero) {
    void* ptr = bpp_alloc(0);
    ASSERT(ptr == NULL);
}

TEST(memory_realloc) {
    void* ptr = bpp_alloc(100);
    ASSERT(ptr != NULL);

    void* new_ptr = bpp_realloc(ptr, 200);
    ASSERT(new_ptr != NULL);

    bpp_free(new_ptr);
}

TEST(memory_free_null) {
    bpp_free(NULL);
    // Should not crash
}

/* ============================================================================
 * String Tests
 * ========================================================================= */

TEST(string_new) {
    bpp_string_t* str = bpp_string_new("Hello, World!");
    ASSERT(str != NULL);
    ASSERT(str->data != NULL);
    ASSERT(strcmp(str->data, "Hello, World!") == 0);
    ASSERT(str->length == 13);
    ASSERT(str->refcount == 1);

    bpp_string_free(str);
}

TEST(string_new_empty) {
    bpp_string_t* str = bpp_string_new("");
    ASSERT(str != NULL);
    ASSERT(str->length == 0);
    ASSERT(str->data[0] == '\0');

    bpp_string_free(str);
}

TEST(string_with_capacity) {
    bpp_string_t* str = bpp_string_with_capacity(100);
    ASSERT(str != NULL);
    ASSERT(str->capacity == 100);
    ASSERT(str->length == 0);

    bpp_string_free(str);
}

TEST(string_concat) {
    bpp_string_t* s1 = bpp_string_new("Hello");
    bpp_string_t* s2 = bpp_string_new(" World");

    bpp_string_t* result = bpp_string_concat(s1, s2);
    ASSERT(result != NULL);
    ASSERT(strcmp(result->data, "Hello World") == 0);
    ASSERT(result->length == 11);

    bpp_string_free(s1);
    bpp_string_free(s2);
    bpp_string_free(result);
}

TEST(string_length) {
    bpp_string_t* str = bpp_string_new("Test");
    ASSERT(bpp_string_length(str) == 4);

    bpp_string_free(str);
}

TEST(string_compare) {
    bpp_string_t* s1 = bpp_string_new("abc");
    bpp_string_t* s2 = bpp_string_new("abc");
    bpp_string_t* s3 = bpp_string_new("xyz");

    ASSERT(bpp_string_compare(s1, s2) == 0);
    ASSERT(bpp_string_compare(s1, s3) < 0);
    ASSERT(bpp_string_compare(s3, s1) > 0);

    bpp_string_free(s1);
    bpp_string_free(s2);
    bpp_string_free(s3);
}

/* ============================================================================
 * I/O Tests
 * ========================================================================= */

TEST(print) {
    bpp_string_t* str = bpp_string_new("Test output");
    bpp_status_t status = bpp_print(str);
    ASSERT(status == BPP_SUCCESS);

    bpp_string_free(str);
}

TEST(println) {
    bpp_string_t* str = bpp_string_new("Test output with newline");
    bpp_status_t status = bpp_println(str);
    ASSERT(status == BPP_SUCCESS);

    bpp_string_free(str);
}

TEST(log) {
    bpp_string_t* msg = bpp_string_new("Test log message");
    bpp_status_t status = bpp_log(msg);
    ASSERT(status == BPP_SUCCESS);

    bpp_string_free(msg);
}

/* ============================================================================
 * Array Tests
 * ========================================================================= */

TEST(array_new) {
    bpp_array_t* arr = bpp_array_new(10, sizeof(int));
    ASSERT(arr != NULL);
    ASSERT(arr->capacity == 10);
    ASSERT(arr->length == 0);
    ASSERT(arr->element_size == sizeof(int));
    ASSERT(arr->refcount == 1);

    bpp_array_free(arr);
}

TEST(array_set_get) {
    bpp_array_t* arr = bpp_array_new(10, sizeof(int));

    int value = 42;
    bpp_status_t status = bpp_array_set(arr, 0, &value);
    ASSERT(status == BPP_SUCCESS);
    ASSERT(arr->length == 1);

    int* retrieved = (int*)bpp_array_get(arr, 0);
    ASSERT(retrieved != NULL);
    ASSERT(*retrieved == 42);

    bpp_array_free(arr);
}

TEST(array_multiple_elements) {
    bpp_array_t* arr = bpp_array_new(5, sizeof(int));

    for (int i = 0; i < 5; i++) {
        bpp_array_set(arr, i, &i);
    }

    ASSERT(arr->length == 5);

    for (int i = 0; i < 5; i++) {
        int* val = (int*)bpp_array_get(arr, i);
        ASSERT(*val == i);
    }

    bpp_array_free(arr);
}

TEST(array_out_of_bounds) {
    bpp_array_t* arr = bpp_array_new(5, sizeof(int));

    void* ptr = bpp_array_get(arr, 10);
    ASSERT(ptr == NULL);

    bpp_array_free(arr);
}

/* ============================================================================
 * Slice Tests
 * ========================================================================= */

TEST(slice_new) {
    bpp_array_t* arr = bpp_array_new(10, sizeof(int));

    for (int i = 0; i < 10; i++) {
        bpp_array_set(arr, i, &i);
    }

    bpp_slice_t* slice = bpp_slice_new(arr, 2, 5);
    ASSERT(slice != NULL);
    ASSERT(slice->length == 3);
    ASSERT(slice->element_size == sizeof(int));

    bpp_slice_free(slice);
    bpp_array_free(arr);
}

/* ============================================================================
 * Utility Tests
 * ========================================================================= */

TEST(timestamp_ms) {
    uint64_t t1 = bpp_timestamp_ms();
    bpp_sleep(10);
    uint64_t t2 = bpp_timestamp_ms();

    ASSERT(t2 >= t1);
    ASSERT(t2 - t1 >= 10);
}

TEST(status_string) {
    ASSERT(strcmp(bpp_status_string(BPP_SUCCESS), "SUCCESS") == 0);
    ASSERT(strcmp(bpp_status_string(BPP_GENERIC_ERROR), "GENERIC_ERROR") == 0);
    ASSERT(strcmp(bpp_status_string(BPP_ACCESS_DENIED), "ACCESS_DENIED") == 0);
    ASSERT(strcmp(bpp_status_string(BPP_NOT_FOUND), "NOT_FOUND") == 0);
}

/* ============================================================================
 * Main Test Runner
 * ========================================================================= */

int main(void) {
    printf("===========================================\n");
    printf("Boogpp Runtime Library Tests\n");
    printf("===========================================\n\n");

    bpp_runtime_init();

    /* Runtime tests */
    RUN_TEST(runtime_init);
    RUN_TEST(runtime_cleanup);

    /* Memory tests */
    RUN_TEST(memory_alloc);
    RUN_TEST(memory_alloc_zero);
    RUN_TEST(memory_realloc);
    RUN_TEST(memory_free_null);

    /* String tests */
    RUN_TEST(string_new);
    RUN_TEST(string_new_empty);
    RUN_TEST(string_with_capacity);
    RUN_TEST(string_concat);
    RUN_TEST(string_length);
    RUN_TEST(string_compare);

    /* I/O tests */
    RUN_TEST(print);
    RUN_TEST(println);
    RUN_TEST(log);

    /* Array tests */
    RUN_TEST(array_new);
    RUN_TEST(array_set_get);
    RUN_TEST(array_multiple_elements);
    RUN_TEST(array_out_of_bounds);

    /* Slice tests */
    RUN_TEST(slice_new);

    /* Utility tests */
    RUN_TEST(timestamp_ms);
    RUN_TEST(status_string);

    bpp_runtime_cleanup();

    printf("\n===========================================\n");
    printf("All tests passed successfully!\n");
    printf("===========================================\n");

    return 0;
}
