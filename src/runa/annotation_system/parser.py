"""
Parser for annotation comments in Runa code.

This module extracts and parses annotation comments from Runa code,
converting them into structured annotation nodes.
"""

import re
import json
from typing import List, Dict, Any, Tuple, Optional, Union
from .nodes import (
    AnnotationNode, AnnotationType, ReasoningAnnotation,
    ImplementationAnnotation, KnowledgeAnnotation, VerificationAnnotation,
    IntentAnnotation, FeedbackAnnotation, AnnotatedCodeBlock
)


class AnnotationParser:
    """Parser for extracting and interpreting annotation comments from Runa code."""
    
    # Regular expressions for annotation detection
    ANNOTATION_PATTERN = r'#\s*@(\w+)\s*(?:\(([^)]*)\))?\s*:\s*(.*?)(?=\n\s*#\s*@\w+|$)'
    LINE_ANNOTATION_PATTERN = r'#\s*@(\w+)(?:\(([^)]*)\))?\s*:\s*(.*?)$'
    BLOCK_START_PATTERN = r'#\s*@block\s*(?:\(([^)]*)\))?\s*:\s*(.*?)$'
    BLOCK_END_PATTERN = r'#\s*@end\s*$'
    
    # Mapping from annotation names to types
    ANNOTATION_TYPE_MAP = {
        "reasoning": AnnotationType.REASONING,
        "implementation": AnnotationType.IMPLEMENTATION,
        "verification": AnnotationType.VERIFICATION,
        "knowledge": AnnotationType.KNOWLEDGE,
        "intent": AnnotationType.INTENT,
        "feedback": AnnotationType.FEEDBACK
    }

    def __init__(self):
        """Initialize the annotation parser."""
        # Compile regular expressions for efficiency
        self.annotation_regex = re.compile(self.ANNOTATION_PATTERN, re.MULTILINE | re.DOTALL)
        self.line_annotation_regex = re.compile(self.LINE_ANNOTATION_PATTERN)
        self.block_start_regex = re.compile(self.BLOCK_START_PATTERN)
        self.block_end_regex = re.compile(self.BLOCK_END_PATTERN)
    
    def parse_annotations(self, code: str) -> List[AnnotationNode]:
        """
        Parse all annotations in the given code string.
        
        Args:
            code: The Runa code containing annotations.
            
        Returns:
            List of parsed annotation nodes.
        """
        annotations = []
        
        # Extract standalone annotations
        for match in self.annotation_regex.finditer(code):
            annotation_type, params_str, content = match.groups()
            
            # Get source position
            line_num = code[:match.start()].count('\n') + 1
            pos = {"line": line_num, "start": match.start(), "end": match.end()}
            
            # Parse parameters if present
            params = {}
            if params_str:
                params = self._parse_params(params_str)
            
            # Create the annotation
            annotation = self._create_annotation(annotation_type.lower(), content, pos, params)
            if annotation:
                annotations.append(annotation)
        
        return annotations
    
    def parse_line_annotations(self, line: str, line_num: int) -> List[AnnotationNode]:
        """
        Parse annotations in a single line of code.
        
        Args:
            line: The line of Runa code.
            line_num: The line number in the source file.
            
        Returns:
            List of parsed annotation nodes.
        """
        annotations = []
        match = self.line_annotation_regex.search(line)
        if match:
            annotation_type, params_str, content = match.groups()
            
            # Source position for the line
            pos = {"line": line_num, "start": match.start(), "end": match.end()}
            
            # Parse parameters if present
            params = {}
            if params_str:
                params = self._parse_params(params_str)
            
            # Create the annotation
            annotation = self._create_annotation(annotation_type.lower(), content, pos, params)
            if annotation:
                annotations.append(annotation)
        
        return annotations
    
    def parse_annotated_blocks(self, code: str) -> List[AnnotatedCodeBlock]:
        """
        Parse code blocks with their associated annotations.
        
        Args:
            code: The Runa code containing annotated blocks.
            
        Returns:
            List of annotated code blocks.
        """
        blocks = []
        lines = code.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            block_start = self.block_start_regex.search(line)
            
            if block_start:
                # Found a block start
                params_str, description = block_start.groups()
                block_start_line = i
                
                # Parse parameters if present
                params = {}
                if params_str:
                    params = self._parse_params(params_str)
                
                # Find the end of the block
                block_code = []
                block_annotations = []
                
                # Add the initial description as an annotation if provided
                if description:
                    pos = {"line": i+1, "start": block_start.start(), "end": block_start.end()}
                    annotation = IntentAnnotation(
                        annotation_type=AnnotationType.INTENT,
                        content=description,
                        source_position=pos,
                        goal=description
                    )
                    block_annotations.append(annotation)
                
                # Move to the next line
                i += 1
                
                # Collect code and annotations until the end block
                while i < len(lines) and not self.block_end_regex.search(lines[i]):
                    current_line = lines[i]
                    
                    # Check for line annotations
                    line_annotations = self.parse_line_annotations(current_line, i+1)
                    block_annotations.extend(line_annotations)
                    
                    # Add the line to the block code
                    block_code.append(current_line)
                    i += 1
                
                # Check if we found the end marker
                if i < len(lines) and self.block_end_regex.search(lines[i]):
                    # Create the annotated block
                    block = AnnotatedCodeBlock(
                        code='\n'.join(block_code),
                        annotations=block_annotations
                    )
                    blocks.append(block)
                    i += 1  # Move past the end marker
                else:
                    # No end marker found, treat as normal code
                    i = block_start_line + 1
            else:
                # Not a block start, move to next line
                i += 1
        
        return blocks
    
    def _parse_params(self, params_str: str) -> Dict[str, Any]:
        """
        Parse parameter string into a dictionary.
        
        Args:
            params_str: String containing parameters in the format "key=value, key2=value2"
            
        Returns:
            Dictionary of parameter key-value pairs.
        """
        params = {}
        if not params_str:
            return params
            
        # Split by commas, but handle potential JSON values
        items = []
        current_item = ""
        in_quotes = False
        in_braces = 0
        
        for char in params_str:
            if char == '"' and (not current_item or current_item[-1] != '\\'):
                in_quotes = not in_quotes
            elif char == '{' and not in_quotes:
                in_braces += 1
            elif char == '}' and not in_quotes:
                in_braces -= 1
            
            if char == ',' and not in_quotes and in_braces == 0:
                items.append(current_item.strip())
                current_item = ""
            else:
                current_item += char
                
        if current_item:
            items.append(current_item.strip())
        
        # Process each key-value pair
        for item in items:
            parts = item.split('=', 1)
            if len(parts) == 2:
                key, value = parts
                key = key.strip()
                value = value.strip()
                
                # Try to parse as JSON
                try:
                    if value.startswith('{') or value.startswith('['):
                        params[key] = json.loads(value)
                    elif value.lower() == 'true':
                        params[key] = True
                    elif value.lower() == 'false':
                        params[key] = False
                    elif value.lower() == 'null':
                        params[key] = None
                    elif value.replace('.', '', 1).isdigit():
                        params[key] = float(value) if '.' in value else int(value)
                    else:
                        # Remove quotes if they exist
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        params[key] = value
                except (json.JSONDecodeError, ValueError):
                    # If not valid JSON, store as string
                    params[key] = value
        
        return params
    
    def _create_annotation(
        self, 
        annotation_type: str, 
        content: str, 
        position: Dict[str, int], 
        params: Dict[str, Any]
    ) -> Optional[AnnotationNode]:
        """
        Create an annotation node based on type and parameters.
        
        Args:
            annotation_type: The type identifier of the annotation.
            content: The main content of the annotation.
            position: The source position information.
            params: Additional parameters for the annotation.
            
        Returns:
            An annotation node of the appropriate type, or None if invalid.
        """
        if annotation_type not in self.ANNOTATION_TYPE_MAP:
            return None
        
        enum_type = self.ANNOTATION_TYPE_MAP[annotation_type]
        
        # Create the appropriate annotation type
        if enum_type == AnnotationType.REASONING:
            return ReasoningAnnotation(
                annotation_type=enum_type,
                content=content,
                source_position=position,
                premise=params.get('premise', []),
                conclusion=params.get('conclusion'),
                confidence=params.get('confidence', 1.0)
            )
        elif enum_type == AnnotationType.IMPLEMENTATION:
            return ImplementationAnnotation(
                annotation_type=enum_type,
                content=content,
                source_position=position,
                algorithm=params.get('algorithm'),
                complexity=params.get('complexity'),
                alternative_approaches=params.get('alternative_approaches', [])
            )
        elif enum_type == AnnotationType.KNOWLEDGE:
            return KnowledgeAnnotation(
                annotation_type=enum_type,
                content=content,
                source_position=position,
                entity_id=params.get('entity_id'),
                relation_type=params.get('relation_type'),
                confidence=params.get('confidence', 1.0),
                graph_source=params.get('graph_source')
            )
        elif enum_type == AnnotationType.VERIFICATION:
            return VerificationAnnotation(
                annotation_type=enum_type,
                content=content,
                source_position=position,
                assertion=params.get('assertion', content),
                verification_method=params.get('method', 'manual'),
                status=params.get('status')
            )
        elif enum_type == AnnotationType.INTENT:
            return IntentAnnotation(
                annotation_type=enum_type,
                content=content,
                source_position=position,
                goal=params.get('goal', content),
                rationale=params.get('rationale'),
                alternatives_considered=params.get('alternatives', [])
            )
        elif enum_type == AnnotationType.FEEDBACK:
            return FeedbackAnnotation(
                annotation_type=enum_type,
                content=content,
                source_position=position,
                suggestion=params.get('suggestion', content),
                improvement_area=params.get('area', 'general'),
                priority=params.get('priority', 'medium')
            )
        else:
            # Generic annotation
            return AnnotationNode(
                annotation_type=enum_type,
                content=content,
                source_position=position,
                metadata=params
            )
