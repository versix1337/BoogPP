"""
Boogpp Code Generator
LLVM IR code generation from AST.
"""

from .llvm_codegen import LLVMCodeGenerator, generate_code

__all__ = ['LLVMCodeGenerator', 'generate_code']
