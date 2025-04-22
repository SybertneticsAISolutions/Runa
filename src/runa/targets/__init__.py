"""
Target language support for the Runa programming language.

This module provides code generators for different target languages.
"""
from src.runa.targets.js_generator import JsCodeGenerator
from src.runa.generator import PyCodeGenerator

# Dictionary of supported target languages
SUPPORTED_TARGETS = {
    "python": PyCodeGenerator,
    "javascript": JsCodeGenerator,
    "js": JsCodeGenerator  # Alias for javascript
}


def get_generator(target):
    """
    Get a code generator for the specified target language.

    Args:
        target: The target language (e.g., 'python', 'javascript')

    Returns:
        A code generator instance for the target language

    Raises:
        ValueError: If the target language is not supported
    """
    target = target.lower()

    if target not in SUPPORTED_TARGETS:
        raise ValueError(f"Unsupported target language: {target}")

    generator_class = SUPPORTED_TARGETS[target]
    return generator_class()


def list_targets():
    """
    Get a list of supported target languages.

    Returns:
        A list of supported target language names
    """
    # Return unique target names (excluding aliases)
    return ["python", "javascript"]