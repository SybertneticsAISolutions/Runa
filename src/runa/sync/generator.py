"""
Code generation for asynchronous programming in Runa.
This module extends the Python code generator to handle async nodes.
"""
from nodes import AsyncProcessDefinition, AwaitExpression, AsyncForEachStatement


def extend_generator(generator_class):
    """
    Extend a code generator class with methods for generating code for async nodes.

    Args:
        generator_class: The code generator class to extend

    Returns:
        The extended code generator class
    """

    # Add generation methods for async nodes

    def visit_AsyncProcessDefinition(self, node):
        """Generate code for an async process definition."""
        # Create the function signature
        param_list = ", ".join([param.name for param in node.parameters])
        func_def = f"async def {node.name}({param_list}):"

        # Generate the function body
        body = []
        for stmt in node.body:
            stmt_code = self.generate(stmt)
            if stmt_code:
                body.append(f"    {stmt_code}")

        # If the body is empty, add a pass statement
        if not body:
            body.append("    pass")

        func_def += "\n" + "\n".join(body)

        return func_def

    def visit_AwaitExpression(self, node):
        """Generate code for an await expression."""
        value_code = self.generate(node.value)
        return f"await {value_code}"

    def visit_AsyncForEachStatement(self, node):
        """Generate code for an async for-each statement."""
        iterable_code = self.generate(node.iterable)

        # Generate the async for loop
        for_code = f"async for {node.variable} in {iterable_code}:"
        body = []
        for stmt in node.body:
            stmt_code = self.generate(stmt)
            if stmt_code:
                body.append(f"    {stmt_code}")

        for_code += "\n" + "\n".join(body)

        return for_code

    # Add the methods to the code generator class
    generator_class.visit_AsyncProcessDefinition = visit_AsyncProcessDefinition
    generator_class.visit_AwaitExpression = visit_AwaitExpression
    generator_class.visit_AsyncForEachStatement = visit_AsyncForEachStatement

    return generator_class