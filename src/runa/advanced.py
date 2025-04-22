"""
Advanced language features for the Runa programming language.

This module integrates the pattern matching, asynchronous programming,
functional programming, and enhanced type system features into the Runa language.
"""
from src.runa.parser import RunaParser
from src.runa.analyzer import SemanticAnalyzer
from src.runa.generator import PyCodeGenerator
from src.runa.ast.visitors import Visitor

from src.runa.patterns import integrate_pattern_matching
from src.runa.sync import integrate_async_support
from src.runa.functional import integrate_functional_programming
from src.runa.types import integrate_type_system


def create_advanced_parser():
    """
    Create a parser with all advanced language features.

    Returns:
        A parser that supports all advanced language features.
    """
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    # Integrate pattern matching
    parser_class, visitor_class, generator_class = integrate_pattern_matching(
        parser_class, visitor_class, generator_class
    )

    # Integrate asynchronous programming
    parser_class, visitor_class, generator_class = integrate_async_support(
        parser_class, visitor_class, generator_class
    )

    # Integrate functional programming
    parser_class, visitor_class, generator_class = integrate_functional_programming(
        parser_class, visitor_class, generator_class
    )

    # Integrate enhanced type system
    parser_class, visitor_class, generator_class = integrate_type_system(
        parser_class, visitor_class, generator_class
    )

    return parser_class()


def create_advanced_analyzer():
    """
    Create a semantic analyzer compatible with all advanced language features.

    Returns:
        A semantic analyzer for advanced Runa code.
    """
    return SemanticAnalyzer()


def create_advanced_generator():
    """
    Create a code generator with all advanced language features.

    Returns:
        A code generator that supports all advanced language features.
    """
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    # Integrate pattern matching
    parser_class, visitor_class, generator_class = integrate_pattern_matching(
        parser_class, visitor_class, generator_class
    )

    # Integrate asynchronous programming
    parser_class, visitor_class, generator_class = integrate_async_support(
        parser_class, visitor_class, generator_class
    )

    # Integrate functional programming
    parser_class, visitor_class, generator_class = integrate_functional_programming(
        parser_class, visitor_class, generator_class
    )

    # Integrate enhanced type system
    parser_class, visitor_class, generator_class = integrate_type_system(
        parser_class, visitor_class, generator_class
    )

    return generator_class()


def parse_advanced(source):
    """
    Parse a Runa source code string with all advanced language features.

    Args:
        source: The Runa source code as a string

    Returns:
        The AST representing the parsed source
    """
    parser = create_advanced_parser()
    return parser.parse(source)


def analyze_advanced(ast):
    """
    Perform semantic analysis on an AST with all advanced language features.

    Args:
        ast: The AST to analyze

    Returns:
        Whether the AST is semantically valid

    Side effects:
        Updates the analyzer's errors and warnings
    """
    analyzer = create_advanced_analyzer()
    return analyzer.analyze(ast)


def generate_advanced(ast):
    """
    Generate Python code from an AST with all advanced language features.

    Args:
        ast: The AST to generate code from

    Returns:
        The generated Python code as a string
    """
    generator = create_advanced_generator()
    return generator.generate(ast)


def transpile_advanced(source):
    """
    Transpile Runa source code with all advanced language features to Python.

    Args:
        source: The Runa source code as a string

    Returns:
        A tuple (python_code, valid, errors, warnings) where:
        - python_code: The generated Python code (or None if analysis failed)
        - valid: A boolean indicating if the code is valid
        - errors: A list of error messages
        - warnings: A list of warning messages
    """
    # Parse the source code
    ast = parse_advanced(source)

    if not ast:
        return None, False, ["Failed to parse the source code"], []

    # Perform semantic analysis
    analyzer = create_advanced_analyzer()
    valid = analyzer.analyze(ast)
    errors = analyzer.errors
    warnings = analyzer.warnings

    if not valid:
        return None, False, errors, warnings

    # Generate Python code
    generator = create_advanced_generator()
    code = generator.generate(ast)

    return code, True, errors, warnings