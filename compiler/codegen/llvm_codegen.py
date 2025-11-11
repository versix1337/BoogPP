"""
Boogpp LLVM IR Code Generator
Generates LLVM IR from the AST.
"""

from typing import Optional, Dict, List, Any
from ..parser.ast_nodes import *
from ..typechecker.type_system import Type, TypeKind, PRIMITIVE_TYPES


class LLVMCodeGenerator:
    """Generates LLVM IR code from AST"""

    def __init__(self, module_name: str = "main"):
        self.module_name = module_name
        self.output = []
        self.indent_level = 0

        # Symbol tables
        self.global_symbols: Dict[str, str] = {}  # name -> LLVM identifier
        self.local_symbols: Dict[str, str] = {}   # name -> LLVM identifier
        self.functions: Dict[str, Dict] = {}      # function name -> metadata

        # Register allocation
        self.next_register = 1
        self.next_label = 1
        self.next_string = 1

        # Current function context
        self.current_function = None
        self.current_function_return_type = None

        # String literals
        self.string_literals: Dict[str, str] = {}  # content -> global name

        # Type annotations from type checker
        self.type_annotations: Dict[ASTNode, Type] = {}

    def generate(self, program: Program, type_annotations: Optional[Dict[ASTNode, Type]] = None) -> str:
        """Generate LLVM IR for a program"""
        self.output = []
        self.type_annotations = type_annotations or {}

        # Emit module header
        self._emit(f"; ModuleID = '{self.module_name}'")
        self._emit(f'source_filename = "{self.module_name}.bpp"')
        self._emit('')

        # Emit target triple
        self._emit('target triple = "x86_64-pc-windows-msvc"')
        self._emit('')

        # Generate declarations first
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                self._register_function(decl)

        # Generate function definitions
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                self.generate_function(decl)
            elif isinstance(decl, StructDecl):
                self.generate_struct(decl)

        # Emit string literals at the end
        self._emit_string_literals()

        # Emit standard library declarations
        self._emit_stdlib_declarations()

        return '\n'.join(self.output)

    def _emit(self, code: str = "") -> None:
        """Emit a line of code with proper indentation"""
        if code:
            self.output.append("  " * self.indent_level + code)
        else:
            self.output.append("")

    def _indent(self) -> None:
        """Increase indentation"""
        self.indent_level += 1

    def _dedent(self) -> None:
        """Decrease indentation"""
        self.indent_level = max(0, self.indent_level - 1)

    def _new_register(self) -> str:
        """Allocate a new register"""
        reg = f"%{self.next_register}"
        self.next_register += 1
        return reg

    def _new_label(self, prefix: str = "label") -> str:
        """Allocate a new label"""
        label = f"{prefix}.{self.next_label}"
        self.next_label += 1
        return label

    def _register_function(self, func: FunctionDecl) -> None:
        """Register a function for forward declarations"""
        param_types = []
        for param in func.parameters:
            llvm_type = self._get_llvm_type_from_annotation(param.type_annotation)
            param_types.append(llvm_type)

        return_type = (self._get_llvm_type_from_annotation(func.return_type)
                      if func.return_type else "void")

        self.functions[func.name] = {
            'return_type': return_type,
            'param_types': param_types,
            'params': func.parameters
        }

    def _get_llvm_type_from_annotation(self, type_node: Optional[TypeNode]) -> str:
        """Convert type annotation to LLVM type"""
        if type_node is None:
            return "void"

        if isinstance(type_node, TypeName):
            return self._get_llvm_primitive_type(type_node.name)

        elif isinstance(type_node, TypePtr):
            element_type = self._get_llvm_type_from_annotation(type_node.element_type)
            return f"{element_type}*"

        elif isinstance(type_node, TypeArray):
            element_type = self._get_llvm_type_from_annotation(type_node.element_type)
            return f"[{type_node.size} x {element_type}]"

        elif isinstance(type_node, TypeSlice):
            # Slice is represented as {ptr, length}
            element_type = self._get_llvm_type_from_annotation(type_node.element_type)
            return f"{{ {element_type}*, i64 }}"

        elif isinstance(type_node, TypeTuple):
            element_types = [self._get_llvm_type_from_annotation(t) for t in type_node.element_types]
            types_str = ", ".join(element_types)
            return f"{{ {types_str} }}"

        elif isinstance(type_node, TypeResult):
            # Result is represented as {status, value}
            value_type = self._get_llvm_type_from_annotation(type_node.value_type)
            return f"{{ i32, {value_type} }}"

        return "i32"  # Default

    def _get_llvm_type(self, typ: Type) -> str:
        """Convert Boogpp type to LLVM type string"""
        if typ.kind == TypeKind.I8:
            return "i8"
        elif typ.kind == TypeKind.I16:
            return "i16"
        elif typ.kind == TypeKind.I32 or typ.kind == TypeKind.STATUS:
            return "i32"
        elif typ.kind == TypeKind.I64:
            return "i64"
        elif typ.kind == TypeKind.U8:
            return "i8"
        elif typ.kind == TypeKind.U16:
            return "i16"
        elif typ.kind == TypeKind.U32:
            return "i32"
        elif typ.kind == TypeKind.U64 or typ.kind == TypeKind.HANDLE:
            return "i64"
        elif typ.kind == TypeKind.F32:
            return "float"
        elif typ.kind == TypeKind.F64:
            return "double"
        elif typ.kind == TypeKind.BOOL:
            return "i1"
        elif typ.kind == TypeKind.CHAR:
            return "i8"
        elif typ.kind == TypeKind.STRING:
            return "i8*"
        elif typ.kind == TypeKind.VOID:
            return "void"
        elif typ.kind == TypeKind.POINTER:
            elem_type = self._get_llvm_type(typ.element_type)
            return f"{elem_type}*"
        elif typ.kind == TypeKind.ARRAY:
            elem_type = self._get_llvm_type(typ.element_type)
            return f"[{typ.size} x {elem_type}]"
        elif typ.kind == TypeKind.SLICE:
            elem_type = self._get_llvm_type(typ.element_type)
            return f"{{ {elem_type}*, i64 }}"
        elif typ.kind == TypeKind.TUPLE:
            elem_types = [self._get_llvm_type(t) for t in typ.element_types]
            return f"{{ {', '.join(elem_types)} }}"
        else:
            return "i32"  # Default fallback

    def _get_llvm_primitive_type(self, name: str) -> str:
        """Get LLVM type for primitive type name"""
        type_map = {
            'i8': 'i8', 'i16': 'i16', 'i32': 'i32', 'i64': 'i64',
            'u8': 'i8', 'u16': 'i16', 'u32': 'i32', 'u64': 'i64',
            'f32': 'float', 'f64': 'double',
            'bool': 'i1', 'char': 'i8', 'string': 'i8*',
            'void': 'void', 'status': 'i32', 'handle': 'i64'
        }
        return type_map.get(name, 'i32')

    def generate_function(self, func: FunctionDecl) -> None:
        """Generate code for a function"""
        # Reset local context
        self.local_symbols = {}
        self.next_register = 1
        self.next_label = 1
        self.current_function = func.name

        # Build parameter list
        params = []
        for i, param in enumerate(func.parameters):
            param_type = self._get_llvm_type_from_annotation(param.type_annotation)
            param_name = f"%{param.name}"
            params.append(f"{param_type} {param_name}")
            self.local_symbols[param.name] = param_name

        params_str = ", ".join(params) if params else ""

        # Get return type
        return_type = (self._get_llvm_type_from_annotation(func.return_type)
                      if func.return_type else "void")
        self.current_function_return_type = return_type

        # Emit function signature
        func_name = f"@{func.name}" if func.name != "main" else "@main"
        self._emit(f"define {return_type} {func_name}({params_str}) {{")
        self._indent()

        # Emit entry label
        self._emit("entry:")
        self._indent()

        # Initialize runtime at program start (best-effort)
        if func.name == "main":
            self._emit("call i32 @bpp_runtime_init()")

        # Generate function body
        self.generate_statement(func.body)

        # Ensure function has a return
        if return_type == "void":
            self._emit("ret void")
        else:
            # This should have been caught by type checker
            self._emit(f"ret {return_type} 0  ; default return")

        self._dedent()
        self._dedent()
        self._emit("}")
        self._emit("")

    def generate_struct(self, struct: StructDecl) -> None:
        """Generate code for a struct"""
        field_types = []
        for field in struct.fields:
            field_type = self._get_llvm_type_from_annotation(field.type_annotation)
            field_types.append(field_type)

        fields_str = ", ".join(field_types)
        self._emit(f"%struct.{struct.name} = type {{ {fields_str} }}")
        self._emit("")

    def generate_statement(self, stmt: Statement) -> None:
        """Generate code for a statement"""
        if isinstance(stmt, Block):
            for s in stmt.statements:
                self.generate_statement(s)

        elif isinstance(stmt, ReturnStmt):
            if stmt.value:
                value_reg = self.generate_expression(stmt.value)
                value_type = self._get_expression_type(stmt.value)
                llvm_type = self._get_llvm_type(value_type)
                self._emit(f"ret {llvm_type} {value_reg}")
            else:
                self._emit("ret void")

        elif isinstance(stmt, IfStmt):
            self.generate_if_statement(stmt)

        elif isinstance(stmt, WhileStmt):
            self.generate_while_statement(stmt)

        elif isinstance(stmt, ForStmt):
            self.generate_for_statement(stmt)

        elif isinstance(stmt, ExprStmt):
            self.generate_expression(stmt.expression)

        elif isinstance(stmt, AssignStmt):
            self.generate_assignment(stmt)

        elif isinstance(stmt, VariableDecl):
            self.generate_variable_decl(stmt)

        elif isinstance(stmt, PassStmt):
            # No-op
            pass

        elif isinstance(stmt, BreakStmt):
            # Would need loop context
            self._emit("br label %break")

        elif isinstance(stmt, ContinueStmt):
            # Would need loop context
            self._emit("br label %continue")

    def generate_if_statement(self, stmt: IfStmt) -> None:
        """Generate code for if statement"""
        then_label = self._new_label("if.then")
        else_label = self._new_label("if.else")
        end_label = self._new_label("if.end")

        # Generate condition
        cond_reg = self.generate_expression(stmt.condition)

        # Branch
        if stmt.else_block or stmt.elif_clauses:
            self._emit(f"br i1 {cond_reg}, label %{then_label}, label %{else_label}")
        else:
            self._emit(f"br i1 {cond_reg}, label %{then_label}, label %{end_label}")

        # Then block
        self._dedent()
        self._emit(f"{then_label}:")
        self._indent()
        self.generate_statement(stmt.then_block)
        self._emit(f"br label %{end_label}")

        # Else/elif blocks
        if stmt.elif_clauses or stmt.else_block:
            self._dedent()
            self._emit(f"{else_label}:")
            self._indent()

            # Handle elif clauses
            for cond, block in stmt.elif_clauses:
                elif_then = self._new_label("elif.then")
                elif_else = self._new_label("elif.else")

                elif_cond_reg = self.generate_expression(cond)
                self._emit(f"br i1 {elif_cond_reg}, label %{elif_then}, label %{elif_else}")

                self._dedent()
                self._emit(f"{elif_then}:")
                self._indent()
                self.generate_statement(block)
                self._emit(f"br label %{end_label}")

                self._dedent()
                self._emit(f"{elif_else}:")
                self._indent()

            # Handle final else
            if stmt.else_block:
                self.generate_statement(stmt.else_block)

            self._emit(f"br label %{end_label}")

        # End block
        self._dedent()
        self._emit(f"{end_label}:")
        self._indent()

    def generate_while_statement(self, stmt: WhileStmt) -> None:
        """Generate code for while statement"""
        cond_label = self._new_label("while.cond")
        body_label = self._new_label("while.body")
        end_label = self._new_label("while.end")

        # Jump to condition
        self._emit(f"br label %{cond_label}")

        # Condition block
        self._dedent()
        self._emit(f"{cond_label}:")
        self._indent()
        cond_reg = self.generate_expression(stmt.condition)
        self._emit(f"br i1 {cond_reg}, label %{body_label}, label %{end_label}")

        # Body block
        self._dedent()
        self._emit(f"{body_label}:")
        self._indent()
        self.generate_statement(stmt.body)
        self._emit(f"br label %{cond_label}")

        # End block
        self._dedent()
        self._emit(f"{end_label}:")
        self._indent()

    def generate_for_statement(self, stmt: ForStmt) -> None:
        """Generate code for for statement"""
        # For now, simplified version
        # Full implementation would handle iterators properly
        self._emit("; for loop (simplified)")

    def generate_assignment(self, stmt: AssignStmt) -> None:
        """Generate code for assignment"""
        # Get target (must be an identifier for now)
        if isinstance(stmt.target, IdentifierExpr):
            value_reg = self.generate_expression(stmt.value)
            target_name = stmt.target.name

            if target_name in self.local_symbols:
                target_reg = self.local_symbols[target_name]
                value_type = self._get_expression_type(stmt.value)
                llvm_type = self._get_llvm_type(value_type)

                # Store to alloca'd location
                self._emit(f"store {llvm_type} {value_reg}, {llvm_type}* {target_reg}")

    def generate_variable_decl(self, decl: VariableDecl) -> None:
        """Generate code for variable declaration"""
        # Allocate stack space
        if decl.type_annotation:
            llvm_type = self._get_llvm_type_from_annotation(decl.type_annotation)
        else:
            # Infer from initializer
            init_type = self._get_expression_type(decl.initializer)
            llvm_type = self._get_llvm_type(init_type)

        var_reg = self._new_register()
        self._emit(f"{var_reg} = alloca {llvm_type}")
        self.local_symbols[decl.name] = var_reg

        # Initialize if present
        if decl.initializer:
            init_reg = self.generate_expression(decl.initializer)
            self._emit(f"store {llvm_type} {init_reg}, {llvm_type}* {var_reg}")

    def generate_expression(self, expr: Expression) -> str:
        """Generate code for an expression and return the register holding the result"""
        if isinstance(expr, LiteralExpr):
            return self.generate_literal(expr)

        elif isinstance(expr, IdentifierExpr):
            return self.generate_identifier(expr)

        elif isinstance(expr, BinaryExpr):
            return self.generate_binary_expr(expr)

        elif isinstance(expr, UnaryExpr):
            return self.generate_unary_expr(expr)

        elif isinstance(expr, CallExpr):
            return self.generate_call_expr(expr)

        elif isinstance(expr, MemberExpr):
            return self.generate_member_expr(expr)

        elif isinstance(expr, IndexExpr):
            return self.generate_index_expr(expr)

        elif isinstance(expr, TupleExpr):
            return self.generate_tuple_expr(expr)

        elif isinstance(expr, ArrayExpr):
            return self.generate_array_expr(expr)

        else:
            # Default fallback
            return "0"

    def generate_literal(self, literal: LiteralExpr) -> str:
        """Generate code for a literal"""
        if literal.literal_type in ('int', 'integer'):
            return str(literal.value)
        elif literal.literal_type == 'float':
            return str(literal.value)
        elif literal.literal_type == 'string':
            return self._get_string_literal(str(literal.value))
        elif literal.literal_type in ('bool', 'boolean'):
            return "1" if literal.value else "0"
        elif literal.literal_type == 'char':
            return str(ord(literal.value))
        return "0"

    def generate_identifier(self, ident: IdentifierExpr) -> str:
        """Generate code for an identifier"""
        # Handle built-in constants
        if ident.name == 'SUCCESS':
            return "0"
        elif ident.name == 'true':
            return "1"
        elif ident.name == 'false':
            return "0"

        if ident.name in self.local_symbols:
            var_reg = self.local_symbols[ident.name]
            result_reg = self._new_register()

            # Load from memory
            var_type = self._get_expression_type(ident)
            llvm_type = self._get_llvm_type(var_type)
            self._emit(f"{result_reg} = load {llvm_type}, {llvm_type}* {var_reg}")
            return result_reg

        return "0"  # Unknown identifier

    def generate_binary_expr(self, expr: BinaryExpr) -> str:
        """Generate code for binary expression"""
        left_reg = self.generate_expression(expr.left)
        right_reg = self.generate_expression(expr.right)
        result_reg = self._new_register()

        left_type = self._get_expression_type(expr.left)
        llvm_type = self._get_llvm_type(left_type)

        # Arithmetic operators
        if expr.operator == '+':
            if left_type.is_float():
                self._emit(f"{result_reg} = fadd {llvm_type} {left_reg}, {right_reg}")
            else:
                self._emit(f"{result_reg} = add {llvm_type} {left_reg}, {right_reg}")
        elif expr.operator == '-':
            if left_type.is_float():
                self._emit(f"{result_reg} = fsub {llvm_type} {left_reg}, {right_reg}")
            else:
                self._emit(f"{result_reg} = sub {llvm_type} {left_reg}, {right_reg}")
        elif expr.operator == '*':
            if left_type.is_float():
                self._emit(f"{result_reg} = fmul {llvm_type} {left_reg}, {right_reg}")
            else:
                self._emit(f"{result_reg} = mul {llvm_type} {left_reg}, {right_reg}")
        elif expr.operator == '/':
            if left_type.is_float():
                self._emit(f"{result_reg} = fdiv {llvm_type} {left_reg}, {right_reg}")
            elif left_type.is_signed():
                self._emit(f"{result_reg} = sdiv {llvm_type} {left_reg}, {right_reg}")
            else:
                self._emit(f"{result_reg} = udiv {llvm_type} {left_reg}, {right_reg}")
        elif expr.operator == '%':
            if left_type.is_signed():
                self._emit(f"{result_reg} = srem {llvm_type} {left_reg}, {right_reg}")
            else:
                self._emit(f"{result_reg} = urem {llvm_type} {left_reg}, {right_reg}")

        # Comparison operators
        elif expr.operator == '==':
            if left_type.is_float():
                self._emit(f"{result_reg} = fcmp oeq {llvm_type} {left_reg}, {right_reg}")
            else:
                self._emit(f"{result_reg} = icmp eq {llvm_type} {left_reg}, {right_reg}")
        elif expr.operator == '!=':
            if left_type.is_float():
                self._emit(f"{result_reg} = fcmp one {llvm_type} {left_reg}, {right_reg}")
            else:
                self._emit(f"{result_reg} = icmp ne {llvm_type} {left_reg}, {right_reg}")
        elif expr.operator == '<':
            if left_type.is_float():
                self._emit(f"{result_reg} = fcmp olt {llvm_type} {left_reg}, {right_reg}")
            elif left_type.is_signed():
                self._emit(f"{result_reg} = icmp slt {llvm_type} {left_reg}, {right_reg}")
            else:
                self._emit(f"{result_reg} = icmp ult {llvm_type} {left_reg}, {right_reg}")
        elif expr.operator == '>':
            if left_type.is_float():
                self._emit(f"{result_reg} = fcmp ogt {llvm_type} {left_reg}, {right_reg}")
            elif left_type.is_signed():
                self._emit(f"{result_reg} = icmp sgt {llvm_type} {left_reg}, {right_reg}")
            else:
                self._emit(f"{result_reg} = icmp ugt {llvm_type} {left_reg}, {right_reg}")
        elif expr.operator == '<=':
            if left_type.is_float():
                self._emit(f"{result_reg} = fcmp ole {llvm_type} {left_reg}, {right_reg}")
            elif left_type.is_signed():
                self._emit(f"{result_reg} = icmp sle {llvm_type} {left_reg}, {right_reg}")
            else:
                self._emit(f"{result_reg} = icmp ule {llvm_type} {left_reg}, {right_reg}")
        elif expr.operator == '>=':
            if left_type.is_float():
                self._emit(f"{result_reg} = fcmp oge {llvm_type} {left_reg}, {right_reg}")
            elif left_type.is_signed():
                self._emit(f"{result_reg} = icmp sge {llvm_type} {left_reg}, {right_reg}")
            else:
                self._emit(f"{result_reg} = icmp uge {llvm_type} {left_reg}, {right_reg}")

        # Logical operators
        elif expr.operator == 'and':
            self._emit(f"{result_reg} = and i1 {left_reg}, {right_reg}")
        elif expr.operator == 'or':
            self._emit(f"{result_reg} = or i1 {left_reg}, {right_reg}")

        # Bitwise operators
        elif expr.operator == '&':
            self._emit(f"{result_reg} = and {llvm_type} {left_reg}, {right_reg}")
        elif expr.operator == '|':
            self._emit(f"{result_reg} = or {llvm_type} {left_reg}, {right_reg}")
        elif expr.operator == '^':
            self._emit(f"{result_reg} = xor {llvm_type} {left_reg}, {right_reg}")
        elif expr.operator == '<<':
            self._emit(f"{result_reg} = shl {llvm_type} {left_reg}, {right_reg}")
        elif expr.operator == '>>':
            if left_type.is_signed():
                self._emit(f"{result_reg} = ashr {llvm_type} {left_reg}, {right_reg}")
            else:
                self._emit(f"{result_reg} = lshr {llvm_type} {left_reg}, {right_reg}")
        else:
            self._emit(f"{result_reg} = add {llvm_type} {left_reg}, {right_reg}  ; unknown operator")

        return result_reg

    def generate_unary_expr(self, expr: UnaryExpr) -> str:
        """Generate code for unary expression"""
        operand_reg = self.generate_expression(expr.operand)
        result_reg = self._new_register()

        operand_type = self._get_expression_type(expr.operand)
        llvm_type = self._get_llvm_type(operand_type)

        if expr.operator == '-':
            if operand_type.is_float():
                self._emit(f"{result_reg} = fneg {llvm_type} {operand_reg}")
            else:
                self._emit(f"{result_reg} = sub {llvm_type} 0, {operand_reg}")
        elif expr.operator == 'not':
            self._emit(f"{result_reg} = xor i1 {operand_reg}, 1")
        elif expr.operator == '~':
            self._emit(f"{result_reg} = xor {llvm_type} {operand_reg}, -1")

        return result_reg

    def generate_call_expr(self, expr: CallExpr) -> str:
        """Generate code for function call"""
        # Get function name
        func_name = None
        if isinstance(expr.callee, IdentifierExpr):
            func_name = expr.callee.name

        if not func_name:
            return "0"

        # Generate arguments
        args = []
        for arg in expr.arguments:
            arg_reg = self.generate_expression(arg)
            arg_type = self._get_expression_type(arg)
            llvm_type = self._get_llvm_type(arg_type)
            args.append(f"{llvm_type} {arg_reg}")

        args_str = ", ".join(args) if args else ""

        # Get function info
        if func_name in self.functions:
            func_info = self.functions[func_name]
            return_type = func_info['return_type']

            if return_type == "void":
                self._emit(f"call void @{func_name}({args_str})")
                return "0"
            else:
                result_reg = self._new_register()
                self._emit(f"{result_reg} = call {return_type} @{func_name}({args_str})")
                return result_reg
        else:
            # Built-in or external function
            return self.generate_builtin_call(func_name, expr.arguments)

    def generate_builtin_call(self, func_name: str, args: List[Expression]) -> str:
        """Generate code for built-in/stdlib-like functions (println/print/log)."""
        if not args:
            return "0"

        # Helper: turn a string literal into i8* using GEP
        def _emit_cstr_ptr(lit: LiteralExpr) -> Optional[str]:
            if lit.literal_type != 'string':
                return None
            content = str(lit.value)
            global_name = self._get_string_literal(content)
            length = len(content) + 1
            reg = self._new_register()
            self._emit(f"{reg} = getelementptr inbounds ([{length} x i8], [{length} x i8]* {global_name}, i32 0, i32 0)")
            return reg

        first = args[0]

        # println -> bpp_println(bpp_string_new(cstr))
        if func_name in ("println", "print", "log"):
            cstr_ptr = None
            if isinstance(first, LiteralExpr):
                cstr_ptr = _emit_cstr_ptr(first)
            else:
                # Fallback: try evaluating expression and hope it's already i8*
                maybe_ptr = self.generate_expression(first)
                cstr_ptr = maybe_ptr

            if func_name == "println":
                # Build bpp_string and call println
                sreg = self._new_register()
                self._emit(f"{sreg} = call %bpp_string_t* @bpp_string_new(i8* {cstr_ptr})")
                self._emit(f"call i32 @bpp_println(%bpp_string_t* {sreg})")
                return "0"
            elif func_name == "print":
                sreg = self._new_register()
                self._emit(f"{sreg} = call %bpp_string_t* @bpp_string_new(i8* {cstr_ptr})")
                self._emit(f"call i32 @bpp_print(%bpp_string_t* {sreg})")
                return "0"
            elif func_name == "log":
                sreg = self._new_register()
                self._emit(f"{sreg} = call %bpp_string_t* @bpp_string_new(i8* {cstr_ptr})")
                self._emit(f"call i32 @bpp_log(%bpp_string_t* {sreg})")
                return "0"

        # read_line(): wait for user input; free returned string to avoid leaks
        if func_name == "read_line":
            tmp = self._new_register()
            self._emit(f"{tmp} = call %bpp_string_t* @bpp_read_line()")
            # Free immediately if used as statement
            self._emit(f"call void @bpp_string_free(%bpp_string_t* {tmp})")
            return "0"

        # sleep(ms): call runtime sleep
        if func_name == "sleep":
            ms_reg = self.generate_expression(first)
            self._emit(f"call void @bpp_sleep(i32 {ms_reg})")
            return "0"

        # Default: return 0
        return "0"

    def generate_member_expr(self, expr: MemberExpr) -> str:
        """Generate code for member access"""
        # Simplified version
        return "0"

    def generate_index_expr(self, expr: IndexExpr) -> str:
        """Generate code for array indexing"""
        # Simplified version
        return "0"

    def generate_tuple_expr(self, expr: TupleExpr) -> str:
        """Generate code for tuple literal"""
        # Simplified version
        return "0"

    def generate_array_expr(self, expr: ArrayExpr) -> str:
        """Generate code for array literal"""
        # Simplified version
        return "0"

    def _get_expression_type(self, expr: Expression) -> Type:
        """Get the type of an expression"""
        if expr in self.type_annotations:
            return self.type_annotations[expr]

        # Fallback type inference
        if isinstance(expr, LiteralExpr):
            if expr.literal_type in ('int', 'integer'):
                return PRIMITIVE_TYPES['i32']
            elif expr.literal_type == 'float':
                return PRIMITIVE_TYPES['f64']
            elif expr.literal_type == 'string':
                return PRIMITIVE_TYPES['string']
            elif expr.literal_type in ('bool', 'boolean'):
                return PRIMITIVE_TYPES['bool']

        return PRIMITIVE_TYPES['i32']  # Default

    def _get_string_literal(self, content: str) -> str:
        """Get or create a global string literal"""
        if content in self.string_literals:
            return self.string_literals[content]

        # Create new string literal
        str_name = f"@.str.{self.next_string}"
        self.next_string += 1
        self.string_literals[content] = str_name

        return str_name

    def _emit_string_literals(self) -> None:
        """Emit all string literals as globals"""
        for content, name in self.string_literals.items():
            escaped = content.replace('\\', '\\\\').replace('"', '\\"')
            length = len(content) + 1  # +1 for null terminator
            self._emit(f"{name} = private unnamed_addr constant [{length} x i8] c\"{escaped}\\00\"")

    def _emit_stdlib_declarations(self) -> None:
        """Emit standard library function declarations"""
        self._emit("")
        self._emit("; Boogpp Runtime Library Declarations")
        self._emit("")

        # Runtime initialization
        self._emit("declare i32 @bpp_runtime_init()")
        self._emit("declare void @bpp_runtime_cleanup()")
        self._emit("declare i8* @bpp_runtime_version()")
        self._emit("")

        # Memory management
        self._emit("declare i8* @bpp_alloc(i64)")
        self._emit("declare void @bpp_free(i8*)")
        self._emit("declare i8* @bpp_realloc(i8*, i64)")
        self._emit("declare void @bpp_refcount_inc(i8*)")
        self._emit("declare void @bpp_refcount_dec(i8*)")
        self._emit("")

        # String operations (opaque type)
        self._emit("%bpp_string_t = type opaque")
        self._emit("declare %bpp_string_t* @bpp_string_new(i8*)")
        self._emit("declare %bpp_string_t* @bpp_string_with_capacity(i64)")
        self._emit("declare void @bpp_string_free(%bpp_string_t*)")
        self._emit("declare %bpp_string_t* @bpp_string_concat(%bpp_string_t*, %bpp_string_t*)")
        self._emit("declare i64 @bpp_string_length(%bpp_string_t*)")
        self._emit("declare i32 @bpp_string_compare(%bpp_string_t*, %bpp_string_t*)")
        self._emit("")

        # I/O operations
        self._emit("declare i32 @bpp_print(%bpp_string_t*)")
        self._emit("declare i32 @bpp_println(%bpp_string_t*)")
        self._emit("declare i32 @bpp_log(%bpp_string_t*)")
        self._emit("declare %bpp_string_t* @bpp_read_line()")
        self._emit("")

        # Array operations (opaque type)
        self._emit("%bpp_array_t = type opaque")
        self._emit("declare %bpp_array_t* @bpp_array_new(i64, i64)")
        self._emit("declare void @bpp_array_free(%bpp_array_t*)")
        self._emit("declare i8* @bpp_array_get(%bpp_array_t*, i64)")
        self._emit("declare i32 @bpp_array_set(%bpp_array_t*, i64, i8*)")
        self._emit("")

        # Slice operations (opaque type)
        self._emit("%bpp_slice_t = type opaque")
        self._emit("declare %bpp_slice_t* @bpp_slice_new(%bpp_array_t*, i64, i64)")
        self._emit("declare void @bpp_slice_free(%bpp_slice_t*)")
        self._emit("")

        # Utility functions
        self._emit("declare void @bpp_sleep(i32)")
        self._emit("declare i64 @bpp_timestamp_ms()")
        self._emit("declare i8* @bpp_status_string(i32)")
        self._emit("")

        # C standard library (for compatibility)
        self._emit("; C Standard Library")
        self._emit("declare void @print(i8*)")
        self._emit("declare i8* @malloc(i64)")
        self._emit("declare void @free(i8*)")


def generate_code(program: Program, module_name: str = "main",
                 type_annotations: Optional[Dict[ASTNode, Type]] = None) -> str:
    """Convenience function to generate LLVM IR code"""
    codegen = LLVMCodeGenerator(module_name)
    return codegen.generate(program, type_annotations)
