"""
Pattern matching runtime implementation for Runa.
This module provides the functionality to match values against patterns.
"""
from src.runa.patterns.nodes import (
    WildcardPattern, LiteralPattern, VariablePattern,
    ListPattern, DictionaryPattern, RestPattern, TypePattern
)


class MatchResult:
    """Result of a pattern match."""

    def __init__(self, success, bindings=None):
        self.success = success
        self.bindings = bindings or {}

    def __bool__(self):
        return self.success

    def merge(self, other):
        """Merge with another match result."""
        if not self.success or not other.success:
            return MatchResult(False)

        # Check for conflicting bindings
        for name, value in other.bindings.items():
            if name in self.bindings and self.bindings[name] != value:
                return MatchResult(False)

        # Merge bindings
        bindings = dict(self.bindings)
        bindings.update(other.bindings)
        return MatchResult(True, bindings)


def match_pattern(pattern, value, type_registry=None):
    """
    Match a value against a pattern.

    Args:
        pattern: The pattern to match against
        value: The value to match
        type_registry: A registry of type names to type checking functions

    Returns:
        A MatchResult indicating success and any bindings created
    """
    type_registry = type_registry or {}

    if isinstance(pattern, WildcardPattern):
        # Wildcard always matches
        return MatchResult(True)

    elif isinstance(pattern, LiteralPattern):
        # Literal matches if values are equal
        pattern_value = pattern.value.value  # Unwrap from AST node
        return MatchResult(value == pattern_value)

    elif isinstance(pattern, VariablePattern):
        # Variable pattern always matches and binds the value
        return MatchResult(True, {pattern.name: value})

    elif isinstance(pattern, ListPattern):
        return match_list_pattern(pattern, value)

    elif isinstance(pattern, DictionaryPattern):
        return match_dictionary_pattern(pattern, value)

    elif isinstance(pattern, RestPattern):
        # Rest pattern always matches
        if pattern.name:
            return MatchResult(True, {pattern.name: value})
        return MatchResult(True)

    elif isinstance(pattern, TypePattern):
        # Type pattern matches if value is of the specified type
        type_check = type_registry.get(pattern.type_name)
        if type_check and type_check(value):
            return MatchResult(True)
        return MatchResult(False)

    # Unknown pattern type
    return MatchResult(False)


def match_list_pattern(pattern, value):
    """Match a list pattern against a value."""
    # Check if value is a list-like object
    if not isinstance(value, (list, tuple)):
        return MatchResult(False)

    elements = pattern.elements

    # Handle empty list pattern
    if not elements:
        return MatchResult(len(value) == 0)

    # Check for rest pattern
    rest_index = None
    for i, elem in enumerate(elements):
        if isinstance(elem, RestPattern):
            rest_index = i
            break

    if rest_index is not None:
        # Handle pattern with rest
        before_rest = elements[:rest_index]
        after_rest = elements[rest_index + 1:]

        # Check if there are enough elements
        if len(value) < len(before_rest) + len(after_rest):
            return MatchResult(False)

        # Match elements before rest
        result = MatchResult(True)
        for i, elem in enumerate(before_rest):
            elem_result = match_pattern(elem, value[i])
            result = result.merge(elem_result)
            if not result.success:
                return result

        # Match elements after rest
        for i, elem in enumerate(after_rest):
            value_index = len(value) - len(after_rest) + i
            elem_result = match_pattern(elem, value[value_index])
            result = result.merge(elem_result)
            if not result.success:
                return result

        # Bind the rest if named
        rest_pattern = elements[rest_index]
        if rest_pattern.name:
            rest_value = value[len(before_rest):len(value) - len(after_rest)]
            rest_result = MatchResult(True, {rest_pattern.name: rest_value})
            result = result.merge(rest_result)

        return result
    else:
        # Handle pattern without rest
        if len(value) != len(elements):
            return MatchResult(False)

        # Match each element
        result = MatchResult(True)
        for i, elem in enumerate(elements):
            elem_result = match_pattern(elem, value[i])
            result = result.merge(elem_result)
            if not result.success:
                return result

        return result


def match_dictionary_pattern(pattern, value):
    """Match a dictionary pattern against a value."""
    # Check if value is a dict-like object
    if not isinstance(value, dict):
        return MatchResult(False)

    entries = pattern.entries

    # Handle empty dictionary pattern
    if not entries:
        return MatchResult(len(value) == 0)

    # Match each entry
    result = MatchResult(True)
    for entry in entries:
        key = entry.key.value  # Unwrap from AST node
        if key in value:
            entry_result = match_pattern(entry.value, value[key])
            result = result.merge(entry_result)
            if not result.success:
                return result
        else:
            return MatchResult(False)

    return result