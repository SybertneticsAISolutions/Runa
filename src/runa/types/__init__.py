"""
Enhanced type system for Runa.
This module provides type annotations, inference, and checking capabilities.
"""
from nodes import (
    Type, PrimitiveType, AnyType, UnionType, ListType, DictionaryType,
    FunctionType, GenericType, ParameterizedType, TypeAlias,
    TypedDeclaration, TypedParameter, TypedProcessDefinition
)
from parser import extend_parser
from inference import TypeInferer, TypeEnvironment
from checker import TypeChecker, TypeError


def integrate_type_system(parser_class, visitor_class, generator_class):
    """
    Integrate the enhanced type system into the Runa language.

    Args:
        parser_class: The parser class to extend
        visitor_class: The visitor class to extend
        generator_class: The code generator class to extend

    Returns:
        A tuple of the extended classes (parser_class, visitor_class, generator_class)
    """
    # Extend the parser with type system grammar
    extended_parser = extend_parser(parser_class)

    # The visitor and generator don't need special extensions for types
    # They can handle the AST nodes directly

    return extended_parser, visitor_class, generator_class


# Export type system classes and functions
__all__ = [
    'Type', 'PrimitiveType', 'AnyType', 'UnionType', 'ListType', 'DictionaryType',
    'FunctionType', 'GenericType', 'ParameterizedType', 'TypeAlias',
    'TypedDeclaration', 'TypedParameter', 'TypedProcessDefinition',
    'TypeInferer', 'TypeEnvironment', 'TypeChecker', 'TypeError',
    'integrate_type_system'
]