"""
Language Server Protocol client for the Runa programming language.

This module provides functions for starting and connecting to the Runa LSP server
from various editors and IDEs.
"""
import os
import sys
import subprocess
import threading
from typing import Optional, List, Dict, Any, Union

# Try to import pygls for direct client-server connection
try:
    from pygls.lsp.types import (
        ClientCapabilities,
        ClientInfo,
        InitializeParams,
        TextDocumentSyncKind,
    )
except ImportError:
    # Not required for subprocess connection
    pass


def start_server_process() -> subprocess.Popen:
    """
    Start the Runa language server as a subprocess.

    Returns:
        Server process handle
    """
    # Get the path to the server module
    server_path = os.path.join(os.path.dirname(__file__), 'server.py')

    # Start the server as a Python subprocess
    process = subprocess.Popen(
        [sys.executable, server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        bufsize=0
    )

    return process


def connect_to_running_server(host: str = 'localhost', port: int = 8080) -> Any:
    """
    Connect to a running Runa language server.

    Args:
        host: Server hostname
        port: Server port

    Returns:
        Client connection object
    """
    try:
        import socket

        # Create a socket connection to the server
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))

        return sock
    except ImportError:
        print("Socket module not available.")
        return None
    except Exception as e:
        print(f"Error connecting to server: {str(e)}")
        return None


def start_client(advanced_mode: bool = False) -> Any:
    """
    Start a Runa language client and connect to a server.

    Args:
        advanced_mode: Whether to enable advanced language features

    Returns:
        Client object
    """
    try:
        from pygls.client import Client

        # Create a client
        client = Client()

        # Initialize the client with capabilities
        client.initialize(
            InitializeParams(
                capabilities=ClientCapabilities(),
                client_info=ClientInfo(
                    name="Runa Language Client",
                    version="0.1.0"
                ),
                initialization_options={
                    'advancedMode': advanced_mode
                }
            )
        )

        # Connect to the server (starts a new server if needed)
        client.connect_to_server()

        return client
    except ImportError:
        # If pygls is not available, start a server process instead
        print("PyGLS client not available. Starting server process...")
        server_process = start_server_process()
        return server_process


def create_vscode_extension(output_dir: str, advanced_mode: bool = False) -> bool:
    """
    Create a VSCode extension for the Runa language.

    Args:
        output_dir: Output directory for the extension
        advanced_mode: Whether to enable advanced language features by default

    Returns:
        Whether the extension was created successfully
    """
    try:
        # Create the extension directory structure
        extension_dir = os.path.join(output_dir, 'runa-vscode')
        os.makedirs(extension_dir, exist_ok=True)

        # Create the syntaxes directory for syntax highlighting
        syntaxes_dir = os.path.join(extension_dir, 'syntaxes')
        os.makedirs(syntaxes_dir, exist_ok=True)

        # Create the client directory for the language client
        client_dir = os.path.join(extension_dir, 'client')
        os.makedirs(client_dir, exist_ok=True)

        # Create the server directory for the language server
        server_dir = os.path.join(extension_dir, 'server')
        os.makedirs(server_dir, exist_ok=True)

        # Create the package.json file
        package_json = create_vscode_package_json(advanced_mode)
        with open(os.path.join(extension_dir, 'package.json'), 'w') as f:
            f.write(package_json)

        # Create the syntax highlighting definition
        syntax_json = create_vscode_syntax_json()
        with open(os.path.join(syntaxes_dir, 'runa.tmLanguage.json'), 'w') as f:
            f.write(syntax_json)

        # Create the language configuration
        language_config = create_vscode_language_config()
        with open(os.path.join(extension_dir, 'language-configuration.json'), 'w') as f:
            f.write(language_config)

        # Create the extension.js file
        extension_js = create_vscode_extension_js()
        with open(os.path.join(extension_dir, 'extension.js'), 'w') as f:
            f.write(extension_js)

        # Create the README.md file
        readme_md = create_vscode_readme_md()
        with open(os.path.join(extension_dir, 'README.md'), 'w') as f:
            f.write(readme_md)

        # Copy the language server files
        server_py = open(os.path.join(os.path.dirname(__file__), 'server.py')).read()
        with open(os.path.join(server_dir, 'server.py'), 'w') as f:
            f.write(server_py)

        # Create a simple launcher script
        launcher_py = """#!/usr/bin/env python3
import sys
import os

# Add the server directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and start the server
from server import start_server

if __name__ == "__main__":
    start_server()
"""
        with open(os.path.join(server_dir, 'launcher.py'), 'w') as f:
            f.write(launcher_py)

        # Make the launcher script executable
        os.chmod(os.path.join(server_dir, 'launcher.py'), 0o755)

        return True
    except Exception as e:
        print(f"Error creating VSCode extension: {str(e)}")
        return False


def create_vscode_package_json(advanced_mode: bool = False) -> str:
    """
    Create a package.json file for a VSCode extension.

    Args:
        advanced_mode: Whether to enable advanced language features by default

    Returns:
        The package.json content
    """
    return f'''{{
    "name": "runa-language",
    "displayName": "Runa Language",
    "description": "Runa programming language support",
    "version": "0.1.0",
    "publisher": "runa",
    "engines": {{
        "vscode": "^1.52.0"
    }},
    "categories": [
        "Programming Languages"
    ],
    "activationEvents": [
        "onLanguage:runa"
    ],
    "main": "./extension.js",
    "contributes": {{
        "languages": [
            {{
                "id": "runa",
                "aliases": [
                    "Runa",
                    "runa"
                ],
                "extensions": [
                    ".runa"
                ],
                "configuration": "./language-configuration.json"
            }}
        ],
        "grammars": [
            {{
                "language": "runa",
                "scopeName": "source.runa",
                "path": "./syntaxes/runa.tmLanguage.json"
            }}
        ],
        "configuration": {{
            "type": "object",
            "title": "Runa",
            "properties": {{
                "runaLanguageServer.maxNumberOfProblems": {{
                    "scope": "resource",
                    "type": "number",
                    "default": 100,
                    "description": "Controls the maximum number of problems produced by the server."
                }},
                "runaLanguageServer.trace.server": {{
                    "scope": "window",
                    "type": "string",
                    "enum": [
                        "off",
                        "messages",
                        "verbose"
                    ],
                    "default": "off",
                    "description": "Traces the communication between VS Code and the language server."
                }},
                "runaLanguageServer.advancedMode": {{
                    "scope": "resource",
                    "type": "boolean",
                    "default": {str(advanced_mode).lower()},
                    "description": "Enable advanced language features (pattern matching, async, functional, types)."
                }}
            }}
        }}
    }},
    "scripts": {{
        "vscode:prepublish": "npm run compile",
        "compile": "echo 'No compilation needed for Python'",
        "watch": "echo 'No watch needed for Python'",
        "test": "echo 'No tests yet'"
    }},
    "dependencies": {{
        "vscode-languageclient": "^7.0.0"
    }}
}}
'''


def create_vscode_syntax_json() -> str:
    """
    Create a syntax highlighting definition for VSCode.

    Returns:
        The syntax definition JSON
    """
    return '''
{
    "$schema": "https://raw.githubusercontent.com/martinring/tmlanguage/master/tmlanguage.json",
    "name": "Runa",
    "patterns": [
        {
            "include": "#comments"
        },
        {
            "include": "#keywords"
        },
        {
            "include": "#strings"
        },
        {
            "include": "#numbers"
        },
        {
            "include": "#variables"
        },
        {
            "include": "#functions"
        },
        {
            "include": "#operators"
        }
    ],
    "repository": {
        "comments": {
            "patterns": [
                {
                    "name": "comment.line.number-sign.runa",
                    "match": "#.*$"
                }
            ]
        },
        "keywords": {
            "patterns": [
                {
                    "name": "keyword.control.runa",
                    "match": "\\b(Let|Set|If|Otherwise|For|each|in|Return|Process|called|that|takes|Display|Import|Module|Match|When|Async|await|Lambda|Type|returns)\\b"
                },
                {
                    "name": "keyword.operator.runa",
                    "match": "\\b(is|not|equal|to|greater|than|less|plus|minus|multiplied|divided|modulo|at|index|length|of|and)\\b"
                },
                {
                    "name": "keyword.other.runa",
                    "match": "\\b(list|containing|dictionary|with|as|followed|by)\\b"
                },
                {
                    "name": "constant.language.runa",
                    "match": "\\b(true|false)\\b"
                },
                {
                    "name": "support.type.runa",
                    "match": "\\b(Any|Integer|Float|String|Boolean|List|Dictionary)\\b"
                }
            ]
        },
        "strings": {
            "name": "string.quoted.double.runa",
            "begin": "\"",
            "end": "\"",
            "patterns": [
                {
                    "name": "constant.character.escape.runa",
                    "match": "\\\\."
                }
            ]
        },
        "numbers": {
            "patterns": [
                {
                    "name": "constant.numeric.integer.runa",
                    "match": "\\b[0-9]+\\b"
                },
                {
                    "name": "constant.numeric.float.runa",
                    "match": "\\b[0-9]*\\.[0-9]+\\b"
                }
            ]
        },
        "variables": {
            "patterns": [
                {
                    "name": "variable.other.runa",
                    "match": "\\b[a-zA-Z_][a-zA-Z0-9_]*\\b",
                    "captures": {
                        "0": {
                            "name": "variable.other.runa"
                        }
                    }
                }
            ]
        },
        "functions": {
            "patterns": [
                {
                    "match": "\\b([a-zA-Z_][a-zA-Z0-9_]*)\\s+(with)\\b",
                    "captures": {
                        "1": {
                            "name": "entity.name.function.runa"
                        },
                        "2": {
                            "name": "keyword.operator.runa"
                        }
                    }
                }
            ]
        },
        "operators": {
            "patterns": [
                {
                    "name": "keyword.operator.runa",
                    "match": "\\|>"
                }
            ]
        }
    },
    "scopeName": "source.runa"
}
'''


def create_vscode_language_config() -> str:
    """
    Create a language configuration for VSCode.

    Returns:
        The language configuration JSON
    """
    return '''
{
    "comments": {
        "lineComment": "#"
    },
    "brackets": [
        ["{", "}"],
        ["[", "]"],
        ["(", ")"]
    ],
    "autoClosingPairs": [
        { "open": "{", "close": "}" },
        { "open": "[", "close": "]" },
        { "open": "(", "close": ")" },
        { "open": "\"", "close": "\"", "notIn": ["string"] }
    ],
    "surroundingPairs": [
        ["{", "}"],
        ["[", "]"],
        ["(", ")"],
        ["\"", "\""]
    ],
    "indentationRules": {
        "increaseIndentPattern": ".*:$",
        "decreaseIndentPattern": "^\\s*$"
    },
    "wordPattern": "[a-zA-Z_][a-zA-Z0-9_]*"
}
'''


def create_vscode_extension_js() -> str:
    """
    Create the VSCode extension.js file.

    Returns:
        The extension.js content
    """
    return '''
// The module 'vscode' contains the VS Code extensibility API
const vscode = require('vscode');
const path = require('path');
const { LanguageClient, TransportKind } = require('vscode-languageclient/node');

let client;

function activate(context) {
    // Get the Python executable to use for the server
    const pythonPath = vscode.workspace.getConfiguration('python').get('pythonPath') || 'python';

    // Get configuration
    const config = vscode.workspace.getConfiguration('runaLanguageServer');
    const advancedMode = config.get('advancedMode') || false;

    // The server is implemented in Python
    const serverPath = context.asAbsolutePath(path.join('server', 'launcher.py'));

    // If the extension is launched in debug mode, use a debug server
    const debugOptions = { execArgv: ['--nolazy', '--inspect=6009'] };

    // Options for running the server
    const serverOptions = {
        run: {
            command: pythonPath,
            args: [serverPath],
            options: {
                cwd: context.asAbsolutePath('server')
            }
        },
        debug: {
            command: pythonPath,
            args: [serverPath],
            options: {
                cwd: context.asAbsolutePath('server')
            }
        }
    };

    // Options to control the language client
    const clientOptions = {
        // Register the server for Runa files
        documentSelector: [
            { language: 'runa', scheme: 'file' },
            { language: 'runa', scheme: 'untitled' }
        ],
        synchronize: {
            // Notify the server about file changes in the workspace
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.runa')
        },
        initializationOptions: {
            advancedMode: advancedMode
        }
    };

    // Create the language client and start the client
    client = new LanguageClient(
        'runaLanguageServer',
        'Runa Language Server',
        serverOptions,
        clientOptions
    );

    // Start the client
    client.start();

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('runa.toggleAdvancedMode', () => {
            const config = vscode.workspace.getConfiguration('runaLanguageServer');
            const currentValue = config.get('advancedMode');

            // Toggle the value
            config.update('advancedMode', !currentValue, true).then(() => {
                // Restart the language server
                vscode.window.showInformationMessage(
                    `Advanced mode ${!currentValue ? 'enabled' : 'disabled'}. Please reload the window.`
                );
            });
        })
    );
}

function deactivate() {
    if (!client) {
        return undefined;
    }
    return client.stop();
}

module.exports = {
    activate,
    deactivate
};
'''


def create_vscode_readme_md() -> str:
    """
    Create a README.md file for a VSCode extension.

    Returns:
        The README.md content
    """
    return '''
# Runa Language for Visual Studio Code

This extension provides support for the Runa programming language in Visual Studio Code, including:

- Syntax highlighting
- Code completion
- Hover information
- Go to definition
- Error checking

## Features

### Syntax Highlighting

Runa code is colorized to make it easier to read and understand.

### Code Completion

The extension provides suggestions for keywords, built-in functions, and user-defined symbols.

### Hover Information

Hover over a symbol to see information about it.

### Go to Definition

Use "Go to Definition" to navigate to where a symbol was defined.

### Error Checking

The extension checks your code for errors as you type.

## Advanced Mode

The extension supports advanced Runa language features:

- Pattern matching
- Asynchronous programming
- Functional programming
- Enhanced type system

To enable advanced mode, set the `runaLanguageServer.advancedMode` setting to `true` in your settings.json file.

## Requirements

- Python 3.6 or later
- The `pygls` package (`pip install pygls`)

## Extension Settings

This extension contributes the following settings:

* `runaLanguageServer.maxNumberOfProblems`: Controls the maximum number of problems reported by the server.
* `runaLanguageServer.trace.server`: Traces the communication between VS Code and the language server.
* `runaLanguageServer.advancedMode`: Enables advanced language features.

## Commands

* `Runa: Toggle Advanced Mode`: Toggles advanced language features on/off.

## Release Notes

### 0.1.0

Initial release of the Runa language extension.
'''


if __name__ == "__main__":
    # Example usage: create a VSCode extension in the current directory
    output_dir = os.getcwd()
    create_vscode_extension(output_dir, advanced_mode=True)
    print(f"VSCode extension created in {os.path.join(output_dir, 'runa-vscode')}")