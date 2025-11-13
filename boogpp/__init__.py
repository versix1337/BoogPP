"""
Boogpp Programming Language
A Windows-centric systems programming language with memory safety features.

This package contains the Boogpp compiler and runtime components.
"""

__version__ = "3.0.0"
__author__ = "Boogpp Development Team"
__license__ = "MIT"

# Import main compiler module for convenience
from . import compiler

__all__ = ['compiler']
