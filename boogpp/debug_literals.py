#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/user/BoogPP/boogpp')

from compiler.lexer import tokenize
from compiler.parser import parse
from compiler.typechecker import TypeChecker

code = """
func main() -> i32:
    let x: i32 = 10
    return x
"""

tokens = tokenize(code, "debug.bpp")
print(f"Tokens: {len(tokens)}")

ast = parse(tokens)
print(f"AST declarations: {len(ast.declarations)}")

# Check the function
func = ast.declarations[0]
print(f"Function: {func.name}")
print(f"Body statements: {len(func.body.statements)}")

# Check the variable declaration
var_decl = func.body.statements[0]
print(f"Variable decl type: {type(var_decl).__name__}")
print(f"Variable name: {var_decl.name}")
print(f"Initializer type: {type(var_decl.initializer).__name__}")
print(f"Initializer value: {var_decl.initializer.value}")
print(f"Initializer literal_type: {var_decl.initializer.literal_type}")

# Now type check
type_checker = TypeChecker()
errors = type_checker.check_program(ast)

print(f"\nType errors: {len(errors)}")
for error in errors:
    print(f"  {error}")
