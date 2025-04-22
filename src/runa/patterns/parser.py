"""
Parser for pattern matching constructs in Runa.
This module extends the main parser with pattern matching capabilities.
"""
from src.runa.patterns.nodes import (
    Pattern, WildcardPattern, LiteralPattern, VariablePattern,
    ListPattern, DictionaryPattern, RestPattern, TypePattern,
    MatchCase, MatchExpression
)


def extend_parser(parser_class):
    """
    Extend the parser class with pattern matching capabilities.

    This function adds new grammar rules to the parser.
    """
    # Add tokens for pattern matching
    if 'MATCH' not in parser_class.tokens:
        parser_class.tokens = parser_class.tokens + ('MATCH', 'WHEN', 'UNDERSCORE', 'REST')

    # Add lexer rules for pattern matching
    def t_MATCH(self, t):
        r'Match'
        return t

    def t_WHEN(self, t):
        r'When'
        return t

    def t_UNDERSCORE(self, t):
        r'_'
        return t

    def t_REST(self, t):
        r'\.\.\.'
        return t

    # Add these methods to the lexer
    parser_class.lexer.__class__.t_MATCH = t_MATCH
    parser_class.lexer.__class__.t_WHEN = t_WHEN
    parser_class.lexer.__class__.t_UNDERSCORE = t_UNDERSCORE
    parser_class.lexer.__class__.t_REST = t_REST

    # Add grammar rules for pattern matching

    def p_statement_match(self, p):
        """statement : match_statement"""
        p[0] = p[1]

    def p_match_statement(self, p):
        """match_statement : MATCH expression COLON INDENT match_cases DEDENT"""
        p[0] = MatchExpression(p[2], p[5], self._get_position(p, 1))

    def p_match_cases(self, p):
        """match_cases : match_cases match_case
                       | match_case"""
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_match_case(self, p):
        """match_case : WHEN pattern COLON INDENT statements DEDENT"""
        p[0] = MatchCase(p[2], p[5], self._get_position(p, 1))

    def p_pattern(self, p):
        """pattern : wildcard_pattern
                   | literal_pattern
                   | variable_pattern
                   | list_pattern
                   | dictionary_pattern
                   | rest_pattern
                   | type_pattern"""
        p[0] = p[1]

    def p_wildcard_pattern(self, p):
        """wildcard_pattern : UNDERSCORE"""
        p[0] = WildcardPattern(self._get_position(p, 1))

    def p_literal_pattern(self, p):
        """literal_pattern : STRING
                           | NUMBER
                           | BOOLEAN"""
        global value
        if isinstance(p[1], str):
            from src.runa.ast.nodes import StringLiteral
            value = StringLiteral(p[1], self._get_position(p, 1))
        elif isinstance(p[1], (int, float)):
            from src.runa.ast.nodes import NumberLiteral
            value = NumberLiteral(p[1], self._get_position(p, 1))
        elif isinstance(p[1], bool):
            from src.runa.ast.nodes import BooleanLiteral
            value = BooleanLiteral(p[1], self._get_position(p, 1))

        p[0] = LiteralPattern(value, self._get_position(p, 1))

    def p_variable_pattern(self, p):
        """variable_pattern : ID"""
        p[0] = VariablePattern(p[1], self._get_position(p, 1))

    def p_list_pattern(self, p):
        """list_pattern : LBRACKET pattern_list RBRACKET
                       | LBRACKET RBRACKET"""
        if len(p) == 4:
            p[0] = ListPattern(p[2], self._get_position(p, 1))
        else:
            p[0] = ListPattern([], self._get_position(p, 1))

    def p_pattern_list(self, p):
        """pattern_list : pattern
                        | pattern_list COMMA pattern"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_dictionary_pattern(self, p):
        """dictionary_pattern : LBRACKET dictionary_pattern_entries RBRACKET
                              | LBRACKET COLON RBRACKET"""
        if len(p) == 4 and p[2] != ':':
            p[0] = DictionaryPattern(p[2], self._get_position(p, 1))
        else:
            p[0] = DictionaryPattern({}, self._get_position(p, 1))

    def p_dictionary_pattern_entries(self, p):
        """dictionary_pattern_entries : dictionary_pattern_entry
                                       | dictionary_pattern_entries COMMA dictionary_pattern_entry"""
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_dictionary_pattern_entry(self, p):
        """dictionary_pattern_entry : STRING COLON pattern
                                     | ID COLON pattern"""
        # Create a key-value pair for the dictionary pattern
        from src.runa.ast.nodes import StringLiteral, DictionaryEntry
        if isinstance(p[1], str):
            key = StringLiteral(p[1], self._get_position(p, 1))
        else:
            # ID should be treated as a string in this context
            key = StringLiteral(p[1], self._get_position(p, 1))

        p[0] = DictionaryEntry(key, p[3], self._get_position(p, 2))

    def p_rest_pattern(self, p):
        """rest_pattern : REST
                        | REST ID"""
        if len(p) == 2:
            p[0] = RestPattern(None, self._get_position(p, 1))
        else:
            p[0] = RestPattern(p[2], self._get_position(p, 1))

    def p_type_pattern(self, p):
        """type_pattern : ID pattern"""
        p[0] = TypePattern(p[1], self._get_position(p, 1))

    # Add the new methods to the parser class
    parser_class.p_statement_match = p_statement_match
    parser_class.p_match_statement = p_match_statement
    parser_class.p_match_cases = p_match_cases
    parser_class.p_match_case = p_match_case
    parser_class.p_pattern = p_pattern
    parser_class.p_wildcard_pattern = p_wildcard_pattern
    parser_class.p_literal_pattern = p_literal_pattern
    parser_class.p_variable_pattern = p_variable_pattern
    parser_class.p_list_pattern = p_list_pattern
    parser_class.p_pattern_list = p_pattern_list
    parser_class.p_dictionary_pattern = p_dictionary_pattern
    parser_class.p_dictionary_pattern_entries = p_dictionary_pattern_entries
    parser_class.p_dictionary_pattern_entry = p_dictionary_pattern_entry
    parser_class.p_rest_pattern = p_rest_pattern
    parser_class.p_type_pattern = p_type_pattern

    return parser_class