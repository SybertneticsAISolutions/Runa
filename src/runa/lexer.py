import ply.lex as lex
import re


class RunaLexer:
    """Lexer for the Runa programming language."""

    # List of token names
    tokens = (
        # Keywords
        'LET', 'SET', 'BE', 'TO', 'AS', 'IF', 'OTHERWISE', 'FOR', 'EACH', 'IN',
        'PROCESS', 'CALLED', 'THAT', 'TAKES', 'RETURN', 'DISPLAY', 'WITH',
        'DEFINE', 'CONTAINING', 'WHEN', 'WHILE', 'IS', 'NOT', 'AND', 'OR',

        # Operators
        'PLUS', 'MINUS', 'MULTIPLIED', 'DIVIDED', 'MODULO',
        'GREATER', 'LESS', 'EQUAL', 'NOT_EQUAL',

        # Delimiters
        'COLON', 'COMMA', 'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET',
        'INDENT', 'DEDENT', 'NEWLINE',

        # Literals
        'STRING', 'NUMBER', 'BOOLEAN',

        # Identifier
        'ID',
    )

    # Regular expression rules for simple tokens
    t_COLON = r':'
    t_COMMA = r','
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'

    # Keywords
    def t_LET(self, t):
        r'Let'
        return t

    def t_SET(self, t):
        r'Set'
        return t

    def t_BE(self, t):
        r'be'
        return t

    def t_TO(self, t):
        r'to'
        return t

    def t_AS(self, t):
        r'as'
        return t

    def t_IF(self, t):
        r'If'
        return t

    def t_OTHERWISE(self, t):
        r'Otherwise'
        return t

    def t_FOR(self, t):
        r'For'
        return t

    def t_EACH(self, t):
        r'each'
        return t

    def t_IN(self, t):
        r'in'
        return t

    def t_PROCESS(self, t):
        r'Process'
        return t

    def t_CALLED(self, t):
        r'called'
        return t

    def t_THAT(self, t):
        r'that'
        return t

    def t_TAKES(self, t):
        r'takes'
        return t

    def t_RETURN(self, t):
        r'Return'
        return t

    def t_DISPLAY(self, t):
        r'Display'
        return t

    def t_WITH(self, t):
        r'with'
        return t

    def t_DEFINE(self, t):
        r'Define'
        return t

    def t_CONTAINING(self, t):
        r'containing'
        return t

    def t_WHEN(self, t):
        r'When'
        return t

    def t_WHILE(self, t):
        r'While'
        return t

    def t_IS(self, t):
        r'is'
        return t

    def t_NOT(self, t):
        r'not'
        return t

    def t_AND(self, t):
        r'and'
        return t

    def t_OR(self, t):
        r'or'
        return t

    # Comparison operators
    def t_GREATER(self, t):
        r'greater(\s+than)?'
        return t

    def t_LESS(self, t):
        r'less(\s+than)?'
        return t

    def t_EQUAL(self, t):
        r'equal(\s+to)?'
        return t

    def t_NOT_EQUAL(self, t):
        r'not\s+equal(\s+to)?'
        return t

    # Arithmetic operators
    def t_PLUS(self, t):
        r'plus'
        return t

    def t_MINUS(self, t):
        r'minus'
        return t

    def t_MULTIPLIED(self, t):
        r'multiplied(\s+by)?'
        return t

    def t_DIVIDED(self, t):
        r'divided(\s+by)?'
        return t

    def t_MODULO(self, t):
        r'modulo'
        return t

    # String literal
    def t_STRING(self, t):
        r'"[^"]*"'
        t.value = t.value[1:-1]  # Remove the quotes
        return t

    # Number literal
    def t_NUMBER(self, t):
        r'\d+(\.\d+)?'
        if '.' in t.value:
            t.value = float(t.value)
        else:
            t.value = int(t.value)
        return t

    # Boolean literal
    def t_BOOLEAN(self, t):
        r'True|False'
        t.value = (t.value == 'True')
        return t

    # Identifier
    def t_ID(self, t):
        r'[a-zA-Z][a-zA-Z0-9_]*'
        return t

    # Define a rule so we can track line numbers
    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        return t

    # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t'

    # Error handling rule
    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
        t.lexer.skip(1)

    # Build the lexer
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

        # Initialize indentation tracking
        self.lexer.indentation_stack = [0]
        self.token_queue = []

    def input(self, data):
        self.lexer.input(data)
        self.token_queue = []

    def token(self):
        # Return queued tokens first
        if self.token_queue:
            return self.token_queue.pop(0)

        # Get the next token from the lexer
        token = self.lexer.token()

        # Handle indentation after newlines
        if token and token.type == 'NEWLINE':
            # Calculate the indentation of the next line
            current_pos = self.lexer.lexpos
            line_start = current_pos - 1
            while line_start >= 0 and self.lexer.lexdata[line_start] != '\n':
                line_start -= 1

            indent = 0
            for i in range(line_start + 1, current_pos):
                if self.lexer.lexdata[i] == ' ':
                    indent += 1
                elif self.lexer.lexdata[i] == '\t':
                    indent += 4  # Consider a tab as 4 spaces

            # Compare with the current indentation level
            current_indent = self.lexer.indentation_stack[-1]

            if indent > current_indent:
                # Increase indentation level
                self.lexer.indentation_stack.append(indent)
                # Add INDENT token to queue
                indent_token = lex.LexToken()
                indent_token.type = 'INDENT'
                indent_token.value = None
                indent_token.lineno = token.lineno
                indent_token.lexpos = token.lexpos
                self.token_queue.append(indent_token)

            elif indent < current_indent:
                # Decrease indentation level, possibly multiple levels
                while indent < self.lexer.indentation_stack[-1]:
                    self.lexer.indentation_stack.pop()
                    # Add DEDENT token to queue
                    dedent_token = lex.LexToken()
                    dedent_token.type = 'DEDENT'
                    dedent_token.value = None
                    dedent_token.lineno = token.lineno
                    dedent_token.lexpos = token.lexpos
                    self.token_queue.append(dedent_token)

            # Always return the NEWLINE token first
            return token

        return token