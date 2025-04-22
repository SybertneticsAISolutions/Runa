"""
Tests for the functional programming functionality.
"""
import os
import pytest
from src.runa.parser import RunaParser
from src.runa.analyzer import SemanticAnalyzer
from src.runa.generator import PyCodeGenerator
from src.runa.functional import integrate_functional_programming
from src.runa.ast.visitors import Visitor


def test_functional_integration():
    """Test integration of functional programming components."""
    # Get the original classes
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    # Integrate functional programming
    extended_parser, extended_visitor, extended_generator = integrate_functional_programming(
        parser_class, visitor_class, generator_class
    )

    # Verify that the classes were extended
    assert hasattr(extended_parser, 'p_expression_lambda')
    assert hasattr(extended_visitor, 'visit_LambdaExpression')
    assert hasattr(extended_generator, 'visit_LambdaExpression')


def test_functional_parse():
    """Test parsing of functional programming expressions."""
    # Create a parser with functional programming
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    extended_parser, _, _ = integrate_functional_programming(
        parser_class, visitor_class, generator_class
    )

    # Create an instance of the extended parser
    parser = extended_parser()

    # Parse a simple lambda expression
    source = """
    Let add be Lambda a and b: a plus b
    """

    ast = parser.parse(source)

    # Verify the AST
    assert ast is not None
    assert len(ast.statements) == 1

    # Check that the statement is a Declaration with a LambdaExpression value
    from src.runa.ast.nodes import Declaration
    from src.runa.functional.nodes import LambdaExpression
    assert isinstance(ast.statements[0], Declaration)
    assert isinstance(ast.statements[0].value, LambdaExpression)

    # Check lambda parameters and body
    lambda_expr = ast.statements[0].value
    assert lambda_expr.parameters == ['a', 'b']

    # Parse a pipeline expression
    source = """
    Let result be 5 |> double
    """

    ast = parser.parse(source)

    # Verify the AST
    assert ast is not None
    assert len(ast.statements) == 1

    # Check that the statement is a Declaration with a PipelineExpression value
    from src.runa.functional.nodes import PipelineExpression
    assert isinstance(ast.statements[0], Declaration)
    assert isinstance(ast.statements[0].value, PipelineExpression)


def test_functional_code_generation():
    """Test code generation for functional programming."""
    # Create a parser, analyzer, and generator with functional programming
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    extended_parser, _, extended_generator = integrate_functional_programming(
        parser_class, visitor_class, generator_class
    )

    # Create instances
    parser = extended_parser()
    analyzer = SemanticAnalyzer()  # No need to extend the analyzer
    generator = extended_generator()

    # Parse a simple lambda expression
    source = """
    Let add be Lambda a and b: a plus b
    """

    ast = parser.parse(source)

    # Verify the AST can be analyzed
    valid = analyzer.analyze(ast)
    assert valid

    # Generate code
    code = generator.generate(ast)

    # Verify code contains lambda
    assert "add = lambda a, b: (a + b)" in code

    # Parse a pipeline expression
    source = """
    Process called "double" that takes x:
        Return x multiplied by 2

    Let result be 5 |> double
    """

    ast = parser.parse(source)

    # Verify the AST can be analyzed
    valid = analyzer.analyze(ast)
    assert valid

    # Generate code
    code = generator.generate(ast)

    # Verify code contains pipeline
    assert "def double(x):" in code
    assert "result = pipeline(5, double)" in code


def test_functional_runtime_operations():
    """Test the functional programming runtime operations."""
    from src.runa.functional.operations import (
        pipeline, partial, compose, map_function, filter_function, reduce_function
    )

    # Test pipeline
    def double(x):
        return x * 2

    assert pipeline(5, double) == 10

    # Test partial
    def add(a, b):
        return a + b

    add_five = partial(add, 5)
    assert add_five(10) == 15

    # Test compose
    def square(x):
        return x * x

    square_then_double = compose(double, square)
    assert square_then_double(3) == 18  # (3^2) * 2 = 18

    # Test map_function
    numbers = [1, 2, 3, 4, 5]
    assert map_function(double, numbers) == [2, 4, 6, 8, 10]

    # Test filter_function
    def is_even(x):
        return x % 2 == 0

    assert filter_function(is_even, numbers) == [2, 4]

    # Test reduce_function
    assert reduce_function(add, numbers) == 15
    assert reduce_function(lambda a, b: a * b, numbers, 1) == 120


def test_functional_example():
    """Test the functional programming example file."""
    # Read the functional programming example
    example_path = os.path.join(os.path.dirname(__file__), 'examples', 'functional.runa')
    with open(example_path, 'r') as f:
        source = f.read()

    # Create a parser, analyzer, and generator with functional programming
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    extended_parser, _, extended_generator = integrate_functional_programming(
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

    # Verify code contains functional programming constructs
    assert "def double(x):" in code
    assert "def increment(x):" in code
    assert "def square(x):" in code
    assert "def is_even(x):" in code

    assert "add = lambda a, b: (a + b)" in code
    assert "add_five = lambda x: (x + 5)" in code

    assert "result1 = pipeline(5, pipeline(double, square))" in code
    assert "double_then_square = compose(square, double)" in code
    assert "add_ten = partial(add, a=10)" in code

    assert "doubled_numbers = map_function(double, numbers)" in code
    assert "even_numbers = filter_function(is_even, numbers)" in code
    assert "sum_of_numbers = reduce_function(add, numbers)" in code

    # Create a temporary Python file
    temp_file = "temp_functional.py"
    with open(temp_file, 'w') as f:
        f.write(code)

    try:
        # Execute the generated code to check for runtime errors
        exec_namespace = {}
        with open(temp_file, 'r') as f:
            exec(f.read(), exec_namespace)

        # Verify some of the results
        assert exec_namespace['add'](2, 3) == 5
        assert exec_namespace['add_five'](10) == 15
        assert exec_namespace['result1'] == 100  # (5 * 2)^2 = 100
        assert exec_namespace['double_then_square'](5) == 100
        assert exec_namespace['doubled_numbers'] == [2, 4, 6, 8, 10]
        assert exec_namespace['even_numbers'] == [2, 4]
        assert exec_namespace['sum_of_numbers'] == 15
        assert exec_namespace['product_of_numbers'] == 120

    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)