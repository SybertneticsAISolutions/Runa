# Phase 1: Core Language Design - Formal Grammar Definition
## Formal Grammar Definition in EBNF

```
/* Top-level program structure */
Program         ::= Statement+

/* Statements */
Statement       ::= Declaration
                  | Assignment
                  | Conditional
                  | Loop
                  | ProcessDefinition
                  | ReturnStatement
                  | DisplayStatement
                  | Block

/* Declarations */
Declaration     ::= "Let" Identifier "be" Expression
                  | "Define" Identifier "as" Expression
                  | "Define" Identifier "as" "list" "containing" ExpressionList

/* Assignment */
Assignment      ::= "Set" Identifier "to" Expression

/* Basic expressions */
Expression      ::= Literal
                  | Identifier
                  | BinaryExpression
                  | FunctionCall
                  | ListExpression
                  | "the" "sum" "of" "all" Identifier "in" Identifier
                  | Identifier "multiplied by" Identifier
                  | Identifier "plus" Identifier
                  | Identifier "followed by" Identifier

/* Literals */
Literal         ::= StringLiteral
                  | NumberLiteral
                  | BooleanLiteral

StringLiteral   ::= '"' [^"]* '"'
NumberLiteral   ::= [0-9]+ ('.' [0-9]+)?
BooleanLiteral  ::= "true" | "false"

/* Binary expressions */
BinaryExpression ::= Expression Operator Expression

Operator        ::= "is greater than"
                  | "is less than"
                  | "is equal to"
                  | "plus"
                  | "minus"
                  | "multiplied by"
                  | "divided by"

/* Control structures */
Conditional     ::= "If" Expression ":" Block ("Otherwise" ":" Block)?

Loop            ::= "For" "each" Identifier "in" Expression ":" Block

Block           ::= INDENT Statement+ DEDENT

/* Function definition and calls */
ProcessDefinition ::= "Process" "called" StringLiteral "that" "takes" ParameterList ":" Block

ParameterList   ::= Identifier ("and" Identifier)* 
                  | Identifier ("," Identifier)*

ReturnStatement ::= "Return" Expression

FunctionCall    ::= Identifier "with" NamedArguments
                  | Identifier "with" ":" INDENT NamedArguments DEDENT

NamedArguments  ::= NamedArgument ("and" NamedArgument)*
                  | NamedArgument (NEWLINE NamedArgument)*

NamedArgument   ::= Identifier "as" Expression

/* Display statement */
DisplayStatement ::= "Display" Expression ("with" "message" StringLiteral)?

/* Lists */
ListExpression  ::= "list" "containing" ExpressionList

ExpressionList  ::= Expression ("," Expression)*

/* Identifiers */
Identifier      ::= [a-zA-Z_][a-zA-Z0-9_]* ("." [a-zA-Z_][a-zA-Z0-9_]*)*
                  | [a-zA-Z_][a-zA-Z0-9_]* (" " [a-zA-Z_][a-zA-Z0-9_]*)+
```

## Additional Grammar Rules for AI Model Definition

```
/* AI Model Definition */
ModelDefinition ::= "Define" "neural" "network" StringLiteral ":" ModelBlock

ModelBlock      ::= INDENT ModelStatement+ DEDENT

ModelStatement  ::= "Input" "layer" "accepts" Expression
                  | "Use" "convolutional" "layers" "starting" "with" NumberLiteral "filters"
                  | "Double" "filters" "at" "each" "downsampling"
                  | "Include" "residual" "connections"
                  | "Output" "layer" "has" NumberLiteral "classes" "with" Identifier "activation"

/* Training Configuration */
TrainingConfig  ::= "Configure" "training" "for" Identifier ":" TrainingBlock

TrainingBlock   ::= INDENT TrainingStatement+ DEDENT

TrainingStatement ::= "Use" "dataset" StringLiteral "with" Expression
                    | "Apply" Expression "for" "augmentation"
                    | "Use" Identifier "optimizer" "with" "learning" "rate" NumberLiteral
                    | "Train" "for" NumberLiteral "epochs" "or" "until" Expression
                    | "Save" "best" "model" "based" "on" Expression
```

## Operator Precedence

Let's define a clear operator precedence for Runa:

1. Function calls and member access (highest precedence)
2. Unary operators (not, negation)
3. Multiplicative operators (multiplied by, divided by)
4. Additive operators (plus, minus)
5. Comparison operators (is greater than, is less than, is equal to)
6. Logical AND
7. Logical OR (lowest precedence)

## Scoping Rules

For Runa, we'll implement the following scoping rules:

1. Block-level scoping: Variables declared within a block are only accessible within that block and its nested blocks
2. Function-level scoping: Parameters are accessible throughout the function body
3. Global scope: Top-level declarations are accessible throughout the program
4. No variable shadowing: Inner scopes cannot redefine variables from outer scopes
5. Lexical scoping: Inner functions can access variables from their containing function

Now, let's move on to the next component of Phase 1: Standard Library Specification.

## Standard Library Specification

Based on the requirements, here's a foundational specification for the Runa standard library:

### Core Data Structures

```
# List Operations
- Create a new list
- Get length of list
- Access element by index
- Append element to list
- Remove element from list
- Find element in list
- Filter list based on condition
- Map operation over list
- Reduce list to single value
- Sort list

# Dictionary/Map Operations
- Create a new dictionary
- Get keys/values
- Access value by key
- Add/update key-value pair
- Remove key-value pair
- Check if key exists

# String Operations
- Concatenate strings
- Get string length
- Access character by index
- Substring extraction
- String searching
- String replacement
- Case conversion
- Trimming
- Splitting/joining
```

### Basic Operations

```
# Mathematical Operations
- Basic arithmetic (add, subtract, multiply, divide)
- Advanced math (power, square root, logarithms)
- Trigonometric functions
- Statistical functions (mean, median, mode)
- Random number generation

# Logical Operations
- And, Or, Not
- Conditional evaluation
- Comparison operations

# Type Operations
- Type checking
- Type conversion
- Type information
```

### I/O Operations

```
# Console I/O
- Display message to console
- Read input from console

# File I/O
- Read text file
- Write text file
- Read binary file
- Write binary file
- Check if file exists
- Get file information

# Network I/O
- HTTP requests
- Download file
- Basic socket operations
```

### Error Handling Mechanisms

```
# Error Types
- Syntax Error
- Type Error
- Value Error
- Index Error
- Key Error
- IO Error

# Error Handling
- Try/Catch mechanism
- Error propagation
- Custom error creation
- Error logging
```

## Type System Design

For Runa's type system, we'll implement:

### Basic Types

```
# Primitive Types
- Number (floating-point)
- Integer
- String
- Boolean
- Null/None

# Composite Types
- List
- Dictionary/Map
- Tuple
- Set

# Special Types
- Any (top type)
- Nothing (bottom type)
- Function type
- Process type
```

### Type Rules

1. **Type Compatibility**:
   - Numeric types can be automatically converted (Integer → Number)
   - String concatenation accepts any type (auto-conversion to string)
   - Boolean contexts accept any type (with truthy/falsy rules)

2. **Type Inference**:
   - Variables infer types from their initialization expressions
   - Function return types are inferred from return statements
   - Collection types infer from their contents

3. **Optional Type Annotations**:
   ```
   Let age (Integer) be 30
   Process called "Calculate Area" that takes width (Number) and height (Number) returns (Number):
       Return width multiplied by height
   ```

4. **Coercion Rules**:
   - Automatic numeric coercion for arithmetic operations
   - String concatenation coerces operands to strings
   - Boolean contexts coerce values according to truthy/falsy rules
   - Explicit conversion functions for controlled type conversion

## Semantic Model

### Execution Semantics

1. **Evaluation Order**:
   - Expressions are evaluated left to right
   - Function arguments are evaluated before function call
   - Short-circuit evaluation for logical operators

2. **Assignment Semantics**:
   - Variables are mutable by default
   - Assignment returns the assigned value
   - References to composite objects (pass by reference)

### Variable Scoping

1. **Scope Hierarchy**:
   - Global scope
   - Module scope
   - Function/process scope
   - Block scope (for loops, conditionals)

2. **Scope Resolution**:
   - Inner scopes have access to outer scopes
   - Name resolution searches from innermost to outermost scope
   - Shadowing is disallowed for clarity

### Evaluation Rules

1. **Expression Evaluation**:
   - Literals evaluate to their values
   - Variables evaluate to their current values
   - Operators follow defined precedence and associativity
   - Function calls evaluate arguments, then apply function

2. **Statement Execution**:
   - Sequential execution by default
   - Control structures modify execution flow
   - Return statements exit current function with value

### Module System

1. **Module Structure**:
   - Each file is a module
   - Modules encapsulate declarations and definitions
   - Modules can import other modules

2. **Import Mechanism**:
   ```
   Import module "math" 
   Import function "Calculate Distance" from module "geometry"
   ```

3. **Export Mechanism**:
   ```
   Export process "Calculate Area"
   Export variable "PI"
   ```

4. **Module Resolution**:
   - Relative paths for local modules
   - Standard library modules by name
   - Namespace management for imported symbols

Would you like me to go into more detail on any specific aspect of Phase 1, or shall we move on to discussing the implementation approach for Phase 2?