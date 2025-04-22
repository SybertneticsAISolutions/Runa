"""
AST nodes for AI-specific language extensions in Runa.

This module defines the AST node structures for AI-related language
features, such as model descriptions, knowledge integration, and
AI-to-AI communication directives.
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field


@dataclass
class AIAnnotationNode:
    """Base class for all AI annotation nodes in the AST."""
    annotation_type: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    line: int = 0
    column: int = 0


@dataclass
class KnowledgeReferenceNode(AIAnnotationNode):
    """Node representing a reference to a knowledge graph entity."""
    entity_id: str
    relation_type: Optional[str] = None
    target_entity_id: Optional[str] = None
    confidence: float = 1.0
    
    def __post_init__(self):
        """Initialize with correct annotation type."""
        self.annotation_type = "knowledge"


@dataclass
class ReasoningStepNode(AIAnnotationNode):
    """Node representing a reasoning step in an AI algorithm."""
    premises: List[str] = field(default_factory=list)
    conclusion: Optional[str] = None
    confidence: float = 1.0
    
    def __post_init__(self):
        """Initialize with correct annotation type."""
        self.annotation_type = "reasoning"


@dataclass
class NeuralNetworkLayerNode:
    """Node representing a layer in a neural network."""
    layer_type: str  # e.g., "dense", "conv2d", "lstm"
    name: Optional[str] = None
    input_shape: Optional[List[int]] = None
    output_shape: Optional[List[int]] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    activation: Optional[str] = None
    regularization: Optional[Dict[str, Any]] = None


@dataclass
class NeuralNetworkModelNode:
    """Node representing a neural network model."""
    name: str
    layers: List[NeuralNetworkLayerNode] = field(default_factory=list)
    input_shape: Optional[List[int]] = None
    optimizer: Optional[str] = None
    loss: Optional[str] = None
    metrics: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIModelDefinitionNode:
    """Node representing an AI model definition in the code."""
    model_type: str  # e.g., "neural_network", "decision_tree", "transformer"
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    neural_network: Optional[NeuralNetworkModelNode] = None
    training_config: Dict[str, Any] = field(default_factory=dict)
    inference_config: Dict[str, Any] = field(default_factory=dict)
    line: int = 0
    column: int = 0


@dataclass
class DatasetReferenceNode:
    """Node representing a reference to a dataset."""
    name: str
    source: Optional[str] = None
    schema: Dict[str, Any] = field(default_factory=dict)
    statistics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    line: int = 0
    column: int = 0


@dataclass
class TrainingConfigNode:
    """Node representing training configuration for an AI model."""
    model_ref: str
    dataset_ref: str
    batch_size: Optional[int] = None
    epochs: Optional[int] = None
    learning_rate: Optional[float] = None
    optimizer_params: Dict[str, Any] = field(default_factory=dict)
    callbacks: List[Dict[str, Any]] = field(default_factory=list)
    validation_split: Optional[float] = None
    validation_dataset_ref: Optional[str] = None
    line: int = 0
    column: int = 0


@dataclass
class BrainHatCommunicationNode:
    """
    Node representing communication between the 'brain' (reasoning) and 
    'hat' (implementation) components of an AI system.
    """
    direction: str  # "brain_to_hat" or "hat_to_brain"
    message_type: str  # e.g., "query", "response", "instruction", "confirmation"
    content: str
    context: Dict[str, Any] = field(default_factory=dict)
    references: List[str] = field(default_factory=list)
    line: int = 0
    column: int = 0


@dataclass
class AIFunctionCallNode:
    """Node representing an AI function call in the code."""
    function_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    model_ref: Optional[str] = None
    annotation: Optional[AIAnnotationNode] = None
    async_call: bool = False
    line: int = 0
    column: int = 0


@dataclass
class KnowledgeQueryNode:
    """Node representing a query to a knowledge graph."""
    query_type: str  # e.g., "sparql", "cypher", "structured"
    query_text: str
    graph_ref: Optional[str] = None
    result_var: Optional[str] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    line: int = 0
    column: int = 0


@dataclass
class DataProcessingPipelineNode:
    """Node representing a data processing pipeline for AI."""
    name: str
    stages: List[Dict[str, Any]] = field(default_factory=list)
    input_ref: Optional[str] = None
    output_ref: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    line: int = 0
    column: int = 0


@dataclass
class AIAnnotatedBlockNode:
    """Node representing a block of code with AI annotations."""
    code_nodes: List[Any]  # Any AST node
    annotations: List[AIAnnotationNode] = field(default_factory=list)
    block_type: Optional[str] = None
    line: int = 0
    column: int = 0
