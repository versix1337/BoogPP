"""
Boogpp Compiler
A Windows-centric systems programming language compiler.

Phase 1: Lexer, Parser, Basic Safety Checker
Phase 2: Type Checker, Enhanced Safety Enforcement, LLVM Code Generation
Phase 3: Runtime Library (Memory, Strings, I/O, Arrays)
"""

__version__ = "3.0.0"

from .lexer import Lexer, tokenize
from .parser import Parser, parse
from .safety import SafetyChecker, SafetyMode, check_safety
from .safety.enhanced_checker import EnhancedSafetyChecker, check_safety_enhanced
from .typechecker import TypeChecker, check_types
from .codegen import LLVMCodeGenerator, generate_code

__all__ = [
    'Lexer', 'tokenize',
    'Parser', 'parse',
    'SafetyChecker', 'SafetyMode', 'check_safety',
    'EnhancedSafetyChecker', 'check_safety_enhanced',
    'TypeChecker', 'check_types',
    'LLVMCodeGenerator', 'generate_code'
]
