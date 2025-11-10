#!/usr/bin/env python3
"""
Integration tests for CustomOS Phase 2 components:
- Type Checker
- Enhanced Safety Checker
- LLVM Code Generator
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.typechecker import TypeChecker, check_types
from compiler.safety.enhanced_checker import EnhancedSafetyChecker, SafetyMode
from compiler.codegen import generate_code


def test_type_checker_basic():
    """Test basic type checking"""
    print("=" * 60)
    print("Test: Type Checker - Basic Types")
    print("=" * 60)

    code = """
func add(a: i32, b: i32) -> i32:
    return a + b

func main() -> i32:
    let x: i32 = 10
    let y: i32 = 20
    let res: i32 = add(x, y)
    return res
"""

    try:
        tokens = tokenize(code, "test_basic.cos")
        ast = parse(tokens)
        errors = check_types(ast)

        if errors:
            print("✗ Type errors found:")
            for error in errors:
                print(f"  {error}")
            return False
        else:
            print("✓ Type checking passed")
            return True
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_type_checker_inference():
    """Test type inference"""
    print("\n" + "=" * 60)
    print("Test: Type Checker - Type Inference")
    print("=" * 60)

    code = """
func main() -> i32:
    let x = 42        # Should infer i32
    let y = 3.14      # Should infer f64
    let name = "test" # Should infer string
    let flag = true   # Should infer bool
    return x
"""

    try:
        tokens = tokenize(code, "test_inference.cos")
        ast = parse(tokens)
        errors = check_types(ast)

        if errors:
            print("✗ Type errors found:")
            for error in errors:
                print(f"  {error}")
            return False
        else:
            print("✓ Type inference passed")
            return True
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


def test_type_checker_errors():
    """Test type error detection"""
    print("\n" + "=" * 60)
    print("Test: Type Checker - Error Detection")
    print("=" * 60)

    code = """
func add(a: i32, b: i32) -> i32:
    return a + b

func main() -> i32:
    let x: i32 = 10
    let y: string = "hello"
    let res: i32 = add(x, y)  # Should error: y is string, not i32
    return res
"""

    try:
        tokens = tokenize(code, "test_errors.cos")
        ast = parse(tokens)
        errors = check_types(ast)

        if errors:
            print("✓ Type errors correctly detected:")
            for error in errors:
                print(f"  {error}")
            return True
        else:
            print("✗ Expected type errors but none found")
            return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


def test_enhanced_safety_checker():
    """Test enhanced safety checking"""
    print("\n" + "=" * 60)
    print("Test: Enhanced Safety Checker")
    print("=" * 60)

    code = """
import windows.kernel32

func main() -> i32:
    let p = kernel32.VirtualAlloc(0, 1024, 0x3000, 0x04)
    return 0
"""

    try:
        tokens = tokenize(code, "test_safety.cos")
        ast = parse(tokens)

        # Test in SAFE mode (should block)
        checker = EnhancedSafetyChecker(SafetyMode.SAFE)
        violations = checker.check_program(ast)

        errors = [v for v in violations if v.severity == "error"]
        if errors:
            print("✓ SAFE mode correctly blocked dangerous operation:")
            for error in errors[:3]:  # Show first 3
                print(f"  {error.message}")
        else:
            print("✗ SAFE mode should have blocked VirtualAlloc")
            return False

        # Test in UNSAFE mode (should warn but allow)
        checker_unsafe = EnhancedSafetyChecker(SafetyMode.UNSAFE)
        violations_unsafe = checker_unsafe.check_program(ast)

        errors_unsafe = [v for v in violations_unsafe if v.severity == "error"]
        if not errors_unsafe:
            print("✓ UNSAFE mode correctly allowed operation with warning")
            return True
        else:
            print("✗ UNSAFE mode should allow operation")
            return False

    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_safety_rules_database():
    """Test safety rules database"""
    print("\n" + "=" * 60)
    print("Test: Safety Rules Database")
    print("=" * 60)

    from compiler.safety.safety_rules import SAFETY_RULES, SafetyCategory, OperationRisk

    # Test rule lookup
    alloc_rule = SAFETY_RULES.get_rule('alloc')
    if alloc_rule:
        print(f"✓ Found rule for 'alloc':")
        print(f"  Category: {alloc_rule.category.name}")
        print(f"  Risk: {alloc_rule.risk.name}")
        print(f"  Description: {alloc_rule.description}")
    else:
        print("✗ Rule for 'alloc' not found")
        return False

    # Test category lookup
    memory_rules = SAFETY_RULES.get_rules_by_category(SafetyCategory.MEMORY_MANAGEMENT)
    print(f"✓ Found {len(memory_rules)} memory management rules")

    # Test risk lookup
    critical_rules = SAFETY_RULES.get_rules_by_risk(OperationRisk.CRITICAL)
    print(f"✓ Found {len(critical_rules)} critical risk operations")

    return True


def test_code_generator_basic():
    """Test basic code generation"""
    print("\n" + "=" * 60)
    print("Test: Code Generator - Basic Function")
    print("=" * 60)

    code = """
func add(a: i32, b: i32) -> i32:
    return a + b

func main() -> i32:
    return add(5, 3)
"""

    try:
        tokens = tokenize(code, "test_codegen.cos")
        ast = parse(tokens)

        # Run type checker to get annotations
        type_checker = TypeChecker()
        type_errors = type_checker.check_program(ast)

        if type_errors:
            print("✗ Type errors prevent code generation:")
            for error in type_errors:
                print(f"  {error}")
            return False

        # Generate code
        llvm_ir = generate_code(ast, "test_codegen", type_checker.type_annotations)

        # Verify LLVM IR contains expected elements
        checks = [
            "define i32 @add",
            "define i32 @main",
            "call i32 @add",
            "ret i32"
        ]

        all_found = True
        for check in checks:
            if check in llvm_ir:
                print(f"✓ Found: {check}")
            else:
                print(f"✗ Missing: {check}")
                all_found = False

        if all_found:
            print("\n✓ LLVM IR generated successfully")
            print("\nGenerated LLVM IR (first 50 lines):")
            print("-" * 60)
            for i, line in enumerate(llvm_ir.split('\n')[:50]):
                print(line)
            return True
        else:
            print("\n✗ LLVM IR incomplete")
            return False

    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_code_generator_control_flow():
    """Test code generation with control flow"""
    print("\n" + "=" * 60)
    print("Test: Code Generator - Control Flow")
    print("=" * 60)

    code = """
func max(a: i32, b: i32) -> i32:
    if a > b:
        return a
    else:
        return b

func main() -> i32:
    return max(10, 20)
"""

    try:
        tokens = tokenize(code, "test_control_flow.cos")
        ast = parse(tokens)

        type_checker = TypeChecker()
        type_errors = type_checker.check_program(ast)

        if type_errors:
            print("✗ Type errors prevent code generation")
            return False

        llvm_ir = generate_code(ast, "test_control_flow", type_checker.type_annotations)

        # Verify control flow constructs
        checks = [
            "br i1",      # Conditional branch
            "label %",    # Labels for basic blocks
            "icmp"        # Integer comparison
        ]

        all_found = True
        for check in checks:
            if check in llvm_ir:
                print(f"✓ Found: {check}")
            else:
                print(f"✗ Missing: {check}")
                all_found = False

        return all_found

    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


def test_end_to_end_pipeline():
    """Test complete compilation pipeline"""
    print("\n" + "=" * 60)
    print("Test: End-to-End Compilation Pipeline")
    print("=" * 60)

    code = """
@safety_level(mode: SAFE)

func factorial(n: i32) -> i32:
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)

func main() -> i32:
    let x: i32 = 5
    let res: i32 = factorial(x)
    return res
"""

    try:
        # Step 1: Lexical Analysis
        print("Step 1: Lexical Analysis...")
        tokens = tokenize(code, "test_pipeline.cos")
        print(f"  ✓ Generated {len(tokens)} tokens")

        # Step 2: Parsing
        print("Step 2: Parsing...")
        ast = parse(tokens)
        print(f"  ✓ AST generated with {len(ast.declarations)} declarations")

        # Step 3: Safety Checking
        print("Step 3: Safety Checking...")
        safety_checker = EnhancedSafetyChecker(SafetyMode.SAFE)
        violations = safety_checker.check_program(ast)
        errors = [v for v in violations if v.severity == "error"]
        if errors:
            print(f"  ✗ Safety errors: {len(errors)}")
            for error in errors[:3]:
                print(f"    {error.message}")
            return False
        print(f"  ✓ Safety checks passed")

        # Step 4: Type Checking
        print("Step 4: Type Checking...")
        type_checker = TypeChecker()
        type_errors = type_checker.check_program(ast)
        if type_errors:
            print(f"  ✗ Type errors: {len(type_errors)}")
            for error in type_errors[:3]:
                print(f"    {error}")
            return False
        print(f"  ✓ Type checking passed")

        # Step 5: Code Generation
        print("Step 5: Code Generation...")
        llvm_ir = generate_code(ast, "test_pipeline", type_checker.type_annotations)
        print(f"  ✓ Generated {len(llvm_ir.split())} lines of LLVM IR")

        # Verify complete pipeline
        print("\n✓ Complete pipeline executed successfully")
        print("\nStatistics:")
        stats = safety_checker.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")

        return True

    except Exception as e:
        print(f"✗ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CustomOS Phase 2 Integration Tests")
    print("=" * 60)

    tests = [
        ("Type Checker - Basic", test_type_checker_basic),
        ("Type Checker - Inference", test_type_checker_inference),
        ("Type Checker - Errors", test_type_checker_errors),
        ("Enhanced Safety Checker", test_enhanced_safety_checker),
        ("Safety Rules Database", test_safety_rules_database),
        ("Code Generator - Basic", test_code_generator_basic),
        ("Code Generator - Control Flow", test_code_generator_control_flow),
        ("End-to-End Pipeline", test_end_to_end_pipeline),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
