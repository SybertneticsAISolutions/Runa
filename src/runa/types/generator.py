"""
Code generation for the enhanced type system in Runa.
This module extends the Python code generator to handle type nodes.
"""
from src.runa.types.nodes import (
    Type, PrimitiveType, AnyType, UnionType, ListType, DictionaryType,
    FunctionType, GenericType, ParameterizedType, TypeAlias,
    TypedDeclaration, TypedParameter, TypedProcessDefinition
)


def extend_generator(generator_class):
    """
    Extend a code generator class with methods for generating code for type nodes.

    Args:
        generator_class: The code generator class to extend

    Returns:
        The extended code generator class
    """

    # Add generation methods for type nodes

    def visit_TypeAlias(self, node):
        """Generate code for a type alias."""
        # Python doesn't have direct type aliases, so we add a comment
        return f"# Type alias: {node.name} = {node.target_type}"

    def visit_TypedDeclaration(self, node):
        """Generate code for a typed declaration."""
        # Generate the value code
        value_code = self.generate(node.value) if node.value else "None"

        # Add a type annotation comment
        return f"{node.name} = {value_code}  # type: {node.type_annotation}"

    def visit_TypedProcessDefinition(self, node):
        """Generate code for a typed process definition."""
        # Generate parameter list
        param_list = ", ".join([param.name for param in node.parameters])

        # Add type annotation comment
        param_types = ", ".join([str(param.type_annotation) for param in node.parameters])
        return_type = str(node.return_type)
        func_def = f"def {node.name}({param_list}):  # ({param_types}) -> {return_type}"

        # Generate the function body
        body = []
        for stmt in node.body:
            stmt_code = self.generate(stmt)
            if stmt_code:
                body.append(f"    {stmt_code}")

        # If the body is empty, add a pass statement
        if not body:
            body.append("    pass")

        func_def += "\n" + "\n".join(body)

        return func_def

    def _generate_type_annotation(self, type_node):
        """Generate a Python type annotation for a type node."""
        if isinstance(type_node, PrimitiveType):
            # Map Runa primitive types to Python types
            type_map = {
                "Integer": "int",
                "Float": "float",
                "String": "str",
                "Boolean": "bool",
                "List": "list",
                "Dictionary": "dict"
            }
            return type_map.get(type_node.name, type_node.name)

        elif isinstance(type_node, AnyType):
            return "Any"

        elif isinstance(type_node, UnionType):
            # Generate a union type annotation
            types = " | ".join([self._generate_type_annotation(t) for t in type_node.types])
            return f"Union[{types}]"

        elif isinstance(type_node, ListType):
            # Generate a list type annotation
            elem_type = self._generate_type_annotation(type_node.element_type)
            return f"List[{elem_type}]"

        elif isinstance(type_node, DictionaryType):
            # Generate a dictionary type annotation
            key_type = self._generate_type_annotation(type_node.key_type)
            value_type = self._generate_type_annotation(type_node.value_type)
            return f"Dict[{key_type}, {value_type}]"

        elif isinstance(type_node, FunctionType):
            # Generate a function type annotation
            param_types = ", ".join([self._generate_type_annotation(t) for t in type_node.parameter_types])
            return_type = self._generate_type_annotation(type_node.return_type)
            return f"Callable[[{param_types}], {return_type}]"

        elif isinstance(type_node, GenericType):
            # Generate a generic type parameter
            return type_node.name

        elif isinstance(type_node, ParameterizedType):
            # Generate a parameterized type
            base_type = (self._generate_type_annotation(type_node.base_type)
                         if isinstance(type_node.base_type, Type)
                         else type_node.base_type)
            args = ", ".join([self._generate_type_annotation(t) for t in type_node.type_arguments])
            return f"{base_type}[{args}]"

        else:
            # Default case - use string representation
            return str(type_node)

    # Add the methods to the code generator class
    generator_class.visit_TypeAlias = visit_TypeAlias
    generator_class.visit_TypedDeclaration = visit_TypedDeclaration
    generator_class.visit_TypedProcessDefinition = visit_TypedProcessDefinition
    generator_class._generate_type_annotation = _generate_type_annotation

    return generator_class