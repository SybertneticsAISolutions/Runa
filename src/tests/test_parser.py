import pytest
from src.runa.parser import RunaParser
from src.runa.ast.nodes import *


def test_parser_variable_declaration():
    """Test parsing a variable declaration."""
    parser = RunaParser()

    ast = parser.parse('Let x be 10')

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], Declaration)
    assert ast.statements[0].name == 'x'
    assert isinstance(ast.statements[0].value, NumberLiteral)
    assert ast.statements[0].value.value == 10


def test_parser_if_statement():
    """Test parsing an if statement."""
    parser = RunaParser()

    ast = parser.parse('''If x is greater than 10:
    Display "x is greater than 10"
Otherwise:
    Display "x is not greater than 10"''')

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], IfStatement)

    # Check then block
    assert len(ast.statements[0].then_block) == 1
    assert isinstance(ast.statements[0].then_block[0], DisplayStatement)

    # Check else block
    assert len(ast.statements[0].else_block) == 1
    assert isinstance(ast.statements[0].else_block[0], DisplayStatement)


def test_parser_function_definition():
    """Test parsing a process (function) definition."""
    parser = RunaParser()

    ast = parser.parse('''Process called "add" that takes a and b:
    Return a plus b''')

    assert isinstance(ast, Program)
    assert len(ast.statements) == 1
    assert isinstance(ast.statements[0], ProcessDefinition)
    assert ast.statements[0].name == 'add'
    assert len(ast.statements[0].parameters) == 2
    assert ast.statements[0].parameters[0].name == 'a'
    assert ast.statements[0].parameters[1].name == 'b'