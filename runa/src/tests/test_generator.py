import pytest
from runa.src.runa.parser import RunaParser
from runa.src.runa.analyzer import SemanticAnalyzer
from runa.src.runa.generator import PyCodeGenerator


def test_generator_variable_declaration():
    """Test generating code for a variable declaration."""
    parser = RunaParser()
    analyzer = SemanticAnalyzer()
    generator = PyCodeGenerator()

    ast = parser.parse('Let x be 10')
    valid = analyzer.analyze(ast)
    assert valid

    code = generator.generate(ast)

    assert "# Generated Python code from Runa" in code
    assert "from runa.runtime import *" in code
    assert "x = 10" in code


def test_generator_if_statement():
    """Test generating code for an if statement."""
    parser = RunaParser()
    analyzer = SemanticAnalyzer()
    generator = PyCodeGenerator()

    ast = parser.parse('''Let x be 10
If x is greater than 5:
    Display "x is greater than 5"
Otherwise:
    Display "x is not greater than 5"''')
    valid = analyzer.analyze(ast)
    assert valid

    code = generator.generate(ast)

    assert "if (x > 5):" in code
    assert 'print("x is greater than 5")' in code
    assert 'else:' in code
    assert 'print("x is not greater than 5")' in code


def test_generator_function_definition():
    """Test generating code for a process (function) definition."""
    parser = RunaParser()
    analyzer = SemanticAnalyzer()
    generator = PyCodeGenerator()

    ast = parser.parse('''Process called "add" that takes a and b:
    Return a plus b''')
    valid = analyzer.analyze(ast)
    assert valid

    code = generator.generate(ast)

    assert "def add(a, b):" in code
    assert "return (a + b)" in code