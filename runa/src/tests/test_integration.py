import os
import pytest
from runa.src.runa.transpiler import Transpiler


def test_integration_calculator():
    """Test the entire transpilation pipeline with a calculator example."""
    # Read the calculator example
    example_path = os.path.join(os.path.dirname(__file__), 'examples', 'calculator.runa')
    with open(example_path, 'r') as f:
        source = f.read()

    # Transpile to Python
    transpiler = Transpiler(target="python")
    code, valid, errors, warnings = transpiler.transpile(source)

    # Check if transpilation was successful
    assert valid, f"Transpilation failed with errors: {errors}"
    assert not errors, f"Errors: {errors}"

    # Basic check on the generated code
    assert "def add(a, b):" in code
    assert "def subtract(a, b):" in code
    assert "def multiply(a, b):" in code
    assert "def divide(a, b):" in code
    assert "if (b == 0):" in code

    # Create a temporary Python file
    temp_file = "temp_calculator.py"
    with open(temp_file, 'w') as f:
        f.write(code)

    try:
        # Execute the generated code to check for runtime errors
        # This is a simple smoke test - not checking output values
        exec_namespace = {}
        with open(temp_file, 'r') as f:
            exec(f.read(), exec_namespace)

        # Verify that functions were correctly defined
        assert 'add' in exec_namespace
        assert 'subtract' in exec_namespace
        assert 'multiply' in exec_namespace
        assert 'divide' in exec_namespace

        # Test function execution
        assert exec_namespace['add'](10, 5) == 15
        assert exec_namespace['subtract'](10, 5) == 5
        assert exec_namespace['multiply'](10, 5) == 50
        assert exec_namespace['divide'](10, 5) == 2
        assert exec_namespace['divide'](10, 0) == 0  # Our implementation returns 0 for division by zero

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file):
            os.remove(temp_file)