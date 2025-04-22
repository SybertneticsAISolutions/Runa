"""
Node definitions for pattern matching in Runa.
"""
from src.runa.ast.nodes import Node, Expression, Statement, Position


class Pattern(Node):
    """Base class for all pattern nodes."""
    pass


class WildcardPattern(Pattern):
    """Wildcard pattern that matches anything (_)."""

    def __init__(self, position=None):
        super().__init__(position)


class LiteralPattern(Pattern):
    """Pattern that matches a literal value."""

    def __init__(self, value, position=None):
        super().__init__(position)
        self.value = value


class VariablePattern(Pattern):
    """Pattern that binds a value to a variable."""

    def __init__(self, name, position=None):
        super().__init__(position)
        self.name = name


class ListPattern(Pattern):
    """Pattern that matches and destructures a list."""

    def __init__(self, elements, position=None):
        super().__init__(position)
        self.elements = elements  # List of patterns


class DictionaryPattern(Pattern):
    """Pattern that matches and destructures a dictionary."""

    def __init__(self, entries, position=None):
        super().__init__(position)
        self.entries = entries  # Dictionary of key patterns to value patterns


class RestPattern(Pattern):
    """Pattern that captures the rest of a sequence (...)."""

    def __init__(self, name=None, position=None):
        super().__init__(position)
        self.name = name  # Optional name to bind the rest to


class TypePattern(Pattern):
    """Pattern that matches a value of a specific type."""

    def __init__(self, type_name, position=None):
        super().__init__(position)
        self.type_name = type_name


class MatchCase(Node):
    """A single case in a match expression."""

    def __init__(self, pattern, body, position=None):
        super().__init__(position)
        self.pattern = pattern
        self.body = body


class MatchExpression(Statement, Expression):
    """Match expression for pattern matching."""

    def __init__(self, value, cases, position=None):
        super().__init__(position)
        self.value = value
        self.cases = cases  # List of MatchCase objects