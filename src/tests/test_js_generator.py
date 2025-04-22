"""
Tests for the JavaScript code generator.
"""
import os
import pytest
import subprocess
import tempfile
from src.runa.parser import RunaParser
from src.runa.analyzer import SemanticAnalyzer
from src.runa.targets.js_generator import JsCodeGenerator
from src.runa.transpiler import Transpiler


def test_js_generator_creation():
    """Test creating a JavaScript code generator."""
    generator = JsCodeGenerator()
    assert generator is not None


def test_js_basic_transpilation():
    """Test basic transpilation to JavaScript."""
    # Create a Runa parser and JavaScript generator
    parser = RunaParser()
    analyzer = SemanticAnalyzer()
    generator = JsCodeGenerator()

    # Define a simple Runa program
    source = """
    Let x be 10
    Let y be 20
    Let sum be x plus y
    Display "Sum:" with result as sum
    """

    # Parse the program
    ast = parser.parse(source)
    assert ast is not None

    # Analyze the AST
    valid = analyzer.analyze(ast)
    assert valid

    # Generate JavaScript code
    js_code = generator.generate(ast)
    assert js_code is not None

    # Check that the code contains expected JavaScript constructs
    assert "let x = 10;" in js_code
    assert "let y = 20;" in js_code
    assert "let sum = (x + y);" in js_code
    assert "console.log" in js_code


def test_js_transpiler_api():
    """Test the Transpiler API for JavaScript generation."""
    # Create a Transpiler instance for JavaScript
    transpiler = Transpiler(target="javascript")

    # Define a simple Runa program
    source = """
    Let x be 10
    Let y be 20
    Let sum be x plus y
    Display "Sum:" with result as sum
    """

    # Transpile the program
    js_code, valid, errors, warnings = transpiler.transpile(source)

    # Check that transpilation succeeded
    assert valid
    assert not errors
    assert js_code is not None

    # Check that the code contains expected JavaScript constructs
    assert "let x = 10;" in js_code
    assert "let y = 20;" in js_code
    assert "let sum = (x + y);" in js_code
    assert "console.log" in js_code


def test_js_control_structures():
    """Test JavaScript generation for control structures."""
    # Create a Transpiler instance for JavaScript
    transpiler = Transpiler(target="javascript")

    # Define a Runa program with control structures
    source = """
    Let x be 10

    If x is greater than 5:
        Display "x is greater than 5"
    Otherwise:
        Display "x is not greater than 5"

    Let numbers be list containing 1, 2, 3, 4, 5

    For each num in numbers:
        Display num
    """

    # Transpile the program
    js_code, valid, errors, warnings = transpiler.transpile(source)

    # Check that transpilation succeeded
    assert valid
    assert not errors
    assert js_code is not None

    # Check that the code contains expected JavaScript constructs
    assert "if ((x > 5)) {" in js_code
    assert "else {" in js_code
    assert "for (let num of numbers) {" in js_code


def test_js_functions():
    """Test JavaScript generation for function definitions and calls."""
    # Create a Transpiler instance for JavaScript
    transpiler = Transpiler(target="javascript")

    # Define a Runa program with functions
    source = """
    Process called "add" that takes a and b:
        Return a plus b

    Process called "multiply" that takes a and b:
        Return a multiplied by b

    Let sum be add with a as 5 and b as 10
    Let product be multiply with a as 5 and b as 10

    Display "Sum:" with result as sum
    Display "Product:" with result as product
    """

    # Transpile the program
    js_code, valid, errors, warnings = transpiler.transpile(source)

    # Check that transpilation succeeded
    assert valid
    assert not errors
    assert js_code is not None

    # Check that the code contains expected JavaScript constructs
    assert "function add(a, b) {" in js_code
    assert "return (a + b);" in js_code
    assert "function multiply(a, b) {" in js_code
    assert "return (a * b);" in js_code
    assert "let sum = add({a: 5, b: 10});" in js_code
    assert "let product = multiply({a: 5, b: 10});" in js_code


@pytest.mark.skipif(not os.path.exists("node"), reason="Node.js not installed")
def test_js_runtime():
    """Test executing generated JavaScript code with Node.js."""
    # Skip this test if Node.js is not installed
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        pytest.skip("Node.js not installed or not working")

    # Create a Transpiler instance for JavaScript
    transpiler = Transpiler(target="javascript")

    # Define a simple Runa program
    source = """
    Let x be 10
    Let y be 20
    Let sum be x plus y
    Display "Sum:" with result as sum
    """

    # Transpile the program
    js_code, valid, errors, warnings = transpiler.transpile(source)

    # Check that transpilation succeeded
    assert valid
    assert not errors
    assert js_code is not None

    # Write the JavaScript code to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".js", delete=False) as f:
        f.write(js_code.encode('utf-8'))
        temp_js_file = f.name

    try:
        # Run the JavaScript code with Node.js
        result = subprocess.run(["node", temp_js_file],
                                capture_output=True,
                                text=True,
                                check=True)

        # Check that the output contains the expected result
        assert "Sum: 30" in result.stdout
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_js_file):
            os.remove(temp_js_file)


def test_js_advanced_features():
    """Test JavaScript generation for advanced language features."""
    # Create a Transpiler instance for JavaScript with advanced features
    transpiler = Transpiler(target="javascript", advanced=True)

    # Define a Runa program with advanced features
    source = """
    # Pattern matching
    Let value be 42

    Match value:
        When number if number is greater than 50:
            Display "Large number"
        When number if number is greater than 10:
            Display "Medium number"
        When _:
            Display "Small number or not a number"

    # Lambda expression
    Let double be Lambda x: x multiplied by 2
    Let doubled_value be double with x as value
    Display "Doubled:" with result as doubled_value

    # Pipeline operator
    Let squared be value |> double |> double
    Display "Squared:" with result as squared
    """

    # Transpile the program
    js_code, valid, errors, warnings = transpiler.transpile(source)

    # Check that transpilation succeeded
    assert valid
    assert not errors
    assert js_code is not None

    # Check that the code contains expected JavaScript constructs for advanced features
    assert "const _match_value_" in js_code  # Pattern matching
    assert "(x) => (x * 2)" in js_code  # Lambda expression
    assert "pipeline" in js_code  # Pipeline operator


def test_js_data_structures():
    """Test JavaScript generation for data structures."""
    # Create a Transpiler instance for JavaScript
    transpiler = Transpiler(target="javascript")

    # Define a Runa program with lists and dictionaries
    source = """
    Let numbers be list containing 1, 2, 3, 4, 5
    Let first_number be numbers at index 0

    Let person be dictionary with:
        "name" as "Alice"
        "age" as 30
        "city" as "New York"

    Let name be person at index "name"

    Display "First number:" with result as first_number
    Display "Name:" with result as name
    """

    # Transpile the program
    js_code, valid, errors, warnings = transpiler.transpile(source)

    # Check that transpilation succeeded
    assert valid
    assert not errors
    assert js_code is not None

    # Check that the code contains expected JavaScript constructs
    assert "let numbers = [1, 2, 3, 4, 5];" in js_code
    assert "let first_number = numbers[0];" in js_code
    assert "let person = {\"name\": \"Alice\", \"age\": 30, \"city\": \"New York\"};" in js_code
    assert "let name = person[\"name\"];" in js_code


def test_js_with_html():
    """Test creating a simple HTML page that includes JavaScript code."""
    # Create a Transpiler instance for JavaScript
    transpiler = Transpiler(target="javascript")

    # Define a simple Runa program
    source = """
    Process called "calculateSum" that takes a and b:
        Return a plus b

    Let result be calculateSum with a as 5 and b as 10
    Display "Sum:" with result as result
    """

    # Transpile the program
    js_code, valid, errors, warnings = transpiler.transpile(source)

    # Check that transpilation succeeded
    assert valid
    assert not errors
    assert js_code is not None

    # Create a simple HTML page that includes the JavaScript code
    html_code = f"""<!DOCTYPE html>
<html>
<head>
    <title>Runa JavaScript Test</title>
</head>
<body>
    <h1>Runa JavaScript Test</h1>
    <div id="output"></div>

    <script>
    // Override console.log to write to the output div
    const originalLog = console.log;
    console.log = function() {{
        const output = document.getElementById('output');
        for (let i = 0; i < arguments.length; i++) {{
            const p = document.createElement('p');
            p.textContent = arguments[i];
            output.appendChild(p);
        }}
        // Also call the original console.log
        originalLog.apply(console, arguments);
    }};

    // Runa generated JavaScript code
    {js_code}
    </script>
</body>
</html>"""

    # Write the HTML page to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        f.write(html_code.encode('utf-8'))
        temp_html_file = f.name

    try:
        # Just verify that the file was created - we can't easily test running it in a browser
        assert os.path.exists(temp_html_file)
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_html_file):
            os.remove(temp_html_file)