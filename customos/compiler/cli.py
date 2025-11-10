#!/usr/bin/env python3
"""
CustomOS Compiler CLI
Command-line interface for the CustomOS compiler.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from .lexer import tokenize, LexerError
from .parser import parse, ParseError
from .safety import check_safety, SafetyMode, SafetyViolation


class CompilerError(Exception):
    """Base compiler error"""
    pass


class CustomOSCompiler:
    """CustomOS compiler"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def log(self, message: str) -> None:
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[CustomOS] {message}")

    def compile_file(
        self,
        input_file: Path,
        output_file: Optional[Path] = None,
        safety_mode: SafetyMode = SafetyMode.SAFE,
        optimization_level: int = 0,
        output_type: str = "exe"
    ) -> bool:
        """Compile a CustomOS source file"""

        self.log(f"Compiling {input_file}...")

        # Read source file
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except FileNotFoundError:
            print(f"Error: File not found: {input_file}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return False

        # Lexical analysis
        self.log("Lexical analysis...")
        try:
            tokens = tokenize(source_code, str(input_file))
        except LexerError as e:
            print(f"Lexer error: {e}", file=sys.stderr)
            return False

        self.log(f"Generated {len(tokens)} tokens")

        # Parsing
        self.log("Parsing...")
        try:
            ast = parse(tokens)
        except ParseError as e:
            print(f"Parser error: {e}", file=sys.stderr)
            return False

        self.log("AST generated successfully")

        # Safety checking
        self.log(f"Safety checking (mode: {safety_mode.name})...")
        violations = check_safety(ast, safety_mode)

        # Report violations
        errors = [v for v in violations if v.severity == "error"]
        warnings = [v for v in violations if v.severity == "warning"]

        for warning in warnings:
            print(f"Warning: {warning}", file=sys.stderr)

        if errors:
            for error in errors:
                print(f"Error: {error}", file=sys.stderr)
            print(f"\nCompilation failed with {len(errors)} error(s)", file=sys.stderr)
            return False

        self.log("Safety checks passed")

        # Type checking
        self.log("Type checking...")
        # TODO: Implement type checker
        self.log("Type checking skipped (not implemented yet)")

        # Code generation
        self.log(f"Code generation (optimization level: O{optimization_level})...")
        # TODO: Implement code generator
        self.log("Code generation skipped (not implemented yet)")

        # Determine output file
        if output_file is None:
            output_file = input_file.with_suffix(f".{output_type}")

        self.log(f"Output would be written to: {output_file}")

        print(f"✓ Compilation successful (demo mode - no binary generated)")
        print(f"  Input: {input_file}")
        print(f"  Output: {output_file}")
        print(f"  Safety: {safety_mode.name}")
        print(f"  Type: {output_type}")
        print(f"  Tokens: {len(tokens)}")

        if warnings:
            print(f"  Warnings: {len(warnings)}")

        return True


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="CustomOS Compiler - Windows-centric systems programming language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  customos build main.cos                     # Compile to main.exe
  customos build main.cos -o myapp.exe        # Compile with custom output name
  customos build service.cos --type service   # Compile as Windows service
  customos build driver.cos --type driver     # Compile as kernel driver
  customos build app.cos --safety unsafe -O3  # Compile with UNSAFE mode and O3 optimization

Output types:
  exe     - Executable (default)
  dll     - Dynamic Link Library
  service - Windows Service
  driver  - Kernel Driver (.sys)
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Build command
    build_parser = subparsers.add_parser('build', help='Compile a CustomOS source file')
    build_parser.add_argument('input', type=str, help='Input source file (.cos)')
    build_parser.add_argument('-o', '--output', type=str, help='Output file name')
    build_parser.add_argument('--type', choices=['exe', 'dll', 'service', 'driver'],
                             default='exe', help='Output type (default: exe)')
    build_parser.add_argument('--safety', choices=['safe', 'unsafe', 'custom'],
                             default='safe', help='Safety mode (default: safe)')
    build_parser.add_argument('-O', '--optimization', type=int, choices=[0, 1, 2, 3],
                             default=0, help='Optimization level (default: 0)')
    build_parser.add_argument('-v', '--verbose', action='store_true',
                             help='Verbose output')

    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')

    # Check command
    check_parser = subparsers.add_parser('check', help='Check syntax and safety without compiling')
    check_parser.add_argument('input', type=str, help='Input source file (.cos)')
    check_parser.add_argument('--safety', choices=['safe', 'unsafe', 'custom'],
                             default='safe', help='Safety mode (default: safe)')
    check_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.command == 'version':
        print("CustomOS Compiler v1.0.0")
        print("A Windows-centric systems programming language")
        return 0

    elif args.command == 'build':
        input_file = Path(args.input)
        output_file = Path(args.output) if args.output else None

        # Convert safety mode string to enum
        safety_mode = SafetyMode[args.safety.upper()]

        compiler = CustomOSCompiler(verbose=args.verbose)
        success = compiler.compile_file(
            input_file,
            output_file,
            safety_mode,
            args.optimization,
            args.type
        )

        return 0 if success else 1

    elif args.command == 'check':
        input_file = Path(args.input)
        safety_mode = SafetyMode[args.safety.upper()]

        compiler = CustomOSCompiler(verbose=args.verbose)

        # Read and parse file
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                source_code = f.read()

            tokens = tokenize(source_code, str(input_file))
            ast = parse(tokens)
            violations = check_safety(ast, safety_mode)

            errors = [v for v in violations if v.severity == "error"]
            warnings = [v for v in violations if v.severity == "warning"]

            for warning in warnings:
                print(f"Warning: {warning}")

            for error in errors:
                print(f"Error: {error}")

            if errors:
                print(f"\n✗ Check failed with {len(errors)} error(s)")
                return 1
            else:
                print(f"✓ Check passed")
                if warnings:
                    print(f"  {len(warnings)} warning(s)")
                return 0

        except (LexerError, ParseError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except FileNotFoundError:
            print(f"Error: File not found: {input_file}", file=sys.stderr)
            return 1

    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
