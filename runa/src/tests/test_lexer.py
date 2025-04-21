import pytest
from runa.src.runa.lexer import RunaLexer


def test_lexer_basic():
    """Test basic lexer functionality."""
    lexer = RunaLexer()
    lexer.build()

    lexer.input('Let x be 10')

    tokens = []
    while True:
        token = lexer.token()
        if not token:
            break
        tokens.append(token)

    assert len(tokens) == 4
    assert tokens[0].type == 'LET'
    assert tokens[1].type == 'ID'
    assert tokens[1].value == 'x'
    assert tokens[2].type == 'BE'
    assert tokens[3].type == 'NUMBER'
    assert tokens[3].value == 10


def test_lexer_string():
    """Test lexer with string literals."""
    lexer = RunaLexer()
    lexer.build()

    lexer.input('Let message be "Hello, world!"')

    tokens = []
    while True:
        token = lexer.token()
        if not token:
            break
        tokens.append(token)

    assert len(tokens) == 4
    assert tokens[0].type == 'LET'
    assert tokens[1].type == 'ID'
    assert tokens[1].value == 'message'
    assert tokens[2].type == 'BE'
    assert tokens[3].type == 'STRING'
    assert tokens[3].value == 'Hello, world!'


def test_lexer_indentation():
    """Test lexer with indentation."""
    lexer = RunaLexer()
    lexer.build()

    lexer.input('''If x is greater than 10:
    Display "x is greater than 10"
Otherwise:
    Display "x is not greater than 10"''')

    tokens = []
    while True:
        token = lexer.token()
        if not token:
            break
        tokens.append(token)

    # Check for INDENT and DEDENT tokens
    token_types = [token.type for token in tokens]
    assert 'INDENT' in token_types
    assert 'DEDENT' in token_types