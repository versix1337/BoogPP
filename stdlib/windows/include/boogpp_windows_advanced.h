#ifndef BOOGPP_WINDOWS_ADVANCED_H
#define BOOGPP_WINDOWS_ADVANCED_H

#include "../../runtime/include/boogpp_runtime.h"
#include "boogpp_windows.h"

#ifdef _WIN32
#include <windows.h>
#include <winternl.h>
#else
typedef void* PVOID;
typedef void* FARPROC;
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================================
 * PE File Manipulation
 * ========================================================================= */

typedef struct {
    uint16_t machine;
    uint16_t number_of_sections;
    uint32_t time_date_stamp;
    uint32_t size_of_optional_header;
    uint16_t characteristics;
    uint64_t image_base;
    uint32_t section_alignment;
    uint32_t file_alignment;
    uint16_t subsystem;
    uint32_t size_of_image;
    uint32_t size_of_headers;
    uint32_t checksum;
    uint32_t number_of_rva_and_sizes;
} bpp_pe_info_t;

typedef struct {
    char name[16];
    uint32_t virtual_address;
    uint32_t virtual_size;
    uint32_t raw_data_offset;
    uint32_t raw_data_size;
    uint32_t characteristics;
} bpp_pe_section_t;

typedef struct {
    char dll_name[256];
    char function_name[256];
    uint32_t rva;
    uint16_t ordinal;
} bpp_pe_import_t;

/**
 * Load PE file from disk.
 */
bpp_status_t bpp_pe_load(const char* path, void** pe_data, size_t* size);

/**
 * Get PE file information.
 */
bpp_status_t bpp_pe_get_info(const void* pe_data, bpp_pe_info_t* info);

/**
 * Get PE sections.
 */
bpp_status_t bpp_pe_get_sections(const void* pe_data, bpp_pe_section_t* sections,
                                 size_t max_sections, size_t* count);

/**
 * Get PE imports.
 */
bpp_status_t bpp_pe_get_imports(const void* pe_data, bpp_pe_import_t* imports,
                                size_t max_imports, size_t* count);

/**
 * Patch PE bytes at RVA.
 */
bpp_status_t bpp_pe_patch_bytes(void* pe_data, uint32_t rva,
                               const uint8_t* patch_data, size_t patch_size);

/**
 * Add new section to PE.
 */
bpp_status_t bpp_pe_add_section(void* pe_data, const char* name,
                                const uint8_t* section_data, size_t section_size,
                                uint32_t characteristics);

/**
 * Calculate PE checksum.
 */
bpp_status_t bpp_pe_calculate_checksum(const void* pe_data, size_t size, uint32_t* checksum);

/**
 * Save modified PE to disk.
 */
bpp_status_t bpp_pe_save(const char* path, const void* pe_data, size_t size);

/**
 * Resolve imports in loaded PE.
 */
bpp_status_t bpp_pe_resolve_imports(void* pe_data, uint64_t base_address);

/* ============================================================================
 * Process Injection
 * ========================================================================= */

typedef enum {
    BPP_INJECT_CREATEREMOTETHREAD,
    BPP_INJECT_QUEUEUSERAPC,
    BPP_INJECT_SETWINDOWSHOOKEX,
    BPP_INJECT_THREAD_HIJACKING,
    BPP_INJECT_PROCESS_HOLLOWING
} bpp_inject_method_t;

/**
 * Inject DLL into process.
 */
bpp_status_t bpp_process_inject_dll(DWORD pid, const char* dll_path,
                                    bpp_inject_method_t method);

/**
 * Inject shellcode into process.
 */
bpp_status_t bpp_process_inject_shellcode(DWORD pid, const uint8_t* shellcode,
                                          size_t shellcode_size, bpp_inject_method_t method);

/**
 * Create process in suspended state (for hollowing).
 */
bpp_status_t bpp_process_create_suspended(const char* executable,
                                          DWORD* pid, HANDLE* process_handle,
                                          HANDLE* thread_handle);

/**
 * Hollow process and inject new PE.
 */
bpp_status_t bpp_process_hollow(HANDLE process_handle, HANDLE thread_handle,
                                const void* pe_data, size_t pe_size);

/**
 * Read process memory.
 */
bpp_status_t bpp_process_read_memory(DWORD pid, uint64_t address,
                                    void* buffer, size_t size, size_t* bytes_read);

/**
 * Write process memory.
 */
bpp_status_t bpp_process_write_memory(DWORD pid, uint64_t address,
                                     const void* data, size_t size, size_t* bytes_written);

/**
 * Allocate memory in remote process.
 */
bpp_status_t bpp_process_alloc_memory(DWORD pid, size_t size,
                                     uint32_t protection, uint64_t* address);

/**
 * Free memory in remote process.
 */
bpp_status_t bpp_process_free_memory(DWORD pid, uint64_t address);

/**
 * Get process modules.
 */
bpp_status_t bpp_process_get_modules(DWORD pid, char** module_names,
                                    uint64_t* module_bases, size_t max_count, size_t* count);

/**
 * Find pattern in process memory.
 */
bpp_status_t bpp_process_find_pattern(DWORD pid, const uint8_t* pattern,
                                     size_t pattern_size, const char* mask,
                                     uint64_t* address);

/* ============================================================================
 * Windows Hooks
 * ========================================================================= */

typedef enum {
    BPP_HOOK_KEYBOARD,
    BPP_HOOK_MOUSE,
    BPP_HOOK_MESSAGE,
    BPP_HOOK_CBT,
    BPP_HOOK_DEBUG,
    BPP_HOOK_SHELL,
    BPP_HOOK_FOREGROUND_IDLE
} bpp_hook_type_t;

typedef void (*bpp_hook_callback_t)(int code, uintptr_t wparam, uintptr_t lparam, void* user_data);

/**
 * Install Windows hook.
 */
bpp_status_t bpp_hook_install(bpp_hook_type_t type, bpp_hook_callback_t callback,
                              void* user_data, HANDLE* hook_handle);

/**
 * Uninstall Windows hook.
 */
bpp_status_t bpp_hook_uninstall(HANDLE hook_handle);

/**
 * Install inline hook (function detour).
 */
bpp_status_t bpp_hook_inline_install(void* target_function, void* hook_function,
                                    void** original_function);

/**
 * Uninstall inline hook.
 */
bpp_status_t bpp_hook_inline_uninstall(void* target_function, void* original_function);

/**
 * Hook IAT (Import Address Table).
 */
bpp_status_t bpp_hook_iat(HMODULE module, const char* target_module,
                          const char* target_function, void* hook_function,
                          void** original_function);

/* ============================================================================
 * Driver Operations
 * ========================================================================= */

/**
 * Load kernel driver.
 */
bpp_status_t bpp_driver_load(const char* driver_path, const char* service_name);

/**
 * Unload kernel driver.
 */
bpp_status_t bpp_driver_unload(const char* service_name);

/**
 * Send IOCTL to driver.
 */
bpp_status_t bpp_driver_ioctl(const char* device_name, uint32_t ioctl_code,
                             const void* input_buffer, size_t input_size,
                             void* output_buffer, size_t output_size,
                             size_t* bytes_returned);

/* ============================================================================
 * Token Manipulation
 * ========================================================================= */

typedef enum {
    BPP_PRIVILEGE_DEBUG,
    BPP_PRIVILEGE_LOAD_DRIVER,
    BPP_PRIVILEGE_SYSTEM_PROFILE,
    BPP_PRIVILEGE_SYSTEMTIME,
    BPP_PRIVILEGE_PROFILE_SINGLE_PROCESS,
    BPP_PRIVILEGE_INC_BASE_PRIORITY,
    BPP_PRIVILEGE_CREATE_PAGEFILE,
    BPP_PRIVILEGE_CREATE_PERMANENT,
    BPP_PRIVILEGE_BACKUP,
    BPP_PRIVILEGE_RESTORE,
    BPP_PRIVILEGE_SHUTDOWN,
    BPP_PRIVILEGE_TAKE_OWNERSHIP,
    BPP_PRIVILEGE_IMPERSONATE
} bpp_privilege_t;

/**
 * Enable privilege for current process.
 */
bpp_status_t bpp_token_enable_privilege(bpp_privilege_t privilege);

/**
 * Disable privilege for current process.
 */
bpp_status_t bpp_token_disable_privilege(bpp_privilege_t privilege);

/**
 * Get current user SID.
 */
bpp_status_t bpp_token_get_user_sid(char* sid_string, size_t buffer_size);

/**
 * Elevate to SYSTEM privileges.
 */
bpp_status_t bpp_token_elevate_to_system(void);

/**
 * Impersonate process token.
 */
bpp_status_t bpp_token_impersonate_process(DWORD pid);

/**
 * Revert to self.
 */
bpp_status_t bpp_token_revert_to_self(void);

/* ============================================================================
 * Advanced Registry Operations
 * ========================================================================= */

typedef enum {
    BPP_REG_NOTIFY_CHANGE_NAME,
    BPP_REG_NOTIFY_CHANGE_ATTRIBUTES,
    BPP_REG_NOTIFY_CHANGE_LAST_SET,
    BPP_REG_NOTIFY_CHANGE_SECURITY
} bpp_registry_notify_t;

typedef void (*bpp_registry_callback_t)(const char* key, bpp_registry_notify_t change_type, void* user_data);

/**
 * Watch registry key for changes.
 */
bpp_status_t bpp_registry_watch(const char* key, bpp_registry_notify_t notify_filter,
                               bpp_registry_callback_t callback, void* user_data,
                               HANDLE* watch_handle);

/**
 * Stop watching registry key.
 */
bpp_status_t bpp_registry_unwatch(HANDLE watch_handle);

/**
 * Enumerate registry subkeys.
 */
bpp_status_t bpp_registry_enum_keys(const char* key, char** subkeys,
                                   size_t max_count, size_t* count);

/**
 * Enumerate registry values.
 */
bpp_status_t bpp_registry_enum_values(const char* key, char** value_names,
                                     size_t max_count, size_t* count);

/**
 * Read binary registry value.
 */
bpp_status_t bpp_registry_read_binary(const char* key, const char* value_name,
                                     uint8_t* buffer, size_t buffer_size, size_t* bytes_read);

/**
 * Write binary registry value.
 */
bpp_status_t bpp_registry_write_binary(const char* key, const char* value_name,
                                      const uint8_t* data, size_t data_size);

/**
 * Read DWORD registry value.
 */
bpp_status_t bpp_registry_read_dword(const char* key, const char* value_name, uint32_t* value);

/**
 * Write DWORD registry value.
 */
bpp_status_t bpp_registry_write_dword(const char* key, const char* value_name, uint32_t value);

/* ============================================================================
 * Network Operations
 * ========================================================================= */

/**
 * Get active network connections.
 */
bpp_status_t bpp_network_get_connections(void* connections_buffer,
                                        size_t buffer_size, size_t* count);

/**
 * Block IP address via Windows Firewall.
 */
bpp_status_t bpp_firewall_block_ip(const char* ip_address);

/**
 * Unblock IP address.
 */
bpp_status_t bpp_firewall_unblock_ip(const char* ip_address);

/**
 * Add firewall rule.
 */
bpp_status_t bpp_firewall_add_rule(const char* rule_name, const char* program_path,
                                  bpp_bool allow);

/**
 * Remove firewall rule.
 */
bpp_status_t bpp_firewall_remove_rule(const char* rule_name);

/* ============================================================================
 * Event Log Operations
 * ========================================================================= */

/**
 * Write to Windows Event Log.
 */
bpp_status_t bpp_eventlog_write(const char* source, uint16_t event_type,
                                uint16_t category, uint32_t event_id, const char* message);

/**
 * Read from Event Log.
 */
bpp_status_t bpp_eventlog_read(const char* log_name, void* events_buffer,
                               size_t buffer_size, size_t* count);

/**
 * Clear Event Log.
 */
bpp_status_t bpp_eventlog_clear(const char* log_name);

/* ============================================================================
 * WMI Operations
 * ========================================================================= */

/**
 * Execute WMI query.
 */
bpp_status_t bpp_wmi_query(const char* query, void* results_buffer,
                           size_t buffer_size, size_t* count);

/**
 * Get WMI property.
 */
bpp_status_t bpp_wmi_get_property(const char* class_name, const char* property_name,
                                 char* value_buffer, size_t buffer_size);

#ifdef __cplusplus
}
#endif

#endif /* BOOGPP_WINDOWS_ADVANCED_H */
