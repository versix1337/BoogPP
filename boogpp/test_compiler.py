#!/usr/bin/env python3
"""
Test script to verify Boog++ compiler functionality.
"""

import sys
from pathlib import Path

# Add compiler to path
sys.path.insert(0, str(Path(__file__).parent))

from compiler.lexer import tokenize, LexerError
from compiler.parser import parse, ParseError
from compiler.safety import check_safety, SafetyMode


def test_lexer():
    """Test the lexer"""
    print("Testing Lexer...")

    source = """
@safety_level(mode: SAFE)
module test

import windows.registry

func main() -> i32:
    let x: i32 = 42
    return SUCCESS
"""

    try:
        tokens = tokenize(source, "test.bpp")
        print(f"  ✓ Lexer generated {len(tokens)} tokens")
        return True
    except LexerError as e:
        print(f"  ✗ Lexer error: {e}")
        return False


def test_parser():
    """Test the parser"""
    print("Testing Parser...")

    source = """
@safety_level(mode: SAFE)
module test

import windows.registry

func add(a: i32, b: i32) -> i32:
    return a + b

func main() -> i32:
    let x: i32 = 42
    let y = add(10, 20)
    return SUCCESS
"""

    try:
        tokens = tokenize(source, "test.bpp")
        ast = parse(tokens)
        print(f"  ✓ Parser generated AST successfully")
        print(f"    - Module: {ast.module_decl.name if ast.module_decl else 'None'}")
        print(f"    - Imports: {len(ast.imports)}")
        print(f"    - Declarations: {len(ast.declarations)}")
        return True
    except (LexerError, ParseError) as e:
        print(f"  ✗ Parser error: {e}")
        return False


def test_safety_checker():
    """Test the safety checker"""
    print("Testing Safety Checker...")

    # Safe code
    safe_code = """
@safety_level(mode: SAFE)
module test

import windows.registry

func main() -> i32:
    let x = windows.registry.read("HKLM\\Software", "Value")
    return SUCCESS
"""

    # Unsafe code
    unsafe_code = """
@safety_level(mode: SAFE)
module test

import windows.kernel32

func main() -> i32:
    let addr = windows.kernel32.VirtualAlloc(0, 1024, 0, 0)
    return SUCCESS
"""

    try:
        # Test safe code
        tokens = tokenize(safe_code, "safe.bpp")
        ast = parse(tokens)
        violations = check_safety(ast, SafetyMode.SAFE)
        errors = [v for v in violations if v.severity == "error"]

        if errors:
            print(f"  ✗ Safe code generated errors: {errors}")
            return False

        print(f"  ✓ Safe code passed safety checks")

        # Test unsafe code
        tokens = tokenize(unsafe_code, "unsafe.bpp")
        ast = parse(tokens)
        violations = check_safety(ast, SafetyMode.SAFE)
        errors = [v for v in violations if v.severity == "error"]

        if not errors:
            print(f"  ✗ Unsafe code should have generated errors")
            return False

        print(f"  ✓ Unsafe code correctly detected ({len(errors)} violation(s))")
        return True

    except (LexerError, ParseError) as e:
        print(f"  ✗ Error: {e}")
        return False


def test_example_file():
    """Test compiling an example file"""
    print("Testing Example File Compilation...")

    example_file = Path(__file__).parent / "examples" / "01_hello_world.bpp"

    if not example_file.exists():
        print(f"  ⚠ Example file not found: {example_file}")
        return True

    try:
        with open(example_file, 'r') as f:
            source = f.read()

        tokens = tokenize(source, str(example_file))
        ast = parse(tokens)
        violations = check_safety(ast, SafetyMode.SAFE)

        errors = [v for v in violations if v.severity == "error"]
        warnings = [v for v in violations if v.severity == "warning"]

        if errors:
            print(f"  ✗ Example file has errors:")
            for error in errors:
                print(f"    - {error}")
            return False

        print(f"  ✓ Example file compiled successfully")
        if warnings:
            print(f"    - {len(warnings)} warning(s)")

        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Boog++ Compiler Test Suite")
    print("=" * 60)
    print()

    tests = [
        test_lexer,
        test_parser,
        test_safety_checker,
        test_example_file,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Test crashed: {e}")
            results.append(False)
        print()

    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print(f"✗ {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
