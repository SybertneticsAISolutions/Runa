"""
Functional programming support for Runa.
This module provides functional programming capabilities for the Runa programming language.
"""
from nodes import (
    LambdaExpression, PipelineExpression, PartialApplicationExpression,
    CompositionExpression, MapExpression, FilterExpression, ReduceExpression
)
from parser import extend_parser
from visitors import extend_visitor
from generator import extend_generator
from operations import (
    pipeline, partial, compose, map_function, filter_function, reduce_function
)


def integrate_functional_programming(parser_class, visitor_class, generator_class):
    """
    Integrate functional programming into the Runa language.

    Args:
        parser_class: The parser class to extend
        visitor_class: The visitor class to extend
        generator_class: The code generator class to extend

    Returns:
        A tuple of the extended classes (parser_class, visitor_class, generator_class)
    """
    # Extend the parser with functional programming grammar
    extended_parser = extend_parser(parser_class)

    # Extend visitors with functional programming node handlers
    extended_visitor = extend_visitor(visitor_class)

    # Extend code generator with functional programming code generation
    extended_generator = extend_generator(generator_class)

    return extended_parser, extended_visitor, extended_generator


# Export runtime functions for Runa programs
__all__ = [
    'LambdaExpression', 'PipelineExpression', 'PartialApplicationExpression',
    'CompositionExpression', 'MapExpression', 'FilterExpression', 'ReduceExpression',
    'pipeline', 'partial', 'compose', 'map_function', 'filter_function', 'reduce_function',
    'integrate_functional_programming'
]