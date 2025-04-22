"""
Node definitions for functional programming in Runa.
"""
from src.runa.ast.nodes import Node, Expression, Statement, Position


class LambdaExpression(Expression):
    """Lambda expression for anonymous functions."""

    def __init__(self, parameters, body, position=None):
        super().__init__(position)
        self.parameters = parameters  # List of parameter names
        self.body = body  # Expression that forms the body


class PipelineExpression(Expression):
    """Pipeline expression using the |> operator."""

    def __init__(self, left, right, position=None):
        super().__init__(position)
        self.left = left  # Left expression
        self.right = right  # Right expression (function or lambda)


class PartialApplicationExpression(Expression):
    """Partial application of a function."""

    def __init__(self, function, args, kwargs, position=None):
        super().__init__(position)
        self.function = function  # Function name or expression
        self.args = args or []  # Positional arguments
        self.kwargs = kwargs or {}  # Keyword arguments


class CompositionExpression(Expression):
    """Function composition using the compose operator."""

    def __init__(self, functions, position=None):
        super().__init__(position)
        self.functions = functions  # List of functions to compose (right to left)


class MapExpression(Expression):
    """Map a function over a collection."""

    def __init__(self, function, collection, position=None):
        super().__init__(position)
        self.function = function  # Function to apply
        self.collection = collection  # Collection to map over


class FilterExpression(Expression):
    """Filter a collection using a predicate function."""

    def __init__(self, predicate, collection, position=None):
        super().__init__(position)
        self.predicate = predicate  # Predicate function
        self.collection = collection  # Collection to filter


class ReduceExpression(Expression):
    """Reduce a collection using a function."""

    def __init__(self, function, collection, initial=None, position=None):
        super().__init__(position)
        self.function = function  # Reducer function
        self.collection = collection  # Collection to reduce
        self.initial = initial  # Optional initial value