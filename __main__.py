import sys
from .compiler.cli import main as compiler_main

# Directly dispatch to the CLI entry point.
if __name__ == "__main__":
    sys.exit(compiler_main())
