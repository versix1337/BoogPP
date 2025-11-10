"""
Boogpp Token Definitions
Defines all token types used by the lexer.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional


class TokenType(Enum):
    """All token types in Boogpp language"""

    # Keywords
    FUNC = auto()
    LET = auto()
    VAR = auto()
    IF = auto()
    ELIF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    MATCH = auto()
    CASE = auto()
    RETURN = auto()
    IMPORT = auto()
    FROM = auto()
    MODULE = auto()
    STRUCT = auto()
    ENUM = auto()
    TRAIT = auto()
    IMPL = auto()
    DEFER = auto()
    TRY_CHAIN = auto()
    PRIMARY = auto()
    SECONDARY = auto()
    FALLBACK = auto()
    TRUE = auto()
    FALSE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    PASS = auto()
    BREAK = auto()
    CONTINUE = auto()

    # Types
    I8 = auto()
    I16 = auto()
    I32 = auto()
    I64 = auto()
    U8 = auto()
    U16 = auto()
    U32 = auto()
    U64 = auto()
    F32 = auto()
    F64 = auto()
    BOOL = auto()
    STRING = auto()
    CHAR = auto()
    VOID = auto()
    PTR = auto()
    ARRAY = auto()
    SLICE = auto()
    TUPLE = auto()
    STATUS = auto()
    HANDLE = auto()
    RESULT = auto()

    # Literals
    INTEGER_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()
    CHAR_LITERAL = auto()

    # Identifiers
    IDENTIFIER = auto()

    # Operators
    PLUS = auto()           # +
    MINUS = auto()          # -
    STAR = auto()           # *
    SLASH = auto()          # /
    PERCENT = auto()        # %
    POWER = auto()          # **
    EQ = auto()             # ==
    NE = auto()             # !=
    LT = auto()             # <
    GT = auto()             # >
    LE = auto()             # <=
    GE = auto()             # >=
    ASSIGN = auto()         # =
    PLUS_ASSIGN = auto()    # +=
    MINUS_ASSIGN = auto()   # -=
    STAR_ASSIGN = auto()    # *=
    SLASH_ASSIGN = auto()   # /=
    PERCENT_ASSIGN = auto() # %=
    AMPERSAND = auto()      # &
    PIPE = auto()           # |
    CARET = auto()          # ^
    TILDE = auto()          # ~
    LSHIFT = auto()         # <<
    RSHIFT = auto()         # >>
    AND_ASSIGN = auto()     # &=
    OR_ASSIGN = auto()      # |=
    XOR_ASSIGN = auto()     # ^=

    # Delimiters
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACKET = auto()       # [
    RBRACKET = auto()       # ]
    LBRACE = auto()         # {
    RBRACE = auto()         # }
    COMMA = auto()          # ,
    DOT = auto()            # .
    COLON = auto()          # :
    SEMICOLON = auto()      # ;
    ARROW = auto()          # ->
    DOUBLE_COLON = auto()   # ::
    AT = auto()             # @
    RANGE = auto()          # ..

    # Special
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()
    COMMENT = auto()


@dataclass
class Token:
    """Represents a single token in the source code"""
    type: TokenType
    value: Any
    line: int
    column: int
    filename: Optional[str] = None

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {repr(self.value)}, {self.line}:{self.column})"

    def __str__(self) -> str:
        return f"{self.type.name}({self.value})"


# Keyword mapping
KEYWORDS = {
    'func': TokenType.FUNC,
    'let': TokenType.LET,
    'var': TokenType.VAR,
    'if': TokenType.IF,
    'elif': TokenType.ELIF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'for': TokenType.FOR,
    'in': TokenType.IN,
    'match': TokenType.MATCH,
    'case': TokenType.CASE,
    'return': TokenType.RETURN,
    'import': TokenType.IMPORT,
    'from': TokenType.FROM,
    'module': TokenType.MODULE,
    'struct': TokenType.STRUCT,
    'enum': TokenType.ENUM,
    'trait': TokenType.TRAIT,
    'impl': TokenType.IMPL,
    'defer': TokenType.DEFER,
    'try_chain': TokenType.TRY_CHAIN,
    'primary': TokenType.PRIMARY,
    'secondary': TokenType.SECONDARY,
    'fallback': TokenType.FALLBACK,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'and': TokenType.AND,
    'or': TokenType.OR,
    'not': TokenType.NOT,
    'pass': TokenType.PASS,
    'break': TokenType.BREAK,
    'continue': TokenType.CONTINUE,
    # Types
    'i8': TokenType.I8,
    'i16': TokenType.I16,
    'i32': TokenType.I32,
    'i64': TokenType.I64,
    'u8': TokenType.U8,
    'u16': TokenType.U16,
    'u32': TokenType.U32,
    'u64': TokenType.U64,
    'f32': TokenType.F32,
    'f64': TokenType.F64,
    'bool': TokenType.BOOL,
    'string': TokenType.STRING,
    'char': TokenType.CHAR,
    'void': TokenType.VOID,
    'ptr': TokenType.PTR,
    'array': TokenType.ARRAY,
    'slice': TokenType.SLICE,
    'tuple': TokenType.TUPLE,
    'status': TokenType.STATUS,
    'handle': TokenType.HANDLE,
    'result': TokenType.RESULT,
}


# Safety-related constants
SAFETY_MODES = ['SAFE', 'UNSAFE', 'CUSTOM']
HOOK_EVENTS = [
    'PROCESS_CREATION',
    'PROCESS_TERMINATION',
    'FILE_WRITE',
    'FILE_READ',
    'FILE_DELETE',
    'REGISTRY_WRITE',
    'REGISTRY_READ',
    'NETWORK_CONNECTION',
    'DRIVER_LOAD',
]

# Status codes
STATUS_CODES = {
    'SUCCESS': 0x000000,
    'GENERIC_ERROR': 0x000001,
    'ACCESS_DENIED': 0x000002,
    'TIMEOUT': 0x000003,
    'NOT_FOUND': 0x000004,
    'INVALID_PARAMETER': 0x000005,
}
