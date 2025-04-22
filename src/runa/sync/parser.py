"""
Parser for asynchronous programming constructs in Runa.
This module extends the main parser with async/await capabilities.
"""
from nodes import AsyncProcessDefinition, AwaitExpression, AsyncForEachStatement


def extend_parser(parser_class):
    """
    Extend the parser class with asynchronous programming capabilities.

    This function adds new grammar rules to the parser.
    """
    # Add tokens for async programming
    if 'ASYNC' not in parser_class.tokens:
        parser_class.tokens = parser_class.tokens + ('ASYNC', 'AWAIT')

    # Add lexer rules for async tokens
    def t_ASYNC(self, t):
        r'Async'
        return t

    def t_AWAIT(self, t):
        r'await'
        return t

    # Add these methods to the lexer
    parser_class.lexer.__class__.t_ASYNC = t_ASYNC
    parser_class.lexer.__class__.t_AWAIT = t_AWAIT

    # Add grammar rules for async programming

    def p_statement_async_process(self, p):
        """statement : async_process_definition"""
        p[0] = p[1]

    def p_async_process_definition(self, p):
        """async_process_definition : ASYNC PROCESS CALLED STRING THAT TAKES parameter_list COLON INDENT statements DEDENT
                                     | ASYNC PROCESS CALLED STRING THAT TAKES ID COLON INDENT statements DEDENT"""
        if isinstance(p[7], list):
            # Process with multiple parameters
            from src.runa.ast.nodes import Parameter
            parameters = p[7]
        else:
            # Process with a single parameter
            from src.runa.ast.nodes import Parameter
            parameters = [Parameter(p[7], self._get_position(p, 7))]

        # Remove quotes from the process name
        process_name = p[4]

        p[0] = AsyncProcessDefinition(process_name, parameters, p[10], self._get_position(p, 1))

    def p_expression_await(self, p):
        """expression : AWAIT expression"""
        p[0] = AwaitExpression(p[2], self._get_position(p, 1))

    def p_statement_async_for(self, p):
        """statement : ASYNC FOR EACH ID IN expression COLON INDENT statements DEDENT"""
        p[0] = AsyncForEachStatement(p[4], p[6], p[9], self._get_position(p, 1))

    # Add the new methods to the parser class
    parser_class.p_statement_async_process = p_statement_async_process
    parser_class.p_async_process_definition = p_async_process_definition
    parser_class.p_expression_await = p_expression_await
    parser_class.p_statement_async_for = p_statement_async_for

    return parser_class