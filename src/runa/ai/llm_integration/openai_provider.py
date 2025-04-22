"""
OpenAI provider for LLM integration in Runa.

This module provides integration with OpenAI's API for LLM capabilities.
"""

import os
from typing import Dict, List, Any, Optional, Union
import openai
from .base import LLMProvider, LLMPrompt, LLMResponse, PromptType


class OpenAIProvider(LLMProvider):
    """Provider for OpenAI's API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable).
        """
        super().__init__(api_key or os.environ.get("OPENAI_API_KEY"))
        openai.api_key = self.api_key
        self._available_models = None
    
    def get_available_models(self) -> List[str]:
        """
        Get a list of available OpenAI models.
        
        Returns:
            List of model identifiers.
        """
        if self._available_models is None:
            try:
                response = openai.Model.list()
                self._available_models = [model.id for model in response.data]
            except Exception as e:
                print(f"Error fetching models: {e}")
                # Default to known models
                self._available_models = [
                    "gpt-4", "gpt-4-32k", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"
                ]
        
        return self._available_models
    
    def generate(self, prompt: Union[str, LLMPrompt]) -> LLMResponse:
        """
        Generate a response from OpenAI.
        
        Args:
            prompt: The prompt to send.
            
        Returns:
            The LLM's response.
            
        Raises:
            ValueError: If the model is not available.
            Exception: If the API call fails.
        """
        # Convert string prompt to LLMPrompt
        if isinstance(prompt, str):
            prompt = LLMPrompt(
                content=prompt,
                prompt_type=PromptType.CUSTOM
            )
        
        # Format for OpenAI
        params = prompt.format_for_provider("openai")
        model = params.get("model")
        
        # Validate model
        available_models = self.get_available_models()
        if model and model not in available_models:
            raise ValueError(f"Model not available: {model}")
        
        try:
            # Call the OpenAI API
            response = openai.ChatCompletion.create(**params)
            
            # Extract response content
            content = response.choices[0].message.content
            
            # Create LLMResponse
            return LLMResponse(
                content=content,
                model=response.model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "response_id": response.id
                }
            )
        except Exception as e:
            raise Exception(f"Error generating from OpenAI: {e}")
    
    def get_embedding(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """
        Get an embedding for the given text.
        
        Args:
            text: The text to get an embedding for.
            model: The embedding model to use.
            
        Returns:
            The embedding vector.
        """
        try:
            response = openai.Embedding.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error getting embedding from OpenAI: {e}")
    
    def complete_code(self, code: str, requirements: str, context: str = "", model: str = None) -> LLMResponse:
        """
        Complete a piece of Runa code.
        
        Args:
            code: The code to complete.
            requirements: Requirements for the completion.
            context: Additional context.
            model: The model to use.
            
        Returns:
            The LLM's response with the completed code.
        """
        from .base import llm_manager
        
        prompt = llm_manager.get_template("code_completion").format(
            code=code,
            requirements=requirements,
            context=context,
            model=model
        )
        
        return self.generate(prompt)
    
    def explain_code(self, code: str, model: str = None) -> LLMResponse:
        """
        Generate an explanation for Runa code.
        
        Args:
            code: The code to explain.
            model: The model to use.
            
        Returns:
            The LLM's explanation.
        """
        from .base import llm_manager
        
        prompt = llm_manager.get_template("code_explanation").format(
            code=code,
            model=model
        )
        
        return self.generate(prompt)
    
    def generate_code(self, requirements: str, context: str = "", model: str = None) -> LLMResponse:
        """
        Generate Runa code based on requirements.
        
        Args:
            requirements: What the code should do.
            context: Additional context.
            model: The model to use.
            
        Returns:
            The generated code.
        """
        from .base import llm_manager
        
        prompt = llm_manager.get_template("code_generation").format(
            requirements=requirements,
            context=context,
            model=model
        )
        
        return self.generate(prompt)
    
    def intent_to_code(self, intent: str, context: str = "", model: str = None) -> LLMResponse:
        """
        Convert natural language intent to Runa code.
        
        Args:
            intent: Natural language description of what the code should do.
            context: Additional context.
            model: The model to use.
            
        Returns:
            The generated code.
        """
        from .base import llm_manager
        
        prompt = llm_manager.get_template("intent_to_code").format(
            intent=intent,
            context=context,
            model=model
        )
        
        return self.generate(prompt)
    
    def extract_knowledge(self, code: str, model: str = None) -> LLMResponse:
        """
        Extract knowledge entities and relationships from Runa code.
        
        Args:
            code: The Runa code.
            model: The model to use.
            
        Returns:
            The extracted knowledge.
        """
        from .base import llm_manager
        
        prompt = llm_manager.get_template("knowledge_extraction").format(
            code=code,
            model=model
        )
        
        return self.generate(prompt) 