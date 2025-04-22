"""
Visitor extensions for the enhanced type system in Runa.
This module extends the base visitors to handle type nodes.
"""
from src.runa.types.nodes import (
    Type, PrimitiveType, AnyType, UnionType, ListType, DictionaryType,
    FunctionType, GenericType, ParameterizedType, TypeAlias,
    TypedDeclaration, TypedParameter, TypedProcessDefinition
)


def extend_visitor(visitor_class):
    """
    Extend a visitor class with methods for visiting type system nodes.

    Args:
        visitor_class: The visitor class to extend

    Returns:
        The extended visitor class
    """

    # Add visitor methods for type system nodes

    def visit_TypeAlias(self, node):
        """Visit a type alias."""
        self._visit_type(node.target_type)

    def visit_TypedDeclaration(self, node):
        """Visit a typed declaration."""
        self._visit_type(node.type_annotation)
        if node.value:
            node.value.accept(self)

    def visit_TypedProcessDefinition(self, node):
        """Visit a typed process definition."""
        for param in node.parameters:
            self._visit_type(param.type_annotation)
        self._visit_type(node.return_type)

        if node.generic_params:
            for param in node.generic_params:
                self._visit_type(param)

        for stmt in node.body:
            stmt.accept(self)

    def visit_TypedParameter(self, node):
        """Visit a typed parameter."""
        self._visit_type(node.type_annotation)

    def _visit_type(self, type_node):
        """Visit a type node."""
        if isinstance(type_node, (PrimitiveType, AnyType)):
            # These types have no child nodes to visit
            pass
        elif isinstance(type_node, UnionType):
            for t in type_node.types:
                self._visit_type(t)
        elif isinstance(type_node, ListType):
            self._visit_type(type_node.element_type)
        elif isinstance(type_node, DictionaryType):
            self._visit_type(type_node.key_type)
            self._visit_type(type_node.value_type)
        elif isinstance(type_node, FunctionType):
            for t in type_node.parameter_types:
                self._visit_type(t)
            self._visit_type(type_node.return_type)
        elif isinstance(type_node, GenericType):
            if type_node.constraints:
                for c in type_node.constraints:
                    self._visit_type(c)
        elif isinstance(type_node, ParameterizedType):
            if isinstance(type_node.base_type, Type):
                self._visit_type(type_node.base_type)
            for t in type_node.type_arguments:
                self._visit_type(t)

    # Add the methods to the visitor class
    visitor_class.visit_TypeAlias = visit_TypeAlias
    visitor_class.visit_TypedDeclaration = visit_TypedDeclaration
    visitor_class.visit_TypedProcessDefinition = visit_TypedProcessDefinition
    visitor_class.visit_TypedParameter = visit_TypedParameter
    visitor_class._visit_type = _visit_type

    return visitor_class