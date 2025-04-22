"""
Visitor extensions for functional programming in Runa.
This module extends the base visitors to handle functional programming nodes.
"""
from src.runa.functional.nodes import (
    LambdaExpression, PipelineExpression, PartialApplicationExpression,
    CompositionExpression, MapExpression, FilterExpression, ReduceExpression
)


def extend_visitor(visitor_class):
    """
    Extend a visitor class with methods for visiting functional programming nodes.

    Args:
        visitor_class: The visitor class to extend

    Returns:
        The extended visitor class
    """

    # Add visitor methods for functional programming nodes

    def visit_LambdaExpression(self, node):
        """Visit a lambda expression."""
        node.body.accept(self)

    def visit_PipelineExpression(self, node):
        """Visit a pipeline expression."""
        node.left.accept(self)
        node.right.accept(self)

    def visit_PartialApplicationExpression(self, node):
        """Visit a partial application expression."""
        node.function.accept(self)
        for arg in node.args:
            arg.accept(self)
        for value in node.kwargs.values():
            value.accept(self)

    def visit_CompositionExpression(self, node):
        """Visit a function composition expression."""
        for func in node.functions:
            func.accept(self)

    def visit_MapExpression(self, node):
        """Visit a map expression."""
        node.function.accept(self)
        node.collection.accept(self)

    def visit_FilterExpression(self, node):
        """Visit a filter expression."""
        node.predicate.accept(self)
        node.collection.accept(self)

    def visit_ReduceExpression(self, node):
        """Visit a reduce expression."""
        node.function.accept(self)
        node.collection.accept(self)
        if node.initial:
            node.initial.accept(self)

    # Add the methods to the visitor class
    visitor_class.visit_LambdaExpression = visit_LambdaExpression
    visitor_class.visit_PipelineExpression = visit_PipelineExpression
    visitor_class.visit_PartialApplicationExpression = visit_PartialApplicationExpression
    visitor_class.visit_CompositionExpression = visit_CompositionExpression
    visitor_class.visit_MapExpression = visit_MapExpression
    visitor_class.visit_FilterExpression = visit_FilterExpression
    visitor_class.visit_ReduceExpression = visit_ReduceExpression

    return visitor_class