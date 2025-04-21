class Position:
    """Source code position for error reporting and debugging."""

    def __init__(self, line=0, column=0, file="<unknown>"):
        self.line = line
        self.column = column
        self.file = file

    def __str__(self):
        return f"{self.file}:{self.line}:{self.column}"


class Node:
    """Base class for all AST nodes."""

    def __init__(self, position=None):
        self.position = position or Position()

    def accept(self, visitor):
        """Accept a visitor to process this node."""
        method_name = f"visit_{self.__class__.__name__}"
        visitor_method = getattr(visitor, method_name, visitor.visit_default)
        return visitor_method(self)


class Program(Node):
    """Root node of a Runa program."""

    def __init__(self, statements, position=None):
        super().__init__(position)
        self.statements = statements


class Statement(Node):
    """Base class for all statement nodes."""
    pass


class Expression(Node):
    """Base class for all expression nodes."""
    pass


class Declaration(Statement):
    """Variable declaration statement."""

    def __init__(self, name, value, position=None):
        super().__init__(position)
        self.name = name
        self.value = value


class Assignment(Statement):
    """Variable assignment statement."""

    def __init__(self, name, value, position=None):
        super().__init__(position)
        self.name = name
        self.value = value


class IfStatement(Statement):
    """If statement."""

    def __init__(self, condition, then_block, else_block=None, position=None):
        super().__init__(position)
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block


class ForEachStatement(Statement):
    """For each loop statement."""

    def __init__(self, variable, iterable, body, position=None):
        super().__init__(position)
        self.variable = variable
        self.iterable = iterable
        self.body = body


class ReturnStatement(Statement):
    """Return statement."""

    def __init__(self, value=None, position=None):
        super().__init__(position)
        self.value = value


class DisplayStatement(Statement):
    """Display (print) statement."""

    def __init__(self, value, message=None, position=None):
        super().__init__(position)
        self.value = value
        self.message = message


class ProcessDefinition(Statement):
    """Function/Process definition."""

    def __init__(self, name, parameters, body, position=None):
        super().__init__(position)
        self.name = name
        self.parameters = parameters
        self.body = body


class Parameter:
    """Function parameter."""

    def __init__(self, name, position=None):
        self.name = name
        self.position = position or Position()


class Literal(Expression):
    """Base class for literal values."""
    pass


class StringLiteral(Literal):
    """String literal."""

    def __init__(self, value, position=None):
        super().__init__(position)
        self.value = value


class NumberLiteral(Literal):
    """Number literal."""

    def __init__(self, value, position=None):
        super().__init__(position)
        self.value = value


class BooleanLiteral(Literal):
    """Boolean literal."""

    def __init__(self, value, position=None):
        super().__init__(position)
        self.value = value


class VariableReference(Expression):
    """Variable reference expression."""

    def __init__(self, name, position=None):
        super().__init__(position)
        self.name = name


class BinaryOperation(Expression):
    """Binary operation expression."""

    def __init__(self, left, operator, right, position=None):
        super().__init__(position)
        self.left = left
        self.operator = operator
        self.right = right


class FunctionCall(Expression):
    """Function call expression."""

    def __init__(self, name, arguments=None, named_arguments=None, position=None):
        super().__init__(position)
        self.name = name
        self.arguments = arguments or []
        self.named_arguments = named_arguments or {}


class ListExpression(Expression):
    """List expression."""

    def __init__(self, elements, position=None):
        super().__init__(position)
        self.elements = elements


class DictionaryExpression(Expression):
    """Dictionary expression."""

    def __init__(self, entries, position=None):
        super().__init__(position)
        self.entries = entries


class DictionaryEntry:
    """Entry in a dictionary expression."""

    def __init__(self, key, value, position=None):
        self.key = key
        self.value = value
        self.position = position or Position()


class IndexAccess(Expression):
    """Index access expression (for lists and dictionaries)."""

    def __init__(self, target, index, position=None):
        super().__init__(position)
        self.target = target
        self.index = index