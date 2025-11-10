"""
CustomOS Enhanced Safety Checker
Integrates detailed safety rules with comprehensive checking.
"""

from enum import Enum, auto
from typing import List, Optional, Dict, Set
from ..parser.ast_nodes import *
from .safety_rules import SAFETY_RULES, SafetyCategory, OperationRisk


class SafetyMode(Enum):
    """Safety modes"""
    SAFE = auto()
    UNSAFE = auto()
    CUSTOM = auto()


class SafetyViolation:
    """Represents a safety violation"""
    def __init__(self, message: str, node: ASTNode, severity: str = "error",
                 category: Optional[SafetyCategory] = None,
                 risk: Optional[OperationRisk] = None,
                 suggestion: Optional[str] = None):
        self.message = message
        self.node = node
        self.severity = severity
        self.category = category
        self.risk = risk
        self.suggestion = suggestion
        self.line = node.line
        self.column = node.column
        self.filename = node.filename

    def __str__(self):
        location = f"{self.filename or '<input>'}:{self.line}:{self.column}"
        result = f"{location}: [{self.severity}] {self.message}"
        if self.suggestion:
            result += f"\n  Suggestion: {self.suggestion}"
        if self.category:
            result += f"\n  Category: {self.category.name}"
        if self.risk:
            result += f"\n  Risk Level: {self.risk.name}"
        return result


class EnhancedSafetyChecker:
    """Enhanced safety checker with detailed rules"""

    def __init__(self, mode: SafetyMode = SafetyMode.SAFE):
        self.mode = mode
        self.violations: List[SafetyViolation] = []
        self.custom_rules: Dict[str, bool] = {}  # operation -> allowed
        self.logging_enabled = (mode == SafetyMode.SAFE)
        self.statistics = {
            'total_operations': 0,
            'dangerous_operations': 0,
            'logged_operations': 0,
            'blocked_operations': 0
        }

        # Track unsafe contexts
        self.unsafe_contexts: List[str] = []

    def check_program(self, program: Program) -> List[SafetyViolation]:
        """Check entire program for safety violations"""
        self.violations = []
        self.statistics = {
            'total_operations': 0,
            'dangerous_operations': 0,
            'logged_operations': 0,
            'blocked_operations': 0
        }

        # Check file-level safety decorator
        for decorator in program.decorators:
            if decorator.name == "safety_level":
                mode_arg = decorator.arguments.get("mode")
                if mode_arg and isinstance(mode_arg, IdentifierExpr):
                    try:
                        self.mode = SafetyMode[mode_arg.name]
                    except KeyError:
                        self.violations.append(SafetyViolation(
                            f"Unknown safety mode '{mode_arg.name}'. Valid modes: SAFE, UNSAFE, CUSTOM",
                            decorator,
                            "error"
                        ))

        # Check all declarations
        for decl in program.declarations:
            self.check_declaration(decl)

        return self.violations

    def check_declaration(self, decl: ASTNode) -> None:
        """Check a declaration"""
        if isinstance(decl, FunctionDecl):
            self.check_function(decl)
        elif isinstance(decl, StructDecl):
            # Check struct fields for pointer types in SAFE mode
            if self.mode == SafetyMode.SAFE:
                for field in decl.fields:
                    if isinstance(field.type_annotation, TypePtr):
                        self.violations.append(SafetyViolation(
                            f"Raw pointer type in struct field '{field.name}' not allowed in SAFE mode",
                            decl,
                            "error",
                            category=SafetyCategory.MEMORY_MANAGEMENT,
                            risk=OperationRisk.HIGH,
                            suggestion="Use references or safe pointer wrappers instead"
                        ))

    def check_function(self, func: FunctionDecl) -> None:
        """Check function for safety violations"""
        # Check if function has @unsafe decorator
        function_mode = self.mode
        has_unsafe_decorator = False

        for decorator in func.decorators:
            if decorator.name == "unsafe":
                has_unsafe_decorator = True
                function_mode = SafetyMode.UNSAFE
                break
            elif decorator.name == "hook":
                # Hooks require validation
                event = decorator.arguments.get("event")
                if not event:
                    self.violations.append(SafetyViolation(
                        f"Hook decorator on function '{func.name}' must specify 'event' parameter",
                        decorator,
                        "error"
                    ))
            elif decorator.name == "service":
                # Services should be validated
                if self.mode == SafetyMode.SAFE:
                    self.violations.append(SafetyViolation(
                        f"Service decorator on function '{func.name}' requires elevated safety mode",
                        decorator,
                        "warning",
                        suggestion="Consider using UNSAFE mode or proper service validation"
                    ))

        # Warn if function should be marked unsafe but isn't
        if self.mode == SafetyMode.SAFE and not has_unsafe_decorator:
            # Check parameters for raw pointers
            for param in func.parameters:
                if isinstance(param.type_annotation, TypePtr):
                    self.violations.append(SafetyViolation(
                        f"Function '{func.name}' uses raw pointer parameter '{param.name}' but is not marked @unsafe",
                        func,
                        "error",
                        category=SafetyCategory.MEMORY_MANAGEMENT,
                        risk=OperationRisk.HIGH,
                        suggestion=f"Add @unsafe decorator to function '{func.name}'"
                    ))

            # Check return type for raw pointers
            if isinstance(func.return_type, TypePtr):
                self.violations.append(SafetyViolation(
                    f"Function '{func.name}' returns raw pointer but is not marked @unsafe",
                    func,
                    "error",
                    category=SafetyCategory.MEMORY_MANAGEMENT,
                    risk=OperationRisk.HIGH,
                    suggestion=f"Add @unsafe decorator to function '{func.name}'"
                ))

        # Save current mode and switch to function mode
        saved_mode = self.mode
        self.mode = function_mode

        if has_unsafe_decorator:
            self.unsafe_contexts.append(func.name)

        # Check function body
        self.check_statement(func.body)

        # Restore mode
        if has_unsafe_decorator:
            self.unsafe_contexts.pop()
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
            # Check for potential out-of-bounds access
            if self.mode == SafetyMode.SAFE:
                self.statistics['total_operations'] += 1

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
        self.statistics['total_operations'] += 1

        # Get the function name
        func_name = self.get_call_name(call)

        if not func_name:
            return

        # Look up the safety rule
        rule = SAFETY_RULES.get_rule(func_name)

        if rule:
            # Check if operation is allowed in current mode
            if self.mode == SafetyMode.SAFE:
                if not rule.safe_mode_allowed:
                    self.statistics['blocked_operations'] += 1
                    self.statistics['dangerous_operations'] += 1

                    suggestion = rule.alternative if rule.alternative else "Use @unsafe decorator or switch to UNSAFE mode"

                    self.violations.append(SafetyViolation(
                        f"{rule.category.name} operation '{func_name}' not allowed in SAFE mode: {rule.description}",
                        call,
                        "error",
                        category=rule.category,
                        risk=rule.risk,
                        suggestion=suggestion
                    ))
                elif rule.requires_logging:
                    self.statistics['logged_operations'] += 1
                    self.violations.append(SafetyViolation(
                        f"Operation '{func_name}' will be logged: {rule.description}",
                        call,
                        "info",
                        category=rule.category,
                        risk=rule.risk
                    ))

            elif self.mode == SafetyMode.UNSAFE:
                # In UNSAFE mode, log high-risk operations
                if rule.risk in (OperationRisk.HIGH, OperationRisk.CRITICAL):
                    self.statistics['dangerous_operations'] += 1
                    self.violations.append(SafetyViolation(
                        f"High-risk operation '{func_name}': {rule.description}",
                        call,
                        "warning",
                        category=rule.category,
                        risk=rule.risk,
                        suggestion=rule.alternative
                    ))

                if rule.requires_validation:
                    self.violations.append(SafetyViolation(
                        f"Operation '{func_name}' requires careful validation",
                        call,
                        "info",
                        category=rule.category,
                        risk=rule.risk
                    ))

            elif self.mode == SafetyMode.CUSTOM:
                # Check custom rules
                if func_name in self.custom_rules:
                    if not self.custom_rules[func_name]:
                        self.statistics['blocked_operations'] += 1
                        self.violations.append(SafetyViolation(
                            f"Operation '{func_name}' blocked by custom safety rules",
                            call,
                            "error",
                            category=rule.category,
                            risk=rule.risk
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

    def add_custom_rule(self, operation: str, allowed: bool) -> None:
        """Add a custom safety rule"""
        self.custom_rules[operation] = allowed

    def get_statistics(self) -> Dict[str, int]:
        """Get safety checking statistics"""
        return self.statistics.copy()

    def generate_report(self) -> str:
        """Generate a safety report"""
        report = []
        report.append("=== CustomOS Safety Report ===")
        report.append(f"Safety Mode: {self.mode.name}")
        report.append(f"\nStatistics:")
        report.append(f"  Total Operations: {self.statistics['total_operations']}")
        report.append(f"  Dangerous Operations: {self.statistics['dangerous_operations']}")
        report.append(f"  Logged Operations: {self.statistics['logged_operations']}")
        report.append(f"  Blocked Operations: {self.statistics['blocked_operations']}")

        if self.violations:
            report.append(f"\nViolations by Severity:")
            errors = [v for v in self.violations if v.severity == "error"]
            warnings = [v for v in self.violations if v.severity == "warning"]
            info = [v for v in self.violations if v.severity == "info"]

            report.append(f"  Errors: {len(errors)}")
            report.append(f"  Warnings: {len(warnings)}")
            report.append(f"  Info: {len(info)}")

            if errors:
                report.append("\nErrors:")
                for v in errors[:10]:  # Show first 10
                    report.append(f"  {v}")

            if warnings:
                report.append("\nWarnings:")
                for v in warnings[:10]:  # Show first 10
                    report.append(f"  {v}")

        return "\n".join(report)


def check_safety_enhanced(program: Program, mode: SafetyMode = SafetyMode.SAFE) -> List[SafetyViolation]:
    """Convenience function to check program safety with enhanced rules"""
    checker = EnhancedSafetyChecker(mode)
    return checker.check_program(program)
