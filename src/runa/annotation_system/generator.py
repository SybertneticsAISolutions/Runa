"""
Generator for annotation comments in Runa code.

This module converts annotation nodes to formatted annotation comments
for inclusion in Runa code.
"""

from typing import List, Dict, Any, Optional, Union
from .nodes import (
    AnnotationNode, AnnotationType, ReasoningAnnotation,
    ImplementationAnnotation, KnowledgeAnnotation, VerificationAnnotation,
    IntentAnnotation, FeedbackAnnotation, AnnotatedCodeBlock
)


class AnnotationGenerator:
    """
    Generator for creating annotation comments from annotation nodes.
    """
    
    def __init__(self, indent_size: int = 4):
        """
        Initialize the annotation generator.
        
        Args:
            indent_size: Number of spaces to use for each level of indentation.
        """
        self.indent_size = indent_size
    
    def generate_annotation_comment(
        self, 
        annotation: AnnotationNode, 
        inline: bool = False, 
        indent_level: int = 0
    ) -> str:
        """
        Generate an annotation comment for a single annotation node.
        
        Args:
            annotation: The annotation node to convert to a comment.
            inline: Whether the annotation should be formatted for inline use.
            indent_level: The level of indentation to use.
            
        Returns:
            Formatted annotation comment string.
        """
        indent = " " * (self.indent_size * indent_level)
        annotation_type = annotation.annotation_type.value
        
        # Format parameters based on annotation type
        params_str = self._format_annotation_params(annotation)
        param_segment = f"({params_str})" if params_str else ""
        
        # Format the comment differently based on inline flag
        if inline:
            return f"{indent}# @{annotation_type}{param_segment}: {annotation.content}"
        else:
            return f"{indent}# @{annotation_type}{param_segment}: {annotation.content}"
    
    def generate_block_annotations(
        self, 
        block: AnnotatedCodeBlock, 
        indent_level: int = 0
    ) -> str:
        """
        Generate an annotated code block with block annotations.
        
        Args:
            block: The annotated code block to format.
            indent_level: The level of indentation to use.
            
        Returns:
            Formatted annotated code block string.
        """
        indent = " " * (self.indent_size * indent_level)
        result = []
        
        # Look for intent annotations to use as block description
        intent_annotations = [a for a in block.annotations 
                             if a.annotation_type == AnnotationType.INTENT]
        
        # Start block with description from intent if available
        if intent_annotations:
            intent = intent_annotations[0]
            params_str = self._format_annotation_params(intent)
            param_segment = f"({params_str})" if params_str else ""
            block_description = intent.content
            result.append(f"{indent}# @block{param_segment}: {block_description}")
        else:
            result.append(f"{indent}# @block")
        
        # Add code lines with inline annotations as needed
        code_lines = block.code.split('\n')
        line_annotations = {}
        
        # Group annotations by line if they have position information
        for annotation in block.annotations:
            if annotation.annotation_type != AnnotationType.INTENT:  # Skip intent used for block description
                if annotation.source_position and "line" in annotation.source_position:
                    line = annotation.source_position["line"]
                    if line not in line_annotations:
                        line_annotations[line] = []
                    line_annotations[line].append(annotation)
        
        # Add code with inline annotations
        for i, line in enumerate(code_lines):
            result.append(f"{indent}{line}")
            
            # Add any annotations for this line
            if i + 1 in line_annotations:
                for annotation in line_annotations[i + 1]:
                    result.append(self.generate_annotation_comment(
                        annotation, inline=True, indent_level=indent_level + 1
                    ))
        
        # End block
        result.append(f"{indent}# @end")
        
        return '\n'.join(result)
    
    def generate_annotations_for_code(
        self, 
        code: str, 
        annotations: List[AnnotationNode]
    ) -> str:
        """
        Add annotations to existing code.
        
        Args:
            code: The original code.
            annotations: The annotations to add.
            
        Returns:
            Code with annotations added.
        """
        # Group annotations by line
        line_annotations = {}
        standalone_annotations = []
        
        for annotation in annotations:
            if annotation.source_position and "line" in annotation.source_position:
                line = annotation.source_position["line"]
                if line not in line_annotations:
                    line_annotations[line] = []
                line_annotations[line].append(annotation)
            else:
                standalone_annotations.append(annotation)
        
        # Add standalone annotations at the top
        result = []
        for annotation in standalone_annotations:
            result.append(self.generate_annotation_comment(annotation))
        
        if standalone_annotations:
            result.append("")  # Add blank line after standalone annotations
        
        # Add code with inline annotations
        lines = code.split('\n')
        for i, line in enumerate(lines):
            result.append(line)
            
            # Add any annotations for this line
            if i + 1 in line_annotations:
                indent_level = len(line) - len(line.lstrip()) // self.indent_size + 1
                for annotation in line_annotations[i + 1]:
                    result.append(self.generate_annotation_comment(
                        annotation, inline=True, indent_level=indent_level
                    ))
        
        return '\n'.join(result)
    
    def generate_annotated_code(
        self, 
        blocks: List[AnnotatedCodeBlock]
    ) -> str:
        """
        Generate code with annotation blocks for a list of annotated blocks.
        
        Args:
            blocks: List of annotated code blocks.
            
        Returns:
            Formatted code with annotation blocks.
        """
        result = []
        
        for block in blocks:
            result.append(self.generate_block_annotations(block))
            result.append("")  # Add blank line between blocks
        
        return '\n'.join(result)
    
    def _format_annotation_params(self, annotation: AnnotationNode) -> str:
        """
        Format parameters for an annotation based on its type.
        
        Args:
            annotation: The annotation node.
            
        Returns:
            Formatted parameter string.
        """
        params = []
        
        if annotation.annotation_type == AnnotationType.REASONING:
            if isinstance(annotation, ReasoningAnnotation):
                if annotation.premise:
                    premise_str = self._format_list_param(annotation.premise)
                    params.append(f"premise={premise_str}")
                if annotation.conclusion:
                    params.append(f"conclusion=\"{annotation.conclusion}\"")
                if annotation.confidence != 1.0:
                    params.append(f"confidence={annotation.confidence}")
        
        elif annotation.annotation_type == AnnotationType.IMPLEMENTATION:
            if isinstance(annotation, ImplementationAnnotation):
                if annotation.algorithm:
                    params.append(f"algorithm=\"{annotation.algorithm}\"")
                if annotation.complexity:
                    params.append(f"complexity=\"{annotation.complexity}\"")
                if annotation.alternative_approaches:
                    alt_str = self._format_list_param(annotation.alternative_approaches)
                    params.append(f"alternative_approaches={alt_str}")
        
        elif annotation.annotation_type == AnnotationType.KNOWLEDGE:
            if isinstance(annotation, KnowledgeAnnotation):
                if annotation.entity_id:
                    params.append(f"entity_id=\"{annotation.entity_id}\"")
                if annotation.relation_type:
                    params.append(f"relation_type=\"{annotation.relation_type}\"")
                if annotation.confidence != 1.0:
                    params.append(f"confidence={annotation.confidence}")
                if annotation.graph_source:
                    params.append(f"graph_source=\"{annotation.graph_source}\"")
        
        elif annotation.annotation_type == AnnotationType.VERIFICATION:
            if isinstance(annotation, VerificationAnnotation):
                if annotation.assertion != annotation.content:
                    params.append(f"assertion=\"{annotation.assertion}\"")
                params.append(f"method=\"{annotation.verification_method}\"")
                if annotation.status:
                    params.append(f"status=\"{annotation.status}\"")
        
        elif annotation.annotation_type == AnnotationType.INTENT:
            if isinstance(annotation, IntentAnnotation):
                if annotation.goal != annotation.content:
                    params.append(f"goal=\"{annotation.goal}\"")
                if annotation.rationale:
                    params.append(f"rationale=\"{annotation.rationale}\"")
                if annotation.alternatives_considered:
                    alt_str = self._format_list_param(annotation.alternatives_considered)
                    params.append(f"alternatives={alt_str}")
        
        elif annotation.annotation_type == AnnotationType.FEEDBACK:
            if isinstance(annotation, FeedbackAnnotation):
                if annotation.suggestion != annotation.content:
                    params.append(f"suggestion=\"{annotation.suggestion}\"")
                params.append(f"area=\"{annotation.improvement_area}\"")
                if annotation.priority != "medium":
                    params.append(f"priority=\"{annotation.priority}\"")
        
        # Add any additional metadata
        for key, value in annotation.metadata.items():
            # Skip keys already handled above
            if key in ["premise", "conclusion", "confidence", "algorithm", "complexity", 
                      "alternative_approaches", "entity_id", "relation_type", "graph_source",
                      "assertion", "method", "status", "goal", "rationale", "alternatives",
                      "suggestion", "area", "priority"]:
                continue
                
            # Format the value based on its type
            if isinstance(value, str):
                params.append(f"{key}=\"{value}\"")
            elif isinstance(value, (int, float, bool)):
                params.append(f"{key}={value}")
            elif isinstance(value, list):
                value_str = self._format_list_param(value)
                params.append(f"{key}={value_str}")
            elif isinstance(value, dict):
                # Simple JSON-like formatting for dictionaries
                dict_parts = [f"\"{k}\": \"{v}\"" if isinstance(v, str) else f"\"{k}\": {v}" 
                             for k, v in value.items()]
                dict_str = "{ " + ", ".join(dict_parts) + " }"
                params.append(f"{key}={dict_str}")
        
        return ", ".join(params)
    
    def _format_list_param(self, items: List[Any]) -> str:
        """
        Format a list parameter for an annotation.
        
        Args:
            items: List of items to format.
            
        Returns:
            Formatted list string.
        """
        formatted_items = []
        for item in items:
            if isinstance(item, str):
                formatted_items.append(f"\"{item}\"")
            else:
                formatted_items.append(str(item))
        
        return "[" + ", ".join(formatted_items) + "]"
