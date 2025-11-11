#!/usr/bin/env python3
"""
Boogpp Compiler Entry Point
This is the main driver for the Boogpp compiler CLI.
"""

import sys
from .cli import main

if __name__ == '__main__':
    sys.exit(main())
