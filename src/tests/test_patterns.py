"""
Tests for the pattern matching functionality.
"""
import os
import pytest
from src.runa.parser import RunaParser
from src.runa.analyzer import SemanticAnalyzer
from src.runa.generator import PyCodeGenerator
from src.runa.patterns import integrate_pattern_matching
from src.runa.ast.visitors import Visitor


def test_pattern_matching_integration():
    """Test integration of pattern matching components."""
    # Get the original classes
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    # Integrate pattern matching
    extended_parser, extended_visitor, extended_generator = integrate_pattern_matching(
        parser_class, visitor_class, generator_class
    )

    # Verify that the classes were extended
    assert hasattr(extended_parser, 'p_match_statement')
    assert hasattr(extended_visitor, 'visit_MatchExpression')
    assert hasattr(extended_generator, 'visit_MatchExpression')


def test_pattern_matching_parse():
    """Test parsing of pattern matching expressions."""
    # Create a parser with pattern matching
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    extended_parser, _, _ = integrate_pattern_matching(
        parser_class, visitor_class, generator_class
    )

    # Create an instance of the extended parser
    parser = extended_parser()

    # Parse a simple pattern matching statement
    source = """
    Match value:
        When "hello":
            Display "Matched hello"
        When 42:
            Display "Matched 42"
        When _:
            Display "Matched wildcard"
    """

    ast = parser.parse(source)

    # Verify the AST
    assert ast is not None
    assert len(ast.statements) == 1

    # Check that the statement is a MatchExpression
    from src.runa.patterns.nodes import MatchExpression
    assert isinstance(ast.statements[0], MatchExpression)

    # Check the number of cases
    assert len(ast.statements[0].cases) == 3


def test_pattern_matching_code_generation():
    """Test code generation for pattern matching."""
    # Create a parser, analyzer, and generator with pattern matching
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    extended_parser, extended_visitor, extended_generator = integrate_pattern_matching(
        parser_class, visitor_class, generator_class
    )

    # Create instances
    parser = extended_parser()
    analyzer = SemanticAnalyzer()  # No need to extend the analyzer
    generator = extended_generator()

    # Parse a simple pattern matching statement
    source = """
    Let value be "test"
    Match value:
        When "hello":
            Display "Matched hello"
        When _:
            Display "Matched wildcard"
    """

    ast = parser.parse(source)

    # Verify the AST can be analyzed
    valid = analyzer.analyze(ast)
    assert valid

    # Generate code
    code = generator.generate(ast)

    # Verify code contains pattern matching logic
    assert "value = \"test\"" in code
    assert "_match_value_" in code
    assert "if _match_value_" in code
    assert "print(\"Matched hello\")" in code
    assert "print(\"Matched wildcard\")" in code


def test_pattern_matching_example():
    """Test the pattern matching example file."""
    # Read the pattern matching example
    example_path = os.path.join(os.path.dirname(__file__), 'examples', 'patterns.runa')
    with open(example_path, 'r') as f:
        source = f.read()

    # Create a parser, analyzer, and generator with pattern matching
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    extended_parser, _, extended_generator = integrate_pattern_matching(
        parser_class, visitor_class, generator_class
    )

    # Create instances
    parser = extended_parser()
    analyzer = SemanticAnalyzer()
    generator = extended_generator()

    # Parse the example
    ast = parser.parse(source)

    # Verify the AST can be analyzed
    valid = analyzer.analyze(ast)
    assert valid

    # Generate code
    code = generator.generate(ast)

    # Verify code contains pattern matching logic
    assert "circle = {" in code
    assert "rectangle = {" in code
    assert "triangle = {" in code
    assert "def calculate_area(shape):" in code
    assert "_match_value_" in code

    # Verify pattern matching cases
    assert "\"type\"] == \"circle\"" in code
    assert "\"type\"] == \"rectangle\"" in code
    assert "\"type\"] == \"triangle\"" in code

    # Verify variable bindings in patterns
    assert "r = _match_value_[\"radius\"]" in code
    assert "w = _match_value_[\"width\"]" in code
    assert "h = _match_value_[\"height\"]" in code

    # Create a temporary Python file
    temp_file = "temp_patterns.py"
    with open(temp_file, 'w') as f:
        f.write(code)

    try:
        # Execute the generated code to check for runtime errors
        # This is a simple smoke test - not checking output values
        exec_namespace = {}
        with open(temp_file, 'r') as f:
            exec(f.read(), exec_namespace)

        # Verify functions were defined
        assert 'calculate_area' in exec_namespace
        assert 'sum_first_two' in exec_namespace

        # Verify the results
        assert exec_namespace['circle_area'] == pytest.approx(78.53975)
        assert exec_namespace['rectangle_area'] == 60
        assert exec_namespace['triangle_area'] == pytest.approx(6.0)

    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)