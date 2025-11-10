"""
Boog++ Parser
Builds an Abstract Syntax Tree from tokens.
"""

from typing import List, Optional, Union
from ..lexer.tokens import Token, TokenType
from .ast_nodes import *


class ParseError(Exception):
    """Raised when parser encounters an error"""
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"{token.filename or '<input>'}:{token.line}:{token.column}: {message}")


class Parser:
    """Parses Boog++ tokens into an AST"""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def error(self, message: str) -> ParseError:
        """Create a parse error at current position"""
        return ParseError(message, self.current())

    def current(self) -> Token:
        """Get current token"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # Return EOF token

    def peek(self, offset: int = 0) -> Token:
        """Peek at token at current position + offset"""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]

    def advance(self) -> Token:
        """Advance to next token and return current"""
        token = self.current()
        if token.type != TokenType.EOF:
            self.pos += 1
        return token

    def expect(self, token_type: TokenType) -> Token:
        """Expect a specific token type and consume it"""
        token = self.current()
        if token.type != token_type:
            raise self.error(f"Expected {token_type.name}, got {token.type.name}")
        return self.advance()

    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        return self.current().type in token_types

    def skip_newlines(self) -> None:
        """Skip newline tokens"""
        while self.match(TokenType.NEWLINE):
            self.advance()

    def consume_newlines(self) -> None:
        """Consume at least one newline"""
        if not self.match(TokenType.NEWLINE):
            raise self.error("Expected newline")
        self.skip_newlines()

    # ===== Type Parsing =====

    def parse_type(self) -> TypeNode:
        """Parse a type annotation"""
        token = self.current()

        # Simple type names
        if self.match(TokenType.I8, TokenType.I16, TokenType.I32, TokenType.I64,
                     TokenType.U8, TokenType.U16, TokenType.U32, TokenType.U64,
                     TokenType.F32, TokenType.F64, TokenType.BOOL, TokenType.STRING,
                     TokenType.CHAR, TokenType.VOID, TokenType.STATUS, TokenType.HANDLE):
            name = self.advance().value
            return TypeName(name, token.line, token.column, token.filename)

        # Identifier (custom types)
        if self.match(TokenType.IDENTIFIER):
            name = self.advance().value
            return TypeName(name, token.line, token.column, token.filename)

        # Pointer type: ptr[T]
        if self.match(TokenType.PTR):
            self.advance()
            self.expect(TokenType.LBRACKET)
            element_type = self.parse_type()
            self.expect(TokenType.RBRACKET)
            return TypePtr(element_type, token.line, token.column, token.filename)

        # Array type: array[T, N]
        if self.match(TokenType.ARRAY):
            self.advance()
            self.expect(TokenType.LBRACKET)
            element_type = self.parse_type()
            self.expect(TokenType.COMMA)
            size_token = self.expect(TokenType.INTEGER_LITERAL)
            self.expect(TokenType.RBRACKET)
            return TypeArray(element_type, size_token.value, token.line, token.column, token.filename)

        # Slice type: slice[T]
        if self.match(TokenType.SLICE):
            self.advance()
            self.expect(TokenType.LBRACKET)
            element_type = self.parse_type()
            self.expect(TokenType.RBRACKET)
            return TypeSlice(element_type, token.line, token.column, token.filename)

        # Tuple type: tuple(T1, T2, ...)
        if self.match(TokenType.TUPLE):
            self.advance()
            self.expect(TokenType.LPAREN)
            element_types = []
            while not self.match(TokenType.RPAREN):
                element_types.append(self.parse_type())
                if not self.match(TokenType.RPAREN):
                    self.expect(TokenType.COMMA)
            self.expect(TokenType.RPAREN)
            return TypeTuple(element_types, token.line, token.column, token.filename)

        # Result type: result[T]
        if self.match(TokenType.RESULT):
            self.advance()
            self.expect(TokenType.LBRACKET)
            value_type = self.parse_type()
            self.expect(TokenType.RBRACKET)
            return TypeResult(value_type, token.line, token.column, token.filename)

        raise self.error(f"Expected type, got {token.type.name}")

    # ===== Decorator Parsing =====

    def parse_decorator(self) -> Decorator:
        """Parse a decorator: @name(arg1: val1, arg2: val2)"""
        token = self.expect(TokenType.AT)
        name_token = self.expect(TokenType.IDENTIFIER)
        name = name_token.value

        arguments = {}
        if self.match(TokenType.LPAREN):
            self.advance()
            while not self.match(TokenType.RPAREN):
                arg_name = self.expect(TokenType.IDENTIFIER).value
                self.expect(TokenType.COLON)
                arg_value = self.parse_primary_expr()
                arguments[arg_name] = arg_value

                if not self.match(TokenType.RPAREN):
                    self.expect(TokenType.COMMA)
            self.expect(TokenType.RPAREN)

        self.skip_newlines()
        return Decorator(name, arguments, token.line, token.column, token.filename)

    # ===== Expression Parsing =====

    def parse_primary_expr(self) -> Expression:
        """Parse primary expressions"""
        token = self.current()

        # Literals
        if self.match(TokenType.INTEGER_LITERAL):
            value = self.advance().value
            return LiteralExpr(value, "int", token.line, token.column, token.filename)

        if self.match(TokenType.FLOAT_LITERAL):
            value = self.advance().value
            return LiteralExpr(value, "float", token.line, token.column, token.filename)

        if self.match(TokenType.STRING_LITERAL):
            value = self.advance().value
            return LiteralExpr(value, "string", token.line, token.column, token.filename)

        if self.match(TokenType.TRUE, TokenType.FALSE):
            value = self.advance().type == TokenType.TRUE
            return LiteralExpr(value, "bool", token.line, token.column, token.filename)

        # Identifier
        if self.match(TokenType.IDENTIFIER):
            name = self.advance().value
            return IdentifierExpr(name, token.line, token.column, token.filename)

        # Parenthesized expression or tuple
        if self.match(TokenType.LPAREN):
            self.advance()
            if self.match(TokenType.RPAREN):
                # Empty tuple
                self.advance()
                return TupleExpr([], token.line, token.column, token.filename)

            first_expr = self.parse_expression()

            if self.match(TokenType.COMMA):
                # Tuple
                elements = [first_expr]
                while self.match(TokenType.COMMA):
                    self.advance()
                    if self.match(TokenType.RPAREN):
                        break
                    elements.append(self.parse_expression())
                self.expect(TokenType.RPAREN)
                return TupleExpr(elements, token.line, token.column, token.filename)
            else:
                # Just parenthesized
                self.expect(TokenType.RPAREN)
                return first_expr

        # Array literal
        if self.match(TokenType.LBRACKET):
            self.advance()
            elements = []
            while not self.match(TokenType.RBRACKET):
                elements.append(self.parse_expression())
                if not self.match(TokenType.RBRACKET):
                    self.expect(TokenType.COMMA)
            self.expect(TokenType.RBRACKET)
            return ArrayExpr(elements, token.line, token.column, token.filename)

        # try_chain
        if self.match(TokenType.TRY_CHAIN):
            return self.parse_try_chain()

        raise self.error(f"Expected expression, got {token.type.name}")

    def parse_postfix_expr(self) -> Expression:
        """Parse postfix expressions (calls, member access, indexing)"""
        expr = self.parse_primary_expr()

        while True:
            token = self.current()

            # Function call
            if self.match(TokenType.LPAREN):
                self.advance()
                arguments = []
                while not self.match(TokenType.RPAREN):
                    arguments.append(self.parse_expression())
                    if not self.match(TokenType.RPAREN):
                        self.expect(TokenType.COMMA)
                self.expect(TokenType.RPAREN)
                expr = CallExpr(expr, arguments, token.line, token.column, token.filename)

            # Member access
            elif self.match(TokenType.DOT):
                self.advance()
                member = self.expect(TokenType.IDENTIFIER).value
                expr = MemberExpr(expr, member, token.line, token.column, token.filename)

            # Indexing
            elif self.match(TokenType.LBRACKET):
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                expr = IndexExpr(expr, index, token.line, token.column, token.filename)

            else:
                break

        return expr

    def parse_unary_expr(self) -> Expression:
        """Parse unary expressions"""
        token = self.current()

        if self.match(TokenType.MINUS, TokenType.NOT, TokenType.TILDE):
            op = self.advance().value
            operand = self.parse_unary_expr()
            return UnaryExpr(op, operand, token.line, token.column, token.filename)

        return self.parse_postfix_expr()

    def parse_binary_expr(self, min_precedence: int = 0) -> Expression:
        """Parse binary expressions using precedence climbing"""
        left = self.parse_unary_expr()

        while True:
            token = self.current()
            precedence = self.get_precedence(token.type)

            if precedence < min_precedence:
                break

            op_token = self.advance()
            right = self.parse_binary_expr(precedence + 1)
            left = BinaryExpr(left, op_token.value, right, token.line, token.column, token.filename)

        return left

    def get_precedence(self, token_type: TokenType) -> int:
        """Get operator precedence"""
        precedence_map = {
            TokenType.OR: 1,
            TokenType.AND: 2,
            TokenType.EQ: 3,
            TokenType.NE: 3,
            TokenType.LT: 4,
            TokenType.GT: 4,
            TokenType.LE: 4,
            TokenType.GE: 4,
            TokenType.PIPE: 5,
            TokenType.CARET: 6,
            TokenType.AMPERSAND: 7,
            TokenType.LSHIFT: 8,
            TokenType.RSHIFT: 8,
            TokenType.PLUS: 9,
            TokenType.MINUS: 9,
            TokenType.STAR: 10,
            TokenType.SLASH: 10,
            TokenType.PERCENT: 10,
            TokenType.POWER: 11,
        }
        return precedence_map.get(token_type, -1)

    def parse_expression(self) -> Expression:
        """Parse an expression"""
        return self.parse_binary_expr()

    def parse_try_chain(self) -> TryChainExpr:
        """Parse try_chain expression"""
        token = self.expect(TokenType.TRY_CHAIN)
        self.expect(TokenType.COLON)
        self.consume_newlines()

        # Primary
        self.expect(TokenType.INDENT)
        self.expect(TokenType.PRIMARY)
        self.expect(TokenType.COLON)
        self.skip_newlines()
        primary = self.parse_expression()
        self.skip_newlines()
        self.expect(TokenType.DEDENT)

        # Secondary (optional)
        secondary = None
        if self.match(TokenType.SECONDARY):
            self.advance()
            self.expect(TokenType.COLON)
            self.skip_newlines()
            secondary = self.parse_expression()
            self.skip_newlines()

        # Fallback (optional)
        fallback = None
        if self.match(TokenType.FALLBACK):
            self.advance()
            self.expect(TokenType.COLON)
            self.skip_newlines()
            fallback = self.parse_expression()
            self.skip_newlines()

        return TryChainExpr(primary, secondary, fallback, token.line, token.column, token.filename)

    # ===== Statement Parsing =====

    def parse_block(self) -> Block:
        """Parse a block of statements"""
        token = self.current()
        statements = []

        self.expect(TokenType.INDENT)
        self.skip_newlines()

        while not self.match(TokenType.DEDENT):
            statements.append(self.parse_statement())
            self.skip_newlines()

        self.expect(TokenType.DEDENT)

        return Block(statements, token.line, token.column, token.filename)

    def parse_statement(self) -> Statement:
        """Parse a statement"""
        token = self.current()

        # Return statement
        if self.match(TokenType.RETURN):
            self.advance()
            value = None
            if not self.match(TokenType.NEWLINE):
                value = self.parse_expression()
            self.skip_newlines()
            return ReturnStmt(value, token.line, token.column, token.filename)

        # If statement
        if self.match(TokenType.IF):
            return self.parse_if_stmt()

        # While statement
        if self.match(TokenType.WHILE):
            return self.parse_while_stmt()

        # For statement
        if self.match(TokenType.FOR):
            return self.parse_for_stmt()

        # Match statement
        if self.match(TokenType.MATCH):
            return self.parse_match_stmt()

        # Pass statement
        if self.match(TokenType.PASS):
            self.advance()
            self.skip_newlines()
            return PassStmt(token.line, token.column, token.filename)

        # Break statement
        if self.match(TokenType.BREAK):
            self.advance()
            self.skip_newlines()
            return BreakStmt(token.line, token.column, token.filename)

        # Continue statement
        if self.match(TokenType.CONTINUE):
            self.advance()
            self.skip_newlines()
            return ContinueStmt(token.line, token.column, token.filename)

        # Defer statement
        if self.match(TokenType.DEFER):
            self.advance()
            stmt = self.parse_statement()
            return DeferStmt(stmt, token.line, token.column, token.filename)

        # Variable declaration
        if self.match(TokenType.LET, TokenType.VAR):
            return self.parse_variable_decl()

        # Assignment or expression statement
        expr = self.parse_expression()

        # Check for assignment
        if self.match(TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
                     TokenType.STAR_ASSIGN, TokenType.SLASH_ASSIGN, TokenType.PERCENT_ASSIGN):
            op = self.advance().value
            value = self.parse_expression()
            self.skip_newlines()
            return AssignStmt(expr, value, op, token.line, token.column, token.filename)

        self.skip_newlines()
        return ExprStmt(expr, token.line, token.column, token.filename)

    def parse_if_stmt(self) -> IfStmt:
        """Parse if statement"""
        token = self.expect(TokenType.IF)
        condition = self.parse_expression()
        self.expect(TokenType.COLON)
        self.consume_newlines()
        then_block = self.parse_block()

        elif_clauses = []
        while self.match(TokenType.ELIF):
            self.advance()
            elif_cond = self.parse_expression()
            self.expect(TokenType.COLON)
            self.consume_newlines()
            elif_block = self.parse_block()
            elif_clauses.append((elif_cond, elif_block))

        else_block = None
        if self.match(TokenType.ELSE):
            self.advance()
            self.expect(TokenType.COLON)
            self.consume_newlines()
            else_block = self.parse_block()

        return IfStmt(condition, then_block, elif_clauses, else_block, token.line, token.column, token.filename)

    def parse_while_stmt(self) -> WhileStmt:
        """Parse while statement"""
        token = self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        self.expect(TokenType.COLON)
        self.consume_newlines()
        body = self.parse_block()
        return WhileStmt(condition, body, token.line, token.column, token.filename)

    def parse_for_stmt(self) -> ForStmt:
        """Parse for statement"""
        token = self.expect(TokenType.FOR)
        variable = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.IN)
        iterable = self.parse_expression()
        self.expect(TokenType.COLON)
        self.consume_newlines()
        body = self.parse_block()
        return ForStmt(variable, iterable, body, token.line, token.column, token.filename)

    def parse_match_stmt(self) -> MatchStmt:
        """Parse match statement"""
        token = self.expect(TokenType.MATCH)
        value = self.parse_expression()
        self.expect(TokenType.COLON)
        self.consume_newlines()

        self.expect(TokenType.INDENT)
        self.skip_newlines()

        cases = []
        while self.match(TokenType.CASE):
            self.advance()
            pattern = self.parse_expression()
            self.expect(TokenType.COLON)
            self.consume_newlines()
            case_body = self.parse_block()
            cases.append(CaseClause(pattern, case_body, token.line, token.column, token.filename))
            self.skip_newlines()

        self.expect(TokenType.DEDENT)

        return MatchStmt(value, cases, token.line, token.column, token.filename)

    def parse_variable_decl(self) -> VariableDecl:
        """Parse variable declaration"""
        token = self.current()
        is_mutable = self.match(TokenType.VAR)
        self.advance()

        name = self.expect(TokenType.IDENTIFIER).value

        type_annotation = None
        if self.match(TokenType.COLON):
            self.advance()
            type_annotation = self.parse_type()

        initializer = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            initializer = self.parse_expression()

        self.skip_newlines()

        return VariableDecl(name, type_annotation, initializer, is_mutable, token.line, token.column, token.filename)

    # ===== Declaration Parsing =====

    def parse_function_decl(self, decorators: List[Decorator] = None) -> FunctionDecl:
        """Parse function declaration"""
        if decorators is None:
            decorators = []

        token = self.expect(TokenType.FUNC)
        name = self.expect(TokenType.IDENTIFIER).value

        # Parameters
        self.expect(TokenType.LPAREN)
        parameters = []
        while not self.match(TokenType.RPAREN):
            param_token = self.current()
            param_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.COLON)
            param_type = self.parse_type()
            parameters.append(Parameter(param_name, param_type, None, param_token.line, param_token.column, param_token.filename))

            if not self.match(TokenType.RPAREN):
                self.expect(TokenType.COMMA)
        self.expect(TokenType.RPAREN)

        # Return type
        return_type = None
        if self.match(TokenType.ARROW):
            self.advance()
            return_type = self.parse_type()

        self.expect(TokenType.COLON)
        self.consume_newlines()

        # Body
        body = self.parse_block()

        return FunctionDecl(name, parameters, return_type, body, decorators, token.line, token.column, token.filename)

    def parse_import_stmt(self) -> Union[ImportStmt, FromImportStmt]:
        """Parse import statement"""
        token = self.current()

        if self.match(TokenType.FROM):
            # from import
            self.advance()
            module_path = [self.expect(TokenType.IDENTIFIER).value]

            while self.match(TokenType.DOT):
                self.advance()
                module_path.append(self.expect(TokenType.IDENTIFIER).value)

            self.expect(TokenType.IMPORT)

            names = [self.expect(TokenType.IDENTIFIER).value]
            while self.match(TokenType.COMMA):
                self.advance()
                names.append(self.expect(TokenType.IDENTIFIER).value)

            self.skip_newlines()
            return FromImportStmt(module_path, names, token.line, token.column, token.filename)
        else:
            # regular import
            self.expect(TokenType.IMPORT)
            module_path = [self.expect(TokenType.IDENTIFIER).value]

            while self.match(TokenType.DOT):
                self.advance()
                module_path.append(self.expect(TokenType.IDENTIFIER).value)

            alias = None
            if self.match(TokenType.IDENTIFIER) and self.current().value == "as":
                self.advance()
                alias = self.expect(TokenType.IDENTIFIER).value

            self.skip_newlines()
            return ImportStmt(module_path, alias, token.line, token.column, token.filename)

    def parse_module_decl(self) -> ModuleDecl:
        """Parse module declaration"""
        token = self.expect(TokenType.MODULE)
        name = self.expect(TokenType.IDENTIFIER).value
        self.skip_newlines()
        return ModuleDecl(name, token.line, token.column, token.filename)

    def parse_program(self) -> Program:
        """Parse entire program"""
        token = self.current()
        self.skip_newlines()

        # Parse file-level decorators
        decorators = []
        while self.match(TokenType.AT):
            decorators.append(self.parse_decorator())

        # Parse module declaration
        module_decl = None
        if self.match(TokenType.MODULE):
            module_decl = self.parse_module_decl()

        # Parse imports
        imports = []
        while self.match(TokenType.IMPORT, TokenType.FROM):
            imports.append(self.parse_import_stmt())

        # Parse declarations
        declarations = []
        while not self.match(TokenType.EOF):
            self.skip_newlines()

            if self.match(TokenType.EOF):
                break

            # Check for decorators
            decl_decorators = []
            while self.match(TokenType.AT):
                decl_decorators.append(self.parse_decorator())

            # Function declaration
            if self.match(TokenType.FUNC):
                declarations.append(self.parse_function_decl(decl_decorators))
            else:
                if decl_decorators:
                    raise self.error("Decorators can only be applied to functions")
                # Other declarations can be added here
                self.skip_newlines()

        return Program(decorators, module_decl, imports, declarations, token.line, token.column, token.filename)


def parse(tokens: List[Token]) -> Program:
    """Convenience function to parse tokens into an AST"""
    parser = Parser(tokens)
    return parser.parse_program()
