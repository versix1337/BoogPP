#include "../include/boogpp_windows.h"
#include <stdio.h>
#include <string.h>

#ifdef _WIN32
#include <windows.h>
#include <tlhelp32.h>
#include <psapi.h>

/* ============================================================================
 * Registry Operations
 * ========================================================================= */

bpp_status_t bpp_registry_read(const char* key, const char* value_name,
                               char* buffer, size_t buffer_size) {
    if (!key || !value_name || !buffer || buffer_size == 0) {
        return BPP_INVALID_PARAMETER;
    }

    HKEY hKey;
    DWORD dwType = REG_SZ;
    DWORD dwSize = (DWORD)buffer_size;

    // Parse root key
    HKEY hRoot = HKEY_LOCAL_MACHINE;
    const char* subkey = key;

    if (strncmp(key, "HKLM\\", 5) == 0) {
        hRoot = HKEY_LOCAL_MACHINE;
        subkey = key + 5;
    } else if (strncmp(key, "HKCU\\", 5) == 0) {
        hRoot = HKEY_CURRENT_USER;
        subkey = key + 5;
    } else if (strncmp(key, "HKCR\\", 5) == 0) {
        hRoot = HKEY_CLASSES_ROOT;
        subkey = key + 5;
    }

    LONG result = RegOpenKeyExA(hRoot, subkey, 0, KEY_READ, &hKey);
    if (result != ERROR_SUCCESS) {
        return BPP_NOT_FOUND;
    }

    result = RegQueryValueExA(hKey, value_name, NULL, &dwType,
                             (LPBYTE)buffer, &dwSize);
    RegCloseKey(hKey);

    if (result != ERROR_SUCCESS) {
        return BPP_NOT_FOUND;
    }

    return BPP_SUCCESS;
}

bpp_status_t bpp_registry_write(const char* key, const char* value_name,
                                const char* value) {
    if (!key || !value_name || !value) {
        return BPP_INVALID_PARAMETER;
    }

    HKEY hKey;
    HKEY hRoot = HKEY_LOCAL_MACHINE;
    const char* subkey = key;

    if (strncmp(key, "HKLM\\", 5) == 0) {
        hRoot = HKEY_LOCAL_MACHINE;
        subkey = key + 5;
    } else if (strncmp(key, "HKCU\\", 5) == 0) {
        hRoot = HKEY_CURRENT_USER;
        subkey = key + 5;
    }

    LONG result = RegCreateKeyExA(hRoot, subkey, 0, NULL, REG_OPTION_NON_VOLATILE,
                                  KEY_WRITE, NULL, &hKey, NULL);
    if (result != ERROR_SUCCESS) {
        return BPP_ACCESS_DENIED;
    }

    result = RegSetValueExA(hKey, value_name, 0, REG_SZ,
                           (const BYTE*)value, (DWORD)(strlen(value) + 1));
    RegCloseKey(hKey);

    return (result == ERROR_SUCCESS) ? BPP_SUCCESS : BPP_GENERIC_ERROR;
}

bpp_status_t bpp_registry_delete(const char* key, const char* value_name) {
    if (!key || !value_name) {
        return BPP_INVALID_PARAMETER;
    }

    HKEY hKey;
    HKEY hRoot = HKEY_LOCAL_MACHINE;
    const char* subkey = key;

    if (strncmp(key, "HKLM\\", 5) == 0) {
        hRoot = HKEY_LOCAL_MACHINE;
        subkey = key + 5;
    } else if (strncmp(key, "HKCU\\", 5) == 0) {
        hRoot = HKEY_CURRENT_USER;
        subkey = key + 5;
    }

    LONG result = RegOpenKeyExA(hRoot, subkey, 0, KEY_WRITE, &hKey);
    if (result != ERROR_SUCCESS) {
        return BPP_NOT_FOUND;
    }

    result = RegDeleteValueA(hKey, value_name);
    RegCloseKey(hKey);

    return (result == ERROR_SUCCESS) ? BPP_SUCCESS : BPP_NOT_FOUND;
}

/* ============================================================================
 * Process Management
 * ========================================================================= */

bpp_status_t bpp_process_list(bpp_process_info_t* processes,
                              size_t max_count, size_t* count) {
    if (!processes || !count || max_count == 0) {
        return BPP_INVALID_PARAMETER;
    }

    *count = 0;

    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnapshot == INVALID_HANDLE_VALUE) {
        return BPP_GENERIC_ERROR;
    }

    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);

    if (Process32First(hSnapshot, &pe32)) {
        do {
            if (*count >= max_count) break;

            processes[*count].pid = pe32.th32ProcessID;
            strncpy(processes[*count].name, pe32.szExeFile, 259);
            processes[*count].name[259] = '\0';
            processes[*count].threads = pe32.cntThreads;
            processes[*count].is_running = true;

            (*count)++;
        } while (Process32Next(hSnapshot, &pe32));
    }

    CloseHandle(hSnapshot);
    return BPP_SUCCESS;
}

bpp_status_t bpp_process_start(const char* executable, const char* arguments,
                               DWORD* pid) {
    if (!executable || !pid) {
        return BPP_INVALID_PARAMETER;
    }

    STARTUPINFOA si = {0};
    PROCESS_INFORMATION pi = {0};
    si.cb = sizeof(si);

    char cmdline[4096];
    snprintf(cmdline, sizeof(cmdline), "\"%s\" %s", executable,
             arguments ? arguments : "");

    if (!CreateProcessA(NULL, cmdline, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) {
        return BPP_GENERIC_ERROR;
    }

    *pid = pi.dwProcessId;

    CloseHandle(pi.hProcess);
    CloseHandle(pi.hThread);

    return BPP_SUCCESS;
}

bpp_status_t bpp_process_terminate(DWORD pid) {
    HANDLE hProcess = OpenProcess(PROCESS_TERMINATE, FALSE, pid);
    if (!hProcess) {
        return BPP_ACCESS_DENIED;
    }

    BOOL result = TerminateProcess(hProcess, 1);
    CloseHandle(hProcess);

    return result ? BPP_SUCCESS : BPP_GENERIC_ERROR;
}

bpp_bool bpp_process_is_running(DWORD pid) {
    HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION, FALSE, pid);
    if (!hProcess) {
        return false;
    }

    DWORD exitCode;
    BOOL result = GetExitCodeProcess(hProcess, &exitCode);
    CloseHandle(hProcess);

    return (result && exitCode == STILL_ACTIVE);
}

/* ============================================================================
 * Service Management
 * ========================================================================= */

bpp_status_t bpp_service_create(const char* name, const char* display_name,
                                const char* executable) {
    if (!name || !display_name || !executable) {
        return BPP_INVALID_PARAMETER;
    }

    SC_HANDLE hSCM = OpenSCManager(NULL, NULL, SC_MANAGER_CREATE_SERVICE);
    if (!hSCM) {
        return BPP_ACCESS_DENIED;
    }

    SC_HANDLE hService = CreateServiceA(
        hSCM, name, display_name,
        SERVICE_ALL_ACCESS,
        SERVICE_WIN32_OWN_PROCESS,
        SERVICE_DEMAND_START,
        SERVICE_ERROR_NORMAL,
        executable,
        NULL, NULL, NULL, NULL, NULL
    );

    if (!hService) {
        CloseServiceHandle(hSCM);
        return BPP_GENERIC_ERROR;
    }

    CloseServiceHandle(hService);
    CloseServiceHandle(hSCM);

    return BPP_SUCCESS;
}

bpp_status_t bpp_service_start(const char* name) {
    if (!name) {
        return BPP_INVALID_PARAMETER;
    }

    SC_HANDLE hSCM = OpenSCManager(NULL, NULL, SC_MANAGER_CONNECT);
    if (!hSCM) {
        return BPP_ACCESS_DENIED;
    }

    SC_HANDLE hService = OpenServiceA(hSCM, name, SERVICE_START);
    if (!hService) {
        CloseServiceHandle(hSCM);
        return BPP_NOT_FOUND;
    }

    BOOL result = StartService(hService, 0, NULL);
    CloseServiceHandle(hService);
    CloseServiceHandle(hSCM);

    return result ? BPP_SUCCESS : BPP_GENERIC_ERROR;
}

bpp_status_t bpp_service_stop(const char* name) {
    if (!name) {
        return BPP_INVALID_PARAMETER;
    }

    SC_HANDLE hSCM = OpenSCManager(NULL, NULL, SC_MANAGER_CONNECT);
    if (!hSCM) {
        return BPP_ACCESS_DENIED;
    }

    SC_HANDLE hService = OpenServiceA(hSCM, name, SERVICE_STOP);
    if (!hService) {
        CloseServiceHandle(hSCM);
        return BPP_NOT_FOUND;
    }

    SERVICE_STATUS status;
    BOOL result = ControlService(hService, SERVICE_CONTROL_STOP, &status);

    CloseServiceHandle(hService);
    CloseServiceHandle(hSCM);

    return result ? BPP_SUCCESS : BPP_GENERIC_ERROR;
}

bpp_status_t bpp_service_delete(const char* name) {
    if (!name) {
        return BPP_INVALID_PARAMETER;
    }

    SC_HANDLE hSCM = OpenSCManager(NULL, NULL, SC_MANAGER_CONNECT);
    if (!hSCM) {
        return BPP_ACCESS_DENIED;
    }

    SC_HANDLE hService = OpenServiceA(hSCM, name, DELETE);
    if (!hService) {
        CloseServiceHandle(hSCM);
        return BPP_NOT_FOUND;
    }

    BOOL result = DeleteService(hService);

    CloseServiceHandle(hService);
    CloseServiceHandle(hSCM);

    return result ? BPP_SUCCESS : BPP_GENERIC_ERROR;
}

/* ============================================================================
 * File System Operations
 * ========================================================================= */

bpp_bool bpp_file_exists(const char* path) {
    if (!path) return false;

    DWORD attribs = GetFileAttributesA(path);
    return (attribs != INVALID_FILE_ATTRIBUTES);
}

bpp_status_t bpp_file_delete(const char* path) {
    if (!path) return BPP_INVALID_PARAMETER;

    return DeleteFileA(path) ? BPP_SUCCESS : BPP_GENERIC_ERROR;
}

bpp_status_t bpp_file_copy(const char* source, const char* destination) {
    if (!source || !destination) return BPP_INVALID_PARAMETER;

    return CopyFileA(source, destination, FALSE) ? BPP_SUCCESS : BPP_GENERIC_ERROR;
}

bpp_status_t bpp_file_move(const char* source, const char* destination) {
    if (!source || !destination) return BPP_INVALID_PARAMETER;

    return MoveFileA(source, destination) ? BPP_SUCCESS : BPP_GENERIC_ERROR;
}

bpp_status_t bpp_file_get_size(const char* path, uint64_t* size) {
    if (!path || !size) return BPP_INVALID_PARAMETER;

    HANDLE hFile = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ,
                               NULL, OPEN_EXISTING, 0, NULL);
    if (hFile == INVALID_HANDLE_VALUE) {
        return BPP_NOT_FOUND;
    }

    LARGE_INTEGER fileSize;
    BOOL result = GetFileSizeEx(hFile, &fileSize);
    CloseHandle(hFile);

    if (!result) return BPP_GENERIC_ERROR;

    *size = (uint64_t)fileSize.QuadPart;
    return BPP_SUCCESS;
}

/* ============================================================================
 * System Information
 * ========================================================================= */

bpp_status_t bpp_system_get_info(bpp_system_info_t* info) {
    if (!info) return BPP_INVALID_PARAMETER;

    // Get OS version
    OSVERSIONINFOA osvi = {0};
    osvi.dwOSVersionInfoSize = sizeof(osvi);
    #pragma warning(suppress : 4996)
    if (GetVersionExA(&osvi)) {
        snprintf(info->os_version, sizeof(info->os_version),
                "Windows %lu.%lu Build %lu",
                osvi.dwMajorVersion, osvi.dwMinorVersion, osvi.dwBuildNumber);
    }

    // Get computer name
    DWORD size = sizeof(info->computer_name);
    GetComputerNameA(info->computer_name, &size);

    // Get username
    size = sizeof(info->username);
    GetUserNameA(info->username, &size);

    // Get memory info
    MEMORYSTATUSEX memInfo = {0};
    memInfo.dwLength = sizeof(memInfo);
    if (GlobalMemoryStatusEx(&memInfo)) {
        info->total_memory = memInfo.ullTotalPhys;
        info->available_memory = memInfo.ullAvailPhys;
    }

    // Get processor count
    SYSTEM_INFO sysInfo;
    GetSystemInfo(&sysInfo);
    info->processor_count = sysInfo.dwNumberOfProcessors;

    return BPP_SUCCESS;
}

bpp_status_t bpp_system_get_env(const char* name, char* buffer, size_t buffer_size) {
    if (!name || !buffer || buffer_size == 0) {
        return BPP_INVALID_PARAMETER;
    }

    DWORD result = GetEnvironmentVariableA(name, buffer, (DWORD)buffer_size);
    if (result == 0) {
        return BPP_NOT_FOUND;
    }

    return BPP_SUCCESS;
}

bpp_status_t bpp_system_set_env(const char* name, const char* value) {
    if (!name || !value) {
        return BPP_INVALID_PARAMETER;
    }

    return SetEnvironmentVariableA(name, value) ? BPP_SUCCESS : BPP_GENERIC_ERROR;
}

#else
/* Non-Windows stubs */

bpp_status_t bpp_registry_read(const char* key, const char* value_name,
                               char* buffer, size_t buffer_size) {
    return BPP_NOT_IMPLEMENTED;
}

bpp_status_t bpp_registry_write(const char* key, const char* value_name,
                                const char* value) {
    return BPP_NOT_IMPLEMENTED;
}

bpp_status_t bpp_registry_delete(const char* key, const char* value_name) {
    return BPP_NOT_IMPLEMENTED;
}

bpp_status_t bpp_process_list(bpp_process_info_t* processes,
                              size_t max_count, size_t* count) {
    return BPP_NOT_IMPLEMENTED;
}

bpp_status_t bpp_process_start(const char* executable, const char* arguments,
                               DWORD* pid) {
    return BPP_NOT_IMPLEMENTED;
}

bpp_status_t bpp_process_terminate(DWORD pid) {
    return BPP_NOT_IMPLEMENTED;
}

bpp_bool bpp_process_is_running(DWORD pid) {
    return false;
}

bpp_status_t bpp_service_create(const char* name, const char* display_name,
                                const char* executable) {
    return BPP_NOT_IMPLEMENTED;
}

bpp_status_t bpp_service_start(const char* name) {
    return BPP_NOT_IMPLEMENTED;
}

bpp_status_t bpp_service_stop(const char* name) {
    return BPP_NOT_IMPLEMENTED;
}

bpp_status_t bpp_service_delete(const char* name) {
    return BPP_NOT_IMPLEMENTED;
}

bpp_bool bpp_file_exists(const char* path) {
    return false;
}

bpp_status_t bpp_file_delete(const char* path) {
    return BPP_NOT_IMPLEMENTED;
}

bpp_status_t bpp_file_copy(const char* source, const char* destination) {
    return BPP_NOT_IMPLEMENTED;
}

bpp_status_t bpp_file_move(const char* source, const char* destination) {
    return BPP_NOT_IMPLEMENTED;
}

bpp_status_t bpp_file_get_size(const char* path, uint64_t* size) {
    return BPP_NOT_IMPLEMENTED;
}

bpp_status_t bpp_system_get_info(bpp_system_info_t* info) {
    return BPP_NOT_IMPLEMENTED;
}

bpp_status_t bpp_system_get_env(const char* name, char* buffer, size_t buffer_size) {
    return BPP_NOT_IMPLEMENTED;
}

bpp_status_t bpp_system_set_env(const char* name, const char* value) {
    return BPP_NOT_IMPLEMENTED;
}

#endif
