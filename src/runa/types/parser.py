"""
Parser for the enhanced type system in Runa.
This module extends the main parser with type annotation capabilities.
"""
from nodes import (
    Type, PrimitiveType, AnyType, UnionType, ListType, DictionaryType,
    FunctionType, GenericType, ParameterizedType, TypeAlias,
    TypedDeclaration, TypedParameter, TypedProcessDefinition
)


def extend_parser(parser_class):
    """
    Extend the parser class with enhanced type system capabilities.

    This function adds new grammar rules to the parser.
    """
    # Add tokens for type system
    if 'TYPE' not in parser_class.tokens:
        parser_class.tokens = parser_class.tokens + (
            'TYPE', 'ANY', 'UNION', 'LPAREN', 'RPAREN', 'ARROW',
            'LBRACKET', 'RBRACKET', 'COLON', 'COMMA', 'AMP', 'PIPE',
            'RETURNS'
        )

    # Add lexer rules for type system tokens
    def t_TYPE(self, t):
        r'Type'
        return t

    def t_ANY(self, t):
        r'Any'
        return t

    def t_UNION(self, t):
        r'Union'
        return t

    def t_ARROW(self, t):
        r'->'
        return t

    def t_AMP(self, t):
        r'&'
        return t

    def t_PIPE(self, t):
        r'\|'
        return t

    def t_RETURNS(self, t):
        r'returns'
        return t

    # Add these methods to the lexer if they don't already exist
    if not hasattr(parser_class.lexer.__class__, 't_TYPE'):
        parser_class.lexer.__class__.t_TYPE = t_TYPE

    if not hasattr(parser_class.lexer.__class__, 't_ANY'):
        parser_class.lexer.__class__.t_ANY = t_ANY

    if not hasattr(parser_class.lexer.__class__, 't_UNION'):
        parser_class.lexer.__class__.t_UNION = t_UNION

    if not hasattr(parser_class.lexer.__class__, 't_ARROW'):
        parser_class.lexer.__class__.t_ARROW = t_ARROW

    if not hasattr(parser_class.lexer.__class__, 't_AMP'):
        parser_class.lexer.__class__.t_AMP = t_AMP

    if not hasattr(parser_class.lexer.__class__, 't_PIPE'):
        parser_class.lexer.__class__.t_PIPE = t_PIPE

    if not hasattr(parser_class.lexer.__class__, 't_RETURNS'):
        parser_class.lexer.__class__.t_RETURNS = t_RETURNS

    # Add grammar rules for type system

    def p_statement_type_alias(self, p):
        """statement : TYPE ID IS type"""
        p[0] = TypeAlias(p[2], p[4], self._get_position(p, 1))

    def p_statement_typed_declaration(self, p):
        """statement : LET ID LPAREN type RPAREN BE expression"""
        p[0] = TypedDeclaration(p[2], p[4], p[7], self._get_position(p, 1))

    def p_statement_typed_process(self, p):
        """statement : PROCESS CALLED STRING THAT TAKES typed_parameter_list RETURNS LPAREN type RPAREN COLON INDENT statements DEDENT
                     | PROCESS CALLED STRING THAT TAKES ID RETURNS LPAREN type RPAREN COLON INDENT statements DEDENT
                     | PROCESS LBRACKET generic_param_list RBRACKET CALLED STRING THAT TAKES typed_parameter_list RETURNS LPAREN type RPAREN COLON INDENT statements DEDENT
                     | PROCESS LBRACKET generic_param_list RBRACKET CALLED STRING THAT TAKES ID RETURNS LPAREN type RPAREN COLON INDENT statements DEDENT"""
        if p[1] == 'Process' and p[2] == 'called':
            # Process without generic parameters
            process_name = p[3]

            if isinstance(p[6], list):
                # Process with multiple parameters
                parameters = p[6]
                return_type = p[9]
                body = p[13]
            else:
                # Process with a single parameter
                parameters = [TypedParameter(p[6], PrimitiveType('Any', self._get_position(p, 6)), self._get_position(p, 6))]
                return_type = p[9]
                body = p[13]

            p[0] = TypedProcessDefinition(process_name, parameters, return_type, body, None, self._get_position(p, 1))
        else:
            # Process with generic parameters
            generic_params = p[3]
            process_name = p[6]

            if isinstance(p[9], list):
                # Process with multiple parameters
                parameters = p[9]
                return_type = p[12]
                body = p[16]
            else:
                # Process with a single parameter
                parameters = [TypedParameter(p[9], PrimitiveType('Any', self._get_position(p, 9)), self._get_position(p, 9))]
                return_type = p[12]
                body = p[16]

            p[0] = TypedProcessDefinition(process_name, parameters, return_type, body, generic_params, self._get_position(p, 1))

    def p_typed_parameter_list(self, p):
        """typed_parameter_list : typed_parameter
                                | typed_parameter_list AND typed_parameter"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_typed_parameter(self, p):
        """typed_parameter : ID LPAREN type RPAREN"""
        p[0] = TypedParameter(p[1], p[3], self._get_position(p, 1))

    def p_generic_param_list(self, p):
        """generic_param_list : generic_param
                              | generic_param_list COMMA generic_param"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_generic_param(self, p):
        """generic_param : ID
                         | ID COLON type"""
        if len(p) == 2:
            p[0] = GenericType(p[1], None, self._get_position(p, 1))
        else:
            p[0] = GenericType(p[1], [p[3]], self._get_position(p, 1))

    def p_type(self, p):
        """type : primitive_type
                | any_type
                | union_type
                | list_type
                | dictionary_type
                | function_type
                | generic_type
                | parameterized_type"""
        p[0] = p[1]

    def p_primitive_type(self, p):
        """primitive_type : ID"""
        p[0] = PrimitiveType(p[1], self._get_position(p, 1))

    def p_any_type(self, p):
        """any_type : ANY"""
        p[0] = AnyType(self._get_position(p, 1))

    def p_union_type(self, p):
        """union_type : type PIPE type
                      | UNION LBRACKET type_list RBRACKET"""
        if len(p) == 4:
            # Binary union: T1 | T2
            p[0] = UnionType([p[1], p[3]], self._get_position(p, 2))
        else:
            # General union: Union[T1, T2, ...]
            p[0] = UnionType(p[3], self._get_position(p, 1))

    def p_list_type(self, p):
        """list_type : LIST LBRACKET type RBRACKET"""
        p[0] = ListType(p[3], self._get_position(p, 1))

    def p_dictionary_type(self, p):
        """dictionary_type : DICTIONARY LBRACKET type COMMA type RBRACKET"""
        p[0] = DictionaryType(p[3], p[5], self._get_position(p, 1))

    def p_function_type(self, p):
        """function_type : LPAREN type_list RPAREN ARROW type
                         | LPAREN RPAREN ARROW type"""
        if len(p) == 6:
            # Function with parameters
            p[0] = FunctionType(p[2], p[5], self._get_position(p, 1))
        else:
            # Function without parameters
            p[0] = FunctionType([], p[4], self._get_position(p, 1))

    def p_generic_type(self, p):
        """generic_type : ID"""
        p[0] = GenericType(p[1], None, self._get_position(p, 1))

    def p_parameterized_type(self, p):
        """parameterized_type : ID LBRACKET type_list RBRACKET"""
        p[0] = ParameterizedType(p[1], p[3], self._get_position(p, 1))

    def p_type_list(self, p):
        """type_list : type
                     | type_list COMMA type"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    # Add new tokens to the lexer token list if they don't already exist
    if 'LIST' not in parser_class.tokens:
        parser_class.tokens = parser_class.tokens + ('LIST', 'DICTIONARY')

    def t_LIST(self, t):
        r'List'
        return t

    def t_DICTIONARY(self, t):
        r'Dictionary'
        return t

    if not hasattr(parser_class.lexer.__class__, 't_LIST'):
        parser_class.lexer.__class__.t_LIST = t_LIST

    if not hasattr(parser_class.lexer.__class__, 't_DICTIONARY'):
        parser_class.lexer.__class__.t_DICTIONARY = t_DICTIONARY

    # Add the new methods to the parser class
    parser_class.p_statement_type_alias = p_statement_type_alias
    parser_class.p_statement_typed_declaration = p_statement_typed_declaration
    parser_class.p_statement_typed_process = p_statement_typed_process
    parser_class.p_typed_parameter_list = p_typed_parameter_list
    parser_class.p_typed_parameter = p_typed_parameter
    parser_class.p_generic_param_list = p_generic_param_list
    parser_class.p_generic_param = p_generic_param
    parser_class.p_type = p_type
    parser_class.p_primitive_type = p_primitive_type
    parser_class.p_any_type = p_any_type
    parser_class.p_union_type = p_union_type
    parser_class.p_list_type = p_list_type
    parser_class.p_dictionary_type = p_dictionary_type
    parser_class.p_function_type = p_function_type
    parser_class.p_generic_type = p_generic_type
    parser_class.p_parameterized_type = p_parameterized_type
    parser_class.p_type_list = p_type_list

    return parser_class