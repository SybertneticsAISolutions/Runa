"""
Semantic annotation nodes for AI-to-AI communication in Runa.

This module defines the node structures for the annotation system,
which enables AI components to communicate with each other through
code annotations.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from enum import Enum


class AnnotationType(Enum):
    """Types of annotations supported in the system."""
    REASONING = "reasoning"  # Annotations for reasoning steps
    IMPLEMENTATION = "implementation"  # Annotations for implementation details
    VERIFICATION = "verification"  # Annotations for verification steps
    KNOWLEDGE = "knowledge"  # Annotations linking to knowledge graph
    INTENT = "intent"  # Annotations for explaining intent
    FEEDBACK = "feedback"  # Annotations for feedback between AI systems


@dataclass
class AnnotationNode:
    """Base class for all annotation nodes."""
    annotation_type: AnnotationType
    content: str
    source_position: Optional[Dict[str, int]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert annotation to dictionary representation."""
        return {
            "type": self.annotation_type.value,
            "content": self.content,
            "position": self.source_position,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnnotationNode':
        """Create annotation from dictionary representation."""
        return cls(
            annotation_type=AnnotationType(data["type"]),
            content=data["content"],
            source_position=data.get("position"),
            metadata=data.get("metadata", {})
        )


@dataclass
class ReasoningAnnotation(AnnotationNode):
    """Annotation for reasoning steps in AI-to-AI communication."""
    premise: List[str] = field(default_factory=list)
    conclusion: Optional[str] = None
    confidence: float = 1.0
    
    def __post_init__(self):
        self.annotation_type = AnnotationType.REASONING
        
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "premise": self.premise,
            "conclusion": self.conclusion,
            "confidence": self.confidence
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReasoningAnnotation':
        base = super().from_dict(data)
        return cls(
            annotation_type=base.annotation_type,
            content=base.content,
            source_position=base.source_position,
            metadata=base.metadata,
            premise=data.get("premise", []),
            conclusion=data.get("conclusion"),
            confidence=data.get("confidence", 1.0)
        )


@dataclass
class ImplementationAnnotation(AnnotationNode):
    """Annotation for implementation details in AI-to-AI communication."""
    algorithm: Optional[str] = None
    complexity: Optional[str] = None
    alternative_approaches: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.annotation_type = AnnotationType.IMPLEMENTATION
        
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "algorithm": self.algorithm,
            "complexity": self.complexity,
            "alternative_approaches": self.alternative_approaches
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImplementationAnnotation':
        base = super().from_dict(data)
        return cls(
            annotation_type=base.annotation_type,
            content=base.content,
            source_position=base.source_position,
            metadata=base.metadata,
            algorithm=data.get("algorithm"),
            complexity=data.get("complexity"),
            alternative_approaches=data.get("alternative_approaches", [])
        )


@dataclass
class KnowledgeAnnotation(AnnotationNode):
    """Annotation for knowledge graph connections."""
    entity_id: Optional[str] = None
    relation_type: Optional[str] = None
    confidence: float = 1.0
    graph_source: Optional[str] = None
    
    def __post_init__(self):
        self.annotation_type = AnnotationType.KNOWLEDGE
        
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "entity_id": self.entity_id,
            "relation_type": self.relation_type,
            "confidence": self.confidence,
            "graph_source": self.graph_source
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeAnnotation':
        base = super().from_dict(data)
        return cls(
            annotation_type=base.annotation_type,
            content=base.content,
            source_position=base.source_position,
            metadata=base.metadata,
            entity_id=data.get("entity_id"),
            relation_type=data.get("relation_type"),
            confidence=data.get("confidence", 1.0),
            graph_source=data.get("graph_source")
        )


@dataclass
class VerificationAnnotation(AnnotationNode):
    """Annotation for verification steps."""
    assertion: Optional[str] = None
    verification_method: Optional[str] = None
    status: Optional[str] = None  # "verified", "failed", "pending"
    
    def __post_init__(self):
        self.annotation_type = AnnotationType.VERIFICATION
        
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "assertion": self.assertion,
            "verification_method": self.verification_method,
            "status": self.status
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VerificationAnnotation':
        base = super().from_dict(data)
        return cls(
            annotation_type=base.annotation_type,
            content=base.content,
            source_position=base.source_position,
            metadata=base.metadata,
            assertion=data.get("assertion", ""),
            verification_method=data.get("verification_method", ""),
            status=data.get("status")
        )


@dataclass
class IntentAnnotation(AnnotationNode):
    """Annotation for explaining intent."""
    goal: Optional[str] = None
    rationale: Optional[str] = None
    alternatives_considered: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.annotation_type = AnnotationType.INTENT
        
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "goal": self.goal,
            "rationale": self.rationale,
            "alternatives_considered": self.alternatives_considered
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntentAnnotation':
        base = super().from_dict(data)
        return cls(
            annotation_type=base.annotation_type,
            content=base.content,
            source_position=base.source_position,
            metadata=base.metadata,
            goal=data.get("goal", ""),
            rationale=data.get("rationale"),
            alternatives_considered=data.get("alternatives_considered", [])
        )


@dataclass
class FeedbackAnnotation(AnnotationNode):
    """Annotation for feedback between AI systems."""
    suggestion: str
    improvement_area: str
    priority: str = "medium"  # "high", "medium", "low"
    
    def __post_init__(self):
        self.annotation_type = AnnotationType.FEEDBACK
        
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "suggestion": self.suggestion,
            "improvement_area": self.improvement_area,
            "priority": self.priority
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeedbackAnnotation':
        base = super().from_dict(data)
        return cls(
            annotation_type=base.annotation_type,
            content=base.content,
            source_position=base.source_position,
            metadata=base.metadata,
            suggestion=data.get("suggestion", ""),
            improvement_area=data.get("improvement_area", ""),
            priority=data.get("priority", "medium")
        )


@dataclass
class AnnotatedCodeBlock:
    """Represents a code block with associated annotations."""
    code: str
    annotations: List[AnnotationNode] = field(default_factory=list)
    
    def add_annotation(self, annotation: AnnotationNode) -> None:
        """Add an annotation to this code block."""
        self.annotations.append(annotation)
    
    def get_annotations_by_type(self, annotation_type: AnnotationType) -> List[AnnotationNode]:
        """Get all annotations of a specific type."""
        return [a for a in self.annotations if a.annotation_type == annotation_type]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert annotated code block to dictionary representation."""
        return {
            "code": self.code,
            "annotations": [a.to_dict() for a in self.annotations]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnnotatedCodeBlock':
        """Create annotated code block from dictionary representation."""
        annotations = []
        for a_data in data.get("annotations", []):
            a_type = AnnotationType(a_data["type"])
            if a_type == AnnotationType.REASONING:
                annotation = ReasoningAnnotation.from_dict(a_data)
            elif a_type == AnnotationType.IMPLEMENTATION:
                annotation = ImplementationAnnotation.from_dict(a_data)
            elif a_type == AnnotationType.KNOWLEDGE:
                annotation = KnowledgeAnnotation.from_dict(a_data)
            elif a_type == AnnotationType.VERIFICATION:
                annotation = VerificationAnnotation.from_dict(a_data)
            elif a_type == AnnotationType.INTENT:
                annotation = IntentAnnotation.from_dict(a_data)
            elif a_type == AnnotationType.FEEDBACK:
                annotation = FeedbackAnnotation.from_dict(a_data)
            else:
                annotation = AnnotationNode.from_dict(a_data)
            annotations.append(annotation)
        
        return cls(
            code=data["code"],
            annotations=annotations
        )
