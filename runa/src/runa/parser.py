import ply.yacc as yacc
from lexer import RunaLexer
from ast.nodes import *

from runa.src.runa.ast.nodes import ListExpression


class RunaParser:
    """Parser for the Runa programming language."""

    def __init__(self):
        """Initialize the parser."""
        self.lexer = RunaLexer()
        self.lexer.build()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self)

    def parse(self, text):
        """Parse the given text and return the AST."""
        self.lexer.input(text)
        return self.parser.parse(lexer=self.lexer)

    # Grammar rules

    def p_program(self, p):
        """program : statements"""
        p[0] = Program(p[1])

    def p_statements(self, p):
        """statements : statements statement
                      | statement"""
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_statement(self, p):
        """statement : declaration
                     | assignment
                     | if_statement
                     | for_statement
                     | return_statement
                     | display_statement
                     | process_definition"""
        p[0] = p[1]

    def p_declaration(self, p):
        """declaration : LET ID BE expression
                       | LET ID BE STRING WITH ID AS expression
                       | DEFINE ID AS ID CONTAINING expression_list"""
        if len(p) == 5:
            # Simple declaration: Let x be 10
            p[0] = Declaration(p[2], p[4], self._get_position(p, 1))
        elif len(p) == 9:
            # Declaration with message: Let message be "Hello" with name as user_name
            # This is a common pattern for string formatting
            message = StringLiteral(p[4], self._get_position(p, 4))
            value = FunctionCall(
                "format_string",
                [message],
                {p[6]: p[8]},
                self._get_position(p, 1)
            )
            p[0] = Declaration(p[2], value, self._get_position(p, 1))
        else:
            # Define list_name as list containing 1, 2, 3
            container_type = p[4]  # "list" or "dictionary"
            container_elements = p[6]
            if container_type == "list":
                value = ListExpression(container_elements, self._get_position(p, 3))
            elif container_type == "dictionary":
                # Dictionary entries are already processed in expression_list
                value = DictionaryExpression(container_elements, self._get_position(p, 3))
            else:
                raise SyntaxError(f"Unknown container type: {container_type}")
            p[0] = Declaration(p[2], value, self._get_position(p, 1))

    def p_assignment(self, p):
        """assignment : SET ID TO expression"""
        p[0] = Assignment(p[2], p[4], self._get_position(p, 1))

    def p_if_statement(self, p):
        """if_statement : IF expression COLON INDENT statements DEDENT
                        | IF expression COLON INDENT statements DEDENT OTHERWISE COLON INDENT statements DEDENT"""
        if len(p) == 7:
            # If without else
            p[0] = IfStatement(p[2], p[5], None, self._get_position(p, 1))
        else:
            # If with else
            p[0] = IfStatement(p[2], p[5], p[10], self._get_position(p, 1))

    def p_for_statement(self, p):
        """for_statement : FOR EACH ID IN expression COLON INDENT statements DEDENT"""
        p[0] = ForEachStatement(p[3], p[5], p[8], self._get_position(p, 1))

    def p_return_statement(self, p):
        """return_statement : RETURN expression
                            | RETURN"""
        if len(p) == 3:
            p[0] = ReturnStatement(p[2], self._get_position(p, 1))
        else:
            p[0] = ReturnStatement(None, self._get_position(p, 1))

    def p_display_statement(self, p):
        """display_statement : DISPLAY expression
                             | DISPLAY expression WITH ID AS expression"""
        if len(p) == 3:
            p[0] = DisplayStatement(p[2], None, self._get_position(p, 1))
        else:
            p[0] = DisplayStatement(p[2], FunctionCall(
                "format_message",
                [],
                {p[4]: p[6]},
                self._get_position(p, 4)
            ), self._get_position(p, 1))

    def p_process_definition(self, p):
        """process_definition : PROCESS CALLED STRING THAT TAKES parameter_list COLON INDENT statements DEDENT
                              | PROCESS CALLED STRING THAT TAKES ID COLON INDENT statements DEDENT"""
        if isinstance(p[6], list):
            # Process with multiple parameters
            parameters = p[6]
        else:
            # Process with a single parameter
            parameters = [Parameter(p[6], self._get_position(p, 6))]

        # Remove quotes from the process name
        process_name = p[3]

        p[0] = ProcessDefinition(process_name, parameters, p[9], self._get_position(p, 1))

    def p_parameter_list(self, p):
        """parameter_list : parameter_list AND ID
                          | ID"""
        if len(p) == 4:
            p[0] = p[1] + [Parameter(p[3], self._get_position(p, 3))]
        else:
            p[0] = [Parameter(p[1], self._get_position(p, 1))]

    def p_expression(self, p):
        """expression : literal
                      | variable_reference
                      | binary_operation
                      | function_call
                      | list_expression
                      | dictionary_expression
                      | index_access"""
        p[0] = p[1]

    def p_literal(self, p):
        """literal : STRING
                   | NUMBER
                   | BOOLEAN"""
        if isinstance(p[1], str):
            p[0] = StringLiteral(p[1], self._get_position(p, 1))
        elif isinstance(p[1], (int, float)):
            p[0] = NumberLiteral(p[1], self._get_position(p, 1))
        elif isinstance(p[1], bool):
            p[0] = BooleanLiteral(p[1], self._get_position(p, 1))

    def p_variable_reference(self, p):
        """variable_reference : ID"""
        p[0] = VariableReference(p[1], self._get_position(p, 1))

    def p_binary_operation(self, p):
        """binary_operation : expression PLUS expression
                            | expression MINUS expression
                            | expression MULTIPLIED expression
                            | expression MULTIPLIED BY expression
                            | expression DIVIDED expression
                            | expression DIVIDED BY expression
                            | expression MODULO expression
                            | expression GREATER expression
                            | expression GREATER THAN expression
                            | expression LESS expression
                            | expression LESS THAN expression
                            | expression EQUAL expression
                            | expression EQUAL TO expression
                            | expression NOT_EQUAL expression
                            | expression NOT_EQUAL TO expression
                            | expression AND expression
                            | expression OR expression"""
        # Handle variations of operators
        if len(p) == 4:
            # Simple operator: expr plus expr, expr and expr, etc.
            p[0] = BinaryOperation(p[1], p[2], p[3], self._get_position(p, 2))
        elif len(p) == 5:
            # Extended operator: expr greater than expr, expr equal to expr, etc.
            if p[2] == "GREATER" and p[3] == "THAN":
                operator = "GREATER"
            elif p[2] == "LESS" and p[3] == "THAN":
                operator = "LESS"
            elif p[2] == "EQUAL" and p[3] == "TO":
                operator = "EQUAL"
            elif p[2] == "NOT_EQUAL" and p[3] == "TO":
                operator = "NOT_EQUAL"
            else:
                operator = p[2]  # For other cases
            p[0] = BinaryOperation(p[1], operator, p[4], self._get_position(p, 2))
        elif len(p) == 6:
            # Extended operator with BY: expr multiplied by expr, expr divided by expr
            if p[2] == "MULTIPLIED" and p[3] == "BY":
                operator = "MULTIPLIED"
            elif p[2] == "DIVIDED" and p[3] == "BY":
                operator = "DIVIDED"
            else:
                operator = p[2]  # For other cases
            p[0] = BinaryOperation(p[1], operator, p[4], self._get_position(p, 2))

    def p_function_call(self, p):
        """function_call : ID WITH argument_list
                         | ID WITH named_argument_list
                         | ID WITH argument_list AND named_argument_list"""
        if len(p) == 4:
            # Function call with either positional or named arguments
            if isinstance(p[3][0], tuple):
                # Named arguments only
                named_args = dict(p[3])
                p[0] = FunctionCall(p[1], [], named_args, self._get_position(p, 1))
            else:
                # Positional arguments only
                p[0] = FunctionCall(p[1], p[3], {}, self._get_position(p, 1))
        else:
            # Function call with both positional and named arguments
            positional_args = p[3]
            named_args = dict(p[5])
            p[0] = FunctionCall(p[1], positional_args, named_args, self._get_position(p, 1))

    def p_argument_list(self, p):
        """argument_list : expression
                         | argument_list AND expression"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_named_argument_list(self, p):
        """named_argument_list : ID AS expression
                               | named_argument_list AND ID AS expression"""
        if len(p) == 4:
            p[0] = [(p[1], p[3])]
        else:
            p[0] = p[1] + [(p[3], p[5])]

    def p_list_expression(self, p):
        """list_expression : LBRACKET expression_list RBRACKET
                           | LBRACKET RBRACKET"""
        if len(p) == 4:
            p[0] = ListExpression(p[2], self._get_position(p, 1))
        else:
            p[0] = ListExpression([], self._get_position(p, 1))

    def p_expression_list(self, p):
        """expression_list : expression
                           | expression_list COMMA expression"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_dictionary_expression(self, p):
        """dictionary_expression : dictionary_with_entries
                                 | dictionary_empty"""
        p[0] = p[1]

    def p_dictionary_with_entries(self, p):
        """dictionary_with_entries : LBRACKET dictionary_entry_list RBRACKET"""
        p[0] = DictionaryExpression(p[2], self._get_position(p, 1))

    def p_dictionary_empty(self, p):
        """dictionary_empty : LBRACKET COLON RBRACKET"""
        p[0] = DictionaryExpression([], self._get_position(p, 1))

    def p_dictionary_entry_list(self, p):
        """dictionary_entry_list : dictionary_entry
                                 | dictionary_entry_list COMMA dictionary_entry"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_dictionary_entry(self, p):
        """dictionary_entry : expression COLON expression"""
        p[0] = DictionaryEntry(p[1], p[3], self._get_position(p, 2))

    def p_index_access(self, p):
        """index_access : expression AT index expression
                        | expression AT ID expression"""
        target = p[1]
        index = p[4]
        p[0] = IndexAccess(target, index, self._get_position(p, 2))

    def p_error(self, p):
        if p:
            print(f"Syntax error at '{p.value}', line {p.lineno}")
        else:
            print("Syntax error at EOF")

    def _get_position(self, p, index):
        """Get position information for a token."""
        token = p.slice[index]
        return Position(token.lineno, token.lexpos)