"""
Type checking for the enhanced type system in Runa.
This module provides functions for checking type consistency in programs.
"""
from src.runa.ast.nodes import (
    StringLiteral, NumberLiteral, BooleanLiteral, VariableReference,
    BinaryOperation, FunctionCall, ListExpression, DictionaryExpression,
    IndexAccess, Declaration, Assignment, IfStatement, ForEachStatement,
    ReturnStatement, DisplayStatement, ProcessDefinition
)
from src.runa.types.nodes import (
    Type, PrimitiveType, AnyType, UnionType, ListType, DictionaryType,
    FunctionType, GenericType, ParameterizedType, TypeAlias,
    TypedDeclaration, TypedParameter, TypedProcessDefinition
)
from src.runa.types.inference import TypeInferer


class TypeError:
    """Error detected during type checking."""

    def __init__(self, message, position):
        self.message = message
        self.position = position

    def __str__(self):
        return f"{self.position}: {self.message}"


class TypeChecker:
    """
    Class for checking type consistency in programs.
    """

    def __init__(self):
        # Initialize the type inferer
        self.inferer = TypeInferer()

        # List of detected type errors
        self.errors = []

    def check_program(self, program):
        """
        Check type consistency in a program.

        Args:
            program: The program AST to check

        Returns:
            Whether the program is type-consistent
        """
        # Clear previous errors
        self.errors = []

        # Analyze the program to infer types
        env = self.inferer.analyze_program(program)

        # Check each statement in the program
        for stmt in program.statements:
            self._check_statement(stmt, env)

        # Return whether there were no errors
        return len(self.errors) == 0

    def _check_statement(self, stmt, env):
        """
        Check type consistency in a statement.

        Args:
            stmt: The statement to check
            env: The type environment
        """
        # Dispatch based on statement type
        if isinstance(stmt, Declaration):
            self._check_declaration(stmt, env)
        elif isinstance(stmt, TypedDeclaration):
            self._check_typed_declaration(stmt, env)
        elif isinstance(stmt, Assignment):
            self._check_assignment(stmt, env)
        elif isinstance(stmt, IfStatement):
            self._check_if_statement(stmt, env)
        elif isinstance(stmt, ForEachStatement):
            self._check_for_each_statement(stmt, env)
        elif isinstance(stmt, ReturnStatement):
            self._check_return_statement(stmt, env)
        elif isinstance(stmt, DisplayStatement):
            self._check_display_statement(stmt, env)
        elif isinstance(stmt, ProcessDefinition):
            self._check_process_definition(stmt, env)
        elif isinstance(stmt, TypedProcessDefinition):
            self._check_typed_process_definition(stmt, env)
        elif isinstance(stmt, TypeAlias):
            self._check_type_alias(stmt, env)

    def _check_declaration(self, stmt, env):
        """Check type consistency in a variable declaration."""
        if stmt.value:
            # Infer the type of the value
            value_type = self.inferer.infer_type(stmt.value, env)

            # Update the environment
            env.set_variable_type(stmt.name, value_type)

    def _check_typed_declaration(self, stmt, env):
        """Check type consistency in a typed variable declaration."""
        # Infer the type of the value
        value_type = self.inferer.infer_type(stmt.value, env)

        # Check if the value type is compatible with the declared type
        if not self._is_type_compatible(value_type, stmt.type_annotation, env):
            self.errors.append(TypeError(
                f"Type mismatch in declaration of '{stmt.name}': expected {stmt.type_annotation}, got {value_type}",
                stmt.position
            ))

        # Update the environment
        env.set_variable_type(stmt.name, stmt.type_annotation)

    def _check_assignment(self, stmt, env):
        """Check type consistency in a variable assignment."""
        # Get the variable type from the environment
        var_type = env.get_variable_type(stmt.name)

        if var_type:
            # Infer the type of the value
            value_type = self.inferer.infer_type(stmt.value, env)

            # Check if the value type is compatible with the variable type
            if not self._is_type_compatible(value_type, var_type, env):
                self.errors.append(TypeError(
                    f"Type mismatch in assignment to '{stmt.name}': expected {var_type}, got {value_type}",
                    stmt.position
                ))
        else:
            # Variable not defined - this should be caught by semantic analysis
            pass

    def _check_if_statement(self, stmt, env):
        """Check type consistency in an if statement."""
        # Check the condition type
        condition_type = self.inferer.infer_type(stmt.condition, env)

        # Condition should be boolean
        if not self._is_type_compatible(condition_type, self.inferer.boolean_type, env):
            self.errors.append(TypeError(
                f"Condition must be boolean, got {condition_type}",
                stmt.condition.position
            ))

        # Check the then block
        then_env = env.enter_scope()
        for s in stmt.then_block:
            self._check_statement(s, then_env)

        # Check the else block if it exists
        if stmt.else_block:
            else_env = env.enter_scope()
            for s in stmt.else_block:
                self._check_statement(s, else_env)

    def _check_for_each_statement(self, stmt, env):
        """Check type consistency in a for-each statement."""
        # Infer the type of the iterable
        iterable_type = self.inferer.infer_type(stmt.iterable, env)

        # Check if the iterable type is a list
        if not isinstance(iterable_type, ListType) and not isinstance(iterable_type, AnyType):
            self.errors.append(TypeError(
                f"For-each loop requires a list, got {iterable_type}",
                stmt.iterable.position
            ))
            return

        # Create a new scope for the loop body
        loop_env = env.enter_scope()

        # Determine the element type
        if isinstance(iterable_type, ListType):
            elem_type = iterable_type.element_type
        else:
            elem_type = self.inferer.any_type

        # Bind the loop variable to the element type
        loop_env.set_variable_type(stmt.variable, elem_type)

        # Check the loop body
        for s in stmt.body:
            self._check_statement(s, loop_env)

    def _check_return_statement(self, stmt, env):
        """Check type consistency in a return statement."""
        # No type checking needed for return statements in non-typed functions
        pass

    def _check_display_statement(self, stmt, env):
        """Check type consistency in a display statement."""
        # All types can be displayed, so no type checking needed
        pass

    def _check_process_definition(self, stmt, env):
        """Check type consistency in a process definition."""
        # Create a function type
        param_count = len(stmt.parameters)
        param_types = [self.inferer.any_type] * param_count
        return_type = self.inferer.any_type

        func_type = FunctionType(param_types, return_type)

        # Set the function type in the environment
        env.set_function_type(stmt.name, func_type)

        # Create a new scope for the function body
        func_env = env.enter_scope()

        # Bind parameter names to Any type
        for param in stmt.parameters:
            func_env.set_variable_type(param.name, self.inferer.any_type)

        # Check the function body
        for s in stmt.body:
            self._check_statement(s, func_env)

    def _check_typed_process_definition(self, stmt, env):
        """Check type consistency in a typed process definition."""
        # Extract parameter types and return type
        param_types = [param.type_annotation for param in stmt.parameters]
        return_type = stmt.return_type

        # Create a function type
        func_type = FunctionType(param_types, return_type)

        # Set the function type in the environment
        env.set_function_type(stmt.name, func_type)

        # Create a new scope for the function body
        func_env = env.enter_scope()

        # Bind parameter names to their types
        for param in stmt.parameters:
            func_env.set_variable_type(param.name, param.type_annotation)

        # Check the function body
        for s in stmt.body:
            self._check_statement(s, func_env)

        # TODO: Check that all return statements have the correct type

    def _check_type_alias(self, stmt, env):
        """Check type consistency in a type alias."""
        # Nothing to check for type aliases
        pass

    def _is_type_compatible(self, source_type, target_type, env):
        """
        Check if a source type is compatible with a target type.

        Args:
            source_type: The source type
            target_type: The target type
            env: The type environment

        Returns:
            Whether the source type is compatible with the target type
        """
        # Same type
        if source_type == target_type:
            return True

        # Any type is compatible with any other type
        if isinstance(source_type, AnyType) or isinstance(target_type, AnyType):
            return True

        # Check numeric types
        if self._is_numeric_type(source_type) and self._is_numeric_type(target_type):
            # Integer can be assigned to Float
            if source_type == self.inferer.integer_type and target_type == self.inferer.float_type:
                return True

        # Check list types
        if isinstance(source_type, ListType) and isinstance(target_type, ListType):
            # Check element type compatibility
            return self._is_type_compatible(source_type.element_type, target_type.element_type, env)

        # Check dictionary types
        if isinstance(source_type, DictionaryType) and isinstance(target_type, DictionaryType):
            # Check key and value type compatibility
            return (
                    self._is_type_compatible(source_type.key_type, target_type.key_type, env) and
                    self._is_type_compatible(source_type.value_type, target_type.value_type, env)
            )

        # Check union types
        if isinstance(target_type, UnionType):
            # Source type is compatible if it's compatible with any type in the union
            return any(self._is_type_compatible(source_type, t, env) for t in target_type.types)

        if isinstance(source_type, UnionType):
            # Source type is compatible if all its types are compatible with the target type
            return all(self._is_type_compatible(t, target_type, env) for t in source_type.types)

        # Types are not compatible
        return False

    def _is_numeric_type(self, type_):
        """Check if a type is numeric (Integer or Float)."""
        return type_ == self.inferer.integer_type or type_ == self.inferer.float_type