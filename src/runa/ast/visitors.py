class Visitor:
    """Base visitor class for traversing AST nodes."""

    def visit_default(self, node):
        """Default visit method called for unhandled node types."""
        method_name = f"visit_{node.__class__.__name__}"
        raise NotImplementedError(
            f"No visit method {method_name} defined in {self.__class__.__name__}."
        )

    def visit_Program(self, node):
        for stmt in node.statements:
            stmt.accept(self)

    def visit_Declaration(self, node):
        if node.value:
            node.value.accept(self)

    def visit_Assignment(self, node):
        node.value.accept(self)

    def visit_IfStatement(self, node):
        node.condition.accept(self)
        for stmt in node.then_block:
            stmt.accept(self)
        if node.else_block:
            for stmt in node.else_block:
                stmt.accept(self)

    def visit_ForEachStatement(self, node):
        node.iterable.accept(self)
        for stmt in node.body:
            stmt.accept(self)

    def visit_ReturnStatement(self, node):
        if node.value:
            node.value.accept(self)

    def visit_DisplayStatement(self, node):
        node.value.accept(self)
        if node.message:
            node.message.accept(self)

    def visit_ProcessDefinition(self, node):
        for stmt in node.body:
            stmt.accept(self)

    def visit_StringLiteral(self, node):
        pass

    def visit_NumberLiteral(self, node):
        pass

    def visit_BooleanLiteral(self, node):
        pass

    def visit_VariableReference(self, node):
        pass

    def visit_BinaryOperation(self, node):
        node.left.accept(self)
        node.right.accept(self)

    def visit_FunctionCall(self, node):
        for arg in node.arguments:
            arg.accept(self)
        for arg in node.named_arguments.values():
            arg.accept(self)

    def visit_ListExpression(self, node):
        for element in node.elements:
            element.accept(self)

    def visit_DictionaryExpression(self, node):
        for entry in node.entries:
            entry.key.accept(self)
            entry.value.accept(self)

    def visit_IndexAccess(self, node):
        node.target.accept(self)
        node.index.accept(self)