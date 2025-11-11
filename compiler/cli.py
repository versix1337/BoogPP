#!/usr/bin/env python3
"""
Boogpp Compiler CLI
Command-line interface for the Boogpp compiler.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Version import: support running as part of the boogpp package (python -m boogpp.compiler)
# and as a standalone package inside the repo (python -m compiler from boogpp directory).
try:
    from .. import __version__  # type: ignore
except Exception:
    __version__ = "dev"

from .lexer import tokenize, LexerError
from .parser import parse, ParseError
from .safety import check_safety, SafetyMode, SafetyViolation
from .safety.enhanced_checker import check_safety_enhanced, EnhancedSafetyChecker
from .typechecker import check_types, TypeChecker
from .codegen import generate_code


class CompilerError(Exception):
    """Base compiler error"""
    pass


class BoogppCompiler:
    """Boogpp compiler"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def log(self, message: str) -> None:
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(f"[Boogpp] {message}")

    def compile_file(
        self,
        input_file: Path,
        output_file: Optional[Path] = None,
        safety_mode: SafetyMode = SafetyMode.SAFE,
        optimization_level: int = 0,
        output_type: str = "exe",
        link: bool = False
    ) -> bool:
        """Compile a Boogpp source file"""

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
        type_checker = TypeChecker()
        type_errors = type_checker.check_program(ast)

        # Report type errors
        if type_errors:
            for error in type_errors:
                print(f"Type Error: {error}", file=sys.stderr)
            print(f"\nCompilation failed with {len(type_errors)} type error(s)", file=sys.stderr)
            return False

        self.log("Type checking passed")

        # Determine output file
        if output_file is None:
            output_file = input_file.with_suffix(f".{output_type}")

        # Code generation
        self.log(f"Code generation (optimization level: O{optimization_level})...")
        try:
            llvm_ir = generate_code(ast, str(input_file.stem), type_checker.type_annotations)
            self.log("LLVM IR generated successfully")

            # Write LLVM IR to file
            llvm_file = output_file.with_suffix('.ll')
            with open(llvm_file, 'w', encoding='utf-8') as f:
                f.write(llvm_ir)
            self.log(f"LLVM IR written to {llvm_file}")

        except Exception as e:
            print(f"Code generation error: {e}", file=sys.stderr)
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False

        # Optionally attempt to link using llc + clang if requested
        if link:
            import shutil
            import subprocess

            llc_path = shutil.which('llc')
            clang_path = shutil.which('clang')

            # If clang/llc are not on PATH, try some common install locations
            common_clang = [
                Path("C:/Program Files/LLVM/bin/clang.exe"),
                Path("C:/Program Files (x86)/LLVM/bin/clang.exe"),
            ]
            common_llc = [
                Path("C:/Program Files/LLVM/bin/llc.exe"),
                Path("C:/Program Files (x86)/LLVM/bin/llc.exe"),
            ]
            if not clang_path:
                for c in common_clang:
                    if c.exists():
                        clang_path = str(c)
                        print(f"Found clang at {clang_path}")
                        break
            if not llc_path:
                for c in common_llc:
                    if c.exists():
                        llc_path = str(c)
                        print(f"Found llc at {llc_path}")
                        break

            if not clang_path:
                print('Linking requested but clang not found on PATH. Skipping linking.')
            else:
                obj_file = output_file.with_suffix('.obj')
                # Prefer llc if available, otherwise try clang to compile IR directly
                if llc_path:
                    print(f"Running llc to produce object: {obj_file}...")
                    try:
                        r = subprocess.run([llc_path, '-filetype=obj', '-o', str(obj_file), str(llvm_file)], check=False)
                        if r.returncode != 0:
                            print('llc failed to produce object file. Skipping linking.')
                            obj_file = None
                        
                    except Exception as e:
                        print(f'Error running llc: {e}')
                        obj_file = None
                else:
                    # Use clang to compile LLVM IR to object
                    print(f"llc not found; using clang to compile IR to object: {obj_file}...")
                    try:
                        r = subprocess.run([clang_path, '-c', str(llvm_file), '-o', str(obj_file)], check=False)
                        if r.returncode != 0:
                            print('clang failed to compile LLVM IR to object. Skipping linking.')
                            obj_file = None
                    except Exception as e:
                        print(f'Error running clang on IR: {e}')
                        obj_file = None

                # Compile BoogPP runtime C support library into an object (if available)
                runtime_obj = None
                try:
                    pkg_root = Path(__file__).resolve().parents[1]
                    runtime_c = pkg_root / 'runtime' / 'src' / 'boogpp_runtime.c'
                    runtime_inc = pkg_root / 'runtime' / 'include'
                    if runtime_c.exists():
                        runtime_obj = output_file.with_name('boogpp_runtime.obj')
                        print(f"Compiling runtime support: {runtime_c} -> {runtime_obj}")
                        rrt = subprocess.run([clang_path, '-c', str(runtime_c), '-I', str(runtime_inc), '-o', str(runtime_obj)], check=False)
                        if rrt.returncode != 0:
                            print('Warning: failed to compile runtime support object; proceeding without it.')
                            runtime_obj = None
                except Exception as e:
                    print(f'Warning: error compiling runtime support: {e}')
                    runtime_obj = None

                # If we have an object file, link it (include runtime object if compiled)
                if obj_file and obj_file.exists():
                    try:
                        print(f"Linking object with clang -> {output_file}...")
                        link_cmd = [clang_path, '-o', str(output_file), str(obj_file)]
                        if runtime_obj and Path(runtime_obj).exists():
                            link_cmd.append(str(runtime_obj))
                        # Prefer console subsystem for visibility
                        link_cmd.append('-Wl,/subsystem:console')
                        r2 = subprocess.run(link_cmd, check=False)
                        if r2.returncode != 0:
                            print('clang failed to link object file into executable.')
                            # Try using lld-link (if available) as a fallback
                            lld_link = shutil.which('lld-link')
                            if not lld_link:
                                cand = Path('C:/Program Files/LLVM/bin/lld-link.exe')
                                if cand.exists():
                                    lld_link = str(cand)
                            if lld_link:
                                try:
                                    print(f"Trying lld-link -> {lld_link}")
                                    lld_cmd = [lld_link, str(obj_file), '/subsystem:console']
                                    if runtime_obj and Path(runtime_obj).exists():
                                        lld_cmd.append(str(runtime_obj))
                                    lld_cmd.append(f"-out:{str(output_file)}")
                                    r3 = subprocess.run(lld_cmd, check=False)
                                    if r3.returncode == 0:
                                        print(f'\u2713 Native binary created with lld-link: {output_file}')
                                    else:
                                        print('lld-link failed to link the object file.')
                                        print('Hint: On Windows, installing "Visual Studio Build Tools" and running from an "x64 Native Tools Command Prompt" provides the required CRT and SDK libs.')
                                except Exception as e:
                                    print(f'Error running lld-link: {e}')
                        else:
                            print(f'\u2713 Native binary created: {output_file}')
                    except Exception as e:
                        print(f'Error during linking: {e}')

        self.log(f"Output would be written to: {output_file}")

        print(f"✓ Compilation successful")
        print(f"  Input: {input_file}")
        print(f"  LLVM IR: {output_file.with_suffix('.ll') if output_file else 'not generated'}")
        print(f"  Safety: {safety_mode.name}")
        print(f"  Type: {output_type}")
        print(f"  Tokens: {len(tokens)}")
        print(f"  Optimization: O{optimization_level}")

        if warnings:
            print(f"  Warnings: {len(warnings)}")

        print(f"\nNote: Native binary generation requires LLVM toolchain (llc, clang)")

        return True


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Boogpp Compiler - Windows-centric systems programming language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  boogpp build main.bpp                     # Compile to main.exe
  boogpp build main.bpp -o myapp.exe        # Compile with custom output name
  boogpp build service.bpp --type service   # Compile as Windows service
  boogpp build driver.bpp --type driver     # Compile as kernel driver
  boogpp build app.bpp --safety unsafe -O3  # Compile with UNSAFE mode and O3 optimization

Output types:
  exe     - Executable (default)
  dll     - Dynamic Link Library
  service - Windows Service
  driver  - Kernel Driver (.sys)
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Build command
    build_parser = subparsers.add_parser('build', help='Compile a Boogpp source file')
    build_parser.add_argument('input', type=str, help='Input source file (.bpp)')
    build_parser.add_argument('-o', '--output', type=str, help='Output file name')
    build_parser.add_argument('--type', choices=['exe', 'dll', 'service', 'driver'],
                             default='exe', help='Output type (default: exe)')
    build_parser.add_argument('--safety', choices=['safe', 'unsafe', 'custom'],
                             default='safe', help='Safety mode (default: safe)')
    build_parser.add_argument('-O', '--optimization', type=int, choices=[0, 1, 2, 3],
                             default=0, help='Optimization level (default: 0)')
    build_parser.add_argument('-v', '--verbose', action='store_true',
                             help='Verbose output')
    build_parser.add_argument('--link', action='store_true', help='Run llc+clang to produce native binary if available')

    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')

    # Check command
    check_parser = subparsers.add_parser('check', help='Check syntax and safety without compiling')
    check_parser.add_argument('input', type=str, help='Input source file (.bpp)')
    check_parser.add_argument('--safety', choices=['safe', 'unsafe', 'custom'],
                             default='safe', help='Safety mode (default: safe)')
    check_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if args.command == 'version':
        print(f"Boogpp Compiler v{__version__}")
        print("A Windows-centric systems programming language")
        return 0

    elif args.command == 'build':
        input_file = Path(args.input)
        output_file = Path(args.output) if args.output else None

        # If the input file doesn't exist as given, try locating it inside the package
        if not input_file.exists():
            pkg_root = Path(__file__).resolve().parents[1]
            candidates = [
                pkg_root / args.input,
                pkg_root / 'examples' / args.input,
                pkg_root / 'tests' / args.input,
            ]
            for cand in candidates:
                if cand.exists():
                    print(f"[boogpp] Resolved input path to {cand}")
                    input_file = cand
                    break

        # Convert safety mode string to enum
        safety_mode = SafetyMode[args.safety.upper()]

        compiler = BoogppCompiler(verbose=args.verbose)
        success = compiler.compile_file(
            input_file,
            output_file,
            safety_mode,
            args.optimization,
            args.type,
            link=args.link
        )

        return 0 if success else 1

    elif args.command == 'check':
        input_file = Path(args.input)
        safety_mode = SafetyMode[args.safety.upper()]

        # If the input file doesn't exist as given, try locating it inside the package
        if not input_file.exists():
            pkg_root = Path(__file__).resolve().parents[1]
            candidates = [
                pkg_root / args.input,
                pkg_root / 'examples' / args.input,
                pkg_root / 'tests' / args.input,
            ]
            for cand in candidates:
                if cand.exists():
                    print(f"[boogpp] Resolved input path to {cand}")
                    input_file = cand
                    break

        compiler = BoogppCompiler(verbose=args.verbose)

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
