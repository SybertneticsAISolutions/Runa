import pytest
from src.runa.parser import RunaParser
from src.runa.analyzer import SemanticAnalyzer


def test_analyzer_variable_declaration():
    """Test analyzing a variable declaration."""
    parser = RunaParser()
    analyzer = SemanticAnalyzer()

    ast = parser.parse('Let x be 10')
    valid = analyzer.analyze(ast)

    assert valid
    assert len(analyzer.errors) == 0


def test_analyzer_undefined_variable():
    """Test analyzing a reference to an undefined variable."""
    parser = RunaParser()
    analyzer = SemanticAnalyzer()

    ast = parser.parse('Display y')
    valid = analyzer.analyze(ast)

    assert not valid
    assert len(analyzer.errors) == 1
    assert "undefined variable" in analyzer.errors[0]


def test_analyzer_duplicate_variable():
    """Test analyzing a duplicate variable declaration."""
    parser = RunaParser()
    analyzer = SemanticAnalyzer()

    ast = parser.parse('''Let x be 10
Let x be 20''')
    valid = analyzer.analyze(ast)

    assert not valid
    assert len(analyzer.errors) == 1
    assert "already defined" in analyzer.errors[0]