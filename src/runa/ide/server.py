"""
Language Server Protocol implementation for the Runa programming language.

This module provides LSP server capabilities for IDE integration.
"""
import os
import re
import json
import logging
import asyncio
from typing import List, Dict, Optional, Union, Any, Tuple

from pygls.server import LanguageServer
from pygls.lsp.methods import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_CLOSE,
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_HOVER,
    TEXT_DOCUMENT_DEFINITION,
    INITIALIZE,
)
from pygls.lsp.types import (
    CompletionItem,
    CompletionList,
    CompletionItemKind,
    CompletionParams,
    Diagnostic,
    DiagnosticSeverity,
    DidChangeTextDocumentParams,
    DidOpenTextDocumentParams,
    DidCloseTextDocumentParams,
    Hover,
    HoverParams,
    MarkupContent,
    MarkupKind,
    Position,
    Range,
    TextDocumentPositionParams,
    Location,
    InitializeParams,
    InitializeResult,
    TextDocumentSyncKind,
    CompletionOptions,
)

from src.runa.parser import RunaParser
from src.runa.analyzer import SemanticAnalyzer
from src.runa.advanced import parse_advanced, analyze_advanced

# Set up logging
logging.basicConfig(filename="runa_lsp.log", level=logging.DEBUG)
log = logging.getLogger(__name__)


class RunaLanguageServer(LanguageServer):
    """Runa Language Server implementation."""

    CONFIGURATION_SECTION = "runaLanguageServer"

    def __init__(self):
        """Initialize the Runa language server."""
        super().__init__()

        # Document state
        self.documents = {}
        self.ast_cache = {}
        self.symbol_table = {}
        self.diagnostics_cache = {}

        # Parser and analyzer
        self.parser = RunaParser()
        self.analyzer = SemanticAnalyzer()
        self.advanced_mode = False

        # Keywords and built-in functions for autocompletion
        self.keywords = [
            "Let", "Set", "Process", "called", "that", "takes", "Return",
            "If", "Otherwise", "For", "each", "in", "Display", "Import", "module",
            "list", "containing", "dictionary", "with", "as", "and", "followed", "by",
            "is", "not", "equal", "to", "greater", "than", "less", "plus", "minus",
            "multiplied", "divided", "modulo", "at", "index", "length", "of"
        ]

        self.advanced_keywords = [
            "Match", "When", "Async", "await", "Lambda", "Type",
            "Map", "Filter", "Reduce", "over", "using", "with", "initial",
            "returns", "Any", "Integer", "Float", "String", "Boolean", "List", "Dictionary"
        ]

        self.built_in_functions = [
            "print", "len", "range", "str", "int", "float", "bool", "list", "dict",
            "min", "max", "sum", "sorted", "reversed", "enumerate", "zip", "abs"
        ]

        # Register handlers
        self.register_handlers()

    def register_handlers(self):
        """Register LSP request and notification handlers."""
        # Lifecycle events
        @self.feature(INITIALIZE)
        def initialize(params: InitializeParams) -> InitializeResult:
            """Initialize the language server."""
            # Check if advanced mode is enabled in client configuration
            if hasattr(params, 'initializationOptions') and params.initializationOptions:
                if 'advancedMode' in params.initializationOptions:
                    self.advanced_mode = params.initializationOptions['advancedMode']

            log.info(f"Initialized Runa Language Server (advanced mode: {self.advanced_mode})")

            return InitializeResult(
                capabilities={
                    "textDocumentSync": {
                        "openClose": True,
                        "change": TextDocumentSyncKind.FULL,
                        "willSave": False,
                        "willSaveWaitUntil": False,
                        "save": {"includeText": False}
                    },
                    "completionProvider": {
                        "resolveProvider": False,
                        "triggerCharacters": [" ", "."]
                    },
                    "hoverProvider": True,
                    "definitionProvider": True
                }
            )

        # Document events
        @self.feature(TEXT_DOCUMENT_DID_OPEN)
        def did_open(params: DidOpenTextDocumentParams):
            """Handle document open event."""
            document_uri = params.textDocument.uri
            document_text = params.textDocument.text
            self.documents[document_uri] = document_text

            # Parse and analyze the document
            self._parse_and_analyze(document_uri, document_text)

        @self.feature(TEXT_DOCUMENT_DID_CHANGE)
        def did_change(params: DidChangeTextDocumentParams):
            """Handle document change event."""
            document_uri = params.textDocument.uri
            # We're using FULL sync, so we get the full document content
            document_text = params.contentChanges[0].text
            self.documents[document_uri] = document_text

            # Parse and analyze the document
            self._parse_and_analyze(document_uri, document_text)

        @self.feature(TEXT_DOCUMENT_DID_CLOSE)
        def did_close(params: DidCloseTextDocumentParams):
            """Handle document close event."""
            document_uri = params.textDocument.uri
            if document_uri in self.documents:
                del self.documents[document_uri]
            if document_uri in self.ast_cache:
                del self.ast_cache[document_uri]
            if document_uri in self.symbol_table:
                del self.symbol_table[document_uri]
            if document_uri in self.diagnostics_cache:
                # Clear diagnostics
                self.publish_diagnostics(document_uri, [])
                del self.diagnostics_cache[document_uri]

        # Code intelligence
        @self.feature(TEXT_DOCUMENT_COMPLETION)
        def completion(params: CompletionParams) -> CompletionList:
            """Provide code completion suggestions."""
            document_uri = params.textDocument.uri
            position = params.position

            return self._get_completion_items(document_uri, position)

        @self.feature(TEXT_DOCUMENT_HOVER)
        def hover(params: HoverParams) -> Hover:
            """Provide hover information."""
            document_uri = params.textDocument.uri
            position = params.position

            return self._get_hover_info(document_uri, position)

        @self.feature(TEXT_DOCUMENT_DEFINITION)
        def definition(params: TextDocumentPositionParams) -> Optional[Location]:
            """Provide go-to-definition support."""
            document_uri = params.textDocument.uri
            position = params.position

            return self._get_definition(document_uri, position)

    def _parse_and_analyze(self, document_uri: str, document_text: str):
        """
        Parse and analyze a document.

        Args:
            document_uri: The URI of the document
            document_text: The text content of the document
        """
        try:
            # Parse the document
            if self.advanced_mode:
                ast = parse_advanced(document_text)
            else:
                ast = self.parser.parse(document_text)

            self.ast_cache[document_uri] = ast

            # Reset diagnostics
            diagnostics = []

            if ast:
                # Analyze the document
                if self.advanced_mode:
                    valid = analyze_advanced(ast)
                    errors = []  # We need to extract errors from analyze_advanced
                else:
                    self.analyzer.reset()
                    valid = self.analyzer.analyze(ast)
                    errors = self.analyzer.errors

                # Create diagnostics for errors
                diagnostics = self._create_diagnostics(document_text, errors)

                # Extract symbol information for code intelligence
                self.symbol_table[document_uri] = self._extract_symbols(ast)
            else:
                # Parse error
                line = 0
                column = 0
                diagnostics = [
                    Diagnostic(
                        range=Range(
                            start=Position(line=line, character=column),
                            end=Position(line=line, character=column + 1)
                        ),
                        message="Parse error",
                        severity=DiagnosticSeverity.Error
                    )
                ]

            # Cache and publish diagnostics
            self.diagnostics_cache[document_uri] = diagnostics
            self.publish_diagnostics(document_uri, diagnostics)

        except Exception as e:
            log.error(f"Error parsing document: {str(e)}")
            # Report the exception as a diagnostic
            diagnostics = [
                Diagnostic(
                    range=Range(
                        start=Position(line=0, character=0),
                        end=Position(line=0, character=1)
                    ),
                    message=f"Error parsing document: {str(e)}",
                    severity=DiagnosticSeverity.Error
                )
            ]
            self.diagnostics_cache[document_uri] = diagnostics
            self.publish_diagnostics(document_uri, diagnostics)

    def _create_diagnostics(self, document_text: str, errors: List[str]) -> List[Diagnostic]:
        """
        Create LSP diagnostics from analyzer errors.

        Args:
            document_text: The document text
            errors: List of error messages

        Returns:
            List of Diagnostic objects
        """
        diagnostics = []
        lines = document_text.split('\n')

        for error in errors:
            # Extract line and column information from error message
            # Example: "Line 3, Column 10: Undefined variable 'foo'"
            match = re.search(r'Line (\d+), Column (\d+): (.*)', error)

            if match:
                line = int(match.group(1)) - 1  # LSP uses 0-based line numbers
                column = int(match.group(2)) - 1  # LSP uses 0-based column numbers
                message = match.group(3)

                # Create diagnostic range (from the error position to the end of the "word")
                word_end = column
                if line < len(lines):
                    line_text = lines[line]
                    for i in range(column, len(line_text)):
                        if not line_text[i].isalnum() and line_text[i] != '_':
                            break
                        word_end = i + 1

                # Create diagnostic
                diagnostics.append(
                    Diagnostic(
                        range=Range(
                            start=Position(line=line, character=column),
                            end=Position(line=line, character=word_end)
                        ),
                        message=message,
                        severity=DiagnosticSeverity.Error
                    )
                )
            else:
                # If we can't extract location, use line 0, column 0
                diagnostics.append(
                    Diagnostic(
                        range=Range(
                            start=Position(line=0, character=0),
                            end=Position(line=0, character=1)
                        ),
                        message=error,
                        severity=DiagnosticSeverity.Error
                    )
                )

        return diagnostics

    def _extract_symbols(self, ast) -> Dict[str, Dict[str, Any]]:
        """
        Extract symbol information from the AST.

        Args:
            ast: The abstract syntax tree

        Returns:
            Dictionary mapping symbol names to metadata
        """
        symbols = {}

        if not ast:
            return symbols

        # Extract variable declarations
        for statement in ast.statements:
            # Variable declaration
            from src.runa.ast.nodes import Declaration
            if isinstance(statement, Declaration):
                if hasattr(statement, 'position') and statement.position:
                    symbols[statement.name] = {
                        'kind': 'variable',
                        'position': statement.position,
                        'type': 'unknown'  # We would need type inference for this
                    }

            # Function/process definition
            from src.runa.ast.nodes import ProcessDefinition
            if isinstance(statement, ProcessDefinition):
                if hasattr(statement, 'position') and statement.position:
                    symbols[statement.name] = {
                        'kind': 'function',
                        'position': statement.position,
                        'parameters': [param.name for param in statement.parameters],
                        'return_type': 'unknown'  # We would need type inference for this
                    }

            # Advanced: Type alias
            if self.advanced_mode:
                from src.runa.types.nodes import TypeAlias
                if isinstance(statement, TypeAlias):
                    if hasattr(statement, 'position') and statement.position:
                        symbols[statement.name] = {
                            'kind': 'type',
                            'position': statement.position,
                            'target_type': str(statement.target_type)
                        }

        return symbols

    def _get_word_at_position(self, document_text: str, position: Position) -> str:
        """
        Get the word at a given position in the document.

        Args:
            document_text: The document text
            position: The position

        Returns:
            The word at the position
        """
        lines = document_text.split('\n')
        if position.line >= len(lines):
            return ""

        line = lines[position.line]
        if position.character >= len(line):
            return ""

        # Find the start of the word
        start = position.character
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == '_'):
            start -= 1

        # Find the end of the word
        end = position.character
        while end < len(line) and (line[end].isalnum() or line[end] == '_'):
            end += 1

        return line[start:end]

    def _get_completion_items(self, document_uri: str, position: Position) -> CompletionList:
        """
        Get completion items for a given position.

        Args:
            document_uri: The document URI
            position: The position

        Returns:
            List of completion items
        """
        if document_uri not in self.documents:
            return CompletionList(is_incomplete=False, items=[])

        document_text = self.documents[document_uri]
        lines = document_text.split('\n')

        if position.line >= len(lines):
            return CompletionList(is_incomplete=False, items=[])

        line = lines[position.line]

        # Get the current line up to the cursor position
        line_prefix = line[:position.character]

        # Start with all keywords and built-in functions
        completion_items = []

        # Add keywords
        for keyword in self.keywords:
            completion_items.append(
                CompletionItem(
                    label=keyword,
                    kind=CompletionItemKind.Keyword,
                    detail="Runa keyword",
                    documentation=f"Keyword: {keyword}"
                )
            )

        # Add advanced keywords if in advanced mode
        if self.advanced_mode:
            for keyword in self.advanced_keywords:
                completion_items.append(
                    CompletionItem(
                        label=keyword,
                        kind=CompletionItemKind.Keyword,
                        detail="Runa advanced keyword",
                        documentation=f"Advanced keyword: {keyword}"
                    )
                )

        # Add built-in functions
        for func in self.built_in_functions:
            completion_items.append(
                CompletionItem(
                    label=func,
                    kind=CompletionItemKind.Function,
                    detail="Built-in function",
                    documentation=f"Built-in function: {func}"
                )
            )

        # Add user-defined symbols from the symbol table
        if document_uri in self.symbol_table:
            for name, metadata in self.symbol_table[document_uri].items():
                if metadata['kind'] == 'variable':
                    completion_items.append(
                        CompletionItem(
                            label=name,
                            kind=CompletionItemKind.Variable,
                            detail=f"Variable: {metadata.get('type', 'unknown')}",
                            documentation=f"Variable: {name}"
                        )
                    )
                elif metadata['kind'] == 'function':
                    params = ', '.join(metadata.get('parameters', []))
                    completion_items.append(
                        CompletionItem(
                            label=name,
                            kind=CompletionItemKind.Function,
                            detail=f"Function: ({params}) -> {metadata.get('return_type', 'unknown')}",
                            documentation=f"Function: {name}({params})"
                        )
                    )
                elif metadata['kind'] == 'type':
                    completion_items.append(
                        CompletionItem(
                            label=name,
                            kind=CompletionItemKind.Class,
                            detail=f"Type: {metadata.get('target_type', 'unknown')}",
                            documentation=f"Type: {name} = {metadata.get('target_type', 'unknown')}"
                        )
                    )

        # Filter items based on context
        filtered_items = []

        # Check for specific contexts where we can provide more targeted completions
        # For example, after "Let " we can suggest variable names and types
        if line_prefix.strip().endswith("Let"):
            # Suggest variable names
            for name in ["value", "result", "index", "count", "text", "data", "item", "items"]:
                filtered_items.append(
                    CompletionItem(
                        label=name,
                        kind=CompletionItemKind.Variable,
                        detail="Variable name suggestion",
                        documentation=f"Suggested variable name: {name}"
                    )
                )

        # After "Process called" we can suggest function names
        elif line_prefix.strip().endswith("called"):
            # Suggest function names
            for name in ["calculate", "process", "compute", "format", "validate", "get", "set", "check"]:
                filtered_items.append(
                    CompletionItem(
                        label=f'"{name}"',
                        kind=CompletionItemKind.Function,
                        detail="Function name suggestion",
                        documentation=f'Suggested function name: "{name}"'
                    )
                )

        # After "If" we can suggest conditions
        elif line_prefix.strip().endswith("If"):
            # Suggest conditions
            for cond in ["value is equal to", "value is greater than", "value is less than", "value is not equal to"]:
                filtered_items.append(
                    CompletionItem(
                        label=cond,
                        kind=CompletionItemKind.Snippet,
                        detail="Condition suggestion",
                        documentation=f"Suggested condition: {cond}"
                    )
                )

        # Use filtered items if available, otherwise use all items
        items = filtered_items if filtered_items else completion_items

        return CompletionList(is_incomplete=False, items=items)

    def _get_hover_info(self, document_uri: str, position: Position) -> Optional[Hover]:
        """
        Get hover information for a given position.

        Args:
            document_uri: The document URI
            position: The position

        Returns:
            Hover information, or None if not available
        """
        if document_uri not in self.documents or document_uri not in self.symbol_table:
            return None

        document_text = self.documents[document_uri]
        symbols = self.symbol_table[document_uri]

        # Get the word at the current position
        word = self._get_word_at_position(document_text, position)
        if not word:
            return None

        # Check if the word is a symbol
        if word in symbols:
            metadata = symbols[word]

            if metadata['kind'] == 'variable':
                content = f"Variable: {word}\nType: {metadata.get('type', 'unknown')}"
            elif metadata['kind'] == 'function':
                params = ', '.join(metadata.get('parameters', []))
                content = f"Function: {word}({params})\nReturn type: {metadata.get('return_type', 'unknown')}"
            elif metadata['kind'] == 'type':
                content = f"Type: {word} = {metadata.get('target_type', 'unknown')}"
            else:
                content = f"Symbol: {word}"

            return Hover(
                contents=MarkupContent(kind=MarkupKind.MARKDOWN, value=content),
                range=Range(
                    start=Position(line=position.line, character=position.character - len(word)),
                    end=Position(line=position.line, character=position.character)
                )
            )

        # Check if the word is a keyword
        if word in self.keywords:
            return Hover(
                contents=MarkupContent(kind=MarkupKind.MARKDOWN, value=f"Keyword: {word}"),
                range=Range(
                    start=Position(line=position.line, character=position.character - len(word)),
                    end=Position(line=position.line, character=position.character)
                )
            )

        # Check if the word is an advanced keyword
        if self.advanced_mode and word in self.advanced_keywords:
            return Hover(
                contents=MarkupContent(kind=MarkupKind.MARKDOWN, value=f"Advanced keyword: {word}"),
                range=Range(
                    start=Position(line=position.line, character=position.character - len(word)),
                    end=Position(line=position.line, character=position.character)
                )
            )

        # Check if the word is a built-in function
        if word in self.built_in_functions:
            return Hover(
                contents=MarkupContent(kind=MarkupKind.MARKDOWN, value=f"Built-in function: {word}"),
                range=Range(
                    start=Position(line=position.line, character=position.character - len(word)),
                    end=Position(line=position.line, character=position.character)
                )
            )

        return None

    def _get_definition(self, document_uri: str, position: Position) -> Optional[Location]:
        """
        Get the definition location for a symbol at a given position.

        Args:
            document_uri: The document URI
            position: The position

        Returns:
            Location of the definition, or None if not available
        """
        if document_uri not in self.documents or document_uri not in self.symbol_table:
            return None

        document_text = self.documents[document_uri]
        symbols = self.symbol_table[document_uri]

        # Get the word at the current position
        word = self._get_word_at_position(document_text, position)
        if not word:
            return None

        # Check if the word is a symbol
        if word in symbols:
            metadata = symbols[word]
            if 'position' in metadata and metadata['position']:
                pos = metadata['position']

                # Convert position to LSP location
                return Location(
                    uri=document_uri,
                    range=Range(
                        start=Position(line=pos.line - 1, character=pos.column - 1),
                        end=Position(line=pos.line - 1, character=pos.column - 1 + len(word))
                    )
                )

        return None


def start_server():
    """Start the Runa language server."""
    server = RunaLanguageServer()
    server.start_io()


if __name__ == "__main__":
    start_server()