"""
Context-aware parser extensions for the Runa programming language.

This module extends the basic parser with context-aware capabilities
for better handling of ambiguous syntax and semantics.
"""
from src.runa.context.disambiguator import Disambiguator
from src.runa.context.learner import PrecedentLearner


def extend_parser(parser_class):
    """
    Extend a parser class with context-aware capabilities.

    Args:
        parser_class: The parser class to extend

    Returns:
        The extended parser class
    """
    # Create a copy of the original parser class
    global new_p_indentation, new_p_expression_variable, new_p_expression_function_call
    original_parse = parser_class.parse
    original_init = parser_class.__init__

    def new_init(self, *args, **kwargs):
        """Initialize the context-aware parser."""
        # Call the original init
        original_init(self, *args, **kwargs)

        # Add context-aware components
        self.learner = PrecedentLearner(persistence_file="runa_precedents.json")
        self.disambiguator = Disambiguator(learner=self.learner)

        # Track scope level
        self.scope_level = 0

        # Keep track of parser state for ambiguity resolution
        self.current_statement = ""
        self.possible_interpretations = []

    def new_parse(self, text, **kwargs):
        """Parse with context awareness."""
        # Reset the disambiguator's context for a new parse
        self.disambiguator.clear_local_context()
        self.scope_level = 0
        self.current_statement = ""
        self.possible_interpretations = []

        # Call original parse method
        result = original_parse(self, text, **kwargs)

        return result

    # Add methods for tracking context
    def track_statement(self, statement, scope_level=0):
        """
        Track a statement in the context.

        Args:
            statement: The statement to track
            scope_level: The scope level of the statement
        """
        self.disambiguator.add_to_context(statement, scope_level)
        self.current_statement = statement

    def enter_scope(self):
        """Enter a new scope."""
        self.scope_level += 1

    def exit_scope(self):
        """Exit the current scope."""
        if self.scope_level > 0:
            self.scope_level -= 1

        if self.scope_level == 0:
            self.disambiguator.clear_local_context()

    def resolve_variable(self, name, candidates):
        """
        Resolve a variable reference.

        Args:
            name: The variable name
            candidates: List of possible variables

        Returns:
            The resolved variable
        """
        return self.disambiguator.disambiguate_variable(name, candidates, self.current_statement)

    def resolve_function(self, name, candidates, args=None):
        """
        Resolve a function reference.

        Args:
            name: The function name
            candidates: List of possible functions
            args: Optional list of argument types

        Returns:
            The resolved function
        """
        return self.disambiguator.disambiguate_function(name, candidates, self.current_statement, args)

    def resolve_syntax(self, partial, completions):
        """
        Resolve ambiguous syntax.

        Args:
            partial: The partial or ambiguous statement
            completions: List of possible completions

        Returns:
            The resolved statement
        """
        return self.disambiguator.disambiguate_syntax(partial, completions)

    # Modify p_statement rule to track context
    original_p_statement = parser_class.p_statement

    def new_p_statement(self, p):
        """Process a statement and track it in the context."""
        # Call the original rule
        original_p_statement(self, p)

        # Get the textual representation of the statement
        statement_text = self._get_statement_text(p)

        # Track in context if not empty
        if statement_text:
            self.track_statement(statement_text, self.scope_level)

    def _get_statement_text(self, p):
        """Get the textual representation of a statement."""
        # Simple implementation - in a real parser this would extract
        # the actual text from the input or reconstruct it from the parsed components
        if hasattr(p[0], 'position') and p[0].position:
            # Get the input slice corresponding to this statement
            if hasattr(self, 'input_text'):
                line_start = p[0].position.line - 1
                line_end = p[0].position.end_line if hasattr(p[0].position, 'end_line') else line_start
                col_start = p[0].position.column
                col_end = p[0].position.end_column if hasattr(p[0].position, 'end_column') else len(
                    self.input_text.splitlines()[line_end])

                lines = self.input_text.splitlines()[line_start:line_end + 1]
                if len(lines) == 1:
                    return lines[0][col_start:col_end].strip()
                else:
                    # Multi-line statement
                    lines[0] = lines[0][col_start:]
                    lines[-1] = lines[-1][:col_end]
                    return "\n".join(lines).strip()

        # Fallback - use str representation of the node
        return str(p[0])

    # Modify indentation handling to track scope changes
    original_p_indentation = getattr(parser_class, 'p_indentation', None)

    if original_p_indentation:
        def new_p_indentation(self, p):
            """Handle indentation and track scope changes."""
            # Call the original rule
            original_p_indentation(self, p)

            # Track scope changes
            if p[1] == 'INDENT':
                self.enter_scope()
            elif p[1] == 'DEDENT':
                self.exit_scope()

    # Override variable reference resolution
    original_p_expression_variable = getattr(parser_class, 'p_expression_variable', None)

    if original_p_expression_variable:
        def new_p_expression_variable(self, p):
            """Process a variable reference with context-aware resolution."""
            # Call the original rule
            original_p_expression_variable(self, p)

            # Get variable name
            var_name = p[1]

            # Define variable candidates - in a real implementation,
            # this would come from the symbol table
            var_candidates = [{'name': var_name, 'type': 'Unknown'}]

            # Resolve variable reference
            resolved_var = self.resolve_variable(var_name, var_candidates)

            # Use the resolved variable in the AST (would need to be integrated
            # with the actual AST building logic)

    # Override function call resolution
    original_p_expression_function_call = getattr(parser_class, 'p_expression_function_call', None)

    if original_p_expression_function_call:
        def new_p_expression_function_call(self, p):
            """Process a function call with context-aware resolution."""
            # Call the original rule
            original_p_expression_function_call(self, p)

            # Get function name
            func_name = p[1]

            # Define function candidates - in a real implementation,
            # this would come from the symbol table
            func_candidates = [{'name': func_name, 'parameters': []}]

            # Resolve function reference
            resolved_func = self.resolve_function(func_name, func_candidates)

            # Use the resolved function in the AST (would need to be integrated
            # with the actual AST building logic)

    # Integrate into the parser class
    parser_class.__init__ = new_init
    parser_class.parse = new_parse
    parser_class.track_statement = track_statement
    parser_class.enter_scope = enter_scope
    parser_class.exit_scope = exit_scope
    parser_class.resolve_variable = resolve_variable
    parser_class.resolve_function = resolve_function
    parser_class.resolve_syntax = resolve_syntax
    parser_class.p_statement = new_p_statement
    parser_class._get_statement_text = _get_statement_text

    if original_p_indentation:
        parser_class.p_indentation = new_p_indentation

    if original_p_expression_variable:
        parser_class.p_expression_variable = new_p_expression_variable

    if original_p_expression_function_call:
        parser_class.p_expression_function_call = new_p_expression_function_call

    return parser_class