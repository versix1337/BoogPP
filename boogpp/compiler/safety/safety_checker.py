"""
Boogpp Safety System
Enforces safety rules based on mode (SAFE, UNSAFE, CUSTOM).
"""

from enum import Enum, auto
from typing import Set, List, Optional
from ..parser.ast_nodes import *


class SafetyMode(Enum):
    """Safety modes"""
    SAFE = auto()
    UNSAFE = auto()
    CUSTOM = auto()


class SafetyLevel(Enum):
    """Safety level for operations"""
    SAFE = auto()           # Always allowed
    DANGEROUS = auto()      # Requires UNSAFE mode
    RESTRICTED = auto()     # Requires specific permissions


class SafetyViolation:
    """Represents a safety violation"""
    def __init__(self, message: str, node: ASTNode, severity: str = "error"):
        self.message = message
        self.node = node
        self.severity = severity
        self.line = node.line
        self.column = node.column
        self.filename = node.filename

    def __str__(self):
        location = f"{self.filename or '<input>'}:{self.line}:{self.column}"
        return f"{location}: [{self.severity}] {self.message}"


class SafetyChecker:
    """Checks safety rules and restrictions"""

    # Dangerous operations that require UNSAFE mode
    DANGEROUS_OPERATIONS = {
        'alloc',
        'free',
        'realloc',
        'memcpy',
        'memmove',
        'ptr_read',
        'ptr_write',
        'kernel32.VirtualAlloc',
        'kernel32.VirtualFree',
        'kernel32.WriteProcessMemory',
        'kernel32.ReadProcessMemory',
        'kernel32.CreateRemoteThread',
        'kernel32.OpenProcess',
        'ntdll.NtAllocateVirtualMemory',
        'ntdll.NtWriteVirtualMemory',
    }

    # Process injection operations
    INJECTION_OPERATIONS = {
        'inject_dll',
        'inject_shellcode',
        'create_remote_thread',
        'kernel32.CreateRemoteThread',
        'kernel32.WriteProcessMemory',
    }

    # Kernel operations
    KERNEL_OPERATIONS = {
        'DriverEntry',
        'IoCreateDevice',
        'IoCreateSymbolicLink',
        'IoDeleteDevice',
        'IoDeleteSymbolicLink',
        'KeWaitForSingleObject',
        'ExAllocatePoolWithTag',
        'ExFreePoolWithTag',
    }

    # Registry write operations (logged in SAFE mode)
    REGISTRY_WRITE_OPS = {
        'registry.write',
        'registry.create_key',
        'registry.delete_key',
        'registry.delete_value',
        'RegSetValueEx',
        'RegCreateKeyEx',
        'RegDeleteKey',
        'RegDeleteValue',
    }

    def __init__(self, mode: SafetyMode = SafetyMode.SAFE):
        self.mode = mode
        self.violations: List[SafetyViolation] = []
        self.custom_rules: Set[str] = set()
        self.logging_enabled = (mode == SafetyMode.SAFE)

    def check_program(self, program: Program) -> List[SafetyViolation]:
        """Check entire program for safety violations"""
        self.violations = []

        # Check file-level safety decorator
        for decorator in program.decorators:
            if decorator.name == "safety_level":
                mode_arg = decorator.arguments.get("mode")
                if mode_arg and isinstance(mode_arg, IdentifierExpr):
                    self.mode = SafetyMode[mode_arg.name]

        # Check all declarations
        for decl in program.declarations:
            self.check_declaration(decl)

        return self.violations

    def check_declaration(self, decl: ASTNode) -> None:
        """Check a declaration"""
        if isinstance(decl, FunctionDecl):
            self.check_function(decl)

    def check_function(self, func: FunctionDecl) -> None:
        """Check function for safety violations"""
        # Check if function has @unsafe decorator
        function_mode = self.mode
        for decorator in func.decorators:
            if decorator.name == "unsafe":
                function_mode = SafetyMode.UNSAFE
                break

        # Save current mode and switch to function mode
        saved_mode = self.mode
        self.mode = function_mode

        # Check function body
        self.check_statement(func.body)

        # Restore mode
        self.mode = saved_mode

    def check_statement(self, stmt: Statement) -> None:
        """Check a statement"""
        if isinstance(stmt, Block):
            for s in stmt.statements:
                self.check_statement(s)

        elif isinstance(stmt, ReturnStmt):
            if stmt.value:
                self.check_expression(stmt.value)

        elif isinstance(stmt, IfStmt):
            self.check_expression(stmt.condition)
            self.check_statement(stmt.then_block)
            for cond, block in stmt.elif_clauses:
                self.check_expression(cond)
                self.check_statement(block)
            if stmt.else_block:
                self.check_statement(stmt.else_block)

        elif isinstance(stmt, WhileStmt):
            self.check_expression(stmt.condition)
            self.check_statement(stmt.body)

        elif isinstance(stmt, ForStmt):
            self.check_expression(stmt.iterable)
            self.check_statement(stmt.body)

        elif isinstance(stmt, MatchStmt):
            self.check_expression(stmt.value)
            for case in stmt.cases:
                self.check_expression(case.pattern)
                self.check_statement(case.body)

        elif isinstance(stmt, ExprStmt):
            self.check_expression(stmt.expression)

        elif isinstance(stmt, AssignStmt):
            self.check_expression(stmt.target)
            self.check_expression(stmt.value)

        elif isinstance(stmt, DeferStmt):
            self.check_statement(stmt.statement)

        elif isinstance(stmt, VariableDecl):
            if stmt.initializer:
                self.check_expression(stmt.initializer)

    def check_expression(self, expr: Expression) -> None:
        """Check an expression"""
        if isinstance(expr, BinaryExpr):
            self.check_expression(expr.left)
            self.check_expression(expr.right)

        elif isinstance(expr, UnaryExpr):
            self.check_expression(expr.operand)

        elif isinstance(expr, CallExpr):
            self.check_call(expr)
            for arg in expr.arguments:
                self.check_expression(arg)

        elif isinstance(expr, MemberExpr):
            self.check_expression(expr.object)

        elif isinstance(expr, IndexExpr):
            self.check_expression(expr.object)
            self.check_expression(expr.index)

        elif isinstance(expr, TupleExpr):
            for elem in expr.elements:
                self.check_expression(elem)

        elif isinstance(expr, ArrayExpr):
            for elem in expr.elements:
                self.check_expression(elem)

        elif isinstance(expr, TryChainExpr):
            self.check_expression(expr.primary)
            if expr.secondary:
                self.check_expression(expr.secondary)
            if expr.fallback:
                self.check_expression(expr.fallback)

    def check_call(self, call: CallExpr) -> None:
        """Check a function call for safety violations"""
        # Get the function name
        func_name = self.get_call_name(call)

        if not func_name:
            return

        # Helper function to check if func_name matches any operation (exact or suffix match)
        def matches_operation(func_name: str, operations: set) -> bool:
            if func_name in operations:
                return True
            # Check if any operation is a suffix (e.g., "kernel32.VirtualAlloc" matches "windows.kernel32.VirtualAlloc")
            for op in operations:
                if func_name.endswith(op):
                    return True
            return False

        # Check for dangerous operations
        if self.mode == SafetyMode.SAFE:
            if matches_operation(func_name, self.DANGEROUS_OPERATIONS):
                self.violations.append(SafetyViolation(
                    f"Dangerous operation '{func_name}' not allowed in SAFE mode. "
                    f"Use @unsafe decorator or switch to UNSAFE mode.",
                    call,
                    "error"
                ))

            if matches_operation(func_name, self.INJECTION_OPERATIONS):
                self.violations.append(SafetyViolation(
                    f"Process injection operation '{func_name}' not allowed in SAFE mode. "
                    f"Use @unsafe decorator or switch to UNSAFE mode.",
                    call,
                    "error"
                ))

            if matches_operation(func_name, self.KERNEL_OPERATIONS):
                self.violations.append(SafetyViolation(
                    f"Kernel operation '{func_name}' not allowed in SAFE mode. "
                    f"Use @unsafe decorator or switch to UNSAFE mode.",
                    call,
                    "error"
                ))

            if matches_operation(func_name, self.REGISTRY_WRITE_OPS):
                self.violations.append(SafetyViolation(
                    f"Registry write operation '{func_name}' will be logged in SAFE mode.",
                    call,
                    "warning"
                ))

    def get_call_name(self, call: CallExpr) -> Optional[str]:
        """Extract function name from call expression"""
        if isinstance(call.callee, IdentifierExpr):
            return call.callee.name
        elif isinstance(call.callee, MemberExpr):
            # Build full path like "kernel32.VirtualAlloc"
            parts = []
            expr = call.callee
            while isinstance(expr, MemberExpr):
                parts.insert(0, expr.member)
                expr = expr.object
            if isinstance(expr, IdentifierExpr):
                parts.insert(0, expr.name)
            return ".".join(parts)
        return None

    def add_custom_rule(self, operation: str) -> None:
        """Add a custom safety rule"""
        self.custom_rules.add(operation)

    def is_operation_allowed(self, operation: str) -> bool:
        """Check if an operation is allowed in current mode"""
        if self.mode == SafetyMode.UNSAFE:
            return True

        if self.mode == SafetyMode.SAFE:
            return operation not in self.DANGEROUS_OPERATIONS and \
                   operation not in self.INJECTION_OPERATIONS and \
                   operation not in self.KERNEL_OPERATIONS

        if self.mode == SafetyMode.CUSTOM:
            return operation not in self.custom_rules

        return True


def check_safety(program: Program, mode: SafetyMode = SafetyMode.SAFE) -> List[SafetyViolation]:
    """Convenience function to check program safety"""
    checker = SafetyChecker(mode)
    return checker.check_program(program)
