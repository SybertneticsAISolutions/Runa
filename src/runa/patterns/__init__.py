"""
Pattern matching system for Runa.
This module provides pattern matching capabilities for the Runa programming language.
"""
from src.runa.patterns.nodes import (
    WildcardPattern, LiteralPattern, VariablePattern,
    ListPattern, DictionaryPattern, RestPattern, TypePattern,
    MatchCase, MatchExpression
)
from src.runa.patterns.parser import extend_parser
from src.runa.patterns.visitors import extend_visitor
from src.runa.patterns.generator import extend_generator
from src.runa.patterns.matcher import match_pattern, MatchResult


def integrate_pattern_matching(parser_class, visitor_class, generator_class):
    """
    Integrate pattern matching into the Runa language.

    Args:
        parser_class: The parser class to extend
        visitor_class: The visitor class to extend
        generator_class: The code generator class to extend

    Returns:
        A tuple of the extended classes (parser_class, visitor_class, generator_class)
    """
    # Extend the parser with pattern matching grammar
    extended_parser = extend_parser(parser_class)

    # Extend visitors with pattern matching node handlers
    extended_visitor = extend_visitor(visitor_class)

    # Extend code generator with pattern matching code generation
    extended_generator = extend_generator(generator_class)

    return extended_parser, extended_visitor, extended_generator


# Export matcher functionality for runtime
__all__ = [
    'WildcardPattern', 'LiteralPattern', 'VariablePattern',
    'ListPattern', 'DictionaryPattern', 'RestPattern', 'TypePattern',
    'MatchCase', 'MatchExpression',
    'match_pattern', 'MatchResult',
    'integrate_pattern_matching'
]