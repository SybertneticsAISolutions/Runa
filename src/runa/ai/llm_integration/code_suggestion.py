"""
Code Suggestion System for Runa.

This module provides context-aware code suggestions using LLM integration
and knowledge graph data.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import re
import os

from .base import llm_manager, LLMPrompt, PromptType


class SuggestionContext:
    """Represents the context for a code suggestion."""
    
    def __init__(
        self,
        code_before_cursor: str,
        code_after_cursor: str = "",
        file_path: str = "",
        open_files: List[str] = None,
        imports: List[str] = None,
        project_info: Dict[str, Any] = None,
        use_knowledge_graph: bool = True,
        max_context_length: int = 2000
    ):
        """
        Initialize the suggestion context.
        
        Args:
            code_before_cursor: Code before the cursor position
            code_after_cursor: Code after the cursor position
            file_path: Path of the current file
            open_files: List of other open file paths
            imports: List of imported modules/libraries
            project_info: Additional project information
            use_knowledge_graph: Whether to use knowledge graph for enhanced suggestions
            max_context_length: Maximum context length to send to LLM
        """
        self.code_before_cursor = code_before_cursor
        self.code_after_cursor = code_after_cursor
        self.file_path = file_path
        self.open_files = open_files or []
        self.imports = imports or []
        self.project_info = project_info or {}
        self.use_knowledge_graph = use_knowledge_graph
        self.max_context_length = max_context_length
    
    def get_current_line(self) -> str:
        """Get the current line where the cursor is located."""
        lines_before = self.code_before_cursor.split('\n')
        current_line = lines_before[-1] if lines_before else ""
        
        # If there's code after cursor on same line, add it
        if self.code_after_cursor and '\n' in self.code_after_cursor:
            first_line_after = self.code_after_cursor.split('\n')[0]
            current_line += first_line_after
        elif self.code_after_cursor:
            current_line += self.code_after_cursor
            
        return current_line
    
    def get_surrounding_context(self, lines_before: int = 10, lines_after: int = 5) -> str:
        """Get code context surrounding the cursor."""
        before_lines = self.code_before_cursor.split('\n')
        after_lines = self.code_after_cursor.split('\n')
        
        # Get lines before cursor
        context_before = before_lines[-lines_before:] if len(before_lines) > lines_before else before_lines
        
        # Get lines after cursor
        context_after = after_lines[:lines_after] if len(after_lines) > lines_after else after_lines
        
        # Combine context
        return '\n'.join(context_before) + '\n' + '\n'.join(context_after)
    
    def get_current_function_or_block(self) -> str:
        """Attempt to extract the current function or block being edited."""
        lines = self.code_before_cursor.split('\n')
        
        # Start from the cursor position and move backward
        current_block = []
        indentation_level = None
        found_block_start = False
        
        for line in reversed(lines):
            stripped = line.lstrip()
            
            # Skip empty lines
            if not stripped:
                if current_block:  # Only add empty lines if we've started collecting a block
                    current_block.insert(0, line)
                continue
            
            # Calculate indentation
            current_indent = len(line) - len(stripped)
            
            # If this is the first non-empty line, set indentation level
            if indentation_level is None:
                indentation_level = current_indent
                current_block.insert(0, line)
                continue
            
            # If we find a line with less indentation, it might be the start of the block
            if current_indent < indentation_level:
                # Check if it's a block start (function, if, for, etc.)
                if re.match(r'^\s*(Process|Let|If|For|While|Loop|Class|Match)\b', line):
                    current_block.insert(0, line)
                    found_block_start = True
                    
                    # For some blocks, we want to check deeper indentation levels
                    if not re.match(r'^\s*(If|Else|Elif)\b', line):
                        break
                else:
                    current_block.insert(0, line)
            else:
                current_block.insert(0, line)
        
        # Include code after cursor that might be part of the same block
        if found_block_start:
            after_lines = self.code_after_cursor.split('\n')
            matching_indentation = []
            
            for line in after_lines:
                if not line.strip():
                    matching_indentation.append(line)
                    continue
                    
                current_indent = len(line) - len(line.lstrip())
                if current_indent >= indentation_level:
                    matching_indentation.append(line)
                else:
                    break
            
            current_block.extend(matching_indentation)
        
        return '\n'.join(current_block)
    
    def get_file_type(self) -> str:
        """Get the type of the current file based on extension."""
        if not self.file_path:
            return "unknown"
            
        _, ext = os.path.splitext(self.file_path)
        return ext.lstrip('.').lower() or "unknown"
    
    def to_prompt_context(self) -> Dict[str, Any]:
        """Convert context to a format usable in prompts."""
        current_line = self.get_current_line()
        surrounding_context = self.get_surrounding_context()
        current_block = self.get_current_function_or_block()
        
        return {
            "current_line": current_line,
            "surrounding_context": surrounding_context,
            "current_block": current_block,
            "file_type": self.get_file_type(),
            "imports": self.imports,
            "file_path": self.file_path
        }


class Suggestion:
    """Represents a code suggestion."""
    
    def __init__(
        self,
        text: str,
        display_text: Optional[str] = None,
        replacement_range: Optional[Tuple[int, int]] = None,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a suggestion.
        
        Args:
            text: The suggestion text to insert
            display_text: Text to display in the UI (if different from insertion text)
            replacement_range: Range of text to replace (start, end)
            confidence: Confidence score for the suggestion (0.0 to 1.0)
            metadata: Additional metadata about the suggestion
        """
        self.text = text
        self.display_text = display_text or text
        self.replacement_range = replacement_range
        self.confidence = confidence
        self.metadata = metadata or {}
    
    def __repr__(self) -> str:
        return f"Suggestion(text='{self.text}', confidence={self.confidence:.2f})"


class CodeSuggestionEngine:
    """Engine for generating context-aware code suggestions."""
    
    def __init__(
        self,
        knowledge_manager=None,
        provider_name: Optional[str] = None,
        max_suggestions: int = 5,
        confidence_threshold: float = 0.3
    ):
        """
        Initialize the code suggestion engine.
        
        Args:
            knowledge_manager: Knowledge graph manager for enhanced suggestions
            provider_name: Name of the LLM provider to use
            max_suggestions: Maximum number of suggestions to generate
            confidence_threshold: Minimum confidence threshold for suggestions
        """
        self.knowledge_manager = knowledge_manager
        self.provider_name = provider_name
        self.max_suggestions = max_suggestions
        self.confidence_threshold = confidence_threshold
        self.suggestion_cache = {}
    
    def get_suggestions(self, context: SuggestionContext) -> List[Suggestion]:
        """
        Get code suggestions based on the context.
        
        Args:
            context: The current code context
            
        Returns:
            List of code suggestions
        """
        # Check cache first
        cache_key = self._get_cache_key(context)
        if cache_key in self.suggestion_cache:
            return self.suggestion_cache[cache_key]
        
        # Determine suggestion type
        suggestion_type = self._determine_suggestion_type(context)
        
        # Generate suggestions based on type
        if suggestion_type == "function_completion":
            suggestions = self._generate_function_completion(context)
        elif suggestion_type == "import_completion":
            suggestions = self._generate_import_completion(context)
        elif suggestion_type == "variable_completion":
            suggestions = self._generate_variable_completion(context)
        elif suggestion_type == "parameter_completion":
            suggestions = self._generate_parameter_completion(context)
        elif suggestion_type == "line_completion":
            suggestions = self._generate_line_completion(context)
        else:
            suggestions = self._generate_generic_completion(context)
        
        # Filter by confidence threshold
        filtered_suggestions = [s for s in suggestions if s.confidence >= self.confidence_threshold]
        
        # Limit number of suggestions
        limited_suggestions = filtered_suggestions[:self.max_suggestions]
        
        # Cache results
        self.suggestion_cache[cache_key] = limited_suggestions
        
        return limited_suggestions
    
    def _get_cache_key(self, context: SuggestionContext) -> str:
        """Generate a cache key for the context."""
        current_line = context.get_current_line()
        return f"{current_line}:{len(context.code_before_cursor)}"
    
    def _determine_suggestion_type(self, context: SuggestionContext) -> str:
        """Determine the type of suggestion needed based on context."""
        current_line = context.get_current_line()
        
        # Import completion
        if re.match(r'^\s*import\s+', current_line) or re.match(r'^\s*from\s+.*\s+import\s+', current_line):
            return "import_completion"
        
        # Function completion (e.g., function call)
        if re.search(r'[a-zA-Z0-9_]+\(.*$', current_line):
            return "function_completion"
        
        # Parameter completion
        if re.search(r'[a-zA-Z0-9_]+\s*\(.*\)\s*:$', current_line) or re.search(r'Process\s+called\s+"[^"]+"\s+that\s+takes\s+', current_line):
            return "parameter_completion"
        
        # Variable completion
        if re.match(r'^\s*Let\s+', current_line) or re.match(r'^\s*[a-zA-Z0-9_]+\s*=', current_line):
            return "variable_completion"
        
        # Default to line completion
        return "line_completion"
    
    def _generate_function_completion(self, context: SuggestionContext) -> List[Suggestion]:
        """Generate function completion suggestions."""
        # Get context information for prompt
        prompt_context = context.to_prompt_context()
        
        # Add knowledge graph information if available
        if context.use_knowledge_graph and self.knowledge_manager:
            knowledge_info = self._get_knowledge_graph_context(context)
            prompt_context.update(knowledge_info)
        
        # Create LLM prompt
        prompt = LLMPrompt(
            content=self._create_function_completion_prompt(prompt_context),
            prompt_type=PromptType.CODE_COMPLETION,
            temperature=0.2,
            max_tokens=100
        )
        
        # Generate completion
        response = llm_manager.generate(prompt, provider=self.provider_name)
        
        # Parse response into suggestions
        return self._parse_suggestions(response.content, "function")
    
    def _generate_import_completion(self, context: SuggestionContext) -> List[Suggestion]:
        """Generate import statement completion suggestions."""
        current_line = context.get_current_line()
        
        # Get context information for prompt
        prompt_context = context.to_prompt_context()
        prompt_context["current_imports"] = context.imports
        
        # Create LLM prompt
        prompt = LLMPrompt(
            content=self._create_import_completion_prompt(prompt_context),
            prompt_type=PromptType.CODE_COMPLETION,
            temperature=0.2,
            max_tokens=50
        )
        
        # Generate completion
        response = llm_manager.generate(prompt, provider=self.provider_name)
        
        # Parse response into suggestions
        return self._parse_suggestions(response.content, "import")
    
    def _generate_variable_completion(self, context: SuggestionContext) -> List[Suggestion]:
        """Generate variable completion suggestions."""
        # Get context information for prompt
        prompt_context = context.to_prompt_context()
        
        # Create LLM prompt
        prompt = LLMPrompt(
            content=self._create_variable_completion_prompt(prompt_context),
            prompt_type=PromptType.CODE_COMPLETION,
            temperature=0.3,
            max_tokens=100
        )
        
        # Generate completion
        response = llm_manager.generate(prompt, provider=self.provider_name)
        
        # Parse response into suggestions
        return self._parse_suggestions(response.content, "variable")
    
    def _generate_parameter_completion(self, context: SuggestionContext) -> List[Suggestion]:
        """Generate parameter completion suggestions."""
        # Get context information for prompt
        prompt_context = context.to_prompt_context()
        
        # Create LLM prompt
        prompt = LLMPrompt(
            content=self._create_parameter_completion_prompt(prompt_context),
            prompt_type=PromptType.CODE_COMPLETION,
            temperature=0.3,
            max_tokens=100
        )
        
        # Generate completion
        response = llm_manager.generate(prompt, provider=self.provider_name)
        
        # Parse response into suggestions
        return self._parse_suggestions(response.content, "parameter")
    
    def _generate_line_completion(self, context: SuggestionContext) -> List[Suggestion]:
        """Generate line completion suggestions."""
        # Get context information for prompt
        prompt_context = context.to_prompt_context()
        
        # Create LLM prompt
        prompt = LLMPrompt(
            content=self._create_line_completion_prompt(prompt_context),
            prompt_type=PromptType.CODE_COMPLETION,
            temperature=0.5,
            max_tokens=150
        )
        
        # Generate completion
        response = llm_manager.generate(prompt, provider=self.provider_name)
        
        # Parse response into suggestions
        return self._parse_suggestions(response.content, "line")
    
    def _generate_generic_completion(self, context: SuggestionContext) -> List[Suggestion]:
        """Generate generic code completion suggestions."""
        # Get context information for prompt
        prompt_context = context.to_prompt_context()
        
        # Create LLM prompt
        prompt = LLMPrompt(
            content=self._create_generic_completion_prompt(prompt_context),
            prompt_type=PromptType.CODE_COMPLETION,
            temperature=0.5,
            max_tokens=150
        )
        
        # Generate completion
        response = llm_manager.generate(prompt, provider=self.provider_name)
        
        # Parse response into suggestions
        return self._parse_suggestions(response.content, "generic")
    
    def _create_function_completion_prompt(self, context: Dict[str, Any]) -> str:
        """Create a prompt for function completion."""
        return f"""
# Task: Complete the function call on the current line

## Current line
```
{context['current_line']}
```

## Surrounding code context
```
{context['surrounding_context']}
```

## Available imports
{', '.join(context.get('imports', []))}

## Provide 2-5 likely completions for this function call, showing just the parameters:
"""
    
    def _create_import_completion_prompt(self, context: Dict[str, Any]) -> str:
        """Create a prompt for import completion."""
        return f"""
# Task: Complete the import statement

## Current line
```
{context['current_line']}
```

## Current imports
{', '.join(context.get('current_imports', []))}

## Provide 2-5 likely completions for this import statement:
"""
    
    def _create_variable_completion_prompt(self, context: Dict[str, Any]) -> str:
        """Create a prompt for variable completion."""
        return f"""
# Task: Complete the variable assignment

## Current line
```
{context['current_line']}
```

## Surrounding code context
```
{context['surrounding_context']}
```

## Provide 2-5 likely completions for this variable assignment:
"""
    
    def _create_parameter_completion_prompt(self, context: Dict[str, Any]) -> str:
        """Create a prompt for parameter completion."""
        return f"""
# Task: Complete the function/process parameters

## Current line
```
{context['current_line']}
```

## Surrounding code context
```
{context['surrounding_context']}
```

## Provide 2-5 likely parameter completions with type annotations:
"""
    
    def _create_line_completion_prompt(self, context: Dict[str, Any]) -> str:
        """Create a prompt for line completion."""
        return f"""
# Task: Complete the current line of Runa code

## Current line
```
{context['current_line']}
```

## Surrounding code context
```
{context['surrounding_context']}
```

## Current block
```
{context['current_block']}
```

## Provide 2-5 likely completions for the current line:
"""
    
    def _create_generic_completion_prompt(self, context: Dict[str, Any]) -> str:
        """Create a prompt for generic code completion."""
        return f"""
# Task: Provide code completions

## Current line
```
{context['current_line']}
```

## Surrounding code context
```
{context['surrounding_context']}
```

## Current block
```
{context['current_block']}
```

## Provide 2-5 likely code completions:
"""
    
    def _parse_suggestions(self, content: str, suggestion_type: str) -> List[Suggestion]:
        """Parse LLM response into suggestion objects."""
        suggestions = []
        
        # Split content by lines and look for numbered suggestions
        lines = content.strip().split('\n')
        current_suggestion = None
        confidence_modifiers = {
            "very likely": 0.2,
            "likely": 0.1,
            "possible": 0,
            "common": 0.1,
            "recommended": 0.15,
            "standard": 0.05,
            "typical": 0.05,
            "alternative": -0.05,
            "optional": -0.1,
            "uncommon": -0.15
        }
        
        for line in lines:
            # Look for numbered or bulleted suggestions
            suggestion_match = re.match(r'^[0-9#\-*]+[\.)]?\s*(.+)$', line)
            
            if suggestion_match:
                suggestion_text = suggestion_match.group(1).strip()
                
                # Extract confidence modifiers from text if present
                base_confidence = 0.7  # Default confidence
                
                for modifier, value in confidence_modifiers.items():
                    if f"({modifier})" in suggestion_text.lower():
                        suggestion_text = suggestion_text.replace(f"({modifier})", "").strip()
                        base_confidence += value
                        break
                
                # Create suggestion object
                suggestion = Suggestion(
                    text=suggestion_text,
                    confidence=min(1.0, max(0.1, base_confidence)),
                    metadata={"type": suggestion_type}
                )
                
                suggestions.append(suggestion)
        
        # If no structured suggestions found, try to extract the first code block
        if not suggestions:
            code_blocks = re.findall(r'```[^\n]*\n(.*?)```', content, re.DOTALL)
            
            if code_blocks:
                for block in code_blocks:
                    # Split the block into lines
                    block_lines = block.strip().split('\n')
                    
                    for i, line in enumerate(block_lines):
                        confidence = 0.7 - (i * 0.1)  # Decrease confidence for later lines
                        suggestion = Suggestion(
                            text=line.strip(),
                            confidence=max(0.1, confidence),
                            metadata={"type": suggestion_type}
                        )
                        suggestions.append(suggestion)
            else:
                # Just use the raw content as a single suggestion
                suggestion = Suggestion(
                    text=content.strip(),
                    confidence=0.5,
                    metadata={"type": suggestion_type}
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _get_knowledge_graph_context(self, context: SuggestionContext) -> Dict[str, Any]:
        """Get relevant information from the knowledge graph."""
        if not self.knowledge_manager:
            return {}
            
        # Extract current symbols, function names, etc.
        current_line = context.get_current_line()
        surrounding_context = context.get_surrounding_context()
        
        # Extract function or method name
        function_match = re.search(r'([a-zA-Z0-9_]+)\(', current_line)
        current_function = function_match.group(1) if function_match else None
        
        knowledge_context = {}
        
        if current_function:
            # Query knowledge graph for information about this function
            try:
                function_info = self.knowledge_manager.query({
                    "name_similar_to": current_function,
                    "type": "Function"
                })
                
                if function_info:
                    knowledge_context["function_info"] = function_info
            except Exception as e:
                print(f"Error querying knowledge graph: {e}")
        
        # Extract other types of knowledge based on context
        # ... (implementation details)
        
        return knowledge_context
    
    def clear_cache(self):
        """Clear the suggestion cache."""
        self.suggestion_cache = {} 