"""
Boog++ Compiler
A Windows-centric systems programming language compiler.
"""

__version__ = "1.0.0"

from .lexer import Lexer, tokenize
from .parser import Parser, parse
from .safety import SafetyChecker, SafetyMode, check_safety

__all__ = [
    'Lexer', 'tokenize',
    'Parser', 'parse',
    'SafetyChecker', 'SafetyMode', 'check_safety'
]
