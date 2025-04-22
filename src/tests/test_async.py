"""
Tests for the asynchronous programming functionality.
"""
import os
import pytest
import asyncio
from src.runa.parser import RunaParser
from src.runa.analyzer import SemanticAnalyzer
from src.runa.generator import PyCodeGenerator
from src.runa.sync import integrate_async_support
from src.runa.ast.visitors import Visitor


def test_async_integration():
    """Test integration of async components."""
    # Get the original classes
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    # Integrate async support
    extended_parser, extended_visitor, extended_generator = integrate_async_support(
        parser_class, visitor_class, generator_class
    )

    # Verify that the classes were extended
    assert hasattr(extended_parser, 'p_async_process_definition')
    assert hasattr(extended_visitor, 'visit_AsyncProcessDefinition')
    assert hasattr(extended_generator, 'visit_AsyncProcessDefinition')


def test_async_parse():
    """Test parsing of async expressions."""
    # Create a parser with async support
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    extended_parser, _, _ = integrate_async_support(
        parser_class, visitor_class, generator_class
    )

    # Create an instance of the extended parser
    parser = extended_parser()

    # Parse a simple async function
    source = """
    Async Process called "fetch_data" that takes url:
        Let result be await some_api_call with url as url
        Return result
    """

    ast = parser.parse(source)

    # Verify the AST
    assert ast is not None
    assert len(ast.statements) == 1

    # Check that the statement is an AsyncProcessDefinition
    from src.runa.sync.nodes import AsyncProcessDefinition
    assert isinstance(ast.statements[0], AsyncProcessDefinition)

    # Check the function name and parameters
    assert ast.statements[0].name == "fetch_data"
    assert len(ast.statements[0].parameters) == 1
    assert ast.statements[0].parameters[0].name == "url"


def test_async_code_generation():
    """Test code generation for async expressions."""
    # Create a parser, analyzer, and generator with async support
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    extended_parser, _, extended_generator = integrate_async_support(
        parser_class, visitor_class, generator_class
    )

    # Create instances
    parser = extended_parser()
    analyzer = SemanticAnalyzer()  # No need to extend the analyzer
    generator = extended_generator()

    # Parse a simple async function
    source = """
    Async Process called "fetch_data" that takes url:
        Let result be await some_api_call with url as url
        Return result
    """

    ast = parser.parse(source)

    # Verify the AST can be analyzed
    valid = analyzer.analyze(ast)
    assert valid

    # Generate code
    code = generator.generate(ast)

    # Verify code contains async/await
    assert "async def fetch_data(url):" in code
    assert "result = await some_api_call(url=url)" in code
    assert "return result" in code


def test_async_for_each():
    """Test async for-each statement."""
    # Create a parser with async support
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    extended_parser, _, extended_generator = integrate_async_support(
        parser_class, visitor_class, generator_class
    )

    # Create instances
    parser = extended_parser()
    analyzer = SemanticAnalyzer()
    generator = extended_generator()

    # Parse a simple async for-each
    source = """
    Async Process called "process_items" that takes items:
        Async For each item in items:
            Let result be await process_item with item as item
            Display result
    """

    ast = parser.parse(source)

    # Verify the AST can be analyzed
    valid = analyzer.analyze(ast)
    assert valid

    # Generate code
    code = generator.generate(ast)

    # Verify code contains async for
    assert "async def process_items(items):" in code
    assert "async for item in items:" in code


@pytest.mark.asyncio
async def test_async_runtime():
    """Test the async runtime functions."""
    from src.runa.sync.runtime import async_map, async_filter, async_reduce

    # Test async_map with a sync function
    async def test_map():
        numbers = [1, 2, 3, 4, 5]
        result = await async_map(lambda x: x * 2, numbers)
        assert result == [2, 4, 6, 8, 10]

    await test_map()

    # Test async_map with an async function
    async def test_map_async():
        numbers = [1, 2, 3, 4, 5]

        async def double(x):
            await asyncio.sleep(0.01)  # Small delay to simulate async work
            return x * 2

        result = await async_map(double, numbers)
        assert result == [2, 4, 6, 8, 10]

    await test_map_async()

    # Test async_filter with a sync function
    async def test_filter():
        numbers = [1, 2, 3, 4, 5]
        result = await async_filter(lambda x: x % 2 == 0, numbers)
        assert result == [2, 4]

    await test_filter()

    # Test async_filter with an async function
    async def test_filter_async():
        numbers = [1, 2, 3, 4, 5]

        async def is_even(x):
            await asyncio.sleep(0.01)  # Small delay to simulate async work
            return x % 2 == 0

        result = await async_filter(is_even, numbers)
        assert result == [2, 4]

    await test_filter_async()

    # Test async_reduce with a sync function
    async def test_reduce():
        numbers = [1, 2, 3, 4, 5]
        result = await async_reduce(lambda a, b: a + b, numbers)
        assert result == 15

    await test_reduce()

    # Test async_reduce with an async function
    async def test_reduce_async():
        numbers = [1, 2, 3, 4, 5]

        async def add(a, b):
            await asyncio.sleep(0.01)  # Small delay to simulate async work
            return a + b

        result = await async_reduce(add, numbers)
        assert result == 15

    await test_reduce_async()


def test_async_example():
    """Test the async example file."""
    # Read the async example
    example_path = os.path.join(os.path.dirname(__file__), 'examples', 'async.runa')
    with open(example_path, 'r') as f:
        source = f.read()

    # Create a parser, analyzer, and generator with async support
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    extended_parser, _, extended_generator = integrate_async_support(
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

    # Verify code contains async/await
    assert "import asyncio" in code
    assert "async def fetch_data(url):" in code
    assert "await asyncio.sleep(seconds=1)" in code
    assert "async def fetch_multiple(urls):" in code
    assert "async for url in urls:" in code

    # The code should run, but we won't actually execute it in tests
    # as it would require setting up an event loop and running async code