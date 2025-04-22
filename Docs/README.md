# Runa Programming Language Documentation

Welcome to the Runa Programming Language documentation. This folder contains comprehensive documentation for Runa, a revolutionary programming language designed to bridge human thought patterns with machine execution.

## Documentation Overview

The Runa documentation is organized into the following sections:

### Getting Started
- [Getting Started with Runa](GettingStarted.md) - A beginner's guide to Runa
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions

### Core Language Documentation
- [Language Reference](RunaLanguageReference.md) - Complete reference of Runa's syntax and features
- [Formal Grammar Specifications](RunaFormalGrammarSpecifications.md) - Detailed syntax specifications

### Advanced Features
- [Pattern Matching](PatternMatching.md) - Using pattern matching for data destructuring and control flow
- [Asynchronous Programming](AsyncProgramming.md) - Writing non-blocking, concurrent code
- [Functional Programming](FunctionalProgramming.md) - Functional programming concepts and techniques
- [Enhanced Type System](TypeSystem.md) - Leveraging Runa's powerful type system

### Runtime and Integration
- [Runa Virtual Machine](Runtime/RunaVM.md) - The RunaVM execution environment
- [Embedding Runa](Integration/Embedding_RunaVM.md) - Adding Runa scripting to applications
- [Foreign Function Interface](Integration/Foreign_Function_Interface.md) - Calling native code from Runa
- [Bytecode Format](Development/BytecodeFormat.md) - Runa bytecode specification
- [C API Reference](API/RunaVM_C_API.md) - API for integrating RunaVM in C/C++ applications

### More Documentation
For a complete list of all documentation pages, see the [Documentation Index](index.md).

## Runa Overview

Runa is a revolutionary programming language designed to bridge human thought patterns with machine execution. Named after Norse runes that encoded knowledge and meaning, Runa features pseudocode-like syntax that resembles natural language while maintaining the precision needed for computational execution.

### Project Status

Runa is currently in active development. The language implementation includes both core features and advanced programming paradigms.

### Features

#### Core Features
- Natural language-like syntax
- Python-like indentation for block structure
- Transpilation to Python (with more target languages planned)
- Function definitions with named parameters
- Variables and assignments
- Control structures (if-else, for-each)
- Lists and dictionaries
- Basic type system with inference

#### Advanced Features
- **Pattern Matching**: Sophisticated pattern matching with destructuring for data extraction and case analysis
- **Asynchronous Programming**: Native async/await syntax for non-blocking operations
- **Functional Programming**: First-class functions, pipelines, and higher-order operations
- **Enhanced Type System**: Rich type annotations, inference, and checking
- **AI-to-AI Communication**: Specialized annotations for communication between AI components

#### Runtime Features
- **Native Virtual Machine**: RunaVM for consistent cross-platform execution
- **JIT Compilation**: Just-in-time compilation for optimized performance
- **Bytecode Format**: Compact bytecode representation of Runa programs
- **Embedding API**: Integrate Runa into applications as a scripting language
- **Foreign Function Interface**: Call native libraries from Runa
- **Sandbox Security**: Configurable security controls for untrusted code

## Basic Example

```
# hello_world.runa
Let message be "Hello, world!"
Display message

Process called "greet" that takes name:
    Let greeting be "Hello, " followed by name
    Display greeting

greet with name as "Runa"
```

## Running Runa Code

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

# Run with the RunaVM
runavm hello_world.runa

# Compile to bytecode
runa compile --bytecode hello_world.runa
```

## Embedding Runa

Runa can be embedded in your applications as a scripting language:

```c
#include <runavm.h>

int main() {
    // Create VM
    RunaVM* vm = runa_vm_create();
    
    // Load script
    runa_vm_load_file(vm, "script.runa");
    
    // Call Runa function
    RunaValue result;
    runa_vm_call_function(vm, "calculate", NULL, 0, &result);
    
    // Use result
    printf("Result: %lld\n", runa_value_as_integer(result));
    runa_value_release(&result);
    
    // Clean up
    runa_vm_destroy(vm);
    return 0;
}
```

## License

Runa is developed by Sybertnetics Artificial Intelligence Solutions, Inc. 
© 2023-2024 Sybertnetics Artificial Intelligence Solutions, Inc. All rights reserved.

## Documentation Sections

* [Getting Started](./GettingStarted.md)
* [Language Syntax](./Syntax/README.md)
* [Standard Library](./StandardLibrary/README.md)
* [API Reference](./API/README.md)
* [Examples](./Examples/README.md)
* [Testing Framework](./TestFramework/UnitTesting.md)
* [AI Integration](./AIIntegration/README.md)
* [Runtime](./Runtime/README.md)
* [Integration](./Integration/README.md)
* [Development](./Development/README.md)