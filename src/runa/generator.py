from ast.visitors import Visitor
import ast as py_ast
import astor


class PyCodeGenerator(Visitor):
    """Generates Python code from a Runa AST."""

    def __init__(self):
        self.current_indent = 0
        self.output = []

    def generate(self, node):
        """Generate Python code for an AST node."""
        result = node.accept(self)
        return result

    def visit_Program(self, node):
        """Visit a program node."""
        # Add runtime imports
        self.output.append("# Generated Python code from Runa")
        self.output.append("from runa.runtime import *")
        self.output.append("")

        # Generate code for all statements
        for stmt in node.statements:
            stmt_code = self.generate(stmt)
            if stmt_code:
                self.output.append(stmt_code)

        return "\n".join(self.output)

    def visit_Declaration(self, node):
        """Visit a variable declaration."""
        value_code = self.generate(node.value) if node.value else "None"
        return f"{node.name} = {value_code}"

    def visit_Assignment(self, node):
        """Visit a variable assignment."""
        value_code = self.generate(node.value)
        return f"{node.name} = {value_code}"

    def visit_IfStatement(self, node):
        """Visit an if statement."""
        condition_code = self.generate(node.condition)

        # Generate the if block
        if_code = f"if {condition_code}:"
        then_block = []
        for stmt in node.then_block:
            stmt_code = self.generate(stmt)
            if stmt_code:
                then_block.append(f"    {stmt_code}")

        if_code += "\n" + "\n".join(then_block)

        # Generate the else block if it exists
        if node.else_block:
            if_code += "\nelse:"
            else_block = []
            for stmt in node.else_block:
                stmt_code = self.generate(stmt)
                if stmt_code:
                    else_block.append(f"    {stmt_code}")

            if_code += "\n" + "\n".join(else_block)

        return if_code

    def visit_ForEachStatement(self, node):
        """Visit a for each statement."""
        iterable_code = self.generate(node.iterable)

        # Generate the for loop
        for_code = f"for {node.variable} in {iterable_code}:"
        body = []
        for stmt in node.body:
            stmt_code = self.generate(stmt)
            if stmt_code:
                body.append(f"    {stmt_code}")

        for_code += "\n" + "\n".join(body)

        return for_code

    def visit_ReturnStatement(self, node):
        """Visit a return statement."""
        if node.value:
            value_code = self.generate(node.value)
            return f"return {value_code}"
        else:
            return "return"

    def visit_DisplayStatement(self, node):
        """Visit a display statement."""
        value_code = self.generate(node.value)

        if node.message:
            message_code = self.generate(node.message)
            return f"print({value_code}, {message_code})"
        else:
            return f"print({value_code})"

    def visit_ProcessDefinition(self, node):
        """Visit a process (function) definition."""
        # Create the function signature
        param_list = ", ".join([param.name for param in node.parameters])
        func_def = f"def {node.name}({param_list}):"

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

    def visit_StringLiteral(self, node):
        """Visit a string literal."""
        # Escape quotes if needed
        escaped_value = node.value.replace('"', '\\"')
        return f'"{escaped_value}"'

    def visit_NumberLiteral(self, node):
        """Visit a number literal."""
        return str(node.value)

    def visit_BooleanLiteral(self, node):
        """Visit a boolean literal."""
        return str(node.value)

    def visit_VariableReference(self, node):
        """Visit a variable reference."""
        return node.name

    def visit_BinaryOperation(self, node):
        """Visit a binary operation."""
        left_code = self.generate(node.left)
        right_code = self.generate(node.right)

        # Map Runa operators to Python operators
        operator_map = {
            "PLUS": "+",
            "MINUS": "-",
            "MULTIPLIED": "*",
            "DIVIDED": "/",
            "MODULO": "%",
            "GREATER": ">",
            "LESS": "<",
            "EQUAL": "==",
            "NOT_EQUAL": "!=",
            "AND": "and",
            "OR": "or"
        }

        op = operator_map.get(node.operator, node.operator)

        return f"({left_code} {op} {right_code})"

    def visit_FunctionCall(self, node):
        """Visit a function call."""
        # Handle built-in format_string and format_message functions
        if node.name in ["format_string", "format_message"]:
            if node.arguments:
                string_code = self.generate(node.arguments[0])
                format_args = ", ".join([f"{k}={self.generate(v)}" for k, v in node.named_arguments.items()])
                return f"{string_code}.format({format_args})"
            else:
                format_args = ", ".join([f"{k}={self.generate(v)}" for k, v in node.named_arguments.items()])
                return f"format_string({format_args})"

        # Regular function call
        arg_list = []

        # Add positional arguments
        for arg in node.arguments:
            arg_list.append(self.generate(arg))

        # Add named arguments
        for name, value in node.named_arguments.items():
            arg_list.append(f"{name}={self.generate(value)}")

        # Join all arguments
        all_args = ", ".join(arg_list)

        return f"{node.name}({all_args})"

    def visit_ListExpression(self, node):
        """Visit a list expression."""
        elements = [self.generate(element) for element in node.elements]
        return f"[{', '.join(elements)}]"

    def visit_DictionaryExpression(self, node):
        """Visit a dictionary expression."""
        entries = [f"{self.generate(entry.key)}: {self.generate(entry.value)}" for entry in node.entries]
        return f"{{{', '.join(entries)}}}"

    def visit_IndexAccess(self, node):
        """Visit an index access expression."""
        target_code = self.generate(node.target)
        index_code = self.generate(node.index)
        return f"{target_code}[{index_code}]"