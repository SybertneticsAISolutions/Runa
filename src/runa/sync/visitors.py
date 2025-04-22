"""
Visitor extensions for asynchronous programming in Runa.
This module extends the base visitors to handle async nodes.
"""
from nodes import AsyncProcessDefinition, AwaitExpression, AsyncForEachStatement


def extend_visitor(visitor_class):
    """
    Extend a visitor class with methods for visiting async nodes.

    Args:
        visitor_class: The visitor class to extend

    Returns:
        The extended visitor class
    """

    # Add visitor methods for async nodes

    def visit_AsyncProcessDefinition(self, node):
        """Visit an async process definition."""
        for stmt in node.body:
            stmt.accept(self)

    def visit_AwaitExpression(self, node):
        """Visit an await expression."""
        node.value.accept(self)

    def visit_AsyncForEachStatement(self, node):
        """Visit an async for-each statement."""
        node.iterable.accept(self)
        for stmt in node.body:
            stmt.accept(self)

    # Add the methods to the visitor class
    visitor_class.visit_AsyncProcessDefinition = visit_AsyncProcessDefinition
    visitor_class.visit_AwaitExpression = visit_AwaitExpression
    visitor_class.visit_AsyncForEachStatement = visit_AsyncForEachStatement

    return visitor_class