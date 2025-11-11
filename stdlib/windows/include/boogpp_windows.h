#ifndef BOOGPP_WINDOWS_H
#define BOOGPP_WINDOWS_H

#include "../../runtime/include/boogpp_runtime.h"

#ifdef _WIN32
#include <windows.h>
#else
// Stub types for non-Windows platforms
typedef void* HANDLE;
typedef unsigned long DWORD;
typedef void* HKEY;
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================================
 * Registry Operations
 * ========================================================================= */

/**
 * Read registry value.
 *
 * @param key Registry key path (e.g., "HKLM\\Software\\...")
 * @param value_name Value name to read
 * @param buffer Output buffer
 * @param buffer_size Size of buffer
 * @return Status code
 */
bpp_status_t bpp_registry_read(const char* key, const char* value_name,
                               char* buffer, size_t buffer_size);

/**
 * Write registry value.
 *
 * @param key Registry key path
 * @param value_name Value name to write
 * @param value Value to write
 * @return Status code
 */
bpp_status_t bpp_registry_write(const char* key, const char* value_name,
                                const char* value);

/**
 * Delete registry value.
 *
 * @param key Registry key path
 * @param value_name Value name to delete
 * @return Status code
 */
bpp_status_t bpp_registry_delete(const char* key, const char* value_name);

/* ============================================================================
 * Process Management
 * ========================================================================= */

typedef struct {
    DWORD pid;
    char name[260];
    DWORD threads;
    bpp_bool is_running;
} bpp_process_info_t;

/**
 * Get process list.
 *
 * @param processes Output array of process info
 * @param max_count Maximum processes to return
 * @param count Output count of processes
 * @return Status code
 */
bpp_status_t bpp_process_list(bpp_process_info_t* processes,
                              size_t max_count, size_t* count);

/**
 * Start process.
 *
 * @param executable Path to executable
 * @param arguments Command line arguments
 * @param pid Output process ID
 * @return Status code
 */
bpp_status_t bpp_process_start(const char* executable, const char* arguments,
                               DWORD* pid);

/**
 * Terminate process.
 *
 * @param pid Process ID to terminate
 * @return Status code
 */
bpp_status_t bpp_process_terminate(DWORD pid);

/**
 * Check if process is running.
 *
 * @param pid Process ID
 * @return true if running, false otherwise
 */
bpp_bool bpp_process_is_running(DWORD pid);

/* ============================================================================
 * Service Management
 * ========================================================================= */

typedef enum {
    BPP_SERVICE_STOPPED = 1,
    BPP_SERVICE_START_PENDING,
    BPP_SERVICE_STOP_PENDING,
    BPP_SERVICE_RUNNING,
    BPP_SERVICE_CONTINUE_PENDING,
    BPP_SERVICE_PAUSE_PENDING,
    BPP_SERVICE_PAUSED
} bpp_service_state_t;

/**
 * Create Windows service.
 *
 * @param name Service name
 * @param display_name Display name
 * @param executable Path to service executable
 * @return Status code
 */
bpp_status_t bpp_service_create(const char* name, const char* display_name,
                                const char* executable);

/**
 * Start service.
 *
 * @param name Service name
 * @return Status code
 */
bpp_status_t bpp_service_start(const char* name);

/**
 * Stop service.
 *
 * @param name Service name
 * @return Status code
 */
bpp_status_t bpp_service_stop(const char* name);

/**
 * Delete service.
 *
 * @param name Service name
 * @return Status code
 */
bpp_status_t bpp_service_delete(const char* name);

/**
 * Get service state.
 *
 * @param name Service name
 * @param state Output service state
 * @return Status code
 */
bpp_status_t bpp_service_get_state(const char* name, bpp_service_state_t* state);

/* ============================================================================
 * File System Operations
 * ========================================================================= */

/**
 * Check if file exists.
 *
 * @param path File path
 * @return true if exists, false otherwise
 */
bpp_bool bpp_file_exists(const char* path);

/**
 * Delete file.
 *
 * @param path File path
 * @return Status code
 */
bpp_status_t bpp_file_delete(const char* path);

/**
 * Copy file.
 *
 * @param source Source file path
 * @param destination Destination file path
 * @return Status code
 */
bpp_status_t bpp_file_copy(const char* source, const char* destination);

/**
 * Move file.
 *
 * @param source Source file path
 * @param destination Destination file path
 * @return Status code
 */
bpp_status_t bpp_file_move(const char* source, const char* destination);

/**
 * Get file size.
 *
 * @param path File path
 * @param size Output file size
 * @return Status code
 */
bpp_status_t bpp_file_get_size(const char* path, uint64_t* size);

/* ============================================================================
 * System Information
 * ========================================================================= */

typedef struct {
    char os_version[128];
    char computer_name[128];
    char username[128];
    uint64_t total_memory;
    uint64_t available_memory;
    uint32_t processor_count;
} bpp_system_info_t;

/**
 * Get system information.
 *
 * @param info Output system information
 * @return Status code
 */
bpp_status_t bpp_system_get_info(bpp_system_info_t* info);

/**
 * Get environment variable.
 *
 * @param name Variable name
 * @param buffer Output buffer
 * @param buffer_size Size of buffer
 * @return Status code
 */
bpp_status_t bpp_system_get_env(const char* name, char* buffer, size_t buffer_size);

/**
 * Set environment variable.
 *
 * @param name Variable name
 * @param value Variable value
 * @return Status code
 */
bpp_status_t bpp_system_set_env(const char* name, const char* value);

#ifdef __cplusplus
}
#endif

#endif /* BOOGPP_WINDOWS_H */
