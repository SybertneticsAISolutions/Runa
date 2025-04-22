"""
Integration tests for advanced language features.
Tests the interaction between pattern matching, asynchronous programming,
functional programming, and the enhanced type system.
"""
import os
import pytest
import asyncio
from src.runa.advanced import (
    create_advanced_parser,
    create_advanced_analyzer,
    create_advanced_generator,
    transpile_advanced
)


def test_advanced_parser():
    """Test that the advanced parser can handle all advanced features."""
    # Create an advanced parser
    parser = create_advanced_parser()

    # Source code with all advanced features
    source = """
    # Type declarations
    Type UserId is Integer
    Type Username is String

    # Typed variables
    Let user_id (UserId) be 12345
    Let username (Username) be "johndoe"

    # Async function with typed parameters
    Async Process called "fetch_user" that takes id (UserId) returns (Dictionary[String, Any]):
        # Simulate async operation
        await asyncio.sleep with seconds as 0.1

        # Return user data
        Return dictionary with:
            "id" as id
            "name" as "Unknown"

    # Lambda expression
    Let add_one be Lambda x: x plus 1

    # Pipeline operator
    Let numbers be list containing 1, 2, 3, 4, 5
    Let doubled_numbers be numbers |> Map over double

    # Pattern matching
    Process called "describe_user" that takes user:
        Match user:
            When {"name": name, "role": "admin"}:
                Return "Admin: " followed by name

            When {"name": name}:
                Return "User: " followed by name

            When _:
                Return "Unknown user"

    # Function to be mapped
    Process called "double" that takes x (Integer) returns (Integer):
        Return x multiplied by 2
    """

    # Parse the source code
    ast = parser.parse(source)

    # Verify the AST was created
    assert ast is not None
    assert len(ast.statements) > 0


def test_advanced_analyzer():
    """Test that the advanced analyzer can analyze code with all advanced features."""
    # Create an advanced parser and analyzer
    parser = create_advanced_parser()
    analyzer = create_advanced_analyzer()

    # Source code with all advanced features
    source = """
    # Type declarations
    Type UserId is Integer
    Type Username is String

    # Typed variables
    Let user_id (UserId) be 12345
    Let username (Username) be "johndoe"

    # Async function with typed parameters
    Async Process called "fetch_user" that takes id (UserId) returns (Dictionary[String, Any]):
        # Simulate async operation
        await asyncio.sleep with seconds as 0.1

        # Return user data
        Return dictionary with:
            "id" as id
            "name" as "Unknown"

    # Lambda expression
    Let add_one be Lambda x: x plus 1

    # Function to be used in pipeline
    Process called "double" that takes x:
        Return x multiplied by 2

    # Pipeline operator
    Let numbers be list containing 1, 2, 3, 4, 5
    Let doubled_numbers be numbers |> Map over double

    # Pattern matching
    Process called "describe_user" that takes user:
        Match user:
            When {"name": name, "role": "admin"}:
                Return "Admin: " followed by name

            When {"name": name}:
                Return "User: " followed by name

            When _:
                Return "Unknown user"
    """

    # Parse the source code
    ast = parser.parse(source)

    # Analyze the AST
    valid = analyzer.analyze(ast)

    # Verify the analysis succeeded
    assert valid
    assert len(analyzer.errors) == 0


def test_advanced_generator():
    """Test that the advanced generator can generate code for all advanced features."""
    # Create advanced parser, analyzer, and generator
    parser = create_advanced_parser()
    analyzer = create_advanced_analyzer()
    generator = create_advanced_generator()

    # Source code with all advanced features
    source = """
    # Type declarations
    Type UserId is Integer
    Type Username is String

    # Import asyncio
    Import module "asyncio"

    # Typed variables
    Let user_id (UserId) be 12345
    Let username (Username) be "johndoe"

    # Async function with typed parameters
    Async Process called "fetch_user" that takes id (UserId) returns (Dictionary[String, Any]):
        # Simulate async operation
        await asyncio.sleep with seconds as 0.1

        # Return user data
        Return dictionary with:
            "id" as id
            "name" as "Unknown"

    # Lambda expression
    Let add_one be Lambda x: x plus 1

    # Function to be used in pipeline
    Process called "double" that takes x:
        Return x multiplied by 2

    # Pipeline operator
    Let numbers be list containing 1, 2, 3, 4, 5
    Let doubled_numbers be numbers |> Map over double

    # Pattern matching
    Process called "describe_user" that takes user:
        Match user:
            When {"name": name, "role": "admin"}:
                Return "Admin: " followed by name

            When {"name": name}:
                Return "User: " followed by name

            When _:
                Return "Unknown user"
    """

    # Parse and analyze the source code
    ast = parser.parse(source)
    valid = analyzer.analyze(ast)
    assert valid

    # Generate Python code
    code = generator.generate(ast)

    # Verify the generated code contains expected elements
    assert "# Type alias: UserId = Integer" in code
    assert "# Type alias: Username = String" in code
    assert "user_id = 12345  # type: UserId" in code
    assert "username = \"johndoe\"  # type: Username" in code
    assert "async def fetch_user(id):  # (UserId) -> Dictionary[String, Any]" in code
    assert "await asyncio.sleep(seconds=0.1)" in code
    assert "add_one = lambda x: (x + 1)" in code
    assert "def double(x):" in code
    assert "doubled_numbers = pipeline(numbers, pipeline(Map, double))" in code or "doubled_numbers = map_function(double, numbers)" in code
    assert "def describe_user(user):" in code
    assert "_match_value_" in code
    assert "\"name\"] == " in code


def test_advanced_transpile():
    """Test the advanced transpile function."""
    # Source code with all advanced features
    source = """
    # Type declarations
    Type UserId is Integer
    Type Username is String

    # Import asyncio
    Import module "asyncio"

    # Typed variables
    Let user_id (UserId) be 12345
    Let username (Username) be "johndoe"

    # Async function with typed parameters
    Async Process called "fetch_user" that takes id (UserId) returns (Dictionary[String, Any]):
        # Simulate async operation
        await asyncio.sleep with seconds as 0.1

        # Return user data
        Return dictionary with:
            "id" as id
            "name" as "Unknown"

    # Lambda expression
    Let add_one be Lambda x: x plus 1

    # Function to be used in pipeline
    Process called "double" that takes x:
        Return x multiplied by 2

    # Pipeline operator
    Let numbers be list containing 1, 2, 3, 4, 5
    Let doubled_numbers be numbers |> Map over double

    # Pattern matching
    Process called "describe_user" that takes user:
        Match user:
            When {"name": name, "role": "admin"}:
                Return "Admin: " followed by name

            When {"name": name}:
                Return "User: " followed by name

            When _:
                Return "Unknown user"
    """

    # Transpile the source code
    code, valid, errors, warnings = transpile_advanced(source)

    # Verify the transpilation succeeded
    assert valid
    assert len(errors) == 0
    assert code is not None

    # Verify the generated code contains expected elements
    assert "# Type alias: UserId = Integer" in code
    assert "# Type alias: Username = String" in code
    assert "user_id = 12345  # type: UserId" in code
    assert "username = \"johndoe\"  # type: Username" in code
    assert "async def fetch_user(id):" in code
    assert "await asyncio.sleep(seconds=0.1)" in code
    assert "add_one = lambda x: (x + 1)" in code
    assert "def double(x):" in code
    assert "doubled_numbers = pipeline(numbers, pipeline(Map, double))" in code or "doubled_numbers = map_function(double, numbers)" in code
    assert "def describe_user(user):" in code
    assert "_match_value_" in code


def test_integration_with_python_runtime():
    """Test that Python code generated from advanced Runa code can be executed."""
    # Source code with all advanced features that can be executed
    source = """
    # Function to be used in pipeline
    Process called "double" that takes x:
        Return x multiplied by 2

    # Pipeline operator with functional programming
    Let numbers be list containing 1, 2, 3, 4, 5
    Let doubled_numbers be Map numbers over double

    # Pattern matching
    Process called "describe_value" that takes value:
        Match value:
            When number if number is greater than 10:
                Return "Large number: " followed by number

            When number if number is greater than 0:
                Return "Small number: " followed by number

            When 0:
                Return "Zero"

            When _:
                Return "Other value"

    # Test the pattern matching
    Let description1 be describe_value with value as 15
    Let description2 be describe_value with value as 5
    Let description3 be describe_value with value as 0
    """

    # Transpile the source code
    code, valid, errors, warnings = transpile_advanced(source)

    # Verify the transpilation succeeded
    assert valid
    assert len(errors) == 0
    assert code is not None

    # Create a temporary Python file
    temp_file = "temp_advanced.py"
    with open(temp_file, 'w') as f:
        f.write(code)

    try:
        # Execute the generated code
        exec_namespace = {}
        with open(temp_file, 'r') as f:
            exec(f.read(), exec_namespace)

        # Verify the results
        assert exec_namespace['doubled_numbers'] == [2, 4, 6, 8, 10]
        assert exec_namespace['description1'] == "Large number: 15"
        assert exec_namespace['description2'] == "Small number: 5"
        assert exec_namespace['description3'] == "Zero"

    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)


@pytest.mark.asyncio
async def test_async_integration():
    """Test that async code generated from advanced Runa code can be executed."""
    # Source code with async features
    source = """
    # Import asyncio
    Import module "asyncio"

    # Async function
    Async Process called "delayed_calculation" that takes x:
        # Simulate async operation
        await asyncio.sleep with seconds as 0.1

        # Return result
        Return x multiplied by 2

    # Function to run async code
    Process called "run_async_calculation" that takes x:
        Let result be await delayed_calculation with x as x
        Return result
    """

    # Transpile the source code
    code, valid, errors, warnings = transpile_advanced(source)

    # Verify the transpilation succeeded
    assert valid
    assert len(errors) == 0
    assert code is not None

    # Create a temporary Python file
    temp_file = "temp_async.py"
    with open(temp_file, 'w') as f:
        f.write(code)

    try:
        # Execute the generated code
        exec_namespace = {}
        with open(temp_file, 'r') as f:
            exec(f.read(), exec_namespace)

        # Get the async function
        delayed_calculation = exec_namespace['delayed_calculation']

        # Run the async function and verify the result
        result = await delayed_calculation(5)
        assert result == 10

    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)


def test_combined_example():
    """Create and test a comprehensive example that uses all advanced features together."""
    # Source code combining all advanced features
    source = """
    # Type definitions
    Type UserId is Integer
    Type User is Dictionary[String, Any]
    Type UserList is List[User]

    # Import asyncio
    Import module "asyncio"

    # Create some test data
    Let users (UserList) be list containing
        dictionary with:
            "id" as 1
            "name" as "Alice"
            "role" as "admin"
            "active" as true,
        dictionary with:
            "id" as 2
            "name" as "Bob"
            "role" as "user"
            "active" as true,
        dictionary with:
            "id" as 3
            "name" as "Charlie"
            "role" as "user"
            "active" as false

    # Async function to get user by ID
    Async Process called "get_user_by_id" that takes users (UserList) and user_id (UserId) returns (User):
        # Simulate network delay
        await asyncio.sleep with seconds as 0.1

        # Find the user
        For each user in users:
            If user["id"] is equal to user_id:
                Return user

        # No user found
        Return dictionary with:
            "id" as 0
            "name" as "Unknown"
            "role" as "guest"
            "active" as false

    # Function to categorize a user
    Process called "categorize_user" that takes user (User) returns (String):
        Match user:
            When {"role": "admin", "active": true}:
                Return "Active admin"

            When {"role": "admin", "active": false}:
                Return "Inactive admin"

            When {"role": "user", "active": true}:
                Return "Active user"

            When {"role": "user", "active": false}:
                Return "Inactive user"

            When _:
                Return "Guest"

    # Functional programming - filter for active users
    Let is_active be Lambda user: user["active"] is equal to true
    Let active_users be Filter users using is_active

    # Generate display names using map
    Process called "get_display_name" that takes user (User) returns (String):
        Return user["name"] followed by " (" followed by user["role"] followed by ")"

    Let display_names be Map active_users over get_display_name

    # Pipeline to get and categorize a user
    Process called "get_and_categorize" that takes user_id (UserId) returns (String):
        Let user be await get_user_by_id with users as users and user_id as user_id
        Return user |> categorize_user

    # Run the operations
    Process called "run_operations" that takes:
        # Get categories for all users
        Let categories be list containing
        For each user in users:
            Let category be categorize_user with user as user
            Add category to categories

        Return categories

    Let results be run_operations
    """

    # Transpile the source code
    code, valid, errors, warnings = transpile_advanced(source)

    # Verify the transpilation succeeded
    assert valid
    assert len(errors) == 0
    assert code is not None

    # Create a temporary Python file
    temp_file = "temp_combined.py"
    with open(temp_file, 'w') as f:
        f.write(code)

    try:
        # Execute the generated code
        exec_namespace = {}
        with open(temp_file, 'r') as f:
            exec(f.read(), exec_namespace)

        # Verify the results
        assert len(exec_namespace['users']) == 3
        assert len(exec_namespace['active_users']) == 2
        assert len(exec_namespace['display_names']) == 2
        assert "Alice (admin)" in exec_namespace['display_names']
        assert "Bob (user)" in exec_namespace['display_names']
        assert len(exec_namespace['results']) == 3
        assert "Active admin" in exec_namespace['results']
        assert "Active user" in exec_namespace['results']
        assert "Inactive user" in exec_namespace['results']

    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)