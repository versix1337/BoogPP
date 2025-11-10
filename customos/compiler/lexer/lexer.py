"""
CustomOS Lexer
Tokenizes CustomOS source code with support for whitespace-based indentation.
"""

from typing import List, Optional
from .tokens import Token, TokenType, KEYWORDS
import re


class LexerError(Exception):
    """Raised when lexer encounters an error"""
    def __init__(self, message: str, line: int, column: int, filename: Optional[str] = None):
        self.message = message
        self.line = line
        self.column = column
        self.filename = filename
        super().__init__(f"{filename or '<input>'}:{line}:{column}: {message}")


class Lexer:
    """Tokenizes CustomOS source code"""

    def __init__(self, source: str, filename: Optional[str] = None):
        self.source = source
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.indent_stack = [0]  # Track indentation levels

    def error(self, message: str) -> LexerError:
        """Create a lexer error at current position"""
        return LexerError(message, self.line, self.column, self.filename)

    def peek(self, offset: int = 0) -> Optional[str]:
        """Peek at character at current position + offset"""
        pos = self.pos + offset
        if pos < len(self.source):
            return self.source[pos]
        return None

    def advance(self) -> Optional[str]:
        """Advance position and return current character"""
        if self.pos >= len(self.source):
            return None

        char = self.source[self.pos]
        self.pos += 1

        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def skip_whitespace(self, include_newlines: bool = False) -> None:
        """Skip whitespace characters"""
        while self.peek():
            char = self.peek()
            if char == '\n' and not include_newlines:
                break
            if char in ' \t\r' or (char == '\n' and include_newlines):
                self.advance()
            else:
                break

    def skip_comment(self) -> None:
        """Skip single-line or multi-line comments"""
        if self.peek() == '#':
            # Check for multi-line comment ###
            if self.peek(1) == '#' and self.peek(2) == '#':
                self.advance()  # #
                self.advance()  # #
                self.advance()  # #

                # Find closing ###
                while self.peek():
                    if self.peek() == '#' and self.peek(1) == '#' and self.peek(2) == '#':
                        self.advance()
                        self.advance()
                        self.advance()
                        break
                    self.advance()
            else:
                # Single line comment
                while self.peek() and self.peek() != '\n':
                    self.advance()

    def read_string(self, quote: str) -> str:
        """Read a string literal"""
        value = ""
        self.advance()  # Skip opening quote

        while self.peek() and self.peek() != quote:
            char = self.peek()
            if char == '\\':
                self.advance()
                next_char = self.peek()
                if next_char == 'n':
                    value += '\n'
                elif next_char == 't':
                    value += '\t'
                elif next_char == 'r':
                    value += '\r'
                elif next_char == '\\':
                    value += '\\'
                elif next_char == quote:
                    value += quote
                elif next_char == '0':
                    value += '\0'
                else:
                    value += next_char
                self.advance()
            else:
                value += char
                self.advance()

        if self.peek() != quote:
            raise self.error(f"Unterminated string literal")

        self.advance()  # Skip closing quote
        return value

    def read_number(self) -> Token:
        """Read a number (integer or float)"""
        start_line = self.line
        start_column = self.column
        value = ""

        # Handle hex numbers
        if self.peek() == '0' and self.peek(1) in 'xX':
            value += self.advance()  # 0
            value += self.advance()  # x
            while self.peek() and self.peek() in '0123456789abcdefABCDEF_':
                if self.peek() != '_':
                    value += self.advance()
                else:
                    self.advance()
            return Token(TokenType.INTEGER_LITERAL, int(value, 16), start_line, start_column, self.filename)

        # Handle binary numbers
        if self.peek() == '0' and self.peek(1) in 'bB':
            value += self.advance()  # 0
            value += self.advance()  # b
            while self.peek() and self.peek() in '01_':
                if self.peek() != '_':
                    value += self.advance()
                else:
                    self.advance()
            return Token(TokenType.INTEGER_LITERAL, int(value, 2), start_line, start_column, self.filename)

        # Regular decimal number
        while self.peek() and (self.peek().isdigit() or self.peek() == '_'):
            if self.peek() != '_':
                value += self.advance()
            else:
                self.advance()

        # Check for float
        if self.peek() == '.' and self.peek(1) and self.peek(1).isdigit():
            value += self.advance()  # .
            while self.peek() and (self.peek().isdigit() or self.peek() == '_'):
                if self.peek() != '_':
                    value += self.advance()
                else:
                    self.advance()

            # Scientific notation
            if self.peek() and self.peek() in 'eE':
                value += self.advance()
                if self.peek() and self.peek() in '+-':
                    value += self.advance()
                while self.peek() and self.peek().isdigit():
                    value += self.advance()

            return Token(TokenType.FLOAT_LITERAL, float(value), start_line, start_column, self.filename)

        return Token(TokenType.INTEGER_LITERAL, int(value), start_line, start_column, self.filename)

    def read_identifier(self) -> Token:
        """Read an identifier or keyword"""
        start_line = self.line
        start_column = self.column
        value = ""

        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            value += self.advance()

        # Check if it's a keyword
        token_type = KEYWORDS.get(value, TokenType.IDENTIFIER)

        return Token(token_type, value, start_line, start_column, self.filename)

    def handle_indentation(self, spaces: int) -> List[Token]:
        """Handle indentation at start of line"""
        tokens = []
        current_indent = self.indent_stack[-1]

        if spaces > current_indent:
            # INDENT
            self.indent_stack.append(spaces)
            tokens.append(Token(TokenType.INDENT, spaces, self.line, 1, self.filename))
        elif spaces < current_indent:
            # DEDENT (possibly multiple)
            while self.indent_stack and self.indent_stack[-1] > spaces:
                self.indent_stack.pop()
                tokens.append(Token(TokenType.DEDENT, spaces, self.line, 1, self.filename))

            if self.indent_stack[-1] != spaces:
                raise self.error("Indentation error: mismatched indentation")

        return tokens

    def tokenize(self) -> List[Token]:
        """Tokenize the entire source code"""
        at_line_start = True

        while self.pos < len(self.source):
            # Skip whitespace and comments
            if self.peek() in ' \t' and not at_line_start:
                self.skip_whitespace()
                continue

            if self.peek() == '#':
                self.skip_comment()
                continue

            # Handle indentation at start of line
            if at_line_start and self.peek() not in '\n\r':
                spaces = 0
                start_pos = self.pos
                while self.peek() in ' \t':
                    if self.peek() == ' ':
                        spaces += 1
                    elif self.peek() == '\t':
                        spaces += 4  # Tab = 4 spaces
                    self.advance()

                # Only process indentation if line is not empty
                if self.peek() and self.peek() not in '\n\r#':
                    indent_tokens = self.handle_indentation(spaces)
                    self.tokens.extend(indent_tokens)

                at_line_start = False
                continue

            start_line = self.line
            start_column = self.column
            char = self.peek()

            # Newline
            if char in '\n\r':
                if char == '\r' and self.peek(1) == '\n':
                    self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.NEWLINE, '\\n', start_line, start_column, self.filename))
                at_line_start = True
                continue

            # String literals
            if char in '"\'':
                value = self.read_string(char)
                self.tokens.append(Token(TokenType.STRING_LITERAL, value, start_line, start_column, self.filename))
                continue

            # Numbers
            if char.isdigit():
                token = self.read_number()
                self.tokens.append(token)
                continue

            # Identifiers and keywords
            if char.isalpha() or char == '_':
                token = self.read_identifier()
                self.tokens.append(token)
                continue

            # Operators and delimiters
            if char == '+':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.PLUS_ASSIGN, '+=', start_line, start_column, self.filename))
                else:
                    self.tokens.append(Token(TokenType.PLUS, '+', start_line, start_column, self.filename))
                continue

            if char == '-':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.MINUS_ASSIGN, '-=', start_line, start_column, self.filename))
                elif self.peek() == '>':
                    self.advance()
                    self.tokens.append(Token(TokenType.ARROW, '->', start_line, start_column, self.filename))
                else:
                    self.tokens.append(Token(TokenType.MINUS, '-', start_line, start_column, self.filename))
                continue

            if char == '*':
                self.advance()
                if self.peek() == '*':
                    self.advance()
                    self.tokens.append(Token(TokenType.POWER, '**', start_line, start_column, self.filename))
                elif self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.STAR_ASSIGN, '*=', start_line, start_column, self.filename))
                else:
                    self.tokens.append(Token(TokenType.STAR, '*', start_line, start_column, self.filename))
                continue

            if char == '/':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.SLASH_ASSIGN, '/=', start_line, start_column, self.filename))
                else:
                    self.tokens.append(Token(TokenType.SLASH, '/', start_line, start_column, self.filename))
                continue

            if char == '%':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.PERCENT_ASSIGN, '%=', start_line, start_column, self.filename))
                else:
                    self.tokens.append(Token(TokenType.PERCENT, '%', start_line, start_column, self.filename))
                continue

            if char == '=':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.EQ, '==', start_line, start_column, self.filename))
                else:
                    self.tokens.append(Token(TokenType.ASSIGN, '=', start_line, start_column, self.filename))
                continue

            if char == '!':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.NE, '!=', start_line, start_column, self.filename))
                else:
                    raise self.error(f"Unexpected character: {char}")
                continue

            if char == '<':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.LE, '<=', start_line, start_column, self.filename))
                elif self.peek() == '<':
                    self.advance()
                    self.tokens.append(Token(TokenType.LSHIFT, '<<', start_line, start_column, self.filename))
                else:
                    self.tokens.append(Token(TokenType.LT, '<', start_line, start_column, self.filename))
                continue

            if char == '>':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.GE, '>=', start_line, start_column, self.filename))
                elif self.peek() == '>':
                    self.advance()
                    self.tokens.append(Token(TokenType.RSHIFT, '>>', start_line, start_column, self.filename))
                else:
                    self.tokens.append(Token(TokenType.GT, '>', start_line, start_column, self.filename))
                continue

            if char == '&':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.AND_ASSIGN, '&=', start_line, start_column, self.filename))
                else:
                    self.tokens.append(Token(TokenType.AMPERSAND, '&', start_line, start_column, self.filename))
                continue

            if char == '|':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.OR_ASSIGN, '|=', start_line, start_column, self.filename))
                else:
                    self.tokens.append(Token(TokenType.PIPE, '|', start_line, start_column, self.filename))
                continue

            if char == '^':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.XOR_ASSIGN, '^=', start_line, start_column, self.filename))
                else:
                    self.tokens.append(Token(TokenType.CARET, '^', start_line, start_column, self.filename))
                continue

            if char == '~':
                self.advance()
                self.tokens.append(Token(TokenType.TILDE, '~', start_line, start_column, self.filename))
                continue

            if char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', start_line, start_column, self.filename))
                continue

            if char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', start_line, start_column, self.filename))
                continue

            if char == '[':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACKET, '[', start_line, start_column, self.filename))
                continue

            if char == ']':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACKET, ']', start_line, start_column, self.filename))
                continue

            if char == '{':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACE, '{', start_line, start_column, self.filename))
                continue

            if char == '}':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACE, '}', start_line, start_column, self.filename))
                continue

            if char == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ',', start_line, start_column, self.filename))
                continue

            if char == '.':
                self.advance()
                if self.peek() == '.':
                    self.advance()
                    self.tokens.append(Token(TokenType.RANGE, '..', start_line, start_column, self.filename))
                else:
                    self.tokens.append(Token(TokenType.DOT, '.', start_line, start_column, self.filename))
                continue

            if char == ':':
                self.advance()
                if self.peek() == ':':
                    self.advance()
                    self.tokens.append(Token(TokenType.DOUBLE_COLON, '::', start_line, start_column, self.filename))
                else:
                    self.tokens.append(Token(TokenType.COLON, ':', start_line, start_column, self.filename))
                continue

            if char == ';':
                self.advance()
                self.tokens.append(Token(TokenType.SEMICOLON, ';', start_line, start_column, self.filename))
                continue

            if char == '@':
                self.advance()
                self.tokens.append(Token(TokenType.AT, '@', start_line, start_column, self.filename))
                continue

            raise self.error(f"Unexpected character: {char}")

        # Handle remaining dedents
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token(TokenType.DEDENT, 0, self.line, self.column, self.filename))

        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column, self.filename))

        return self.tokens


def tokenize(source: str, filename: Optional[str] = None) -> List[Token]:
    """Convenience function to tokenize source code"""
    lexer = Lexer(source, filename)
    return lexer.tokenize()
