"""
Parser for functional programming constructs in Runa.
This module extends the main parser with functional programming capabilities.
"""
from src.runa.functional.nodes import (
    LambdaExpression, PipelineExpression, PartialApplicationExpression,
    CompositionExpression, MapExpression, FilterExpression, ReduceExpression
)
from src.runa.ast.nodes import Parameter


def extend_parser(parser_class):
    """
    Extend the parser class with functional programming capabilities.

    This function adds new grammar rules to the parser.
    """
    # Add tokens for functional programming
    if 'LAMBDA' not in parser_class.tokens:
        parser_class.tokens = parser_class.tokens + (
            'LAMBDA', 'PIPE', 'COMPOSE', 'MAP', 'FILTER', 'REDUCE', 'PARTIAL'
        )

    # Add lexer rules for functional tokens
    def t_LAMBDA(self, t):
        r'Lambda'
        return t

    def t_PIPE(self, t):
        r'\|>'
        return t

    def t_COMPOSE(self, t):
        r'compose'
        return t

    def t_MAP(self, t):
        r'Map'
        return t

    def t_FILTER(self, t):
        r'Filter'
        return t

    def t_REDUCE(self, t):
        r'Reduce'
        return t

    def t_PARTIAL(self, t):
        r'Partial'
        return t

    # Add these methods to the lexer
    parser_class.lexer.__class__.t_LAMBDA = t_LAMBDA
    parser_class.lexer.__class__.t_PIPE = t_PIPE
    parser_class.lexer.__class__.t_COMPOSE = t_COMPOSE
    parser_class.lexer.__class__.t_MAP = t_MAP
    parser_class.lexer.__class__.t_FILTER = t_FILTER
    parser_class.lexer.__class__.t_REDUCE = t_REDUCE
    parser_class.lexer.__class__.t_PARTIAL = t_PARTIAL

    # Add grammar rules for functional programming

    def p_expression_lambda(self, p):
        """expression : LAMBDA parameter_list COLON expression"""
        parameters = p[2] if isinstance(p[2], list) else [Parameter(p[2], self._get_position(p, 2))]
        p[0] = LambdaExpression([param.name for param in parameters], p[4], self._get_position(p, 1))

    def p_expression_pipeline(self, p):
        """expression : expression PIPE expression"""
        p[0] = PipelineExpression(p[1], p[3], self._get_position(p, 2))

    def p_expression_partial(self, p):
        """expression : PARTIAL ID WITH argument_list
                      | PARTIAL ID WITH named_argument_list
                      | PARTIAL ID WITH argument_list AND named_argument_list"""
        from src.runa.ast.nodes import VariableReference
        function = VariableReference(p[2], self._get_position(p, 2))

        if len(p) == 5:
            # Partial with either positional or named arguments
            if isinstance(p[4][0], tuple):
                # Named arguments only
                named_args = dict(p[4])
                p[0] = PartialApplicationExpression(function, [], named_args, self._get_position(p, 1))
            else:
                # Positional arguments only
                p[0] = PartialApplicationExpression(function, p[4], {}, self._get_position(p, 1))
        else:
            # Partial with both positional and named arguments
            positional_args = p[4]
            named_args = dict(p[6])
            p[0] = PartialApplicationExpression(function, positional_args, named_args, self._get_position(p, 1))

    def p_expression_compose(self, p):
        """expression : COMPOSE ID WITH ID
                      | COMPOSE ID WITH ID AND ID
                      | COMPOSE ID WITH ID AND ID AND ID"""
        from src.runa.ast.nodes import VariableReference
        functions = []

        # Add functions in reverse order (for right-to-left composition)
        for i in range(len(p) - 1, 3, -2):
            functions.append(VariableReference(p[i], self._get_position(p, i)))

        p[0] = CompositionExpression(functions, self._get_position(p, 1))

    def p_expression_map(self, p):
        """expression : MAP expression OVER expression"""
        p[0] = MapExpression(p[2], p[4], self._get_position(p, 1))

    def p_expression_filter(self, p):
        """expression : FILTER expression USING expression"""
        p[0] = FilterExpression(p[4], p[2], self._get_position(p, 1))

    def p_expression_reduce(self, p):
        """expression : REDUCE expression USING expression
                      | REDUCE expression USING expression WITH INITIAL expression"""
        if len(p) == 5:
            p[0] = ReduceExpression(p[4], p[2], None, self._get_position(p, 1))
        else:
            p[0] = ReduceExpression(p[4], p[2], p[7], self._get_position(p, 1))

    # Add new tokens to the lexer token list
    if 'OVER' not in parser_class.tokens:
        parser_class.tokens = parser_class.tokens + ('OVER', 'USING', 'INITIAL')

    def t_OVER(self, t):
        r'over'
        return t

    def t_USING(self, t):
        r'using'
        return t

    def t_INITIAL(self, t):
        r'initial'
        return t

    parser_class.lexer.__class__.t_OVER = t_OVER
    parser_class.lexer.__class__.t_USING = t_USING
    parser_class.lexer.__class__.t_INITIAL = t_INITIAL

    # Add the new methods to the parser class
    parser_class.p_expression_lambda = p_expression_lambda
    parser_class.p_expression_pipeline = p_expression_pipeline
    parser_class.p_expression_partial = p_expression_partial
    parser_class.p_expression_compose = p_expression_compose
    parser_class.p_expression_map = p_expression_map
    parser_class.p_expression_filter = p_expression_filter
    parser_class.p_expression_reduce = p_expression_reduce

    return parser_class