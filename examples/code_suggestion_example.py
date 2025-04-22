#!/usr/bin/env python3
"""
Code Suggestion Example for Runa

This example demonstrates how to use the code suggestion system to provide
context-aware code completions.
"""

import os
import sys
from typing import List

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.runa.ai.llm_integration import (
    SuggestionContext, CodeSuggestionEngine, llm_manager
)


class MockKnowledgeManager:
    """Mock knowledge manager for the example."""
    
    def query(self, query_dict):
        """Mock query method."""
        name = query_dict.get("name_similar_to", "")
        
        if "sort" in name.lower():
            return [
                {
                    "name": "quick_sort",
                    "type": "Function",
                    "description": "A divide-and-conquer sorting algorithm",
                    "parameters": ["arr: List"],
                    "complexity": "O(n log n) average case"
                },
                {
                    "name": "merge_sort",
                    "type": "Function",
                    "description": "A stable, divide-and-conquer sorting algorithm",
                    "parameters": ["arr: List"],
                    "complexity": "O(n log n)"
                }
            ]
        elif "fibonacci" in name.lower():
            return [
                {
                    "name": "fibonacci",
                    "type": "Function",
                    "description": "Calculates Fibonacci numbers",
                    "parameters": ["n: Int"],
                    "complexity": "O(n)"
                }
            ]
        
        return []


def demonstrate_function_completion():
    """Demonstrate function completion suggestions."""
    print("\n--- Function Completion Example ---")
    
    # Code context for a function call
    code_before = """
Process called "example" that takes arr:
    # Sort the array and calculate sum
    Let sorted_arr be quick_sort("""
    
    code_after = """)
    Let sum = 0
    
    For each num in sorted_arr:
        Set sum to sum + num
    
    Return sum
"""
    
    # Create context and engine
    context = SuggestionContext(
        code_before_cursor=code_before,
        code_after_cursor=code_after,
        imports=["runa.stdlib.sorting"],
        file_path="example.rn"
    )
    
    engine = CodeSuggestionEngine(
        knowledge_manager=MockKnowledgeManager()
    )
    
    # Get suggestions
    suggestions = engine.get_suggestions(context)
    
    # Display suggestions
    print(f"Code position: {code_before}|{code_after}")
    print("\nSuggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion.text} (confidence: {suggestion.confidence:.2f})")


def demonstrate_import_completion():
    """Demonstrate import completion suggestions."""
    print("\n--- Import Completion Example ---")
    
    # Code context for an import statement
    code_before = """
# Import necessary modules
import runa.stdlib.math
import runa.stdlib."""
    
    code_after = """

Process called "main":
    # Implementation
"""
    
    # Create context and engine
    context = SuggestionContext(
        code_before_cursor=code_before,
        code_after_cursor=code_after,
        imports=["runa.stdlib.math"],
        file_path="example.rn"
    )
    
    engine = CodeSuggestionEngine()
    
    # Get suggestions
    suggestions = engine.get_suggestions(context)
    
    # Display suggestions
    print(f"Code position: {code_before}|{code_after}")
    print("\nSuggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion.text} (confidence: {suggestion.confidence:.2f})")


def demonstrate_line_completion():
    """Demonstrate line completion suggestions."""
    print("\n--- Line Completion Example ---")
    
    # Code context for line completion
    code_before = """
Process called "calculate_factorial" that takes n:
    # Calculate factorial recursively
    If n <= 1:
        Return """
    
    code_after = """
    Else:
        Return n * calculate_factorial(n - 1)
"""
    
    # Create context and engine
    context = SuggestionContext(
        code_before_cursor=code_before,
        code_after_cursor=code_after,
        file_path="example.rn"
    )
    
    engine = CodeSuggestionEngine()
    
    # Get suggestions
    suggestions = engine.get_suggestions(context)
    
    # Display suggestions
    print(f"Code position: {code_before}|{code_after}")
    print("\nSuggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion.text} (confidence: {suggestion.confidence:.2f})")


def demonstrate_variable_completion():
    """Demonstrate variable completion suggestions."""
    print("\n--- Variable Completion Example ---")
    
    # Code context for variable completion
    code_before = """
Process called "process_data" that takes data:
    Let count = data.size()
    Let average = data.average()
    Let max_value = """
    
    code_after = """
    
    Return {
        "count": count,
        "average": average,
        "max": max_value
    }
"""
    
    # Create context and engine
    context = SuggestionContext(
        code_before_cursor=code_before,
        code_after_cursor=code_after,
        file_path="example.rn"
    )
    
    engine = CodeSuggestionEngine()
    
    # Get suggestions
    suggestions = engine.get_suggestions(context)
    
    # Display suggestions
    print(f"Code position: {code_before}|{code_after}")
    print("\nSuggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion.text} (confidence: {suggestion.confidence:.2f})")


def demonstrate_parameter_completion():
    """Demonstrate parameter completion suggestions."""
    print("\n--- Parameter Completion Example ---")
    
    # Code context for parameter completion
    code_before = """
# Define a process to calculate statistics
Process called "calculate_statistics" that takes """
    
    code_after = """
    Let count = data.size()
    Let sum = data.sum()
    Let average = sum / count
    
    Return {
        "count": count,
        "sum": sum,
        "average": average
    }
"""
    
    # Create context and engine
    context = SuggestionContext(
        code_before_cursor=code_before,
        code_after_cursor=code_after,
        file_path="example.rn"
    )
    
    engine = CodeSuggestionEngine()
    
    # Get suggestions
    suggestions = engine.get_suggestions(context)
    
    # Display suggestions
    print(f"Code position: {code_before}|{code_after}")
    print("\nSuggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion.text} (confidence: {suggestion.confidence:.2f})")


def demonstrate_knowledge_graph_enhanced_suggestions():
    """Demonstrate knowledge graph enhanced suggestions."""
    print("\n--- Knowledge Graph Enhanced Suggestions ---")
    
    # Code context that can use knowledge graph information
    code_before = """
Process called "fibonacci_sequence" that takes n:
    # Generate Fibonacci sequence up to n
    Let result be list containing
    
    If n <= 0:
        Return result
    
    Let a be 0
    Let b be 1
    
    Add a to result
    
    If n == 1:
        Return result
    
    Add b to result
    
    For i from 2 to n:
        Let next_value be fibonacci("""
    
    code_after = """)
        Add next_value to result
    
    Return result
"""
    
    # Create context and engine
    context = SuggestionContext(
        code_before_cursor=code_before,
        code_after_cursor=code_after,
        use_knowledge_graph=True,
        file_path="example.rn"
    )
    
    engine = CodeSuggestionEngine(
        knowledge_manager=MockKnowledgeManager()
    )
    
    # Get suggestions
    suggestions = engine.get_suggestions(context)
    
    # Display suggestions
    print(f"Code position: {code_before}|{code_after}")
    print("\nSuggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion.text} (confidence: {suggestion.confidence:.2f})")


def main():
    """Run the code suggestion examples."""
    print("Runa Code Suggestion Example")
    print("============================")
    
    # Check if OpenAI API key is available, otherwise use mock responses
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set.")
        print("Using mock suggestions for demonstration purposes...\n")
        
        # Create a mock response provider
        class MockProvider:
            def generate(self, prompt):
                from src.runa.ai.llm_integration import LLMResponse
                
                prompt_type = getattr(prompt, "prompt_type", None)
                
                # Generate mock responses based on context
                if "function_completion" in str(prompt.content).lower():
                    content = "1. arr (confidence: high)\n2. arr, reverse=False\n3. arr, start=0, end=None"
                elif "import_completion" in str(prompt.content).lower():
                    content = "1. sorting\n2. data\n3. io\n4. collections"
                elif "line_completion" in str(prompt.content).lower():
                    content = "1. 1\n2. n if n <= 1 else 1\n3. 1 # Base case"
                elif "variable_completion" in str(prompt.content).lower():
                    content = "1. data.max()\n2. Math.max(data)\n3. max(data)"
                elif "parameter_completion" in str(prompt.content).lower():
                    content = "1. data: List\n2. data: List, options: Dict = None\n3. values: List"
                else:
                    content = "1. Mock suggestion 1\n2. Mock suggestion 2"
                
                return LLMResponse(
                    content=content,
                    model="mock-model",
                    prompt_tokens=100,
                    completion_tokens=50,
                    total_tokens=150
                )
        
        llm_manager.register_provider("mock", MockProvider(), default=True)
    
    # Run examples
    demonstrate_function_completion()
    demonstrate_import_completion()
    demonstrate_line_completion()
    demonstrate_variable_completion()
    demonstrate_parameter_completion()
    demonstrate_knowledge_graph_enhanced_suggestions()
    
    print("\nExample complete!")


if __name__ == "__main__":
    main() 