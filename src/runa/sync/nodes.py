"""
Node definitions for asynchronous programming in Runa.
"""
from src.runa.ast.nodes import Node, Statement, Expression, Position


class AsyncProcessDefinition(Statement):
    """Asynchronous process (function) definition."""

    def __init__(self, name, parameters, body, position=None):
        super().__init__(position)
        self.name = name
        self.parameters = parameters
        self.body = body


class AwaitExpression(Expression):
    """Await expression for asynchronous operations."""

    def __init__(self, value, position=None):
        super().__init__(position)
        self.value = value


class AsyncForEachStatement(Statement):
    """Asynchronous for-each loop statement."""

    def __init__(self, variable, iterable, body, position=None):
        super().__init__(position)
        self.variable = variable
        self.iterable = iterable
        self.body = body