"""
AI-specific language extensions for Runa.

This module provides AI integration features for the Runa language,
including knowledge graph connectivity, model descriptions, and
AI-to-AI communication.
"""

from .nodes import (
    AIAnnotationNode, KnowledgeReferenceNode, ReasoningStepNode,
    NeuralNetworkLayerNode, NeuralNetworkModelNode, AIModelDefinitionNode,
    DatasetReferenceNode, TrainingConfigNode, BrainHatCommunicationNode,
    AIFunctionCallNode, KnowledgeQueryNode, DataProcessingPipelineNode,
    AIAnnotatedBlockNode
)

from .parser import AIParser
from .knowledge import (
    KnowledgeEntity, KnowledgeTriple, KnowledgeGraphConnector,
    RunaKnowledgeMapper
)

__all__ = [
    # AI AST Nodes
    'AIAnnotationNode', 'KnowledgeReferenceNode', 'ReasoningStepNode',
    'NeuralNetworkLayerNode', 'NeuralNetworkModelNode', 'AIModelDefinitionNode',
    'DatasetReferenceNode', 'TrainingConfigNode', 'BrainHatCommunicationNode',
    'AIFunctionCallNode', 'KnowledgeQueryNode', 'DataProcessingPipelineNode',
    'AIAnnotatedBlockNode',
    
    # Parsers
    'AIParser',
    
    # Knowledge Graph
    'KnowledgeEntity', 'KnowledgeTriple', 'KnowledgeGraphConnector',
    'RunaKnowledgeMapper'
]