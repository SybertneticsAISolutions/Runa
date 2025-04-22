"""
Base classes and interfaces for LLM integration in Runa.

This module provides the foundation for integrating Large Language Models
with Runa, including prompt formatting, response handling, and context management.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum


class PromptType(Enum):
    """Types of prompts for different LLM tasks."""
    CODE_GENERATION = "code_generation"
    CODE_COMPLETION = "code_completion"
    CODE_EXPLANATION = "code_explanation"
    INTENT_TO_CODE = "intent_to_code"
    CODE_REVIEW = "code_review"
    KNOWLEDGE_EXTRACTION = "knowledge_extraction"
    KNOWLEDGE_LINKING = "knowledge_linking"
    BRAIN_HAT_COMMUNICATION = "brain_hat_communication"
    CUSTOM = "custom"


@dataclass
class LLMResponse:
    """Represents a response from an LLM."""
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    metadata: Dict[str, Any] = None
    
    @property
    def tokens_used(self) -> int:
        """Get the total number of tokens used."""
        return self.prompt_tokens + self.completion_tokens


@dataclass
class LLMPrompt:
    """Represents a prompt to send to an LLM."""
    content: str
    prompt_type: PromptType
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stop_sequences: List[str] = None
    metadata: Dict[str, Any] = None
    
    def format_for_provider(self, provider: str) -> Dict[str, Any]:
        """
        Format the prompt for a specific provider.
        
        Args:
            provider: The LLM provider name (e.g., "openai", "anthropic").
            
        Returns:
            Dictionary with provider-specific parameters.
        """
        if provider == "openai":
            return {
                "messages": [{"role": "user", "content": self.content}],
                "model": self.model or "gpt-4",
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stop": self.stop_sequences
            }
        elif provider == "anthropic":
            return {
                "prompt": f"Human: {self.content}\n\nAssistant:",
                "model": self.model or "claude-2",
                "temperature": self.temperature,
                "max_tokens_to_sample": self.max_tokens,
                "stop_sequences": self.stop_sequences or ["\n\nHuman:"]
            }
        else:
            # Default format (provider-agnostic)
            return {
                "prompt": self.content,
                "model": self.model,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stop": self.stop_sequences
            }


class PromptTemplate:
    """Template for generating prompts."""
    
    def __init__(
        self, 
        template: str,
        prompt_type: PromptType = PromptType.CUSTOM,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: List[str] = None
    ):
        """
        Initialize a prompt template.
        
        Args:
            template: String template with placeholders.
            prompt_type: Type of prompt this template generates.
            model: Default model to use.
            temperature: Default temperature setting.
            max_tokens: Default maximum tokens to generate.
            stop_sequences: Default stop sequences.
        """
        self.template = template
        self.prompt_type = prompt_type
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stop_sequences = stop_sequences
    
    def format(self, **kwargs) -> LLMPrompt:
        """
        Format the template with provided values.
        
        Args:
            **kwargs: Values to fill in the template placeholders.
            
        Returns:
            Formatted LLMPrompt object.
        """
        content = self.template.format(**kwargs)
        
        # Extract any override parameters from kwargs
        model = kwargs.get("model", self.model)
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        stop_sequences = kwargs.get("stop_sequences", self.stop_sequences)
        
        return LLMPrompt(
            content=content,
            prompt_type=self.prompt_type,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stop_sequences=stop_sequences,
            metadata=kwargs.get("metadata", {})
        )


class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM provider.
        
        Args:
            api_key: API key for the provider.
        """
        self.api_key = api_key
    
    @abstractmethod
    def generate(self, prompt: Union[str, LLMPrompt]) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The prompt to send.
            
        Returns:
            The LLM's response.
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get a list of available models.
        
        Returns:
            List of model identifiers.
        """
        pass


class LLMManager:
    """Manager for LLM interactions."""
    
    def __init__(self):
        """Initialize the LLM manager."""
        self.providers: Dict[str, LLMProvider] = {}
        self.templates: Dict[str, PromptTemplate] = {}
        self.default_provider: Optional[str] = None
    
    def register_provider(self, name: str, provider: LLMProvider, default: bool = False):
        """
        Register an LLM provider.
        
        Args:
            name: Name to register the provider under.
            provider: The provider instance.
            default: Whether this is the default provider.
        """
        self.providers[name] = provider
        
        if default or self.default_provider is None:
            self.default_provider = name
    
    def register_template(self, name: str, template: PromptTemplate):
        """
        Register a prompt template.
        
        Args:
            name: Name to register the template under.
            template: The template instance.
        """
        self.templates[name] = template
    
    def get_provider(self, name: Optional[str] = None) -> LLMProvider:
        """
        Get a provider by name.
        
        Args:
            name: The provider name, or None for the default.
            
        Returns:
            The provider instance.
            
        Raises:
            ValueError: If no provider is found.
        """
        provider_name = name or self.default_provider
        
        if not provider_name or provider_name not in self.providers:
            raise ValueError(f"Provider not found: {provider_name}")
        
        return self.providers[provider_name]
    
    def get_template(self, name: str) -> PromptTemplate:
        """
        Get a template by name.
        
        Args:
            name: The template name.
            
        Returns:
            The template instance.
            
        Raises:
            ValueError: If no template is found.
        """
        if name not in self.templates:
            raise ValueError(f"Template not found: {name}")
        
        return self.templates[name]
    
    def generate(
        self, 
        prompt: Union[str, LLMPrompt],
        provider: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate a response from an LLM.
        
        Args:
            prompt: The prompt to send.
            provider: The provider to use, or None for the default.
            
        Returns:
            The LLM's response.
        """
        provider_instance = self.get_provider(provider)
        return provider_instance.generate(prompt)
    
    def generate_from_template(
        self,
        template_name: str,
        provider: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response using a template.
        
        Args:
            template_name: The name of the template to use.
            provider: The provider to use, or None for the default.
            **kwargs: Values to fill in the template.
            
        Returns:
            The LLM's response.
        """
        template = self.get_template(template_name)
        prompt = template.format(**kwargs)
        return self.generate(prompt, provider)


# Create a global LLM manager instance
llm_manager = LLMManager()


# Common prompt templates
CODE_GENERATION_TEMPLATE = """
# Task: Generate Runa code for the following task

## Requirements
{requirements}

## Additional Context
{context}

## Generate complete, well-documented Runa code that implements the requirements:
"""

CODE_COMPLETION_TEMPLATE = """
# Task: Complete the following Runa code

## Context
{context}

## Code to Complete
```
{code}
```

## Complete the code according to the following requirements
{requirements}

## Your completion should seamlessly continue from the existing code:
"""

CODE_EXPLANATION_TEMPLATE = """
# Task: Explain the following Runa code

## Code
```
{code}
```

## Provide a clear, detailed explanation of how this code works:
"""

INTENT_TO_CODE_TEMPLATE = """
# Task: Convert natural language intent to Runa code

## Intent
{intent}

## Additional Context
{context}

## Generate Runa code that implements the described intent:
"""

KNOWLEDGE_EXTRACTION_TEMPLATE = """
# Task: Extract knowledge entities and relationships from the following Runa code

## Code
```
{code}
```

## Extract and list all relevant knowledge entities (concepts, algorithms, data structures) 
## and the relationships between them:
"""

BRAIN_HAT_TEMPLATE = """
# Task: {task_type} communication between Brain and Hat components

## Context
{context}

## Brain's Reasoning
{brain_reasoning}

## Hat's Implementation
{hat_implementation}

## {task_type} the communication between Brain and Hat components:
"""

# Register standard templates
llm_manager.register_template(
    "code_generation", 
    PromptTemplate(
        template=CODE_GENERATION_TEMPLATE,
        prompt_type=PromptType.CODE_GENERATION
    )
)

llm_manager.register_template(
    "code_completion", 
    PromptTemplate(
        template=CODE_COMPLETION_TEMPLATE,
        prompt_type=PromptType.CODE_COMPLETION
    )
)

llm_manager.register_template(
    "code_explanation", 
    PromptTemplate(
        template=CODE_EXPLANATION_TEMPLATE,
        prompt_type=PromptType.CODE_EXPLANATION
    )
)

llm_manager.register_template(
    "intent_to_code", 
    PromptTemplate(
        template=INTENT_TO_CODE_TEMPLATE,
        prompt_type=PromptType.INTENT_TO_CODE
    )
)

llm_manager.register_template(
    "knowledge_extraction", 
    PromptTemplate(
        template=KNOWLEDGE_EXTRACTION_TEMPLATE,
        prompt_type=PromptType.KNOWLEDGE_EXTRACTION
    )
)

llm_manager.register_template(
    "brain_hat", 
    PromptTemplate(
        template=BRAIN_HAT_TEMPLATE,
        prompt_type=PromptType.BRAIN_HAT_COMMUNICATION
    )
) 