"""
Transpiler for the Runa programming language.
Converts Runa code to target languages (currently only Python).
"""

from lexer import RunaLexer
from parser import RunaParser
from analyzer import SemanticAnalyzer
from generator import PyCodeGenerator


class Transpiler:
    """Main transpiler class for converting Runa code to target languages."""

    def __init__(self, target="python"):
        """Initialize the transpiler with a target language."""
        self.target = target
        self.parser = RunaParser()
        self.analyzer = SemanticAnalyzer()

        # Select the appropriate code generator based on target language
        if target == "python":
            self.generator = PyCodeGenerator()
        else:
            raise ValueError(f"Unsupported target language: {target}")

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
        code = self.generator.generate(ast)

        return code, valid, errors, warnings