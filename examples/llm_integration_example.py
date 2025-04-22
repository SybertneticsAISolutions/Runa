#!/usr/bin/env python3
"""
LLM Integration Example for Runa

This example demonstrates how to use the LLM integration to generate,
complete, and explain Runa code, as well as extract knowledge from it.
"""

import os
import sys
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.runa.ai.llm_integration import (
    llm_manager, OpenAIProvider, PromptTemplate, PromptType
)

# Check if OpenAI API key is available
if not os.environ.get("OPENAI_API_KEY"):
    print("Warning: OPENAI_API_KEY environment variable not set.")
    print("To run this example, set your OpenAI API key as an environment variable:")
    print("export OPENAI_API_KEY='your-api-key'")
    # For demo purposes, continue anyway
    print("Continuing with mock responses for demonstration purposes...\n")


class MockProvider:
    """Mock provider for demonstration when no API key is available."""
    
    def generate(self, prompt):
        """Generate a mock response."""
        from src.runa.ai.llm_integration import LLMResponse
        
        # Extract the prompt type to customize the mock response
        prompt_type = None
        if hasattr(prompt, "prompt_type"):
            prompt_type = prompt.prompt_type
        
        # Generate different mock responses based on prompt type
        if prompt_type == PromptType.CODE_GENERATION:
            content = """
Process called "fibonacci" that takes n:
    # Calculate the nth Fibonacci number
    If n <= 0:
        Return 0
    Else If n == 1:
        Return 1
    Else:
        Let a be 0
        Let b be 1
        Let temp be 0
        
        For i from 2 to n inclusive:
            Set temp to a + b
            Set a to b
            Set b to temp
        
        Return b
"""
        elif prompt_type == PromptType.CODE_COMPLETION:
            content = """
    # Calculate the factorial recursively
    If n <= 1:
        Return 1
    Else:
        Return n * factorial(n - 1)
"""
        elif prompt_type == PromptType.CODE_EXPLANATION:
            content = """
This code defines a function called 'quick_sort' that implements the QuickSort algorithm:

1. It first checks if the input array has 0 or 1 elements, in which case it returns the array unchanged.
2. It selects the first element of the array as the pivot.
3. It creates two empty lists: 'left' and 'right'.
4. It iterates through the rest of the array, placing elements smaller than the pivot in 'left' and others in 'right'.
5. It recursively sorts the 'left' and 'right' subarrays.
6. Finally, it concatenates the sorted 'left' array, the pivot, and the sorted 'right' array.

QuickSort is a divide-and-conquer algorithm with an average time complexity of O(n log n).
"""
        elif prompt_type == PromptType.KNOWLEDGE_EXTRACTION:
            content = """
Knowledge Entities:
1. Algorithm: QuickSort
   - Type: Sorting Algorithm
   - Properties: Divide and Conquer, In-place (partially)
   
2. Data Structure: List/Array
   - Used for: Storing elements to be sorted
   
3. Concept: Pivot Selection
   - Used in: Partitioning step
   
4. Concept: Recursion
   - Applied to: Sorting sub-arrays

Relationships:
1. QuickSort IMPLEMENTS Divide and Conquer approach
2. QuickSort USES Recursion
3. QuickSort MANIPULATES Lists
4. QuickSort SELECTS Pivot for partitioning
"""
        else:
            content = "Mock response for demonstration purposes."
        
        return LLMResponse(
            content=content,
            model="mock-model",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150
        )
    
    def get_available_models(self):
        """Return mock available models."""
        return ["mock-model-small", "mock-model-medium", "mock-model-large"]


def demonstrate_code_generation():
    """Demonstrate generating Runa code from requirements."""
    print("\n--- Code Generation Example ---")
    
    # Define the requirements
    requirements = """
- Create a function called 'fibonacci' that calculates the nth Fibonacci number
- Use an iterative approach with a loop instead of recursion
- Handle edge cases properly (n <= 0)
"""
    
    # Define additional context
    context = """
The Fibonacci sequence starts with 0 and 1, and each subsequent number is the sum of the two preceding ones.
F(0) = 0, F(1) = 1, F(2) = 1, F(3) = 2, F(4) = 3, F(5) = 5, etc.
"""
    
    # Get the OpenAI provider from the manager
    provider = llm_manager.get_provider()
    
    # Generate the code
    print("Generating Fibonacci function code...")
    response = provider.generate_code(requirements, context)
    
    # Print the result
    print("\nGenerated Code:")
    print("=" * 60)
    print(response.content)
    print("=" * 60)
    
    # Print token usage
    print(f"Tokens used: {response.tokens_used} ({response.prompt_tokens} prompt, {response.completion_tokens} completion)")
    
    return response.content


def demonstrate_code_completion():
    """Demonstrate completing partially written Runa code."""
    print("\n--- Code Completion Example ---")
    
    # Define the code to complete
    code = """
# Define a factorial function
Process called "factorial" that takes n:
"""
    
    # Define the requirements for completion
    requirements = """
- Implement a recursive factorial function
- Handle the base case (n <= 1)
"""
    
    # Get the provider
    provider = llm_manager.get_provider()
    
    # Complete the code
    print("Completing factorial function code...")
    response = provider.complete_code(code, requirements)
    
    # Print the result
    print("\nCompleted Code:")
    print("=" * 60)
    print(code + response.content)
    print("=" * 60)
    
    # Print token usage
    print(f"Tokens used: {response.tokens_used} ({response.prompt_tokens} prompt, {response.completion_tokens} completion)")
    
    return code + response.content


def demonstrate_code_explanation():
    """Demonstrate explaining Runa code."""
    print("\n--- Code Explanation Example ---")
    
    # Define the code to explain
    code = """
Process called "quick_sort" that takes arr:
    If length of arr is less than or equal to 1:
        Return arr
    
    Let pivot be arr at index 0
    Let left be list containing
    Let right be list containing
    
    For each x in arr starting from index 1:
        If x is less than pivot:
            Add x to left
        Otherwise:
            Add x to right
    
    Return quick_sort(left) followed by list containing pivot followed by quick_sort(right)
"""
    
    # Get the provider
    provider = llm_manager.get_provider()
    
    # Explain the code
    print("Generating explanation for QuickSort implementation...")
    response = provider.explain_code(code)
    
    # Print the result
    print("\nExplanation:")
    print("=" * 60)
    print(response.content)
    print("=" * 60)
    
    # Print token usage
    print(f"Tokens used: {response.tokens_used} ({response.prompt_tokens} prompt, {response.completion_tokens} completion)")
    
    return response.content


def demonstrate_knowledge_extraction():
    """Demonstrate extracting knowledge from Runa code."""
    print("\n--- Knowledge Extraction Example ---")
    
    # Define the code to analyze
    code = """
Process called "quick_sort" that takes arr:
    If length of arr is less than or equal to 1:
        Return arr
    
    Let pivot be arr at index 0
    Let left be list containing
    Let right be list containing
    
    For each x in arr starting from index 1:
        If x is less than pivot:
            Add x to left
        Otherwise:
            Add x to right
    
    Return quick_sort(left) followed by list containing pivot followed by quick_sort(right)
"""
    
    # Get the provider
    provider = llm_manager.get_provider()
    
    # Extract knowledge
    print("Extracting knowledge from QuickSort implementation...")
    response = provider.extract_knowledge(code)
    
    # Print the result
    print("\nExtracted Knowledge:")
    print("=" * 60)
    print(response.content)
    print("=" * 60)
    
    # Print token usage
    print(f"Tokens used: {response.tokens_used} ({response.prompt_tokens} prompt, {response.completion_tokens} completion)")
    
    return response.content


def demonstrate_custom_template():
    """Demonstrate creating and using a custom prompt template."""
    print("\n--- Custom Template Example ---")
    
    # Define a custom template for creating getter/setter functions
    custom_template = """
# Task: Generate getter and setter methods for a Runa class property

## Class Name
{class_name}

## Property Name
{property_name}

## Property Type
{property_type}

## Additional Requirements
{requirements}

## Generate getter and setter methods for this property:
"""
    
    # Create the template
    getter_setter_template = PromptTemplate(
        template=custom_template,
        prompt_type=PromptType.CODE_GENERATION
    )
    
    # Register the template
    llm_manager.register_template("getter_setter", getter_setter_template)
    
    # Get the provider
    provider = llm_manager.get_provider()
    
    # Generate code using the custom template
    print("Generating getter and setter methods...")
    response = llm_manager.generate_from_template(
        "getter_setter",
        class_name="Person",
        property_name="age",
        property_type="Int",
        requirements="Add validation to ensure age is non-negative"
    )
    
    # Print the result
    print("\nGenerated Methods:")
    print("=" * 60)
    print(response.content)
    print("=" * 60)
    
    # Print token usage
    print(f"Tokens used: {response.tokens_used} ({response.prompt_tokens} prompt, {response.completion_tokens} completion)")
    
    return response.content


def main():
    """Run the LLM integration example."""
    print("Runa LLM Integration Example")
    print("============================")
    
    # Use mock provider if no API key is available
    if not os.environ.get("OPENAI_API_KEY"):
        mock_provider = MockProvider()
        llm_manager.register_provider("mock", mock_provider, default=True)
    
    # Demonstrate code generation
    generated_code = demonstrate_code_generation()
    
    # Demonstrate code completion
    completed_code = demonstrate_code_completion()
    
    # Demonstrate code explanation
    explanation = demonstrate_code_explanation()
    
    # Demonstrate knowledge extraction
    extracted_knowledge = demonstrate_knowledge_extraction()
    
    # Demonstrate custom template
    custom_template_output = demonstrate_custom_template()
    
    # Save outputs to files for reference
    examples_dir = os.path.dirname(__file__)
    with open(os.path.join(examples_dir, "llm_generated_code.rn"), "w") as f:
        f.write(generated_code)
    
    with open(os.path.join(examples_dir, "llm_completed_code.rn"), "w") as f:
        f.write(completed_code)
    
    print("\nExample complete! Generated code saved to example files.")


if __name__ == "__main__":
    main() 