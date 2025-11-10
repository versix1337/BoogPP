"""
CustomOS Enhanced Safety Rules
Defines detailed safety rules and policies for different safety levels.
"""

from enum import Enum, auto
from typing import Set, Dict, List, Optional
from dataclasses import dataclass


class SafetyCategory(Enum):
    """Categories of safety-sensitive operations"""
    MEMORY_MANAGEMENT = auto()
    PROCESS_INJECTION = auto()
    KERNEL_OPERATION = auto()
    REGISTRY_WRITE = auto()
    FILE_SYSTEM = auto()
    NETWORK = auto()
    CRYPTOGRAPHY = auto()
    SYSTEM_CONFIG = auto()
    DRIVER_OPERATION = auto()


class OperationRisk(Enum):
    """Risk levels for operations"""
    SAFE = auto()           # Always allowed, no restrictions
    LOW = auto()            # Minor restrictions, logged in SAFE mode
    MEDIUM = auto()         # Requires explicit permission or UNSAFE mode
    HIGH = auto()           # Requires UNSAFE mode, detailed logging
    CRITICAL = auto()       # Requires UNSAFE mode, additional validation


@dataclass
class SafetyRule:
    """Represents a safety rule for an operation"""
    operation: str
    category: SafetyCategory
    risk: OperationRisk
    description: str
    safe_mode_allowed: bool
    requires_validation: bool = False
    requires_logging: bool = False
    alternative: Optional[str] = None  # Safer alternative


class SafetyRuleDatabase:
    """Database of all safety rules"""

    def __init__(self):
        self.rules: Dict[str, SafetyRule] = {}
        self._init_rules()

    def _init_rules(self):
        """Initialize all safety rules"""

        # ===== Memory Management =====
        self._add_rule(SafetyRule(
            'alloc', SafetyCategory.MEMORY_MANAGEMENT, OperationRisk.HIGH,
            'Manual memory allocation - risk of memory leaks',
            safe_mode_allowed=False,
            requires_validation=True,
            alternative='Use automatic memory management'
        ))
        self._add_rule(SafetyRule(
            'free', SafetyCategory.MEMORY_MANAGEMENT, OperationRisk.HIGH,
            'Manual memory deallocation - risk of double-free or use-after-free',
            safe_mode_allowed=False,
            requires_validation=True
        ))
        self._add_rule(SafetyRule(
            'realloc', SafetyCategory.MEMORY_MANAGEMENT, OperationRisk.HIGH,
            'Memory reallocation - risk of memory corruption',
            safe_mode_allowed=False,
            requires_validation=True
        ))
        self._add_rule(SafetyRule(
            'memcpy', SafetyCategory.MEMORY_MANAGEMENT, OperationRisk.MEDIUM,
            'Raw memory copy - risk of buffer overflow',
            safe_mode_allowed=False,
            requires_validation=True,
            alternative='Use safe array/slice operations'
        ))
        self._add_rule(SafetyRule(
            'memmove', SafetyCategory.MEMORY_MANAGEMENT, OperationRisk.MEDIUM,
            'Raw memory move - risk of buffer overflow',
            safe_mode_allowed=False,
            requires_validation=True
        ))

        # ===== Process Operations =====
        self._add_rule(SafetyRule(
            'kernel32.OpenProcess', SafetyCategory.PROCESS_INJECTION, OperationRisk.HIGH,
            'Opening process handle - can be used for injection',
            safe_mode_allowed=False,
            requires_logging=True
        ))
        self._add_rule(SafetyRule(
            'kernel32.WriteProcessMemory', SafetyCategory.PROCESS_INJECTION, OperationRisk.CRITICAL,
            'Writing to remote process memory - process injection',
            safe_mode_allowed=False,
            requires_validation=True,
            requires_logging=True
        ))
        self._add_rule(SafetyRule(
            'kernel32.ReadProcessMemory', SafetyCategory.PROCESS_INJECTION, OperationRisk.HIGH,
            'Reading from remote process memory',
            safe_mode_allowed=False,
            requires_logging=True
        ))
        self._add_rule(SafetyRule(
            'kernel32.CreateRemoteThread', SafetyCategory.PROCESS_INJECTION, OperationRisk.CRITICAL,
            'Creating thread in remote process - code injection',
            safe_mode_allowed=False,
            requires_validation=True,
            requires_logging=True
        ))
        self._add_rule(SafetyRule(
            'inject_dll', SafetyCategory.PROCESS_INJECTION, OperationRisk.CRITICAL,
            'DLL injection into remote process',
            safe_mode_allowed=False,
            requires_validation=True,
            requires_logging=True
        ))
        self._add_rule(SafetyRule(
            'inject_shellcode', SafetyCategory.PROCESS_INJECTION, OperationRisk.CRITICAL,
            'Shellcode injection - arbitrary code execution',
            safe_mode_allowed=False,
            requires_validation=True,
            requires_logging=True
        ))

        # ===== Kernel Operations =====
        self._add_rule(SafetyRule(
            'DriverEntry', SafetyCategory.KERNEL_OPERATION, OperationRisk.CRITICAL,
            'Kernel driver entry point - kernel-mode execution',
            safe_mode_allowed=False,
            requires_validation=True
        ))
        self._add_rule(SafetyRule(
            'IoCreateDevice', SafetyCategory.KERNEL_OPERATION, OperationRisk.CRITICAL,
            'Creating kernel device object',
            safe_mode_allowed=False,
            requires_validation=True
        ))
        self._add_rule(SafetyRule(
            'IoCreateSymbolicLink', SafetyCategory.KERNEL_OPERATION, OperationRisk.HIGH,
            'Creating kernel symbolic link',
            safe_mode_allowed=False,
            requires_validation=True
        ))
        self._add_rule(SafetyRule(
            'ExAllocatePoolWithTag', SafetyCategory.KERNEL_OPERATION, OperationRisk.HIGH,
            'Kernel pool memory allocation',
            safe_mode_allowed=False,
            requires_validation=True
        ))

        # ===== Registry Operations =====
        self._add_rule(SafetyRule(
            'registry.write', SafetyCategory.REGISTRY_WRITE, OperationRisk.MEDIUM,
            'Writing to Windows registry',
            safe_mode_allowed=True,
            requires_logging=True
        ))
        self._add_rule(SafetyRule(
            'registry.create_key', SafetyCategory.REGISTRY_WRITE, OperationRisk.MEDIUM,
            'Creating registry key',
            safe_mode_allowed=True,
            requires_logging=True
        ))
        self._add_rule(SafetyRule(
            'registry.delete_key', SafetyCategory.REGISTRY_WRITE, OperationRisk.HIGH,
            'Deleting registry key - may affect system stability',
            safe_mode_allowed=False,
            requires_validation=True,
            requires_logging=True
        ))
        self._add_rule(SafetyRule(
            'registry.delete_value', SafetyCategory.REGISTRY_WRITE, OperationRisk.MEDIUM,
            'Deleting registry value',
            safe_mode_allowed=True,
            requires_logging=True
        ))

        # ===== File System Operations =====
        self._add_rule(SafetyRule(
            'fs.delete', SafetyCategory.FILE_SYSTEM, OperationRisk.MEDIUM,
            'Deleting files - potential data loss',
            safe_mode_allowed=True,
            requires_logging=True
        ))
        self._add_rule(SafetyRule(
            'fs.write_system', SafetyCategory.FILE_SYSTEM, OperationRisk.HIGH,
            'Writing to system directories',
            safe_mode_allowed=False,
            requires_validation=True,
            requires_logging=True
        ))
        self._add_rule(SafetyRule(
            'fs.modify_permissions', SafetyCategory.FILE_SYSTEM, OperationRisk.HIGH,
            'Modifying file permissions',
            safe_mode_allowed=False,
            requires_logging=True
        ))

        # ===== Network Operations =====
        self._add_rule(SafetyRule(
            'net.listen', SafetyCategory.NETWORK, OperationRisk.MEDIUM,
            'Listening on network port',
            safe_mode_allowed=True,
            requires_logging=True
        ))
        self._add_rule(SafetyRule(
            'net.raw_socket', SafetyCategory.NETWORK, OperationRisk.HIGH,
            'Creating raw socket - can craft arbitrary packets',
            safe_mode_allowed=False,
            requires_validation=True
        ))

        # ===== Cryptography =====
        self._add_rule(SafetyRule(
            'crypto.weak_algorithm', SafetyCategory.CRYPTOGRAPHY, OperationRisk.MEDIUM,
            'Using weak cryptographic algorithm',
            safe_mode_allowed=True,
            requires_logging=True,
            alternative='Use modern cryptographic algorithms (AES, ChaCha20)'
        ))

        # ===== System Configuration =====
        self._add_rule(SafetyRule(
            'system.set_time', SafetyCategory.SYSTEM_CONFIG, OperationRisk.HIGH,
            'Changing system time',
            safe_mode_allowed=False,
            requires_validation=True
        ))
        self._add_rule(SafetyRule(
            'system.shutdown', SafetyCategory.SYSTEM_CONFIG, OperationRisk.HIGH,
            'System shutdown/restart',
            safe_mode_allowed=False,
            requires_validation=True
        ))

        # Add wildcard Windows API rules
        self._add_wildcard_rules()

    def _add_rule(self, rule: SafetyRule):
        """Add a rule to the database"""
        self.rules[rule.operation] = rule

    def _add_wildcard_rules(self):
        """Add rules that match patterns"""
        # These are checked with suffix matching in the safety checker
        windows_api_dangerous = [
            'VirtualAlloc', 'VirtualFree', 'VirtualProtect',
            'WriteProcessMemory', 'ReadProcessMemory',
            'CreateRemoteThread', 'QueueUserAPC',
            'SetWindowsHookEx', 'NtAllocateVirtualMemory',
            'NtWriteVirtualMemory', 'NtCreateThread'
        ]

        for api in windows_api_dangerous:
            for module in ['kernel32', 'ntdll', 'user32']:
                full_name = f"{module}.{api}"
                if full_name not in self.rules:
                    self._add_rule(SafetyRule(
                        full_name,
                        SafetyCategory.MEMORY_MANAGEMENT if 'Alloc' in api or 'Virtual' in api
                        else SafetyCategory.PROCESS_INJECTION,
                        OperationRisk.CRITICAL if 'Write' in api or 'Create' in api or 'Thread' in api
                        else OperationRisk.HIGH,
                        f'Dangerous Windows API: {api}',
                        safe_mode_allowed=False,
                        requires_validation=True,
                        requires_logging=True
                    ))

    def get_rule(self, operation: str) -> Optional[SafetyRule]:
        """Get rule for an operation"""
        # First try exact match
        if operation in self.rules:
            return self.rules[operation]

        # Try suffix match for module.function patterns
        for rule_name, rule in self.rules.items():
            if operation.endswith(rule_name):
                return rule

        return None

    def get_rules_by_category(self, category: SafetyCategory) -> List[SafetyRule]:
        """Get all rules in a category"""
        return [rule for rule in self.rules.values() if rule.category == category]

    def get_rules_by_risk(self, risk: OperationRisk) -> List[SafetyRule]:
        """Get all rules with a risk level"""
        return [rule for rule in self.rules.values() if rule.risk == risk]


# Global rule database
SAFETY_RULES = SafetyRuleDatabase()
