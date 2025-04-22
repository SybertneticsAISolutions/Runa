"""
JavaScript code generator for the Runa programming language.

This module provides classes and functions for generating JavaScript code
from Runa AST nodes.
"""
from src.runa.ast.visitors import Visitor


class JsCodeGenerator(Visitor):
    """Generator for JavaScript code from Runa AST."""

    def __init__(self):
        """Initialize the JavaScript code generator."""
        super().__init__()
        self.current_indent = 0
        self.indent_str = "    "  # 4 spaces per indent level

    def generate(self, node):
        """
        Generate JavaScript code for an AST node.

        Args:
            node: The AST node to generate code for

        Returns:
            The generated JavaScript code as a string
        """
        if node is None:
            return ""

        # Delegate to the appropriate visit method
        node.accept(self)
        return self.result

    def _indent(self):
        """Return the current indentation string."""
        return self.indent_str * self.current_indent

    def visit_Program(self, node):
        """Generate code for a program."""
        # Generate code for each statement
        stmts = []
        for stmt in node.statements:
            stmt_code = self.generate(stmt)
            if stmt_code:
                stmts.append(stmt_code)

        # Add runtime functions
        runtime = self._generate_runtime()

        # Combine all parts
        self.result = runtime + "\n\n" + "\n".join(stmts)

    def visit_Declaration(self, node):
        """Generate code for a variable declaration."""
        # Generate code for the value
        value_code = self.generate(node.value) if node.value else "null"

        # Generate the declaration
        self.result = f"{self._indent()}let {node.name} = {value_code};"

    def visit_Assignment(self, node):
        """Generate code for a variable assignment."""
        # Generate code for the value
        value_code = self.generate(node.value)

        # Generate the assignment
        self.result = f"{self._indent()}{node.name} = {value_code};"

    def visit_StringLiteral(self, node):
        """Generate code for a string literal."""
        # Escape quotes in the string
        escaped = node.value.replace("\"", "\\\"")

        # Generate the string literal
        self.result = f"\"{escaped}\""

    def visit_NumberLiteral(self, node):
        """Generate code for a number literal."""
        self.result = str(node.value)

    def visit_BooleanLiteral(self, node):
        """Generate code for a boolean literal."""
        self.result = "true" if node.value else "false"

    def visit_VariableReference(self, node):
        """Generate code for a variable reference."""
        self.result = node.name

    def visit_BinaryOperation(self, node):
        """Generate code for a binary operation."""
        # Generate code for the operands
        left_code = self.generate(node.left)
        right_code = self.generate(node.right)

        # Map Runa operators to JavaScript operators
        op_map = {
            "PLUS": "+",
            "MINUS": "-",
            "MULTIPLIED": "*",
            "DIVIDED": "/",
            "MODULO": "%",
            "POWER": "**",
            "EQUAL": "===",
            "NOT_EQUAL": "!==",
            "GREATER": ">",
            "LESS": "<",
            "GREATER_EQUAL": ">=",
            "LESS_EQUAL": "<=",
            "AND": "&&",
            "OR": "||"
        }

        # Generate the operation
        op = op_map.get(node.operator, "/* Unknown operator */")
        self.result = f"({left_code} {op} {right_code})"

    def visit_ListExpression(self, node):
        """Generate code for a list expression."""
        # Generate code for each element
        elements = []
        for elem in node.elements:
            elem_code = self.generate(elem)
            elements.append(elem_code)

        # Generate the list
        self.result = f"[{', '.join(elements)}]"

    def visit_DictionaryExpression(self, node):
        """Generate code for a dictionary expression."""
        # Generate code for each entry
        entries = []
        for entry in node.entries:
            key_code = self.generate(entry.key)
            value_code = self.generate(entry.value)
            entries.append(f"{key_code}: {value_code}")

        # Generate the dictionary
        self.result = f"{{{', '.join(entries)}}}"

    def visit_DictionaryEntry(self, node):
        """Generate code for a dictionary entry."""
        # Generate code for the key and value
        key_code = self.generate(node.key)
        value_code = self.generate(node.value)

        # Generate the entry
        self.result = f"{key_code}: {value_code}"

    def visit_IndexAccess(self, node):
        """Generate code for an index access."""
        # Generate code for the target and index
        target_code = self.generate(node.target)
        index_code = self.generate(node.index)

        # Generate the index access
        self.result = f"{target_code}[{index_code}]"

    def visit_FunctionCall(self, node):
        """Generate code for a function call."""
        # Check for display function
        if node.name == "Display":
            return self.visit_DisplayStatement(node)

        # Generate code for arguments
        args = []
        for arg in node.args:
            arg_code = self.generate(arg)
            args.append(arg_code)

        # Generate the function call
        self.result = f"{node.name}({', '.join(args)})"

    def visit_FunctionCallWithNamedArgs(self, node):
        """Generate code for a function call with named arguments."""
        # Check for display function
        if node.name == "Display":
            return self.visit_DisplayStatement(node)

        # Generate code for arguments
        args = []
        for name, value in node.kwargs.items():
            value_code = self.generate(value)
            # JavaScript doesn't have named arguments, so we pass an object
            args.append(f"{name}: {value_code}")

        # Generate the function call with a parameter object
        self.result = f"{node.name}({{{', '.join(args)}}})"

    def visit_IfStatement(self, node):
        """Generate code for an if statement."""
        # Generate code for the condition
        condition_code = self.generate(node.condition)

        # Generate the if statement
        parts = [f"{self._indent()}if ({condition_code}) {{"]

        # Generate the then block
        self.current_indent += 1
        then_stmts = []
        for stmt in node.then_block:
            stmt_code = self.generate(stmt)
            if stmt_code:
                then_stmts.append(stmt_code)
        parts.extend(then_stmts)
        self.current_indent -= 1

        parts.append(f"{self._indent()}}}")

        # Generate the else block if it exists
        if node.else_block:
            parts.append(f"{self._indent()}else {{")

            self.current_indent += 1
            else_stmts = []
            for stmt in node.else_block:
                stmt_code = self.generate(stmt)
                if stmt_code:
                    else_stmts.append(stmt_code)
            parts.extend(else_stmts)
            self.current_indent -= 1

            parts.append(f"{self._indent()}}}")

        # Combine all parts
        self.result = "\n".join(parts)

    def visit_ForEachStatement(self, node):
        """Generate code for a for-each statement."""
        # Generate code for the iterable
        iterable_code = self.generate(node.iterable)

        # Generate the for-each statement
        parts = [f"{self._indent()}for (let {node.variable} of {iterable_code}) {{"]

        # Generate the loop body
        self.current_indent += 1
        body_stmts = []
        for stmt in node.body:
            stmt_code = self.generate(stmt)
            if stmt_code:
                body_stmts.append(stmt_code)
        parts.extend(body_stmts)
        self.current_indent -= 1

        parts.append(f"{self._indent()}}}")

        # Combine all parts
        self.result = "\n".join(parts)

    def visit_ReturnStatement(self, node):
        """Generate code for a return statement."""
        # Generate code for the value
        value_code = self.generate(node.value) if node.value else ""

        # Generate the return statement
        self.result = f"{self._indent()}return {value_code};"

    def visit_DisplayStatement(self, node):
        """Generate code for a display statement."""
        if node.value and node.message:
            # Display with both value and message
            value_code = self.generate(node.value)
            message_code = self.generate(node.message)
            self.result = f"{self._indent()}console.log({message_code}, {value_code});"
        elif node.value:
            # Display with value only
            value_code = self.generate(node.value)
            self.result = f"{self._indent()}console.log({value_code});"
        elif node.message:
            # Display with message only
            message_code = self.generate(node.message)
            self.result = f"{self._indent()}console.log({message_code});"
        else:
            # Empty display
            self.result = f"{self._indent()}console.log();"

    def visit_ProcessDefinition(self, node):
        """Generate code for a process (function) definition."""
        # Generate parameter list
        params = [param.name for param in node.parameters]

        # Generate the function definition
        parts = [f"{self._indent()}function {node.name}({', '.join(params)}) {{"]

        # Generate the function body
        self.current_indent += 1
        body_stmts = []
        for stmt in node.body:
            stmt_code = self.generate(stmt)
            if stmt_code:
                body_stmts.append(stmt_code)
        parts.extend(body_stmts)
        self.current_indent -= 1

        parts.append(f"{self._indent()}}}")

        # Combine all parts
        self.result = "\n".join(parts)

    def visit_ImportStatement(self, node):
        """Generate code for an import statement."""
        # For built-in modules, we don't need to do anything in JavaScript
        # For custom modules, we would generate an import statement
        self.result = f"{self._indent()}// Import {node.module} module"

    def _generate_runtime(self):
        """Generate the JavaScript runtime library."""
        return """// Runa Runtime Library for JavaScript

// Utility function for working with named arguments
function extractNamedArgs(args, defaults) {
    if (args.length === 1 && typeof args[0] === 'object' && args[0] !== null) {
        return { ...defaults, ...args[0] };
    }
    return defaults;
}

// String formatting for Runa
function formatString(str, ...args) {
    if (args.length === 1 && typeof args[0] === 'object' && args[0] !== null) {
        // Named formatting
        let result = str;
        for (const [key, value] of Object.entries(args[0])) {
            const placeholder = new RegExp(`\\{${key}\\}`, 'g');
            result = result.replace(placeholder, value);
        }
        return result;
    } else {
        // Positional formatting
        return str.replace(/\{\d+\}/g, match => {
            const index = parseInt(match.slice(1, -1));
            return index < args.length ? args[index] : match;
        });
    }
}

// Add utility functions for lists and dictionaries
Array.prototype.add = function(item) {
    this.push(item);
    return this;
};

Array.prototype.remove = function(item) {
    const index = this.indexOf(item);
    if (index !== -1) {
        this.splice(index, 1);
    }
    return this;
};

// Length operation
function length(obj) {
    if (Array.isArray(obj)) {
        return obj.length;
    } else if (typeof obj === 'string') {
        return obj.length;
    } else if (obj && typeof obj === 'object') {
        return Object.keys(obj).length;
    }
    return 0;
}
"""

    # Advanced language features support

    def visit_MatchExpression(self, node):
        """Generate code for a match expression."""
        # Generate code for the value to match
        value_code = self.generate(node.value)

        # Generate a unique temporary variable name for the value
        temp_var = f"_match_value_{id(node) % 10000:04d}"

        # Generate the match statement
        parts = [f"{self._indent()}const {temp_var} = {value_code};"]

        # Process each case
        for i, case in enumerate(node.cases):
            # Generate the condition for this case
            condition = self._generate_pattern_condition(case.pattern, temp_var)

            if i == 0:
                parts.append(f"{self._indent()}if ({condition}) {{")
            else:
                parts.append(f"{self._indent()}else if ({condition}) {{")

            # Generate the bindings for this case
            bindings = self._generate_pattern_bindings(case.pattern, temp_var)

            # Generate the body for this case
            self.current_indent += 1

            # Add bindings before the body
            for binding in bindings:
                parts.append(f"{self._indent()}{binding}")

            # Add the body statements
            for stmt in case.body:
                stmt_code = self.generate(stmt)
                if stmt_code:
                    parts.append(stmt_code)

            self.current_indent -= 1
            parts.append(f"{self._indent()}}}")

        # Add default case
        parts.append(f"{self._indent()}else {{")
        parts.append(f"{self._indent()}    // No pattern matched")
        parts.append(f"{self._indent()}}}")

        # Combine all parts
        self.result = "\n".join(parts)

    def _generate_pattern_condition(self, pattern, value_var):
        """Generate a condition for matching a pattern."""
        from src.runa.patterns.nodes import (
            WildcardPattern, LiteralPattern, VariablePattern,
            ListPattern, DictionaryPattern, RestPattern, TypePattern
        )

        if isinstance(pattern, WildcardPattern):
            # Wildcard always matches
            return "true"

        elif isinstance(pattern, LiteralPattern):
            # Literal matches if values are equal
            lit_code = self.generate(pattern.value)
            return f"{value_var} === {lit_code}"

        elif isinstance(pattern, VariablePattern):
            # Variable pattern always matches
            return "true"

        elif isinstance(pattern, ListPattern):
            # Check if value is a list and has the right length or structure
            elements = pattern.elements

            # Check for rest pattern
            has_rest = any(isinstance(e, RestPattern) for e in elements)

            if not has_rest:
                # Fixed length list pattern
                length_check = f"Array.isArray({value_var}) && {value_var}.length === {len(elements)}"

                # If no elements, just check length
                if not elements:
                    return length_check

                # Check each element
                element_checks = []
                for i, elem in enumerate(elements):
                    elem_check = self._generate_pattern_condition(elem, f"{value_var}[{i}]")
                    element_checks.append(elem_check)

                # Combine checks
                return f"{length_check} && {' && '.join(element_checks)}"
            else:
                # Variable length list pattern with rest
                list_check = f"Array.isArray({value_var})"

                # Count elements before and after rest
                rest_index = next(i for i, e in enumerate(elements) if isinstance(e, RestPattern))
                before_rest = elements[:rest_index]
                after_rest = elements[rest_index + 1:]

                # Minimum length check
                min_length = len(before_rest) + len(after_rest)
                length_check = f"{value_var}.length >= {min_length}"

                # Check elements before rest
                before_checks = []
                for i, elem in enumerate(before_rest):
                    elem_check = self._generate_pattern_condition(elem, f"{value_var}[{i}]")
                    before_checks.append(elem_check)

                # Check elements after rest
                after_checks = []
                for i, elem in enumerate(after_rest):
                    elem_check = self._generate_pattern_condition(
                        elem, f"{value_var}[{value_var}.length - {len(after_rest) - i}]"
                    )
                    after_checks.append(elem_check)

                # Combine checks
                all_checks = [list_check, length_check]
                all_checks.extend(before_checks)
                all_checks.extend(after_checks)

                return " && ".join(all_checks)

        elif isinstance(pattern, DictionaryPattern):
            # Check if value is a dictionary and has the required keys
            entries = pattern.entries

            # If no entries, check if it's an empty dict
            if not entries:
                return f"typeof {value_var} === 'object' && {value_var} !== null && Object.keys({value_var}).length === 0"

            # Check if it's a dictionary
            dict_check = f"typeof {value_var} === 'object' && {value_var} !== null"

            # Check each key exists and its value matches
            key_checks = []
            for entry in entries:
                key_code = self.generate(entry.key)
                key_check = f"{key_code} in {value_var}"

                # Add check for the corresponding value
                value_check = self._generate_pattern_condition(entry.value, f"{value_var}[{key_code}]")
                key_checks.append(f"{key_check} && {value_check}")

            # Combine all checks
            return f"{dict_check} && {' && '.join(key_checks)}"

        elif isinstance(pattern, RestPattern):
            # Rest pattern always matches
            return "true"

        elif isinstance(pattern, TypePattern):
            # Type pattern matches if value is of the specified type
            type_map = {
                "Integer": "Number.isInteger",
                "Float": "Number.isFinite",
                "String": "typeof {} === 'string'",
                "Boolean": "typeof {} === 'boolean'",
                "List": "Array.isArray",
                "Dictionary": "typeof {} === 'object' && {} !== null && !Array.isArray({})"
            }

            type_check = type_map.get(pattern.type_name, "typeof {} === '{}'".format(pattern.type_name.toLowerCase()))

            if "{}" in type_check:
                # Format the type check with the value variable
                type_check = type_check.format(value_var, value_var, value_var)
            else:
                # Call the type checking function with the value variable
                type_check = f"{type_check}({value_var})"

            return type_check

        # Default case
        return "false"

    def _generate_pattern_bindings(self, pattern, value_var):
        """Generate variable bindings for a pattern."""
        from src.runa.patterns.nodes import (
            WildcardPattern, LiteralPattern, VariablePattern,
            ListPattern, DictionaryPattern, RestPattern, TypePattern
        )

        bindings = []

        if isinstance(pattern, VariablePattern) and pattern.name != '_':
            # Bind the variable to the value
            bindings.append(f"const {pattern.name} = {value_var};")

        elif isinstance(pattern, ListPattern):
            # Bind variables in the list pattern
            elements = pattern.elements

            # Check for rest pattern
            rest_index = next((i for i, e in enumerate(elements) if isinstance(e, RestPattern)), None)

            if rest_index is not None:
                # Handle list pattern with rest
                before_rest = elements[:rest_index]
                after_rest = elements[rest_index + 1:]

                # Bind elements before rest
                for i, elem in enumerate(before_rest):
                    elem_bindings = self._generate_pattern_bindings(elem, f"{value_var}[{i}]")
                    bindings.extend(elem_bindings)

                # Bind rest element if named
                rest_pattern = elements[rest_index]
                if isinstance(rest_pattern, RestPattern) and rest_pattern.name:
                    start = len(before_rest)
                    end = len(after_rest)
                    if end > 0:
                        rest_expr = f"{value_var}.slice({start}, {value_var}.length - {end})"
                    else:
                        rest_expr = f"{value_var}.slice({start})"
                    bindings.append(f"const {rest_pattern.name} = {rest_expr};")

                # Bind elements after rest
                for i, elem in enumerate(after_rest):
                    index_expr = f"{value_var}.length - {len(after_rest) - i}"
                    elem_bindings = self._generate_pattern_bindings(elem, f"{value_var}[{index_expr}]")
                    bindings.extend(elem_bindings)
            else:
                # Handle fixed length list pattern
                for i, elem in enumerate(elements):
                    elem_bindings = self._generate_pattern_bindings(elem, f"{value_var}[{i}]")
                    bindings.extend(elem_bindings)

        elif isinstance(pattern, DictionaryPattern):
            # Bind variables in the dictionary pattern
            for entry in pattern.entries:
                key_code = self.generate(entry.key)
                entry_bindings = self._generate_pattern_bindings(entry.value, f"{value_var}[{key_code}]")
                bindings.extend(entry_bindings)

        return bindings

    def visit_AsyncProcessDefinition(self, node):
        """Generate code for an async process definition."""
        # Generate parameter list
        params = [param.name for param in node.parameters]

        # Generate the async function definition
        parts = [f"{self._indent()}async function {node.name}({', '.join(params)}) {{"]

        # Generate the function body
        self.current_indent += 1
        body_stmts = []
        for stmt in node.body:
            stmt_code = self.generate(stmt)
            if stmt_code:
                body_stmts.append(stmt_code)
        parts.extend(body_stmts)
        self.current_indent -= 1

        parts.append(f"{self._indent()}}}")

        # Combine all parts
        self.result = "\n".join(parts)

    def visit_AwaitExpression(self, node):
        """Generate code for an await expression."""
        # Generate code for the value
        value_code = self.generate(node.value)

        # Generate the await expression
        self.result = f"await {value_code}"

    def visit_AsyncForEachStatement(self, node):
        """Generate code for an async for-each statement."""
        # Generate code for the iterable
        iterable_code = self.generate(node.iterable)

        # Generate the async for-each statement
        parts = [f"{self._indent()}for await (const {node.variable} of {iterable_code}) {{"]

        # Generate the loop body
        self.current_indent += 1
        body_stmts = []
        for stmt in node.body:
            stmt_code = self.generate(stmt)
            if stmt_code:
                body_stmts.append(stmt_code)
        parts.extend(body_stmts)
        self.current_indent -= 1

        parts.append(f"{self._indent()}}}")

        # Combine all parts
        self.result = "\n".join(parts)

    def visit_LambdaExpression(self, node):
        """Generate code for a lambda expression."""
        # Generate parameter list
        params = ", ".join(node.parameters)

        # Generate the body
        body_code = self.generate(node.body)

        # Generate the lambda expression
        self.result = f"(({params}) => {body_code})"

    def visit_PipelineExpression(self, node):
        """Generate code for a pipeline expression."""
        # Generate code for left and right expressions
        left_code = self.generate(node.left)
        right_code = self.generate(node.right)

        # Generate the pipeline expression (function call)
        self.result = f"{right_code}({left_code})"

    def visit_PartialApplicationExpression(self, node):
        """Generate code for a partial application expression."""
        # Generate code for the function
        func_code = self.generate(node.function)

        # Generate code for arguments
        args_list = []
        for arg in node.args:
            arg_code = self.generate(arg)
            args_list.append(arg_code)

        # Generate code for keyword arguments
        kwargs_obj = []
        for name, value in node.kwargs.items():
            value_code = self.generate(value)
            kwargs_obj.append(f"{name}: {value_code}")

        # Generate the partial application
        args_str = ", ".join(args_list)
        kwargs_str = "{" + ", ".join(kwargs_obj) + "}" if kwargs_obj else ""

        if args_list and kwargs_obj:
            self.result = f"((...args) => {func_code}({args_str}, ...args, {kwargs_str}))"
        elif args_list:
            self.result = f"((...args) => {func_code}({args_str}, ...args))"
        elif kwargs_obj:
            self.result = f"((...args) => {func_code}(...args, {kwargs_str}))"
        else:
            self.result = func_code  # No partial application needed

    def visit_CompositionExpression(self, node):
        """Generate code for a function composition expression."""
        # Generate code for each function
        func_codes = [self.generate(func) for func in node.functions]

        # Generate the composition expression
        if len(func_codes) == 1:
            self.result = func_codes[0]
        else:
            # Create a function that applies each function in sequence
            funcs_list = ", ".join(func_codes)
            self.result = f"((x) => {func_codes[0]}({func_codes[1:].join('(')}(x){')' * (len(func_codes) - 1)}))"

    def visit_MapExpression(self, node):
        """Generate code for a map expression."""
        # Generate code for the function and collection
        func_code = self.generate(node.function)
        coll_code = self.generate(node.collection)

        # Generate the map expression
        self.result = f"{coll_code}.map({func_code})"

    def visit_FilterExpression(self, node):
        """Generate code for a filter expression."""
        # Generate code for the function and collection
        pred_code = self.generate(node.predicate)
        coll_code = self.generate(node.collection)

        # Generate the filter expression
        self.result = f"{coll_code}.filter({pred_code})"

    def visit_ReduceExpression(self, node):
        """Generate code for a reduce expression."""
        # Generate code for the function, collection, and initial value
        func_code = self.generate(node.function)
        coll_code = self.generate(node.collection)

        # Generate the reduce expression
        if node.initial is not None:
            init_code = self.generate(node.initial)
            self.result = f"{coll_code}.reduce({func_code}, {init_code})"
        else:
            self.result = f"{coll_code}.reduce({func_code})"

    def visit_TypeAlias(self, node):
        """Generate code for a type alias."""
        # JavaScript doesn't have types, so add a comment
        self.result = f"{self._indent()}// Type alias: {node.name} = {node.target_type}"

    def visit_TypedDeclaration(self, node):
        """Generate code for a typed declaration."""
        # Generate code for the value
        value_code = self.generate(node.value) if node.value else "null"

        # Generate the declaration with a type comment
        self.result = f"{self._indent()}let {node.name} = {value_code}; // type: {node.type_annotation}"

    def visit_TypedProcessDefinition(self, node):
        """Generate code for a typed process definition."""
        # Generate parameter list
        params = [param.name for param in node.parameters]

        # Generate parameter types for comment
        param_types = [str(param.type_annotation) for param in node.parameters]
        param_types_str = ", ".join(param_types)
        return_type_str = str(node.return_type)

        # Generate the function definition with type comment
        parts = [f"{self._indent()}function {node.name}({', '.join(params)}) {{ // ({param_types_str}) -> {return_type_str}"]

        # Generate the function body
        self.current_indent += 1
        body_stmts = []
        for stmt in node.body:
            stmt_code = self.generate(stmt)
            if stmt_code:
                body_stmts.append(stmt_code)
        parts.extend(body_stmts)
        self.current_indent -= 1

        parts.append(f"{self._indent()}}}")

        # Combine all parts
        self.result = "\n".join(parts).indent_str = "    "  # 4 spaces per indent level