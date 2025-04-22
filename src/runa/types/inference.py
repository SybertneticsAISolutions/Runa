"""
Type inference for the enhanced type system in Runa.
This module provides functions for inferring types of expressions.
"""
from src.runa.ast.nodes import (
    StringLiteral, NumberLiteral, BooleanLiteral, VariableReference,
    BinaryOperation, FunctionCall, ListExpression, DictionaryExpression,
    IndexAccess
)
from src.runa.types.nodes import (
    PrimitiveType, AnyType, UnionType, ListType, DictionaryType,
    FunctionType, GenericType, ParameterizedType
)


class TypeEnvironment:
    """
    Environment for storing variable and function types.
    """

    def __init__(self, parent=None):
        self.variables = {}  # Map of variable names to types
        self.functions = {}  # Map of function names to function types
        self.parent = parent  # Parent environment (for nested scopes)

    def get_variable_type(self, name):
        """Get the type of a variable."""
        if name in self.variables:
            return self.variables[name]

        if self.parent:
            return self.parent.get_variable_type(name)

        return None

    def set_variable_type(self, name, type_):
        """Set the type of a variable."""
        self.variables[name] = type_

    def get_function_type(self, name):
        """Get the type of a function."""
        if name in self.functions:
            return self.functions[name]

        if self.parent:
            return self.parent.get_function_type(name)

        return None

    def set_function_type(self, name, type_):
        """Set the type of a function."""
        self.functions[name] = type_

    def enter_scope(self):
        """Create and return a new nested scope."""
        return TypeEnvironment(self)


class TypeInferer:
    """
    Class for inferring types of expressions.
    """

    def __init__(self):
        # Initialize the type environment with built-in types
        self.env = TypeEnvironment()
        self._initialize_built_ins()

    def _initialize_built_ins(self):
        """Initialize built-in types."""
        # Built-in primitive types
        self.integer_type = PrimitiveType("Integer")
        self.float_type = PrimitiveType("Float")
        self.string_type = PrimitiveType("String")
        self.boolean_type = PrimitiveType("Boolean")
        self.any_type = AnyType()

        # Numeric type (union of Integer and Float)
        self.numeric_type = UnionType([self.integer_type, self.float_type])

        # Built-in functions
        # format_string: (String, Any) -> String
        self.env.set_function_type(
            "format_string",
            FunctionType([self.string_type, self.any_type], self.string_type)
        )

        # format_message: (Any) -> String
        self.env.set_function_type(
            "format_message",
            FunctionType([self.any_type], self.string_type)
        )

    def infer_type(self, node, env=None):
        """
        Infer the type of an expression node.

        Args:
            node: The AST node to infer the type of
            env: Optional type environment to use

        Returns:
            The inferred type of the expression
        """
        if env is None:
            env = self.env

        # Dispatch to the appropriate method based on node type
        if isinstance(node, StringLiteral):
            return self._infer_string_literal(node, env)
        elif isinstance(node, NumberLiteral):
            return self._infer_number_literal(node, env)
        elif isinstance(node, BooleanLiteral):
            return self._infer_boolean_literal(node, env)
        elif isinstance(node, VariableReference):
            return self._infer_variable_reference(node, env)
        elif isinstance(node, BinaryOperation):
            return self._infer_binary_operation(node, env)
        elif isinstance(node, FunctionCall):
            return self._infer_function_call(node, env)
        elif isinstance(node, ListExpression):
            return self._infer_list_expression(node, env)
        elif isinstance(node, DictionaryExpression):
            return self._infer_dictionary_expression(node, env)
        elif isinstance(node, IndexAccess):
            return self._infer_index_access(node, env)
        else:
            # Default to Any type for unknown node types
            return self.any_type

    def _infer_string_literal(self, node, env):
        """Infer the type of a string literal."""
        return self.string_type

    def _infer_number_literal(self, node, env):
        """Infer the type of a number literal."""
        # Check if the value is an integer or float
        if isinstance(node.value, int):
            return self.integer_type
        else:
            return self.float_type

    def _infer_boolean_literal(self, node, env):
        """Infer the type of a boolean literal."""
        return self.boolean_type

    def _infer_variable_reference(self, node, env):
        """Infer the type of a variable reference."""
        # Look up the variable type in the environment
        var_type = env.get_variable_type(node.name)

        if var_type:
            return var_type

        # Default to Any type for unknown variables
        return self.any_type

    def _infer_binary_operation(self, node, env):
        """Infer the type of a binary operation."""
        # Infer the types of the operands
        left_type = self.infer_type(node.left, env)
        right_type = self.infer_type(node.right, env)

        # Type inference rules for binary operations
        if node.operator in ["PLUS", "MINUS", "MULTIPLIED", "DIVIDED", "MODULO"]:
            # Arithmetic operations

            # String concatenation
            if node.operator == "PLUS" and (
                left_type == self.string_type or right_type == self.string_type
            ):
                return self.string_type

            # Numeric operations
            if self._is_numeric_type(left_type) and self._is_numeric_type(right_type):
                # If either operand is a float, the result is a float
                if left_type == self.float_type or right_type == self.float_type:
                    return self.float_type

                # Otherwise, the result is an integer
                return self.integer_type

        elif node.operator in ["GREATER", "LESS", "EQUAL", "NOT_EQUAL"]:
            # Comparison operations - result is always boolean
            return self.boolean_type

        elif node.operator in ["AND", "OR"]:
            # Logical operations - result is always boolean
            return self.boolean_type

        # Default to Any type for unknown operations
        return self.any_type

    def _infer_function_call(self, node, env):
        """Infer the type of a function call."""
        # Get the function type from the environment
        func_type = env.get_function_type(node.name)

        if func_type and isinstance(func_type, FunctionType):
            # Return the function's return type
            return func_type.return_type

        # Default to Any type for unknown functions
        return self.any_type

    def _infer_list_expression(self, node, env):
        """Infer the type of a list expression."""
        if not node.elements:
            # Empty list - default to List[Any]
            return ListType(self.any_type)

        # Infer the type of the first element
        elem_type = self.infer_type(node.elements[0], env)

        # Check if all elements have the same type
        for elem in node.elements[1:]:
            other_type = self.infer_type(elem, env)
            if not self._types_are_compatible(elem_type, other_type):
                # If types are incompatible, default to List[Any]
                return ListType(self.any_type)

        # All elements have compatible types
        return ListType(elem_type)

    def _infer_dictionary_expression(self, node, env):
        """Infer the type of a dictionary expression."""
        if not node.entries:
            # Empty dictionary - default to Dictionary[Any, Any]
            return DictionaryType(self.any_type, self.any_type)

        # Infer the types of the first entry's key and value
        key_type = self.infer_type(node.entries[0].key, env)
        value_type = self.infer_type(node.entries[0].value, env)

        # Check if all entries have compatible key and value types
        for entry in node.entries[1:]:
            other_key_type = self.infer_type(entry.key, env)
            other_value_type = self.infer_type(entry.value, env)

            if not self._types_are_compatible(key_type, other_key_type):
                key_type = self.any_type

            if not self._types_are_compatible(value_type, other_value_type):
                value_type = self.any_type

        # Return the dictionary type
        return DictionaryType(key_type, value_type)

    def _infer_index_access(self, node, env):
        """Infer the type of an index access expression."""
        # Infer the type of the target
        target_type = self.infer_type(node.target, env)

        if isinstance(target_type, ListType):
            # List index access returns the element type
            return target_type.element_type

        if isinstance(target_type, DictionaryType):
            # Dictionary index access returns the value type
            return target_type.value_type

        # Default to Any type for unknown target types
        return self.any_type

    def _is_numeric_type(self, type_):
        """Check if a type is numeric (Integer or Float)."""
        return type_ == self.integer_type or type_ == self.float_type

    def _types_are_compatible(self, type1, type2):
        """Check if two types are compatible (can be unified)."""
        # Same type
        if type1 == type2:
            return True

        # Any type is compatible with any other type
        if isinstance(type1, AnyType) or isinstance(type2, AnyType):
            return True

        # Both are numeric types
        if self._is_numeric_type(type1) and self._is_numeric_type(type2):
            return True

        # Both are list types with compatible element types
        if (isinstance(type1, ListType) and isinstance(type2, ListType) and
                self._types_are_compatible(type1.element_type, type2.element_type)):
            return True

        # Both are dictionary types with compatible key and value types
        if (isinstance(type1, DictionaryType) and isinstance(type2, DictionaryType) and
                self._types_are_compatible(type1.key_type, type2.key_type) and
                self._types_are_compatible(type1.value_type, type2.value_type)):
            return True

        # Check if either type is a union type
        if isinstance(type1, UnionType):
            # Type2 is compatible if it's compatible with any type in the union
            return any(self._types_are_compatible(t, type2) for t in type1.types)

        if isinstance(type2, UnionType):
            # Type1 is compatible if it's compatible with any type in the union
            return any(self._types_are_compatible(type1, t) for t in type2.types)

        # Types are not compatible
        return False

    def _unify_types(self, type1, type2):
        """
        Unify two types into a single type that can represent both.

        Args:
            type1: First type
            type2: Second type

        Returns:
            A type that can represent both input types
        """
        # Same type
        if type1 == type2:
            return type1

        # If either type is Any, the result is the other type
        if isinstance(type1, AnyType):
            return type2
        if isinstance(type2, AnyType):
            return type1

        # Both are numeric types
        if self._is_numeric_type(type1) and self._is_numeric_type(type2):
            # If either is float, the unified type is float
            if type1 == self.float_type or type2 == self.float_type:
                return self.float_type
            # Otherwise, both are integer
            return self.integer_type

        # Both are list types
        if isinstance(type1, ListType) and isinstance(type2, ListType):
            # Unify the element types
            unified_elem_type = self._unify_types(type1.element_type, type2.element_type)
            return ListType(unified_elem_type)

        # Both are dictionary types
        if isinstance(type1, DictionaryType) and isinstance(type2, DictionaryType):
            # Unify the key and value types
            unified_key_type = self._unify_types(type1.key_type, type2.key_type)
            unified_value_type = self._unify_types(type1.value_type, type2.value_type)
            return DictionaryType(unified_key_type, unified_value_type)

        # If type1 is a union type
        if isinstance(type1, UnionType):
            # Add type2 to the union if not already included
            if not any(self._types_are_compatible(t, type2) for t in type1.types):
                return UnionType(type1.types + [type2])
            return type1

        # If type2 is a union type
        if isinstance(type2, UnionType):
            # Add type1 to the union if not already included
            if not any(self._types_are_compatible(type1, t) for t in type2.types):
                return UnionType([type1] + type2.types)
            return type2

        # Create a new union type
        return UnionType([type1, type2])

    def analyze_program(self, program):
        """
        Analyze a program and infer types for all variables and functions.

        Args:
            program: The program AST to analyze

        Returns:
            A type environment with inferred types
        """
        # Create a fresh type environment
        env = TypeEnvironment()

        # Process each statement in the program
        for stmt in program.statements:
            self._analyze_statement(stmt, env)

        return env

    def _analyze_statement(self, stmt, env):
        """
        Analyze a statement and update the type environment.

        Args:
            stmt: The statement to analyze
            env: The type environment to update
        """
        # Dispatch based on statement type
        from src.runa.ast.nodes import Declaration, Assignment, IfStatement, ForEachStatement, ReturnStatement, DisplayStatement, ProcessDefinition

        if isinstance(stmt, Declaration):
            # Infer the type of the value and bind it to the variable
            value_type = self.infer_type(stmt.value, env) if stmt.value else self.any_type
            env.set_variable_type(stmt.name, value_type)

        elif isinstance(stmt, Assignment):
            # Infer the type of the value
            value_type = self.infer_type(stmt.value, env)

            # Get the existing variable type
            var_type = env.get_variable_type(stmt.name)

            if var_type:
                # Unify the types if the variable already has a type
                unified_type = self._unify_types(var_type, value_type)
                env.set_variable_type(stmt.name, unified_type)
            else:
                # Otherwise, set the variable type to the value type
                env.set_variable_type(stmt.name, value_type)

        elif isinstance(stmt, IfStatement):
            # Analyze the condition
            self.infer_type(stmt.condition, env)

            # Create a new scope for the then block
            then_env = env.enter_scope()
            for s in stmt.then_block:
                self._analyze_statement(s, then_env)

            # Create a new scope for the else block if it exists
            if stmt.else_block:
                else_env = env.enter_scope()
                for s in stmt.else_block:
                    self._analyze_statement(s, else_env)

        elif isinstance(stmt, ForEachStatement):
            # Infer the type of the iterable
            iterable_type = self.infer_type(stmt.iterable, env)

            # Determine the element type
            if isinstance(iterable_type, ListType):
                elem_type = iterable_type.element_type
            else:
                elem_type = self.any_type

            # Create a new scope for the loop body
            loop_env = env.enter_scope()

            # Bind the loop variable to the element type
            loop_env.set_variable_type(stmt.variable, elem_type)

            # Analyze the loop body
            for s in stmt.body:
                self._analyze_statement(s, loop_env)

        elif isinstance(stmt, ProcessDefinition):
            # Create a type for the function
            param_types = [self.any_type] * len(stmt.parameters)
            return_type = self.any_type

            # Set the function type in the environment
            func_type = FunctionType(param_types, return_type)
            env.set_function_type(stmt.name, func_type)

            # Create a new scope for the function body
            func_env = env.enter_scope()

            # Bind parameter names to Any type
            for i, param in enumerate(stmt.parameters):
                func_env.set_variable_type(param.name, self.any_type)

            # Analyze the function body
            for s in stmt.body:
                self._analyze_statement(s, func_env)

        elif isinstance(stmt, ReturnStatement):
            # Infer the type of the return value if it exists
            if stmt.value:
                self.infer_type(stmt.value, env)

        elif isinstance(stmt, DisplayStatement):
            # Infer the types of the value and message
            self.infer_type(stmt.value, env)
            if stmt.message:
                self.infer_type(stmt.message, env)