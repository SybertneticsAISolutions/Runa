"""
Tests for the enhanced type system.
"""
import os
import pytest
from src.runa.parser import RunaParser
from src.runa.analyzer import SemanticAnalyzer
from src.runa.generator import PyCodeGenerator
from src.runa.types import integrate_type_system
from src.runa.types.inference import TypeInferer
from src.runa.types.checker import TypeChecker
from src.runa.ast.visitors import Visitor


def test_type_system_integration():
    """Test integration of type system components."""
    # Get the original classes
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    # Integrate type system
    extended_parser, extended_visitor, extended_generator = integrate_type_system(
        parser_class, visitor_class, generator_class
    )

    # Verify that the parser class was extended
    assert hasattr(extended_parser, 'p_statement_type_alias')
    assert hasattr(extended_parser, 'p_statement_typed_declaration')
    assert hasattr(extended_parser, 'p_statement_typed_process')


def test_type_inference():
    """Test type inference."""
    # Create a type inferer
    inferer = TypeInferer()

    # Create a sample program
    parser = RunaParser()
    ast = parser.parse("""
    Let x be 10
    Let y be 3.14
    Let z be "hello"
    Let b be true
    Let numbers be list containing 1, 2, 3
    Let person be dictionary with:
        "name" as "John"
        "age" as 30
    """)

    # Analyze the program
    env = inferer.analyze_program(ast)

    # Verify inferred types
    assert env.get_variable_type("x") == inferer.integer_type
    assert env.get_variable_type("y") == inferer.float_type
    assert env.get_variable_type("z") == inferer.string_type
    assert env.get_variable_type("b") == inferer.boolean_type

    # Check list type
    numbers_type = env.get_variable_type("numbers")
    assert isinstance(numbers_type, inferer.inferer.__class__.ListType)
    assert numbers_type.element_type == inferer.integer_type

    # Check dictionary type
    person_type = env.get_variable_type("person")
    assert isinstance(person_type, inferer.inferer.__class__.DictionaryType)
    assert person_type.key_type == inferer.string_type

    # Mixed list should have Any element type
    ast = parser.parse("Let mixed be list containing 1, 2.5, \"three\"")
    env = inferer.analyze_program(ast)
    mixed_type = env.get_variable_type("mixed")
    assert isinstance(mixed_type, inferer.inferer.__class__.ListType)
    assert isinstance(mixed_type.element_type, inferer.inferer.__class__.AnyType)


def test_type_checker():
    """Test type checking."""
    # Create a type checker
    checker = TypeChecker()

    # Create a typed program with no errors
    parser = RunaParser()
    ast = parser.parse("""
    Let x (Integer) be 10
    Let y (Float) be 3.14
    Let z (String) be "hello"
    
    Process called "add" that takes a (Integer) and b (Integer) returns (Integer):
        Return a plus b
    
    Let result (Integer) be add with a as 5 and b as 7
    """)

    # Check the program
    is_valid = checker.check_program(ast)
    assert is_valid
    assert len(checker.errors) == 0

    # Create a typed program with errors
    ast = parser.parse("""
    Let x (Integer) be 10
    Let y (Float) be 3.14
    
    # Type error: assigning string to integer
    Set x to "hello"
    """)

    # Check the program
    is_valid = checker.check_program(ast)
    assert not is_valid
    assert len(checker.errors) > 0


def test_type_system_parse():
    """Test parsing of type system constructs."""
    # Create a parser with type system support
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    extended_parser, _, _ = integrate_type_system(
        parser_class, visitor_class, generator_class
    )

    # Create an instance of the extended parser
    parser = extended_parser()

    # Parse a type alias
    source = """
    Type UserId is Integer
    """

    ast = parser.parse(source)

    # Verify the AST
    assert ast is not None
    assert len(ast.statements) == 1

    # Check that the statement is a TypeAlias
    from src.runa.types.nodes import TypeAlias, PrimitiveType
    assert isinstance(ast.statements[0], TypeAlias)
    assert ast.statements[0].name == "UserId"
    assert isinstance(ast.statements[0].target_type, PrimitiveType)
    assert ast.statements[0].target_type.name == "Integer"

    # Parse a typed declaration
    source = """
    Let x (Integer) be 10
    """

    ast = parser.parse(source)

    # Verify the AST
    assert ast is not None
    assert len(ast.statements) == 1

    # Check that the statement is a TypedDeclaration
    from src.runa.types.nodes import TypedDeclaration
    assert isinstance(ast.statements[0], TypedDeclaration)
    assert ast.statements[0].name == "x"
    assert isinstance(ast.statements[0].type_annotation, PrimitiveType)
    assert ast.statements[0].type_annotation.name == "Integer"

    # Parse a typed process definition
    source = """
    Process called "add" that takes a (Integer) and b (Integer) returns (Integer):
        Return a plus b
    """

    ast = parser.parse(source)

    # Verify the AST
    assert ast is not None
    assert len(ast.statements) == 1

    # Check that the statement is a TypedProcessDefinition
    from src.runa.types.nodes import TypedProcessDefinition
    assert isinstance(ast.statements[0], TypedProcessDefinition)
    assert ast.statements[0].name == "add"
    assert len(ast.statements[0].parameters) == 2
    assert ast.statements[0].parameters[0].name == "a"
    assert isinstance(ast.statements[0].parameters[0].type_annotation, PrimitiveType)
    assert ast.statements[0].parameters[0].type_annotation.name == "Integer"
    assert isinstance(ast.statements[0].return_type, PrimitiveType)
    assert ast.statements[0].return_type.name == "Integer"


def test_type_system_code_generation():
    """Test code generation for type system."""
    # Create a parser, analyzer, and generator with type system
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    extended_parser, _, extended_generator = integrate_type_system(
        parser_class, visitor_class, generator_class
    )

    # Create instances
    parser = extended_parser()
    analyzer = SemanticAnalyzer()  # No need to extend the analyzer
    generator = extended_generator()

    # Parse a simple type alias
    source = """
    Type UserId is Integer
    """

    ast = parser.parse(source)

    # Verify the AST can be analyzed
    valid = analyzer.analyze(ast)
    assert valid

    # Generate code
    code = generator.generate(ast)

    # Verify code contains type alias as comment
    assert "# Type alias: UserId = Integer" in code

    # Parse a typed declaration
    source = """
    Let x (Integer) be 10
    """

    ast = parser.parse(source)

    # Verify the AST can be analyzed
    valid = analyzer.analyze(ast)
    assert valid

    # Generate code
    code = generator.generate(ast)

    # Verify code contains type annotation as comment
    assert "x = 10  # type: Integer" in code

    # Parse a typed process definition
    source = """
    Process called "add" that takes a (Integer) and b (Integer) returns (Integer):
        Return a plus b
    """

    ast = parser.parse(source)

    # Verify the AST can be analyzed
    valid = analyzer.analyze(ast)
    assert valid

    # Generate code
    code = generator.generate(ast)

    # Verify code contains type annotations as comments
    assert "def add(a, b):  # (Integer, Integer) -> Integer" in code
    assert "return (a + b)" in code


def test_types_example():
    """Test the types example file."""
    # Read the types example
    example_path = os.path.join(os.path.dirname(__file__), 'examples', 'types.runa')
    with open(example_path, 'r') as f:
        source = f.read()

    # Create a parser, analyzer, and generator with type system
    parser_class = RunaParser
    visitor_class = Visitor
    generator_class = PyCodeGenerator

    extended_parser, _, extended_generator = integrate_type_system(
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

    # Verify code contains type aliases
    assert "# Type alias: UserId = Integer" in code
    assert "# Type alias: Username = String" in code

    # Verify code contains typed declarations
    assert "user_id = 12345  # type: UserId" in code
    assert "username = \"johndoe\"  # type: Username" in code

    # Verify code contains typed functions
    assert "def get_user_greeting(name, role):  # (String, UserRole) -> String" in code

    # Create a temporary Python file
    temp_file = "temp_types.py"
    with open(temp_file, 'w') as f:
        f.write(code)

    try:
        # Execute the generated code to check for runtime errors
        exec_namespace = {}
        with open(temp_file, 'r') as f:
            exec(f.read(), exec_namespace)

        # Verify some of the results
        assert exec_namespace['user_id'] == 12345
        assert exec_namespace['username'] == "johndoe"
        assert exec_namespace['user_role'] == "admin"
        assert "Admin" in exec_namespace['greeting']
        assert exec_namespace['first_number'] == 1
        assert exec_namespace['first_name'] == "Alice"
        assert exec_namespace['doubled_numbers'] == [2, 4, 6, 8, 10]

    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)