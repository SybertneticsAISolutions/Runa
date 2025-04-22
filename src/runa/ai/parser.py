"""
Parser for AI-specific language constructs in Runa.

This module provides parsing functionality for AI-related language features,
such as model descriptions, knowledge integrations, and AI-to-AI communication.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import re
from .nodes import (
    AIAnnotationNode, KnowledgeReferenceNode, ReasoningStepNode,
    NeuralNetworkLayerNode, NeuralNetworkModelNode, AIModelDefinitionNode,
    BrainHatCommunicationNode, KnowledgeQueryNode
)


class AIParser:
    """Parser for AI-specific language constructs in Runa."""
    
    def __init__(self):
        """Initialize the AI parser."""
        self.annotation_pattern = re.compile(r'#\s*@(\w+)(?:\(([^)]*)\))?\s*:\s*(.*?)$')
        # Patterns for parsing AI-specific syntax
        self.neural_model_pattern = re.compile(r'Neural\s+Model\s+called\s+"([^"]+)"')
        self.model_layer_pattern = re.compile(r'Layer\s+(\w+)(?:\s+called\s+"([^"]+)")?')
        self.brain_hat_pattern = re.compile(r'(Brain|Hat)\s+(\w+)(?:\s+with\s+([^:]+))?:')
        self.knowledge_query_pattern = re.compile(r'Knowledge\s+Query\s+(?:from\s+"([^"]+)")?\s*:')
    
    def parse_ai_annotation(self, comment_text: str, line: int = 0, column: int = 0) -> Optional[AIAnnotationNode]:
        """
        Parse an AI annotation from a comment.
        
        Args:
            comment_text: The text of the comment (including the # prefix).
            line: Line number of the comment.
            column: Column number of the comment.
            
        Returns:
            Parsed annotation node, or None if not an AI annotation.
        """
        # Check for AI annotation using regex
        match = self.annotation_pattern.match(comment_text)
        if not match:
            return None
        
        annotation_type = match.group(1).lower()
        param_str = match.group(2) or ""
        content = match.group(3)
        
        # Parse parameters
        params = {}
        for param in param_str.split(","):
            param = param.strip()
            if not param:
                continue
                
            if "=" in param:
                key, value = param.split("=", 1)
                params[key.strip()] = value.strip()
        
        # Create the appropriate annotation node
        if annotation_type == "knowledge":
            return KnowledgeReferenceNode(
                annotation_type=annotation_type,
                content=content,
                metadata=params,
                line=line,
                column=column,
                entity_id=params.get("entity", ""),
                relation_type=params.get("relation"),
                target_entity_id=params.get("target"),
                confidence=float(params.get("confidence", 1.0))
            )
        elif annotation_type == "reasoning":
            premises = []
            if "premise" in params:
                # Parse premises as a list
                premise_str = params["premise"]
                if premise_str.startswith("[") and premise_str.endswith("]"):
                    premises = [p.strip().strip('"\'') for p in premise_str[1:-1].split(",")]
            
            return ReasoningStepNode(
                annotation_type=annotation_type,
                content=content,
                metadata=params,
                line=line,
                column=column,
                premises=premises,
                conclusion=params.get("conclusion"),
                confidence=float(params.get("confidence", 1.0))
            )
        else:
            # Generic AI annotation
            return AIAnnotationNode(
                annotation_type=annotation_type,
                content=content,
                metadata=params,
                line=line,
                column=column
            )
    
    def parse_neural_network_model(self, code: str) -> Optional[AIModelDefinitionNode]:
        """
        Parse a neural network model definition from code.
        
        Args:
            code: The code containing a neural network model definition.
            
        Returns:
            An AIModelDefinitionNode if a model is found, None otherwise.
        """
        # Find model definition
        model_match = self.neural_model_pattern.search(code)
        if not model_match:
            return None
        
        model_name = model_match.group(1)
        
        # Create model node
        model = AIModelDefinitionNode(
            model_type="neural_network",
            name=model_name,
            line=0,  # We don't have position info in this simplified version
            column=0
        )
        
        # Create neural network structure
        nn_model = NeuralNetworkModelNode(name=model_name)
        
        # Find layers
        for layer_match in self.model_layer_pattern.finditer(code):
            layer_type = layer_match.group(1)
            layer_name = layer_match.group(2) if layer_match.group(2) else None
            
            layer = NeuralNetworkLayerNode(
                layer_type=layer_type,
                name=layer_name
            )
            
            nn_model.layers.append(layer)
        
        # Attach neural network to model definition
        model.neural_network = nn_model
        
        return model
    
    def parse_brain_hat_communication(self, code: str) -> List[BrainHatCommunicationNode]:
        """
        Parse brain-hat communication constructs from code.
        
        Args:
            code: The code containing brain-hat communication.
            
        Returns:
            List of BrainHatCommunicationNode instances.
        """
        results = []
        
        # Find brain-hat patterns
        for match in self.brain_hat_pattern.finditer(code):
            direction = "brain_to_hat" if match.group(1) == "Brain" else "hat_to_brain"
            message_type = match.group(2)
            
            # Find content (everything after the colon until the end of the indented block)
            start_pos = match.end()
            colon_pos = code.find(":", start_pos)
            if colon_pos != -1:
                # Find the end of the indented block
                content_start = colon_pos + 1
                content_end = content_start
                
                # Simple heuristic for block end (end of file or line with same/less indentation)
                current_line_start = code.rfind("\n", 0, colon_pos) + 1
                base_indent = colon_pos - current_line_start
                
                lines = code[content_start:].split("\n")
                for i, line in enumerate(lines):
                    if i == 0:  # Skip first line (it's the line with the colon)
                        continue
                    
                    # Check if this line is less indented (end of block)
                    stripped_line = line.lstrip()
                    if not stripped_line:  # Skip empty lines
                        continue
                    
                    indent = len(line) - len(stripped_line)
                    if indent <= base_indent:
                        content_end = content_start + code[content_start:].find(line)
                        break
                
                # If we didn't find the end, go to the end of the file
                if content_end == content_start:
                    content_end = len(code)
                
                content = code[content_start:content_end].strip()
                
                # Create the node
                comm_node = BrainHatCommunicationNode(
                    direction=direction,
                    message_type=message_type.lower(),
                    content=content,
                    line=0,  # We don't have position info in this simplified version
                    column=0
                )
                
                results.append(comm_node)
        
        return results
    
    def parse_knowledge_query(self, code: str) -> List[KnowledgeQueryNode]:
        """
        Parse knowledge query constructs from code.
        
        Args:
            code: The code containing knowledge queries.
            
        Returns:
            List of KnowledgeQueryNode instances.
        """
        results = []
        
        # Find knowledge query patterns
        for match in self.knowledge_query_pattern.finditer(code):
            graph_ref = match.group(1)
            
            # Find query text (everything after the colon until the end of the indented block)
            start_pos = match.end()
            colon_pos = code.find(":", start_pos)
            if colon_pos != -1:
                # Find the end of the indented block (similar to brain-hat parsing)
                content_start = colon_pos + 1
                content_end = content_start
                
                # Simple heuristic for block end (end of file or line with same/less indentation)
                current_line_start = code.rfind("\n", 0, colon_pos) + 1
                base_indent = colon_pos - current_line_start
                
                lines = code[content_start:].split("\n")
                for i, line in enumerate(lines):
                    if i == 0:  # Skip first line (it's the line with the colon)
                        continue
                    
                    # Check if this line is less indented (end of block)
                    stripped_line = line.lstrip()
                    if not stripped_line:  # Skip empty lines
                        continue
                    
                    indent = len(line) - len(stripped_line)
                    if indent <= base_indent:
                        content_end = content_start + code[content_start:].find(line)
                        break
                
                # If we didn't find the end, go to the end of the file
                if content_end == content_start:
                    content_end = len(code)
                
                query_text = code[content_start:content_end].strip()
                
                # Create the node
                query_node = KnowledgeQueryNode(
                    query_type="sparql",  # Default query type
                    query_text=query_text,
                    graph_ref=graph_ref,
                    line=0,  # We don't have position info in this simplified version
                    column=0
                )
                
                results.append(query_node)
        
        return results
    
    def extract_ai_annotations(self, code: str) -> List[AIAnnotationNode]:
        """
        Extract all AI annotations from code.
        
        Args:
            code: The Runa source code.
            
        Returns:
            List of annotation nodes.
        """
        annotations = []
        
        # Split code into lines and process each line
        lines = code.split('\n')
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Look for comment lines that might contain annotations
            comment_pos = line.find('#')
            if comment_pos != -1:
                comment = line[comment_pos:]
                annotation = self.parse_ai_annotation(comment, line_num, comment_pos)
                
                if annotation:
                    annotations.append(annotation)
        
        return annotations
