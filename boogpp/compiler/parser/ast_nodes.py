"""
Boogpp Abstract Syntax Tree Node Definitions
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Union
from enum import Enum, auto


class NodeType(Enum):
    """AST Node Types"""
    # Program structure
    PROGRAM = auto()
    MODULE = auto()
    IMPORT = auto()
    FROM_IMPORT = auto()

    # Declarations
    FUNCTION_DECL = auto()
    VARIABLE_DECL = auto()
    STRUCT_DECL = auto()
    ENUM_DECL = auto()
    TRAIT_DECL = auto()
    IMPL_DECL = auto()

    # Statements
    RETURN_STMT = auto()
    IF_STMT = auto()
    WHILE_STMT = auto()
    FOR_STMT = auto()
    MATCH_STMT = auto()
    EXPR_STMT = auto()
    ASSIGN_STMT = auto()
    PASS_STMT = auto()
    BREAK_STMT = auto()
    CONTINUE_STMT = auto()
    DEFER_STMT = auto()
    BLOCK = auto()

    # Expressions
    BINARY_EXPR = auto()
    UNARY_EXPR = auto()
    CALL_EXPR = auto()
    MEMBER_EXPR = auto()
    INDEX_EXPR = auto()
    LITERAL_EXPR = auto()
    IDENTIFIER_EXPR = auto()
    TRY_CHAIN_EXPR = auto()
    TUPLE_EXPR = auto()
    ARRAY_EXPR = auto()

    # Types
    TYPE_NAME = auto()
    TYPE_PTR = auto()
    TYPE_ARRAY = auto()
    TYPE_SLICE = auto()
    TYPE_TUPLE = auto()
    TYPE_RESULT = auto()

    # Decorators
    DECORATOR = auto()

    # Other
    PARAMETER = auto()
    CASE_CLAUSE = auto()


class ASTNode:
    """Base class for all AST nodes"""
    def __init__(self, line: int, column: int, filename: Optional[str] = None):
        self.line = line
        self.column = column
        self.filename = filename
        self.node_type = None


# ===== Program Structure =====

class Program(ASTNode):
    """Root node of the AST"""
    def __init__(self, decorators: List, module_decl: Optional['ModuleDecl'],
                 imports: List, declarations: List, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.PROGRAM
        self.decorators = decorators
        self.module_decl = module_decl
        self.imports = imports
        self.declarations = declarations


class ModuleDecl(ASTNode):
    """Module declaration: module my_module"""
    def __init__(self, name: str, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.MODULE
        self.name = name


class ImportStmt(ASTNode):
    """Import statement: import windows.registry"""
    def __init__(self, module_path: List[str], alias: Optional[str], line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.IMPORT
        self.module_path = module_path
        self.alias = alias


class FromImportStmt(ASTNode):
    """From import: from windows.user32 import MessageBoxW"""
    def __init__(self, module_path: List[str], names: List[str], line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.FROM_IMPORT
        self.module_path = module_path
        self.names = names


# ===== Type Nodes =====

class TypeNode(ASTNode):
    """Base class for type nodes"""
    pass


class TypeName(TypeNode):
    """Simple type name: i32, string, etc."""
    def __init__(self, name: str, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.TYPE_NAME
        self.name = name


class TypePtr(TypeNode):
    """Pointer type: ptr[T]"""
    def __init__(self, element_type: TypeNode, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.TYPE_PTR
        self.element_type = element_type


class TypeArray(TypeNode):
    """Array type: array[T, N]"""
    def __init__(self, element_type: TypeNode, size: int, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.TYPE_ARRAY
        self.element_type = element_type
        self.size = size


class TypeSlice(TypeNode):
    """Slice type: slice[T]"""
    def __init__(self, element_type: TypeNode, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.TYPE_SLICE
        self.element_type = element_type


class TypeTuple(TypeNode):
    """Tuple type: tuple(T1, T2, ...)"""
    def __init__(self, element_types: List[TypeNode], line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.TYPE_TUPLE
        self.element_types = element_types


class TypeResult(TypeNode):
    """Result type: result[T]"""
    def __init__(self, value_type: TypeNode, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.TYPE_RESULT
        self.value_type = value_type


# ===== Decorators =====

class Decorator(ASTNode):
    """Decorator: @hook(event: PROCESS_CREATION)"""
    def __init__(self, name: str, arguments: dict, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.DECORATOR
        self.name = name
        self.arguments = arguments


# ===== Declarations =====

class Parameter(ASTNode):
    """Function parameter"""
    def __init__(self, name: str, type_annotation: TypeNode, default_value: Optional['Expression'],
                 line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.PARAMETER
        self.name = name
        self.type_annotation = type_annotation
        self.default_value = default_value


class FunctionDecl(ASTNode):
    """Function declaration"""
    def __init__(self, name: str, parameters: List[Parameter], return_type: Optional[TypeNode],
                 body: 'Block', decorators: List[Decorator], line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.FUNCTION_DECL
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.body = body
        self.decorators = decorators


class VariableDecl(ASTNode):
    """Variable declaration: let/var name: type = value"""
    def __init__(self, name: str, type_annotation: Optional[TypeNode], initializer: Optional['Expression'],
                 is_mutable: bool, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.VARIABLE_DECL
        self.name = name
        self.type_annotation = type_annotation
        self.initializer = initializer
        self.is_mutable = is_mutable


@dataclass
class StructField:
    """Struct field"""
    name: str
    type_annotation: TypeNode


class StructDecl(ASTNode):
    """Struct declaration"""
    def __init__(self, name: str, fields: List[StructField], line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.STRUCT_DECL
        self.name = name
        self.fields = fields


@dataclass
class EnumVariant:
    """Enum variant"""
    name: str
    value: Optional[int] = None


class EnumDecl(ASTNode):
    """Enum declaration"""
    def __init__(self, name: str, variants: List[EnumVariant], line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.ENUM_DECL
        self.name = name
        self.variants = variants


# ===== Statements =====

class Statement(ASTNode):
    """Base class for statements"""
    pass


class Block(Statement):
    """Block of statements"""
    def __init__(self, statements: List[Statement], line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.BLOCK
        self.statements = statements


class ReturnStmt(Statement):
    """Return statement"""
    def __init__(self, value: Optional['Expression'], line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.RETURN_STMT
        self.value = value


class IfStmt(Statement):
    """If statement"""
    def __init__(self, condition: 'Expression', then_block: Block, elif_clauses: List,
                 else_block: Optional[Block], line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.IF_STMT
        self.condition = condition
        self.then_block = then_block
        self.elif_clauses = elif_clauses
        self.else_block = else_block


class WhileStmt(Statement):
    """While statement"""
    def __init__(self, condition: 'Expression', body: Block, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.WHILE_STMT
        self.condition = condition
        self.body = body


class ForStmt(Statement):
    """For statement"""
    def __init__(self, variable: str, iterable: 'Expression', body: Block,
                 line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.FOR_STMT
        self.variable = variable
        self.iterable = iterable
        self.body = body


class CaseClause(ASTNode):
    """Match case clause"""
    def __init__(self, pattern: 'Expression', body: Block, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.CASE_CLAUSE
        self.pattern = pattern
        self.body = body


class MatchStmt(Statement):
    """Match statement"""
    def __init__(self, value: 'Expression', cases: List[CaseClause], line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.MATCH_STMT
        self.value = value
        self.cases = cases


class ExprStmt(Statement):
    """Expression statement"""
    def __init__(self, expression: 'Expression', line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.EXPR_STMT
        self.expression = expression


class AssignStmt(Statement):
    """Assignment statement"""
    def __init__(self, target: 'Expression', value: 'Expression', operator: str,
                 line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.ASSIGN_STMT
        self.target = target
        self.value = value
        self.operator = operator


class PassStmt(Statement):
    """Pass statement"""
    def __init__(self, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.PASS_STMT


class BreakStmt(Statement):
    """Break statement"""
    def __init__(self, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.BREAK_STMT


class ContinueStmt(Statement):
    """Continue statement"""
    def __init__(self, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.CONTINUE_STMT


class DeferStmt(Statement):
    """Defer statement"""
    def __init__(self, statement: Statement, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.DEFER_STMT
        self.statement = statement


# ===== Expressions =====

class Expression(ASTNode):
    """Base class for expressions"""
    pass


class LiteralExpr(Expression):
    """Literal expression"""
    def __init__(self, value: Any, literal_type: str, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.LITERAL_EXPR
        self.value = value
        self.literal_type = literal_type


class IdentifierExpr(Expression):
    """Identifier expression"""
    def __init__(self, name: str, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.IDENTIFIER_EXPR
        self.name = name


class BinaryExpr(Expression):
    """Binary expression"""
    def __init__(self, left: Expression, operator: str, right: Expression,
                 line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.BINARY_EXPR
        self.left = left
        self.operator = operator
        self.right = right


class UnaryExpr(Expression):
    """Unary expression"""
    def __init__(self, operator: str, operand: Expression, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.UNARY_EXPR
        self.operator = operator
        self.operand = operand


class CallExpr(Expression):
    """Function call expression"""
    def __init__(self, callee: Expression, arguments: List[Expression],
                 line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.CALL_EXPR
        self.callee = callee
        self.arguments = arguments


class MemberExpr(Expression):
    """Member access expression: obj.member"""
    def __init__(self, object: Expression, member: str, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.MEMBER_EXPR
        self.object = object
        self.member = member


class IndexExpr(Expression):
    """Index expression: arr[index]"""
    def __init__(self, object: Expression, index: Expression, line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.INDEX_EXPR
        self.object = object
        self.index = index


class TupleExpr(Expression):
    """Tuple expression"""
    def __init__(self, elements: List[Expression], line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.TUPLE_EXPR
        self.elements = elements


class ArrayExpr(Expression):
    """Array literal expression"""
    def __init__(self, elements: List[Expression], line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.ARRAY_EXPR
        self.elements = elements


class TryChainExpr(Expression):
    """try_chain expression"""
    def __init__(self, primary: Expression, secondary: Optional[Expression], fallback: Optional[Expression],
                 line: int, column: int, filename: Optional[str] = None):
        super().__init__(line, column, filename)
        self.node_type = NodeType.TRY_CHAIN_EXPR
        self.primary = primary
        self.secondary = secondary
        self.fallback = fallback
