"""
Boogpp Type System
Defines types, type checking, and type inference.
"""

from enum import Enum, auto
from typing import Optional, List, Dict, Set
from dataclasses import dataclass


class TypeKind(Enum):
    """Type kinds"""
    # Primitives
    I8 = auto()
    I16 = auto()
    I32 = auto()
    I64 = auto()
    U8 = auto()
    U16 = auto()
    U32 = auto()
    U64 = auto()
    F32 = auto()
    F64 = auto()
    BOOL = auto()
    CHAR = auto()
    STRING = auto()
    VOID = auto()

    # Compound types
    POINTER = auto()
    ARRAY = auto()
    SLICE = auto()
    TUPLE = auto()
    RESULT = auto()
    FUNCTION = auto()

    # User-defined
    STRUCT = auto()
    ENUM = auto()
    TRAIT = auto()

    # Special
    STATUS = auto()      # Alias for i32
    HANDLE = auto()      # Alias for u64
    UNKNOWN = auto()     # For type inference
    TYPE_VAR = auto()    # Type variable for generics
    ERROR = auto()       # Error type


@dataclass
class Type:
    """Represents a type in the type system"""
    kind: TypeKind
    name: Optional[str] = None

    # For compound types
    element_type: Optional['Type'] = None      # For pointer, array, slice
    element_types: Optional[List['Type']] = None  # For tuple
    size: Optional[int] = None                  # For array

    # For function types
    param_types: Optional[List['Type']] = None
    return_type: Optional['Type'] = None

    # For struct/enum types
    fields: Optional[Dict[str, 'Type']] = None
    variants: Optional[List[str]] = None

    # For type variables
    type_var_id: Optional[int] = None

    def __str__(self) -> str:
        """String representation of type"""
        if self.kind == TypeKind.POINTER:
            return f"ptr[{self.element_type}]"
        elif self.kind == TypeKind.ARRAY:
            return f"array[{self.element_type}, {self.size}]"
        elif self.kind == TypeKind.SLICE:
            return f"slice[{self.element_type}]"
        elif self.kind == TypeKind.TUPLE:
            elem_strs = ", ".join(str(t) for t in self.element_types)
            return f"tuple({elem_strs})"
        elif self.kind == TypeKind.RESULT:
            return f"result[{self.element_type}]"
        elif self.kind == TypeKind.FUNCTION:
            param_strs = ", ".join(str(t) for t in self.param_types)
            return f"func({param_strs}) -> {self.return_type}"
        elif self.kind == TypeKind.TYPE_VAR:
            return f"T{self.type_var_id}"
        elif self.name:
            return self.name
        else:
            return self.kind.name.lower()

    def __eq__(self, other) -> bool:
        """Check type equality"""
        if not isinstance(other, Type):
            return False

        if self.kind != other.kind:
            return False

        # Check compound types
        if self.kind == TypeKind.POINTER:
            return self.element_type == other.element_type
        elif self.kind == TypeKind.ARRAY:
            return (self.element_type == other.element_type and
                   self.size == other.size)
        elif self.kind == TypeKind.SLICE:
            return self.element_type == other.element_type
        elif self.kind == TypeKind.TUPLE:
            return self.element_types == other.element_types
        elif self.kind == TypeKind.RESULT:
            return self.element_type == other.element_type
        elif self.kind == TypeKind.FUNCTION:
            return (self.param_types == other.param_types and
                   self.return_type == other.return_type)
        elif self.kind in (TypeKind.STRUCT, TypeKind.ENUM, TypeKind.TRAIT):
            return self.name == other.name

        return True

    def __hash__(self):
        """Hash for use in sets/dicts"""
        return hash((self.kind, self.name))

    def is_numeric(self) -> bool:
        """Check if type is numeric"""
        return self.kind in (
            TypeKind.I8, TypeKind.I16, TypeKind.I32, TypeKind.I64,
            TypeKind.U8, TypeKind.U16, TypeKind.U32, TypeKind.U64,
            TypeKind.F32, TypeKind.F64
        )

    def is_integer(self) -> bool:
        """Check if type is integer"""
        return self.kind in (
            TypeKind.I8, TypeKind.I16, TypeKind.I32, TypeKind.I64,
            TypeKind.U8, TypeKind.U16, TypeKind.U32, TypeKind.U64
        )

    def is_signed(self) -> bool:
        """Check if type is signed integer"""
        return self.kind in (TypeKind.I8, TypeKind.I16, TypeKind.I32, TypeKind.I64)

    def is_unsigned(self) -> bool:
        """Check if type is unsigned integer"""
        return self.kind in (TypeKind.U8, TypeKind.U16, TypeKind.U32, TypeKind.U64)

    def is_float(self) -> bool:
        """Check if type is floating point"""
        return self.kind in (TypeKind.F32, TypeKind.F64)

    def is_pointer(self) -> bool:
        """Check if type is pointer"""
        return self.kind == TypeKind.POINTER

    def can_assign_to(self, other: 'Type') -> bool:
        """Check if this type can be assigned to other type"""
        # Exact match
        if self == other:
            return True

        # Numeric conversions (with potential loss)
        if self.is_numeric() and other.is_numeric():
            # Allow implicit widening conversions
            if self.is_integer() and other.is_integer():
                self_bits = int(self.kind.name[1:])
                other_bits = int(other.kind.name[1:])
                # Same signedness and widening
                if self.is_signed() == other.is_signed() and self_bits <= other_bits:
                    return True
            # Allow int to float
            if self.is_integer() and other.is_float():
                return True

        # STATUS is compatible with i32
        if self.kind == TypeKind.STATUS and other.kind == TypeKind.I32:
            return True
        if self.kind == TypeKind.I32 and other.kind == TypeKind.STATUS:
            return True

        # HANDLE is compatible with u64
        if self.kind == TypeKind.HANDLE and other.kind == TypeKind.U64:
            return True
        if self.kind == TypeKind.U64 and other.kind == TypeKind.HANDLE:
            return True

        return False


class TypeVariable:
    """Type variable for type inference"""
    _counter = 0

    def __init__(self):
        self.id = TypeVariable._counter
        TypeVariable._counter += 1
        self.bound_type: Optional[Type] = None

    def get_type(self) -> Type:
        """Get the type, following any bindings"""
        if self.bound_type:
            if self.bound_type.kind == TypeKind.TYPE_VAR:
                # Follow the chain
                return self.bound_type
            return self.bound_type
        return Type(TypeKind.TYPE_VAR, type_var_id=self.id)

    def bind(self, typ: Type) -> None:
        """Bind this type variable to a concrete type"""
        self.bound_type = typ


class TypeEnvironment:
    """Type environment for symbol resolution"""

    def __init__(self, parent: Optional['TypeEnvironment'] = None):
        self.parent = parent
        self.symbols: Dict[str, Type] = {}
        self.functions: Dict[str, Type] = {}
        self.structs: Dict[str, Type] = {}
        self.enums: Dict[str, Type] = {}
        self.type_vars: Dict[str, TypeVariable] = {}

    def define_variable(self, name: str, typ: Type) -> None:
        """Define a variable in this scope"""
        self.symbols[name] = typ

    def define_function(self, name: str, typ: Type) -> None:
        """Define a function in this scope"""
        self.functions[name] = typ

    def define_struct(self, name: str, typ: Type) -> None:
        """Define a struct type"""
        self.structs[name] = typ

    def define_enum(self, name: str, typ: Type) -> None:
        """Define an enum type"""
        self.enums[name] = typ

    def lookup_variable(self, name: str) -> Optional[Type]:
        """Look up a variable type"""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup_variable(name)
        return None

    def lookup_function(self, name: str) -> Optional[Type]:
        """Look up a function type"""
        if name in self.functions:
            return self.functions[name]
        if self.parent:
            return self.parent.lookup_function(name)
        return None

    def lookup_struct(self, name: str) -> Optional[Type]:
        """Look up a struct type"""
        if name in self.structs:
            return self.structs[name]
        if self.parent:
            return self.parent.lookup_struct(name)
        return None

    def lookup_enum(self, name: str) -> Optional[Type]:
        """Look up an enum type"""
        if name in self.enums:
            return self.enums[name]
        if self.parent:
            return self.parent.lookup_enum(name)
        return None

    def create_child(self) -> 'TypeEnvironment':
        """Create a child environment"""
        return TypeEnvironment(parent=self)


# Built-in type instances
PRIMITIVE_TYPES = {
    'i8': Type(TypeKind.I8, 'i8'),
    'i16': Type(TypeKind.I16, 'i16'),
    'i32': Type(TypeKind.I32, 'i32'),
    'i64': Type(TypeKind.I64, 'i64'),
    'u8': Type(TypeKind.U8, 'u8'),
    'u16': Type(TypeKind.U16, 'u16'),
    'u32': Type(TypeKind.U32, 'u32'),
    'u64': Type(TypeKind.U64, 'u64'),
    'f32': Type(TypeKind.F32, 'f32'),
    'f64': Type(TypeKind.F64, 'f64'),
    'bool': Type(TypeKind.BOOL, 'bool'),
    'char': Type(TypeKind.CHAR, 'char'),
    'string': Type(TypeKind.STRING, 'string'),
    'void': Type(TypeKind.VOID, 'void'),
    'status': Type(TypeKind.STATUS, 'status'),
    'handle': Type(TypeKind.HANDLE, 'handle'),
}


def get_primitive_type(name: str) -> Optional[Type]:
    """Get a primitive type by name"""
    return PRIMITIVE_TYPES.get(name)
