"""
Context-aware interpretation for the Runa programming language.

This module provides semantic understanding capabilities for improving
code parsing and interpretation based on context.
"""

from src.runa.context.embeddings import get_embedding, get_similarity
from src.runa.context.disambiguator import Disambiguator
from src.runa.context.learner import PrecedentLearner


def integrate_context_awareness(parser_class):
    """
    Integrate context-aware interpretation into a parser class.

    Args:
        parser_class: The parser class to extend

    Returns:
        The extended parser class
    """
    from src.runa.context.parser import extend_parser
    return extend_parser(parser_class)