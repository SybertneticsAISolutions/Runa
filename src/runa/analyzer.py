from ast.visitors import Visitor
from collections import defaultdict


class Symbol:
    """Symbol in the symbol table."""

    def __init__(self, name, symbol_type=None, value=None):
        self.name = name
        self.type = symbol_type
        self.value = value


class Scope:
    """Scope for symbol resolution."""

    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def define(self, name, symbol):
        """Define a symbol in the current scope."""
        self.symbols[name] = symbol
        return symbol

    def resolve(self, name):
        """Resolve a symbol name to its Symbol object."""
        if name in self.symbols:
            return self.symbols[name]
        elif self.parent:
            return self.parent.resolve(name)
        return None

    def is_defined_in_current_scope(self, name):
        """Check if a symbol is defined in the current scope."""
        return name in self.symbols


class SemanticAnalyzer(Visitor):
    """Performs semantic analysis on the AST."""

    def __init__(self):
        self.current_scope = Scope()
        self.errors = []
        self.warnings = []

    def analyze(self, program):
        """Analyze a program AST and return whether it is valid."""
        program.accept(self)
        return len(self.errors) == 0

    def error(self, message, position):
        """Report a semantic error."""
        self.errors.append(f"{position}: {message}")

    def warning(self, message, position):
        """Report a semantic warning."""
        self.warnings.append(f"{position}: {message}")

    def enter_scope(self):
        """Enter a new scope."""
        self.current_scope = Scope(self.current_scope)

    def exit_scope(self):
        """Exit the current scope."""
        self.current_scope = self.current_scope.parent

    def visit_Program(self, node):
        """Visit a program node."""
        for stmt in node.statements:
            stmt.accept(self)

    def visit_Declaration(self, node):
        """Visit a variable declaration."""
        # Check if the variable is already defined in the current scope
        if self.current_scope.is_defined_in_current_scope(node.name):
            self.error(f"Variable '{node.name}' is already defined in this scope", node.position)

        # Evaluate the initializer expression
        if node.value:
            node.value.accept(self)

        # Add the variable to the symbol table
        self.current_scope.define(node.name, Symbol(node.name))

    def visit_Assignment(self, node):
        """Visit a variable assignment."""
        # Check if the variable is defined
        symbol = self.current_scope.resolve(node.name)
        if not symbol:
            self.error(f"Assignment to undefined variable '{node.name}'", node.position)

        # Evaluate the value expression
        if node.value:
            node.value.accept(self)

    def visit_IfStatement(self, node):
        """Visit an if statement."""
        # Evaluate the condition
        node.condition.accept(self)

        # Enter a new scope for the then block
        self.enter_scope()
        for stmt in node.then_block:
            stmt.accept(self)
        self.exit_scope()

        # Enter a new scope for the else block if it exists
        if node.else_block:
            self.enter_scope()
            for stmt in node.else_block:
                stmt.accept(self)
            self.exit_scope()

    def visit_ForEachStatement(self, node):
        """Visit a for each statement."""
        # Evaluate the iterable expression
        node.iterable.accept(self)

        # Enter a new scope for the loop body
        self.enter_scope()

        # Define the loop variable in the new scope
        self.current_scope.define(node.variable, Symbol(node.variable))

        # Visit the loop body
        for stmt in node.body:
            stmt.accept(self)

        self.exit_scope()

    def visit_ReturnStatement(self, node):
        """Visit a return statement."""
        # Evaluate the return value if it exists
        if node.value:
            node.value.accept(self)

    def visit_DisplayStatement(self, node):
        """Visit a display statement."""
        # Evaluate the value to display
        node.value.accept(self)

        # Evaluate the message if it exists
        if node.message:
            node.message.accept(self)

    def visit_ProcessDefinition(self, node):
        """Visit a process (function) definition."""
        # Define the process in the current scope
        self.current_scope.define(node.name, Symbol(node.name, "process"))

        # Enter a new scope for the process body
        self.enter_scope()

        # Define parameters in the new scope
        for param in node.parameters:
            self.current_scope.define(param.name, Symbol(param.name))

        # Visit the process body
        for stmt in node.body:
            stmt.accept(self)

        self.exit_scope()

    def visit_StringLiteral(self, node):
        """Visit a string literal."""
        # Nothing to analyze for a literal
        pass

    def visit_NumberLiteral(self, node):
        """Visit a number literal."""
        # Nothing to analyze for a literal
        pass

    def visit_BooleanLiteral(self, node):
        """Visit a boolean literal."""
        # Nothing to analyze for a literal
        pass

    def visit_VariableReference(self, node):
        """Visit a variable reference."""
        # Check if the variable is defined
        symbol = self.current_scope.resolve(node.name)
        if not symbol:
            self.error(f"Reference to undefined variable '{node.name}'", node.position)

    def visit_BinaryOperation(self, node):
        """Visit a binary operation."""
        # Evaluate the left and right operands
        node.left.accept(self)
        node.right.accept(self)

        # Type checking could be added here in a more sophisticated analyzer

    def visit_FunctionCall(self, node):
        """Visit a function call."""
        # Check if the function is defined
        symbol = self.current_scope.resolve(node.name)
        if not symbol:
            if node.name not in ["format_string", "format_message"]:  # Built-in functions
                self.error(f"Call to undefined function '{node.name}'", node.position)

        # Evaluate all arguments
        for arg in node.arguments:
            arg.accept(self)

        for arg in node.named_arguments.values():
            arg.accept(self)

    def visit_ListExpression(self, node):
        """Visit a list expression."""
        # Evaluate all list elements
        for element in node.elements:
            element.accept(self)

    def visit_DictionaryExpression(self, node):
        """Visit a dictionary expression."""
        # Evaluate all dictionary keys and values
        for entry in node.entries:
            entry.key.accept(self)
            entry.value.accept(self)

    def visit_IndexAccess(self, node):
        """Visit an index access expression."""
        # Evaluate the target and the index
        node.target.accept(self)
        node.index.accept(self)