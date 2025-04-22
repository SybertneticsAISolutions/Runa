"""
Transpiler for the Runa programming language.
Converts Runa code to target languages (currently Python and JavaScript).
"""

from src.runa.lexer import RunaLexer
from src.runa.parser import RunaParser
from src.runa.analyzer import SemanticAnalyzer
from src.runa.targets import get_generator, list_targets, SUPPORTED_TARGETS
from src.runa.advanced import transpile_advanced


class Transpiler:
    """Main transpiler class for converting Runa code to target languages."""

    def __init__(self, target="python", advanced=False):
        """
        Initialize the transpiler with a target language and advanced features flag.

        Args:
            target: The target language to transpile to (e.g., 'python', 'javascript')
            advanced: Whether to enable advanced language features
        """
        self.target = target.lower()
        self.advanced = advanced

        # Verify that the target language is supported
        if self.target not in SUPPORTED_TARGETS:
            supported = ", ".join(list_targets())
            raise ValueError(f"Unsupported target language: {self.target}. Supported languages: {supported}")

        if not advanced:
            # Standard transpiler components
            self.parser = RunaParser()
            self.analyzer = SemanticAnalyzer()
            self.generator = get_generator(self.target)

    def transpile(self, source, analyze=True):
        """
        Transpile Runa source code to the target language.

        Args:
            source: The Runa source code to transpile
            analyze: Whether to perform semantic analysis

        Returns:
            A tuple (code, valid, errors, warnings) where:
            - code is the generated code (or None if analysis failed)
            - valid is a boolean indicating if the code is valid
            - errors is a list of error messages
            - warnings is a list of warning messages
        """
        if self.advanced:
            # Use the advanced transpiler with Python first
            code, valid, errors, warnings = transpile_advanced(source)

            # If targeting Python, return the result
            if self.target == "python":
                return code, valid, errors, warnings

            # Otherwise, parse the AST and generate for the target language
            if not valid:
                return None, False, errors, warnings

            # Re-parse the source to get the AST
            ast = self.parser.parse(source)

            # Generate code for the target language
            try:
                target_code = self.generator.generate(ast)
                return target_code, True, errors, warnings
            except Exception as e:
                errors.append(f"Error generating {self.target.capitalize()} code: {str(e)}")
                return None, False, errors, warnings

        else:
            # Standard transpilation process
            # Parse the source code
            ast = self.parser.parse(source)

            if not ast:
                return None, False, ["Failed to parse the source code"], []

            # Perform semantic analysis if requested
            if analyze:
                valid = self.analyzer.analyze(ast)
                errors = self.analyzer.errors
                warnings = self.analyzer.warnings

                if not valid:
                    return None, False, errors, warnings
            else:
                valid = True
                errors = []
                warnings = []

            # Generate code for the target language
            try:
                code = self.generator.generate(ast)
                return code, valid, errors, warnings
            except Exception as e:
                errors.append(f"Error generating {self.target.capitalize()} code: {str(e)}")
                return None, False, errors, warnings

    @staticmethod
    def supported_targets():
        """
        Get a list of supported target languages.

        Returns:
            A list of supported target language names
        """
        return list_targets()