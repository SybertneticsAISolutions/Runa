"""
Visitor extensions for pattern matching in Runa.
This module extends the base visitors to handle pattern matching nodes.
"""
from src.runa.patterns.nodes import (
    WildcardPattern, LiteralPattern, VariablePattern,
    ListPattern, DictionaryPattern, RestPattern, TypePattern,
    MatchCase, MatchExpression
)


def extend_visitor(visitor_class):
    """
    Extend a visitor class with methods for visiting pattern matching nodes.

    Args:
        visitor_class: The visitor class to extend

    Returns:
        The extended visitor class
    """

    # Add visitor methods for pattern matching nodes

    def visit_MatchExpression(self, node):
        """Visit a match expression."""
        node.value.accept(self)
        for case in node.cases:
            case.accept(self)

    def visit_MatchCase(self, node):
        """Visit a match case."""
        visit_pattern(self, node.pattern)
        for stmt in node.body:
            stmt.accept(self)

    # Helper function for visiting patterns
    def visit_pattern(self, pattern):
        """Visit a pattern node."""
        if isinstance(pattern, (WildcardPattern, VariablePattern, TypePattern)):
            # These patterns have no child nodes to visit
            pass
        elif isinstance(pattern, LiteralPattern):
            # Visit the literal value
            pattern.value.accept(self)
        elif isinstance(pattern, ListPattern):
            # Visit each element pattern
            for elem in pattern.elements:
                visit_pattern(self, elem)
        elif isinstance(pattern, DictionaryPattern):
            # Visit each key and value pattern
            for entry in pattern.entries:
                entry.key.accept(self)
                visit_pattern(self, entry.value)
        elif isinstance(pattern, RestPattern):
            # Rest pattern has no child nodes to visit
            pass

    # Add the methods to the visitor class
    visitor_class.visit_MatchExpression = visit_MatchExpression
    visitor_class.visit_MatchCase = visit_MatchCase
    visitor_class._visit_pattern = visit_pattern

    return visitor_class