"""
LLM Integration for Runa.

This package provides integration with Large Language Models for code generation,
completion, explanation, and knowledge extraction.
"""

from .base import (
    PromptType, LLMPrompt, LLMResponse, PromptTemplate,
    LLMProvider, LLMManager, llm_manager
)
from .openai_provider import OpenAIProvider
from .code_suggestion import SuggestionContext, Suggestion, CodeSuggestionEngine

# Register the OpenAI provider as the default
try:
    openai_provider = OpenAIProvider()
    llm_manager.register_provider("openai", openai_provider, default=True)
except Exception as e:
    print(f"Warning: Failed to initialize OpenAI provider: {e}")

__all__ = [
    'PromptType',
    'LLMPrompt',
    'LLMResponse',
    'PromptTemplate',
    'LLMProvider',
    'LLMManager',
    'llm_manager',
    'OpenAIProvider',
    'SuggestionContext',
    'Suggestion',
    'CodeSuggestionEngine'
] 