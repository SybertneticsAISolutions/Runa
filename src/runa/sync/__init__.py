"""
Asynchronous programming support for Runa.
This module provides async/await capabilities for the Runa programming language.
"""
from nodes import AsyncProcessDefinition, AwaitExpression, AsyncForEachStatement
from parser import extend_parser
from visitors import extend_visitor
from generator import extend_generator
from runtime import run_async, async_map, async_filter, async_reduce


def integrate_async_support(parser_class, visitor_class, generator_class):
    """
    Integrate asynchronous programming support into the Runa language.

    Args:
        parser_class: The parser class to extend
        visitor_class: The visitor class to extend
        generator_class: The code generator class to extend

    Returns:
        A tuple of the extended classes (parser_class, visitor_class, generator_class)
    """
    # Extend the parser with async grammar
    extended_parser = extend_parser(parser_class)

    # Extend visitors with async node handlers
    extended_visitor = extend_visitor(visitor_class)

    # Extend code generator with async code generation
    extended_generator = extend_generator(generator_class)

    return extended_parser, extended_visitor, extended_generator


# Export runtime functions for Runa programs
__all__ = [
    'AsyncProcessDefinition', 'AwaitExpression', 'AsyncForEachStatement',
    'run_async', 'async_map', 'async_filter', 'async_reduce',
    'integrate_async_support'
]