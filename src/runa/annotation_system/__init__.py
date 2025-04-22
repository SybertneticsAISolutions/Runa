"""
Runa Annotation System for AI-to-AI Communication.

This package provides tools for creating, parsing, analyzing, and generating
annotations that facilitate communication between AI components.
"""

from .nodes import (
    AnnotationNode, AnnotationType,
    ReasoningAnnotation, ImplementationAnnotation, KnowledgeAnnotation,
    VerificationAnnotation, IntentAnnotation, FeedbackAnnotation,
    AnnotatedCodeBlock
)

from .parser import AnnotationParser
from .analyzer import AnnotationAnalyzer
from .generator import AnnotationGenerator

__all__ = [
    'AnnotationNode', 'AnnotationType',
    'ReasoningAnnotation', 'ImplementationAnnotation', 'KnowledgeAnnotation',
    'VerificationAnnotation', 'IntentAnnotation', 'FeedbackAnnotation',
    'AnnotatedCodeBlock',
    'AnnotationParser', 'AnnotationAnalyzer', 'AnnotationGenerator',
]
