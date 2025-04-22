"""
Node definitions for the enhanced type system in Runa.
"""
from src.runa.ast.nodes import Node, Expression, Statement, Position


class Type(Node):
    """Base class for all type nodes."""
    pass


class PrimitiveType(Type):
    """Primitive type like Integer, String, Boolean, etc."""

    def __init__(self, name, position=None):
        super().__init__(position)
        self.name = name

    def __str__(self):
        return self.name


class AnyType(Type):
    """Represents the 'Any' type that can be any type."""

    def __init__(self, position=None):
        super().__init__(position)

    def __str__(self):
        return "Any"


class UnionType(Type):
    """Represents a union of types (T1 | T2 | ...)."""

    def __init__(self, types, position=None):
        super().__init__(position)
        self.types = types  # List of Type nodes

    def __str__(self):
        return " | ".join(str(t) for t in self.types)


class ListType(Type):
    """Represents a list type with element type."""

    def __init__(self, element_type, position=None):
        super().__init__(position)
        self.element_type = element_type  # Type node

    def __str__(self):
        return f"List[{self.element_type}]"


class DictionaryType(Type):
    """Represents a dictionary type with key and value types."""

    def __init__(self, key_type, value_type, position=None):
        super().__init__(position)
        self.key_type = key_type  # Type node
        self.value_type = value_type  # Type node

    def __str__(self):
        return f"Dictionary[{self.key_type}, {self.value_type}]"


class FunctionType(Type):
    """Represents a function type with parameter and return types."""

    def __init__(self, parameter_types, return_type, position=None):
        super().__init__(position)
        self.parameter_types = parameter_types  # List of Type nodes
        self.return_type = return_type  # Type node

    def __str__(self):
        params = ", ".join(str(t) for t in self.parameter_types)
        return f"({params}) -> {self.return_type}"


class GenericType(Type):
    """Represents a generic type parameter."""

    def __init__(self, name, constraints=None, position=None):
        super().__init__(position)
        self.name = name
        self.constraints = constraints or []  # List of Type nodes (constraints)

    def __str__(self):
        if self.constraints:
            constraints = " & ".join(str(c) for c in self.constraints)
            return f"{self.name}: {constraints}"
        return self.name


class ParameterizedType(Type):
    """Represents a type with generic parameters."""

    def __init__(self, base_type, type_arguments, position=None):
        super().__init__(position)
        self.base_type = base_type  # Type node or string
        self.type_arguments = type_arguments  # List of Type nodes

    def __str__(self):
        args = ", ".join(str(t) for t in self.type_arguments)
        return f"{self.base_type}[{args}]"


class TypeAlias(Statement):
    """Defines a type alias."""

    def __init__(self, name, target_type, position=None):
        super().__init__(position)
        self.name = name
        self.target_type = target_type  # Type node

    def __str__(self):
        return f"Type {self.name} is {self.target_type}"


class TypedDeclaration(Statement):
    """Variable declaration with explicit type annotation."""

    def __init__(self, name, type_annotation, value, position=None):
        super().__init__(position)
        self.name = name
        self.type_annotation = type_annotation  # Type node
        self.value = value  # Expression node

    def __str__(self):
        return f"Let {self.name} ({self.type_annotation}) be {self.value}"


class TypedParameter(Node):
    """Function parameter with type annotation."""

    def __init__(self, name, type_annotation, position=None):
        super().__init__(position)
        self.name = name
        self.type_annotation = type_annotation  # Type node

    def __str__(self):
        return f"{self.name} ({self.type_annotation})"


class TypedProcessDefinition(Statement):
    """Process (function) definition with type annotations."""

    def __init__(self, name, parameters, return_type, body, generic_params=None, position=None):
        super().__init__(position)
        self.name = name
        self.parameters = parameters  # List of TypedParameter nodes
        self.return_type = return_type  # Type node
        self.body = body  # List of Statement nodes
        self.generic_params = generic_params or []  # List of GenericType nodes

    def __str__(self):
        generics = ""
        if self.generic_params:
            params = ", ".join(str(p) for p in self.generic_params)
            generics = f"[{params}]"

        params = ", ".join(str(p) for p in self.parameters)
        return f"Process{generics} called \"{self.name}\" that takes {params} returns ({self.return_type}): ..."