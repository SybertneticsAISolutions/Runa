/**
 * Monaco Editor integration for the Runa programming language.
 *
 * This module provides language definition, syntax highlighting,
 * and LSP client for the Monaco Editor.
 */

// Define the Runa language for Monaco Editor
export function defineRunaLanguage(monaco) {
    // Register a new language
    monaco.languages.register({ id: 'runa' });

    // Define the token provider for syntax highlighting
    monaco.languages.setMonarchTokensProvider('runa', {
        // Set defaultToken to invalid to see what you do not tokenize yet
        defaultToken: 'invalid',

        keywords: [
            'Let', 'Set', 'Process', 'called', 'that', 'takes', 'Return',
            'If', 'Otherwise', 'For', 'each', 'in', 'Display', 'Import', 'module',
            'list', 'containing', 'dictionary', 'with', 'as', 'and', 'followed', 'by',
            'is', 'not', 'equal', 'to', 'greater', 'than', 'less', 'plus', 'minus',
            'multiplied', 'divided', 'modulo', 'at', 'index', 'length', 'of'
        ],

        advancedKeywords: [
            'Match', 'When', 'Async', 'await', 'Lambda', 'Type',
            'Map', 'Filter', 'Reduce', 'over', 'using', 'with', 'initial',
            'returns', 'Any', 'Integer', 'Float', 'String', 'Boolean', 'List', 'Dictionary'
        ],

        typeKeywords: [
            'Any', 'Integer', 'Float', 'String', 'Boolean', 'List', 'Dictionary'
        ],

        operators: [
            '+', '-', '*', '/', '%', '=', '!', '>', '<', '&', '|', '^'
        ],

        // we include these common regular expressions
        symbols: /[=><!~?:&|+\-*\/^%]+/,
        escapes: /\\(?:[abfnrtv\\"']|x[0-9A-Fa-f]{1,4}|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8})/,

        // The main tokenizer for our languages
        tokenizer: {
            root: [
                // Comments
                [/#.*$/, 'comment'],

                // Strings
                [/"([^"\\]|\\.)*$/, 'string.invalid'],  // non-terminated string
                [/'([^'\\]|\\.)*$/, 'string.invalid'],  // non-terminated string
                [/"/, { token: 'string.quote', bracket: '@open', next: '@string_double' }],
                [/'/, { token: 'string.quote', bracket: '@open', next: '@string_single' }],

                // Numbers
                [/\d+\.\d*([eE][-+]?\d+)?/, 'number.float'],
                [/\.\d+([eE][-+]?\d+)?/, 'number.float'],
                [/\d+[eE][-+]?\d+/, 'number.float'],
                [/\d+/, 'number'],

                // Booleans
                [/true|false/, 'keyword'],

                // Identifiers and keywords
                [/[a-zA-Z_]\w*/, {
                    cases: {
                        '@keywords': 'keyword',
                        '@advancedKeywords': 'keyword.advanced',
                        '@typeKeywords': 'keyword.type',
                        '@default': 'identifier'
                    }
                }],

                // Delimiters and operators
                [/[()\[\]{}]/, '@brackets'],
                [/[<>](?!@symbols)/, '@brackets'],
                [/@symbols/, {
                    cases: {
                        '@operators': 'operator',
                        '@default': ''
                    }
                }],

                // Whitespace
                [/\s+/, 'white']
            ],

            string_double: [
                [/[^\\"]+/, 'string'],
                [/@escapes/, 'string.escape'],
                [/\\./, 'string.escape.invalid'],
                [/"/, { token: 'string.quote', bracket: '@close', next: '@pop' }]
            ],

            string_single: [
                [/[^\\']+/, 'string'],
                [/@escapes/, 'string.escape'],
                [/\\./, 'string.escape.invalid'],
                [/'/, { token: 'string.quote', bracket: '@close', next: '@pop' }]
            ]
        }
    });

    // Define a language configuration for comment toggling, brackets, auto-closing, etc.
    monaco.languages.setLanguageConfiguration('runa', {
        comments: {
            lineComment: '#',
        },
        brackets: [
            ['{', '}'],
            ['[', ']'],
            ['(', ')']
        ],
        autoClosingPairs: [
            { open: '{', close: '}' },
            { open: '[', close: ']' },
            { open: '(', close: ')' },
            { open: '"', close: '"', notIn: ['string'] },
            { open: '\'', close: '\'', notIn: ['string'] },
        ],
        surroundingPairs: [
            { open: '{', close: '}' },
            { open: '[', close: ']' },
            { open: '(', close: ')' },
            { open: '"', close: '"' },
            { open: '\'', close: '\'' },
        ],
        folding: {
            markers: {
                start: new RegExp('^\\s*#region\\b'),
                end: new RegExp('^\\s*#endregion\\b')
            }
        },
        indentationRules: {
            increaseIndentPattern: new RegExp('^.*:\\s*$'),
            decreaseIndentPattern: new RegExp('^\\s*(?:Otherwise|When)\\b')
        }
    });

    // Define the language completion provider
    monaco.languages.registerCompletionItemProvider('runa', {
        provideCompletionItems: (model, position) => {
            const text = model.getValue();
            const line = model.getLineContent(position.lineNumber);
            const word = model.getWordUntilPosition(position);
            const range = {
                startLineNumber: position.lineNumber,
                endLineNumber: position.lineNumber,
                startColumn: word.startColumn,
                endColumn: word.endColumn
            };

            // Create suggestions based on context
            const suggestions = [];

            // Add keywords
            const keywords = [
                'Let', 'Set', 'Process', 'called', 'that', 'takes', 'Return',
                'If', 'Otherwise', 'For', 'each', 'in', 'Display', 'Import', 'module',
                'list', 'containing', 'dictionary', 'with', 'as', 'and', 'followed', 'by',
                'is', 'not', 'equal', 'to', 'greater', 'than', 'less', 'plus', 'minus',
                'multiplied', 'divided', 'modulo', 'at', 'index', 'length', 'of'
            ];

            const advancedKeywords = [
                'Match', 'When', 'Async', 'await', 'Lambda', 'Type',
                'Map', 'Filter', 'Reduce', 'over', 'using', 'with', 'initial',
                'returns', 'Any', 'Integer', 'Float', 'String', 'Boolean', 'List', 'Dictionary'
            ];

            // Add all keywords with descriptions
            for (const keyword of keywords) {
                suggestions.push({
                    label: keyword,
                    kind: monaco.languages.CompletionItemKind.Keyword,
                    insertText: keyword,
                    range: range,
                    detail: 'Runa keyword',
                    documentation: `Keyword: ${keyword}`
                });
            }

            // Add advanced keywords if needed
            const useAdvanced = true; // This could be configurable
            if (useAdvanced) {
                for (const keyword of advancedKeywords) {
                    suggestions.push({
                        label: keyword,
                        kind: monaco.languages.CompletionItemKind.Keyword,
                        insertText: keyword,
                        range: range,
                        detail: 'Runa advanced keyword',
                        documentation: `Advanced keyword: ${keyword}`
                    });
                }
            }

            // Context-sensitive suggestions
            const lineUntilPosition = line.substring(0, position.column - 1).trim();

            // After "Let" suggest variable names
            if (lineUntilPosition.endsWith('Let')) {
                for (const suggestion of ['value', 'result', 'index', 'count', 'text', 'data', 'item', 'items']) {
                    suggestions.push({
                        label: suggestion,
                        kind: monaco.languages.CompletionItemKind.Variable,
                        insertText: suggestion,
                        range: range,
                        detail: 'Variable name suggestion',
                        documentation: `Suggested variable name: ${suggestion}`
                    });
                }
            }

            // After "Process called" suggest function names
            else if (lineUntilPosition.endsWith('called')) {
                for (const suggestion of ['calculate', 'process', 'compute', 'format', 'validate', 'get', 'set', 'check']) {
                    suggestions.push({
                        label: `"${suggestion}"`,
                        kind: monaco.languages.CompletionItemKind.Function,
                        insertText: `"${suggestion}"`,
                        range: range,
                        detail: 'Function name suggestion',
                        documentation: `Suggested function name: "${suggestion}"`
                    });
                }
            }

            // After "If" suggest conditions
            else if (lineUntilPosition.endsWith('If')) {
                for (const suggestion of ['value is equal to', 'value is greater than', 'value is less than', 'value is not equal to']) {
                    suggestions.push({
                        label: suggestion,
                        kind: monaco.languages.CompletionItemKind.Snippet,
                        insertText: suggestion,
                        range: range,
                        detail: 'Condition suggestion',
                        documentation: `Suggested condition: ${suggestion}`
                    });
                }
            }

            // Return the suggestions
            return {
                suggestions: suggestions
            };
        }
    });

    // Define a theme for Runa
    monaco.editor.defineTheme('runa-theme', {
        base: 'vs',
        inherit: true,
        rules: [
            { token: 'keyword', foreground: '0000ff', fontStyle: 'bold' },
            { token: 'keyword.advanced', foreground: '8000ff', fontStyle: 'bold' },
            { token: 'keyword.type', foreground: '008000', fontStyle: 'bold' },
            { token: 'identifier', foreground: '000000' },
            { token: 'string', foreground: 'a31515' },
            { token: 'number', foreground: '098658' },
            { token: 'comment', foreground: '008800', fontStyle: 'italic' }
        ],
        colors: {
            'editor.foreground': '#000000',
            'editor.background': '#ffffff',
            'editor.selectionBackground': '#b5d5ff',
            'editor.lineHighlightBackground': '#f0f0f0',
            'editorCursor.foreground': '#000000',
            'editorWhitespace.foreground': '#d3d3d3'
        }
    });
}

// Create a connection to the language server
export function createLanguageClient(monaco, editorInstance, workspaceRoot) {
    // Check if the Monaco language client is available
    if (!window.MonacoServices || !window.monaco.languages.register) {
        console.error('Monaco language client not available');
        return null;
    }

    // Register Monaco languages
    window.MonacoServices.install(monaco);

    // Create the WebSocket connection to the language server
    const url = 'ws://localhost:3000/runa-lsp';
    const webSocket = new WebSocket(url);

    // Create the language client
    const languageClient = new window.monaco.languages.LanguageClient({
        name: 'Runa Language Client',
        clientOptions: {
            // Use the current workspace directory
            workspaceFolder: {
                uri: monaco.Uri.file(workspaceRoot),
                name: 'Runa Workspace'
            },
            // Define the language IDs that the client supports
            documentSelector: ['runa'],
            // Synchronize settings, file events, etc.
            synchronize: {
                configurationSection: 'runaLanguageServer',
                fileEvents: monaco.workspace.onDidCreateFiles
            },
            // Initialization options sent to the server
            initializationOptions: {
                advancedMode: true
            }
        },
        // Communication via WebSocket
        connectionProvider: {
            get: () => {
                return Promise.resolve({
                    reader: webSocket,
                    writer: webSocket
                });
            }
        }
    });

    // Set up event listeners for WebSocket
    webSocket.addEventListener('open', () => {
        console.log('WebSocket connection to Runa language server established');
        languageClient.start();
    });

    webSocket.addEventListener('error', (error) => {
        console.error('WebSocket connection error:', error);
    });

    webSocket.addEventListener('close', () => {
        console.log('WebSocket connection to Runa language server closed');
    });

    return languageClient;
}

// Create a Monaco editor with Runa language support
export function createRunaEditor(container, initialValue = '', options = {}) {
    // Load Monaco editor
    const monaco = window.monaco;
    if (!monaco) {
        console.error('Monaco editor not loaded');
        return null;
    }

    // Define the Runa language
    defineRunaLanguage(monaco);

    // Create editor with default options
    const defaultOptions = {
        value: initialValue,
        language: 'runa',
        theme: 'runa-theme',
        automaticLayout: true,
        minimap: { enabled: true },
        lineNumbers: 'on',
        scrollBeyondLastLine: false,
        roundedSelection: true,
        padding: { top: 10 },
        fontSize: 14,
        fontFamily: 'Menlo, Monaco, "Courier New", monospace',
        rulers: [],
        wordWrap: 'on'
    };

    // Merge default options with user-provided options
    const editorOptions = { ...defaultOptions, ...options };

    // Create the editor
    return monaco.editor.create(container, editorOptions);
}