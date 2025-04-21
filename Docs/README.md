# Runa Programming Language

Runa is a revolutionary programming language designed to bridge human thought patterns with machine execution. Named after Norse runes that encoded knowledge and meaning, Runa features pseudocode-like syntax that resembles natural language while maintaining the precision needed for computational execution.

## Project Status

This is Phase 2 of the Runa language implementation, focusing on the parser and transpiler components. The language is currently in active development and not ready for production use.

## Features

- Natural language-like syntax
- Python-like indentation for block structure
- Transpilation to Python (with more target languages planned)
- Function definitions with named parameters
- Variables and assignments
- Control structures (if-else, for-each)
- Lists and dictionaries
- Basic type system with inference

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
```

## Language Guide

### Variables
```
# Variable declaration
Let variable_name be value

# Variable assignment
Set variable_name to new_value
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

### Functions(Processes)
```
# Function definition
Process called "function_name" that takes parameter1 and parameter2:
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
## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest

# Run tests
pytest
```

## Future Plans
- Context-aware interpretation
- Multiple target languages
- IDE integration
- AI-to-AI communication features
- Enhanced type system
- Pattern matching
- Asynchronous programming
- Functional programming extensions

## License

This Project is licensed under the MIT License - see the LICENSE file for details.