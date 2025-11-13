"""
Boogpp Type Checker
Performs type checking and type inference on the AST.
"""

from typing import List, Optional, Dict
from ..parser.ast_nodes import *
from .type_system import (
    Type, TypeKind, TypeEnvironment, TypeVariable,
    get_primitive_type, PRIMITIVE_TYPES
)


class TypeError:
    """Represents a type error"""
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


class TypeChecker:
    """Type checker for Boogpp"""

    def __init__(self):
        self.env = TypeEnvironment()
        self.errors: List[TypeError] = []
        self.type_annotations: Dict[ASTNode, Type] = {}
        self.current_function_return_type: Optional[Type] = None

        # Initialize built-in types and functions
        self._init_builtins()

    def _init_builtins(self) -> None:
        """Initialize built-in functions and types"""
        # Built-in constants
        self.env.define_variable('SUCCESS', PRIMITIVE_TYPES['i32'])
        self.env.define_variable('true', PRIMITIVE_TYPES['bool'])
        self.env.define_variable('false', PRIMITIVE_TYPES['bool'])

        # Built-in functions
        self.env.define_function('print', Type(
            TypeKind.FUNCTION,
            param_types=[PRIMITIVE_TYPES['string']],
            return_type=PRIMITIVE_TYPES['void']
        ))
        self.env.define_function('len', Type(
            TypeKind.FUNCTION,
            param_types=[Type(TypeKind.UNKNOWN)],  # Generic
            return_type=PRIMITIVE_TYPES['u64']
        ))
        self.env.define_function('alloc', Type(
            TypeKind.FUNCTION,
            param_types=[PRIMITIVE_TYPES['u64']],
            return_type=Type(TypeKind.POINTER, element_type=PRIMITIVE_TYPES['u8'])
        ))
        self.env.define_function('free', Type(
            TypeKind.FUNCTION,
            param_types=[Type(TypeKind.POINTER, element_type=Type(TypeKind.UNKNOWN))],
            return_type=PRIMITIVE_TYPES['void']
        ))
        self.env.define_function('sleep', Type(
            TypeKind.FUNCTION,
            param_types=[PRIMITIVE_TYPES['u64']],
            return_type=PRIMITIVE_TYPES['void']
        ))
        self.env.define_function('range', Type(
            TypeKind.FUNCTION,
            param_types=[PRIMITIVE_TYPES['i32'], PRIMITIVE_TYPES['i32']],
            return_type=Type(TypeKind.SLICE, element_type=PRIMITIVE_TYPES['i32'])
        ))

    def check_program(self, program: Program) -> List[TypeError]:
        """Check entire program for type errors"""
        self.errors = []

        # First pass: collect all function and struct declarations
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                self._register_function(decl)
            elif isinstance(decl, StructDecl):
                self._register_struct(decl)
            elif isinstance(decl, EnumDecl):
                self._register_enum(decl)

        # Second pass: type check all declarations
        for decl in program.declarations:
            self.check_declaration(decl)

        return self.errors

    def _register_function(self, func: FunctionDecl) -> None:
        """Register a function in the type environment"""
        param_types = []
        for param in func.parameters:
            param_type = self.resolve_type_annotation(param.type_annotation)
            param_types.append(param_type)

        return_type = (self.resolve_type_annotation(func.return_type)
                      if func.return_type else PRIMITIVE_TYPES['void'])

        func_type = Type(
            TypeKind.FUNCTION,
            name=func.name,
            param_types=param_types,
            return_type=return_type
        )
        self.env.define_function(func.name, func_type)

    def _register_struct(self, struct: StructDecl) -> None:
        """Register a struct in the type environment"""
        fields = {}
        for field in struct.fields:
            field_type = self.resolve_type_annotation(field.type_annotation)
            fields[field.name] = field_type

        struct_type = Type(TypeKind.STRUCT, name=struct.name, fields=fields)
        self.env.define_struct(struct.name, struct_type)

    def _register_enum(self, enum: EnumDecl) -> None:
        """Register an enum in the type environment"""
        variants = [variant.name for variant in enum.variants]
        enum_type = Type(TypeKind.ENUM, name=enum.name, variants=variants)
        self.env.define_enum(enum.name, enum_type)

    def resolve_type_annotation(self, type_node: Optional[TypeNode]) -> Type:
        """Resolve a type annotation to a Type"""
        if type_node is None:
            return Type(TypeKind.UNKNOWN)

        if isinstance(type_node, TypeName):
            # Check for primitive types
            prim_type = get_primitive_type(type_node.name)
            if prim_type:
                return prim_type

            # Check for user-defined types
            struct_type = self.env.lookup_struct(type_node.name)
            if struct_type:
                return struct_type

            enum_type = self.env.lookup_enum(type_node.name)
            if enum_type:
                return enum_type

            # Unknown type
            self.errors.append(TypeError(
                f"Unknown type '{type_node.name}'",
                type_node
            ))
            return Type(TypeKind.ERROR)

        elif isinstance(type_node, TypePtr):
            element_type = self.resolve_type_annotation(type_node.element_type)
            return Type(TypeKind.POINTER, element_type=element_type)

        elif isinstance(type_node, TypeArray):
            element_type = self.resolve_type_annotation(type_node.element_type)
            return Type(TypeKind.ARRAY, element_type=element_type, size=type_node.size)

        elif isinstance(type_node, TypeSlice):
            element_type = self.resolve_type_annotation(type_node.element_type)
            return Type(TypeKind.SLICE, element_type=element_type)

        elif isinstance(type_node, TypeTuple):
            element_types = [self.resolve_type_annotation(t) for t in type_node.element_types]
            return Type(TypeKind.TUPLE, element_types=element_types)

        elif isinstance(type_node, TypeResult):
            value_type = self.resolve_type_annotation(type_node.value_type)
            return Type(TypeKind.RESULT, element_type=value_type)

        return Type(TypeKind.UNKNOWN)

    def check_declaration(self, decl: ASTNode) -> None:
        """Check a declaration"""
        if isinstance(decl, FunctionDecl):
            self.check_function(decl)
        elif isinstance(decl, VariableDecl):
            self.check_variable_decl(decl)

    def check_function(self, func: FunctionDecl) -> None:
        """Check a function declaration"""
        # Create new scope for function
        self.env = self.env.create_child()

        # Add parameters to scope
        for param in func.parameters:
            param_type = self.resolve_type_annotation(param.type_annotation)
            self.env.define_variable(param.name, param_type)

        # Set current return type
        self.current_function_return_type = (
            self.resolve_type_annotation(func.return_type)
            if func.return_type else PRIMITIVE_TYPES['void']
        )

        # Check function body
        self.check_statement(func.body)

        # Restore previous scope
        self.env = self.env.parent
        self.current_function_return_type = None

    def check_variable_decl(self, decl: VariableDecl) -> None:
        """Check a variable declaration"""
        # Type check initializer if present
        init_type = None
        if decl.initializer:
            init_type = self.check_expression(decl.initializer)

        # Resolve declared type
        declared_type = None
        if decl.type_annotation:
            declared_type = self.resolve_type_annotation(decl.type_annotation)

        # Determine variable type
        if declared_type and init_type:
            # Both declared and inferred - check compatibility
            if not init_type.can_assign_to(declared_type):
                self.errors.append(TypeError(
                    f"Cannot assign value of type '{init_type}' to variable of type '{declared_type}'",
                    decl
                ))
            var_type = declared_type
        elif declared_type:
            var_type = declared_type
        elif init_type:
            var_type = init_type
        else:
            self.errors.append(TypeError(
                f"Variable '{decl.name}' must have either a type annotation or initializer",
                decl
            ))
            var_type = Type(TypeKind.ERROR)

        # Add to environment
        self.env.define_variable(decl.name, var_type)
        self.type_annotations[decl] = var_type

    def check_statement(self, stmt: Statement) -> None:
        """Check a statement"""
        if isinstance(stmt, Block):
            # Create new scope for block
            self.env = self.env.create_child()
            for s in stmt.statements:
                self.check_statement(s)
            self.env = self.env.parent

        elif isinstance(stmt, ReturnStmt):
            if stmt.value:
                return_type = self.check_expression(stmt.value)
                if self.current_function_return_type:
                    if not return_type.can_assign_to(self.current_function_return_type):
                        self.errors.append(TypeError(
                            f"Cannot return value of type '{return_type}', expected '{self.current_function_return_type}'",
                            stmt
                        ))
            else:
                if (self.current_function_return_type and
                    self.current_function_return_type.kind != TypeKind.VOID):
                    self.errors.append(TypeError(
                        f"Must return a value of type '{self.current_function_return_type}'",
                        stmt
                    ))

        elif isinstance(stmt, IfStmt):
            cond_type = self.check_expression(stmt.condition)
            if cond_type.kind != TypeKind.BOOL:
                self.errors.append(TypeError(
                    f"If condition must be bool, got '{cond_type}'",
                    stmt.condition
                ))
            self.check_statement(stmt.then_block)
            for cond, block in stmt.elif_clauses:
                cond_type = self.check_expression(cond)
                if cond_type.kind != TypeKind.BOOL:
                    self.errors.append(TypeError(
                        f"Elif condition must be bool, got '{cond_type}'",
                        cond
                    ))
                self.check_statement(block)
            if stmt.else_block:
                self.check_statement(stmt.else_block)

        elif isinstance(stmt, WhileStmt):
            cond_type = self.check_expression(stmt.condition)
            if cond_type.kind != TypeKind.BOOL:
                self.errors.append(TypeError(
                    f"While condition must be bool, got '{cond_type}'",
                    stmt.condition
                ))
            self.check_statement(stmt.body)

        elif isinstance(stmt, ForStmt):
            iter_type = self.check_expression(stmt.iterable)
            # Check if iterable is a slice or array
            if iter_type.kind not in (TypeKind.SLICE, TypeKind.ARRAY):
                self.errors.append(TypeError(
                    f"For loop requires iterable type (slice or array), got '{iter_type}'",
                    stmt.iterable
                ))
            # Add loop variable to scope
            self.env = self.env.create_child()
            elem_type = iter_type.element_type if iter_type.element_type else Type(TypeKind.UNKNOWN)
            self.env.define_variable(stmt.variable, elem_type)
            self.check_statement(stmt.body)
            self.env = self.env.parent

        elif isinstance(stmt, MatchStmt):
            value_type = self.check_expression(stmt.value)
            for case in stmt.cases:
                pattern_type = self.check_expression(case.pattern)
                # Pattern should be compatible with value type
                if not pattern_type.can_assign_to(value_type):
                    self.errors.append(TypeError(
                        f"Match pattern type '{pattern_type}' incompatible with value type '{value_type}'",
                        case.pattern
                    ))
                self.check_statement(case.body)

        elif isinstance(stmt, ExprStmt):
            self.check_expression(stmt.expression)

        elif isinstance(stmt, AssignStmt):
            target_type = self.check_expression(stmt.target)
            value_type = self.check_expression(stmt.value)

            if stmt.operator == '=':
                if not value_type.can_assign_to(target_type):
                    self.errors.append(TypeError(
                        f"Cannot assign value of type '{value_type}' to target of type '{target_type}'",
                        stmt
                    ))
            else:
                # Compound assignment (+=, -=, etc.)
                # Check operator compatibility
                if not target_type.is_numeric() or not value_type.is_numeric():
                    self.errors.append(TypeError(
                        f"Compound assignment requires numeric types, got '{target_type}' and '{value_type}'",
                        stmt
                    ))

        elif isinstance(stmt, DeferStmt):
            self.check_statement(stmt.statement)

        elif isinstance(stmt, VariableDecl):
            self.check_variable_decl(stmt)

    def check_expression(self, expr: Expression) -> Type:
        """Check an expression and return its type"""
        if isinstance(expr, LiteralExpr):
            return self.check_literal(expr)

        elif isinstance(expr, IdentifierExpr):
            var_type = self.env.lookup_variable(expr.name)
            if var_type is None:
                self.errors.append(TypeError(
                    f"Undefined variable '{expr.name}'",
                    expr
                ))
                return Type(TypeKind.ERROR)
            self.type_annotations[expr] = var_type
            return var_type

        elif isinstance(expr, BinaryExpr):
            return self.check_binary_expr(expr)

        elif isinstance(expr, UnaryExpr):
            return self.check_unary_expr(expr)

        elif isinstance(expr, CallExpr):
            return self.check_call_expr(expr)

        elif isinstance(expr, MemberExpr):
            return self.check_member_expr(expr)

        elif isinstance(expr, IndexExpr):
            return self.check_index_expr(expr)

        elif isinstance(expr, TupleExpr):
            element_types = [self.check_expression(e) for e in expr.elements]
            tuple_type = Type(TypeKind.TUPLE, element_types=element_types)
            self.type_annotations[expr] = tuple_type
            return tuple_type

        elif isinstance(expr, ArrayExpr):
            if not expr.elements:
                # Empty array - need type annotation
                return Type(TypeKind.ARRAY, element_type=Type(TypeKind.UNKNOWN), size=0)

            # Check all elements have same type
            first_type = self.check_expression(expr.elements[0])
            for elem in expr.elements[1:]:
                elem_type = self.check_expression(elem)
                if elem_type != first_type:
                    self.errors.append(TypeError(
                        f"Array elements must have same type, got '{first_type}' and '{elem_type}'",
                        elem
                    ))

            array_type = Type(TypeKind.ARRAY, element_type=first_type, size=len(expr.elements))
            self.type_annotations[expr] = array_type
            return array_type

        elif isinstance(expr, TryChainExpr):
            # All branches should have compatible types
            primary_type = self.check_expression(expr.primary)
            if expr.secondary:
                secondary_type = self.check_expression(expr.secondary)
                if not secondary_type.can_assign_to(primary_type):
                    self.errors.append(TypeError(
                        f"try_chain secondary type '{secondary_type}' incompatible with primary type '{primary_type}'",
                        expr.secondary
                    ))
            if expr.fallback:
                fallback_type = self.check_expression(expr.fallback)
                if not fallback_type.can_assign_to(primary_type):
                    self.errors.append(TypeError(
                        f"try_chain fallback type '{fallback_type}' incompatible with primary type '{primary_type}'",
                        expr.fallback
                    ))
            self.type_annotations[expr] = primary_type
            return primary_type

        return Type(TypeKind.UNKNOWN)

    def check_literal(self, literal: LiteralExpr) -> Type:
        """Check a literal expression"""
        if literal.literal_type in ('int', 'integer'):
            # Default to i32 for integer literals
            lit_type = PRIMITIVE_TYPES['i32']
        elif literal.literal_type == 'float':
            lit_type = PRIMITIVE_TYPES['f64']
        elif literal.literal_type == 'string':
            lit_type = PRIMITIVE_TYPES['string']
        elif literal.literal_type in ('bool', 'boolean'):
            lit_type = PRIMITIVE_TYPES['bool']
        elif literal.literal_type == 'char':
            lit_type = PRIMITIVE_TYPES['char']
        else:
            lit_type = Type(TypeKind.UNKNOWN)

        self.type_annotations[literal] = lit_type
        return lit_type

    def check_binary_expr(self, expr: BinaryExpr) -> Type:
        """Check a binary expression"""
        left_type = self.check_expression(expr.left)
        right_type = self.check_expression(expr.right)

        # Arithmetic operators
        if expr.operator in ('+', '-', '*', '/', '%', '**'):
            if not left_type.is_numeric() or not right_type.is_numeric():
                self.errors.append(TypeError(
                    f"Arithmetic operator '{expr.operator}' requires numeric types, got '{left_type}' and '{right_type}'",
                    expr
                ))
                return Type(TypeKind.ERROR)
            # Result type is the wider of the two types
            result_type = left_type if left_type == right_type else PRIMITIVE_TYPES['i32']
            self.type_annotations[expr] = result_type
            return result_type

        # Comparison operators
        elif expr.operator in ('==', '!=', '<', '>', '<=', '>='):
            if not left_type.is_numeric() or not right_type.is_numeric():
                if left_type != right_type:
                    self.errors.append(TypeError(
                        f"Comparison operator '{expr.operator}' requires compatible types, got '{left_type}' and '{right_type}'",
                        expr
                    ))
            result_type = PRIMITIVE_TYPES['bool']
            self.type_annotations[expr] = result_type
            return result_type

        # Logical operators
        elif expr.operator in ('and', 'or'):
            if left_type.kind != TypeKind.BOOL or right_type.kind != TypeKind.BOOL:
                self.errors.append(TypeError(
                    f"Logical operator '{expr.operator}' requires bool types, got '{left_type}' and '{right_type}'",
                    expr
                ))
            result_type = PRIMITIVE_TYPES['bool']
            self.type_annotations[expr] = result_type
            return result_type

        # Bitwise operators
        elif expr.operator in ('&', '|', '^', '<<', '>>'):
            if not left_type.is_integer() or not right_type.is_integer():
                self.errors.append(TypeError(
                    f"Bitwise operator '{expr.operator}' requires integer types, got '{left_type}' and '{right_type}'",
                    expr
                ))
                return Type(TypeKind.ERROR)
            result_type = left_type
            self.type_annotations[expr] = result_type
            return result_type

        return Type(TypeKind.UNKNOWN)

    def check_unary_expr(self, expr: UnaryExpr) -> Type:
        """Check a unary expression"""
        operand_type = self.check_expression(expr.operand)

        if expr.operator == 'not':
            if operand_type.kind != TypeKind.BOOL:
                self.errors.append(TypeError(
                    f"Logical not requires bool type, got '{operand_type}'",
                    expr
                ))
            result_type = PRIMITIVE_TYPES['bool']
        elif expr.operator == '-':
            if not operand_type.is_numeric():
                self.errors.append(TypeError(
                    f"Unary minus requires numeric type, got '{operand_type}'",
                    expr
                ))
            result_type = operand_type
        elif expr.operator == '~':
            if not operand_type.is_integer():
                self.errors.append(TypeError(
                    f"Bitwise not requires integer type, got '{operand_type}'",
                    expr
                ))
            result_type = operand_type
        else:
            result_type = Type(TypeKind.UNKNOWN)

        self.type_annotations[expr] = result_type
        return result_type

    def check_call_expr(self, expr: CallExpr) -> Type:
        """Check a function call expression"""
        # Get function name
        func_name = None
        if isinstance(expr.callee, IdentifierExpr):
            func_name = expr.callee.name
        elif isinstance(expr.callee, MemberExpr):
            # Method call - handle later
            pass

        if func_name:
            func_type = self.env.lookup_function(func_name)
            if func_type is None:
                self.errors.append(TypeError(
                    f"Undefined function '{func_name}'",
                    expr
                ))
                return Type(TypeKind.ERROR)

            # Check argument count
            expected_params = len(func_type.param_types)
            actual_args = len(expr.arguments)
            if expected_params != actual_args:
                self.errors.append(TypeError(
                    f"Function '{func_name}' expects {expected_params} arguments, got {actual_args}",
                    expr
                ))

            # Check argument types
            for i, (arg, expected_type) in enumerate(zip(expr.arguments, func_type.param_types)):
                arg_type = self.check_expression(arg)
                if expected_type.kind != TypeKind.UNKNOWN:  # Skip generic types
                    if not arg_type.can_assign_to(expected_type):
                        self.errors.append(TypeError(
                            f"Argument {i+1} to function '{func_name}': expected '{expected_type}', got '{arg_type}'",
                            arg
                        ))

            self.type_annotations[expr] = func_type.return_type
            return func_type.return_type

        # If not a simple function call, return unknown
        return Type(TypeKind.UNKNOWN)

    def check_member_expr(self, expr: MemberExpr) -> Type:
        """Check a member access expression"""
        object_type = self.check_expression(expr.object)

        if object_type.kind == TypeKind.STRUCT:
            if object_type.fields and expr.member in object_type.fields:
                member_type = object_type.fields[expr.member]
                self.type_annotations[expr] = member_type
                return member_type
            else:
                self.errors.append(TypeError(
                    f"Struct '{object_type.name}' has no field '{expr.member}'",
                    expr
                ))
                return Type(TypeKind.ERROR)

        # For now, allow member access on unknown types (e.g., module access)
        return Type(TypeKind.UNKNOWN)

    def check_index_expr(self, expr: IndexExpr) -> Type:
        """Check an index expression"""
        object_type = self.check_expression(expr.object)
        index_type = self.check_expression(expr.index)

        # Index must be integer
        if not index_type.is_integer():
            self.errors.append(TypeError(
                f"Array index must be integer type, got '{index_type}'",
                expr.index
            ))

        # Object must be array or slice
        if object_type.kind in (TypeKind.ARRAY, TypeKind.SLICE):
            elem_type = object_type.element_type
            self.type_annotations[expr] = elem_type
            return elem_type
        else:
            self.errors.append(TypeError(
                f"Cannot index into type '{object_type}'",
                expr
            ))
            return Type(TypeKind.ERROR)


def check_types(program: Program) -> List[TypeError]:
    """Convenience function to type check a program"""
    checker = TypeChecker()
    return checker.check_program(program)
