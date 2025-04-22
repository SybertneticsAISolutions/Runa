# Setting Up Your Runa Development Environment

This guide covers everything you need to set up a productive development environment for Runa programming.

## Command-Line Interface

Runa provides a powerful command-line interface (CLI) for various development tasks.

### Basic Commands

Here are the essential CLI commands:

```bash
# Run a Runa file
runa run filename.runa

# Compile a Runa file to Python
runa compile filename.runa

# Start the interactive REPL
runa repl

# Run tests
runa test tests/

# Display help
runa --help

# Show Runa version
runa --version
```

### CLI Options

Common options that can be used with Runa commands:

```bash
# Enable verbose output
runa --verbose run filename.runa

# Specify target language for compilation
runa compile --target python filename.runa
runa compile --target javascript filename.runa

# Enable specific features
runa --feature knowledge_graphs run ai_app.runa

# Specify output file
runa compile --output compiled_code.py filename.runa

# Specify configuration file
runa --config my_config.json run filename.runa
```

### Configuration File

You can create a `runa.config.json` file in your project root to store common settings:

```json
{
  "target": "python",
  "output_dir": "./build",
  "features": ["advanced_types", "knowledge_graphs"],
  "optimization": "performance",
  "verbosity": "info"
}
```

## IDE Integration

### Visual Studio Code

VS Code provides the richest development experience for Runa through our official extension.

#### Installation

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X / Cmd+Shift+X)
3. Search for "Runa Language"
4. Click Install

Alternatively, install from the command line:

```bash
code --install-extension runa-lang.runa-vscode
```

#### Features

- Syntax highlighting
- Code completion
- Error diagnostics
- Go to definition
- Find references
- Code formatting
- Run and debug integration
- Snippets
- Knowledge graph visualization

#### Configuration

You can customize the Runa VS Code extension in your settings.json:

```json
{
  "runa.linting.enabled": true,
  "runa.traceServer": "off",
  "runa.format.enabled": true,
  "runa.completion.snippets": true,
  "runa.path": "/custom/path/to/runa",
  "runa.knowledgeGraphVisualization.enabled": true
}
```

### JetBrains IDEs

For users of IntelliJ IDEA, PyCharm, WebStorm, and other JetBrains IDEs:

1. Go to Settings/Preferences > Plugins
2. Search for "Runa Language Support"
3. Click Install
4. Restart your IDE

### Neovim/Vim

For Vim users, you can set up Runa support:

1. Install a language server client plugin such as coc.nvim or vim-lsp
2. Configure it to connect to the Runa Language Server

Example configuration for coc.nvim (`coc-settings.json`):

```json
{
  "languageserver": {
    "runa": {
      "command": "runa-language-server",
      "filetypes": ["runa"],
      "rootPatterns": ["runa.config.json", ".git/"]
    }
  }
}
```

## Editor Configuration

### File Extensions

Runa uses the following file extensions:
- `.runa` - Standard Runa source files
- `.runatest` - Runa test files
- `.runai` - AI-enhanced Runa files (with specialized AI annotations)

### Editor Settings

Recommended editor settings for Runa development:

- **Indentation**: 4 spaces (configurable)
- **Line endings**: LF (Unix-style)
- **Character encoding**: UTF-8
- **Trailing newline**: Enabled

Example `.editorconfig` file:

```ini
[*.{runa,runatest,runai}]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true
```

## Project Setup

### Creating a New Project

To create a new Runa project from scratch:

```bash
# Create a new project using the built-in template
runa new my_project

# Create a specific type of project
runa new --template api my_api_project
runa new --template cli my_cli_tool
runa new --template web my_web_app
runa new --template ai my_ai_app
```

### Project Structure

A typical Runa project has the following structure:

```
my_project/
├── runa.config.json       # Project configuration
├── README.md              # Project documentation
├── src/                   # Source code
│   ├── main.runa          # Entry point
│   └── modules/           # Project modules
│       ├── module1.runa
│       └── module2.runa
├── tests/                 # Test files
│   ├── test_module1.runatest
│   └── test_module2.runatest
├── data/                  # Data files
├── assets/                # Static assets
├── docs/                  # Documentation
└── build/                 # Build output (generated)
```

### Dependencies

Manage project dependencies using `runa.config.json`:

```json
{
  "dependencies": {
    "runa-http": "1.2.0",
    "runa-data": "0.9.5",
    "runa-ai": "2.0.1"
  },
  "devDependencies": {
    "runa-test": "1.0.0"
  }
}
```

To install dependencies:

```bash
runa install
```

## Debugging Tools

### Built-in Debugger

Runa includes a powerful debugger:

```bash
# Start debugging a Runa file
runa debug filename.runa

# Debug with specific entry point
runa debug --entry-point main filename.runa
```

### VS Code Debugging

Configure VS Code to debug Runa applications:

1. Create a `.vscode/launch.json` file in your project:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "runa",
      "request": "launch",
      "name": "Debug Runa Program",
      "program": "${file}",
      "args": [],
      "cwd": "${workspaceFolder}",
      "stopOnEntry": false,
      "console": "integratedTerminal"
    }
  ]
}
```

2. Use the Run and Debug panel (F5) to start debugging

### Logging

Runa provides a built-in logging system:

```
import runa.core.logging

Let logger = logging.create_logger("my_module")

Process called do_something()
    logger.debug("Debug information")
    logger.info("Informational message")
    logger.warning("Warning message")
    logger.error("Error message")
End Process
```

Configure logging in `runa.config.json`:

```json
{
  "logging": {
    "level": "info",
    "file": "logs/application.log",
    "format": "{timestamp} [{level}] {message}",
    "console": true
  }
}
```

## Advanced Tools

### Performance Profiling

Analyze your code's performance:

```bash
# Run with profiling enabled
runa run --profile filename.runa

# Save profiling results to a file
runa run --profile --profile-output results.prof filename.runa

# Visualize profiling results
runa profile-visualize results.prof
```

### Linting and Code Quality

Ensure consistent code quality:

```bash
# Lint a file or directory
runa lint filename.runa
runa lint src/

# Automatically fix linting issues
runa lint --fix filename.runa

# Use a specific linting configuration
runa lint --config .runalint.json src/
```

### Code Generation Tools

Runa includes utilities for generating code:

```bash
# Generate a module from a schema
runa generate module --from-schema schema.json

# Generate a knowledge graph model
runa generate knowledge-graph --from-ontology ontology.owl

# Create a new component
runa generate component MyComponent
```

## Container Development

### Docker Integration

For containerized development, use our Docker support:

```bash
# Run a Runa app in Docker
docker run -v $(pwd):/app runaproject/runa run /app/main.runa

# Development container with hot-reload
docker run -v $(pwd):/app -p 8000:8000 runaproject/runa-dev
```

Example `Dockerfile` for a Runa application:

```dockerfile
FROM runaproject/runa:latest

WORKDIR /app

COPY . .

RUN runa install
RUN runa compile --target python main.runa

CMD ["runa", "run", "main.runa"]
```

## Git Integration

### Recommended Git Configuration

Add this to your `.gitignore`:

```
# Runa specific
*.runa.py
*.runa.js
build/
.runa-cache/
logs/

# Editor specific
.vscode/
.idea/
*.swp
*.swo

# System files
.DS_Store
Thumbs.db
```

### Git Hooks

Set up Git hooks for Runa projects:

```bash
# Install the Runa Git hooks
runa hooks install

# Create custom Git hooks
runa hooks create pre-commit "runa lint"
```

## Next Steps

Now that your development environment is set up, proceed to:

- [Language Concepts](./LanguageConcepts/README.md) to learn about Runa's core features
- [Working with Projects](./Projects/README.md) for more details on project management
- [Testing and Debugging](./TestingDebugging/README.md) to learn how to ensure code quality 