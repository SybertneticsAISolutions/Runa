# Runa Programming Language

Runa is a revolutionary programming language designed to bridge human thought patterns with machine execution. Named after Norse runes that encoded knowledge and meaning, Runa features pseudocode-like syntax that resembles natural language while maintaining the precision needed for computational execution.

## Project Status

Runa is currently in active development. The language implementation includes both core features and advanced programming paradigms.

## Features

### Core Features
- Natural language-like syntax
- Python-like indentation for block structure
- Transpilation to Python (with more target languages planned)
- Function definitions with named parameters
- Variables and assignments
- Control structures (if-else, for-each)
- Lists and dictionaries
- Basic type system with inference

### Advanced Features
- **Pattern Matching**: Sophisticated pattern matching with destructuring for data extraction and case analysis
- **Asynchronous Programming**: Native async/await syntax for non-blocking operations
- **Functional Programming**: First-class functions, pipelines, and higher-order operations
- **Enhanced Type System**: Rich type annotations, inference, and checking

## Installation

```bash
# Clone the repository
git clone https://github.com/SybertneticsAISolutions/Runa.git
cd runa

# Install the package in development mode
pip install -e .
```

## Usage

### Basic Example

```bash
# hello_world.runa
Let message be "Hello, world!"
Display message

Process called "greet" that takes name:
    Let greeting be "Hello, " with name as name
    Display greeting

greet with "Runa"
```

### Running Runa Code

```bash
# Compile Runa to Python
runa compile hello_world.runa

# Run Runa code directly
runa run hello_world.runa

# Start the REPL
runa repl

# Enable advanced language features
runa compile --advanced hello_world.runa
runa run --advanced hello_world.runa
runa repl --advanced
```

## Language Guide

### Variables
```
# Variable declaration
Let variable_name be value

# Variable assignment
Set variable_name to new_value

# Typed variable declaration
Let variable_name (Type) be value
```

### Control Structures
```
# If-else statement
If condition:
    # Then block
Otherwise:
    # Else block

# For-each loop
For each item in collection:
    # Loop body
```

### Functions (Processes)
```
# Function definition
Process called "function_name" that takes parameter1 and parameter2:
    # Function body
    Return result

# Typed function definition
Process called "function_name" that takes parameter1 (Type1) and parameter2 (Type2) returns (ReturnType):
    # Function body
    Return result

# Function call
function_name with parameter1 and parameter2

# Function call with named parameters
function_name with param1 as value1 and param2 as value2
```

### Data Structures
```
# List
Let numbers be list containing 1, 2, 3, 4

# Dictionary
Let person be dictionary with:
    "name" as "John"
    "age" as 30
    "city" as "New York"
```

### Advanced Features

#### Pattern Matching
```
Match value:
    When pattern1:
        # Code for pattern1
    When pattern2:
        # Code for pattern2
    When _:
        # Default case
```

#### Asynchronous Programming
```
# Async function definition
Async Process called "fetch_data" that takes url:
    # Async operations
    Let response be await http_client.get with url as url
    Return response

# Async for loop
Async For each item in items:
    # Async loop body
```

#### Functional Programming
```
# Lambda expression
Let add be Lambda a and b: a plus b

# Pipeline operator
Let result be data |> process |> format

# Higher-order functions
Let doubled be Map numbers over double
Let evens be Filter numbers using is_even
Let sum be Reduce numbers using add
```

#### Type System
```
# Type aliases
Type UserId is Integer
Type User is Dictionary[String, Any]

# Typed variable declarations
Let user_id (UserId) be 12345

# Generic types
Type Pair[T, U] is Dictionary[String, Any]

# Generic functions
Process [T] called "first" that takes items (List[T]) returns (T):
    Return items at index 0
```

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest

# Run tests
pytest
```

### Project Structure
```
runa/
├── src/
│   ├── runa/           # Core language components
│   │   ├── async/      # Asynchronous programming support
│   │   ├── functional/ # Functional programming features
│   │   ├── patterns/   # Pattern matching system
│   │   ├── types/      # Enhanced type system
│   └── tests/          # Test suite
├── docs/               # Documentation
```

## License

This Project is licensed under the MIT License - see the LICENSE file for details.