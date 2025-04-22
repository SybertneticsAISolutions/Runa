"""
Annotation system for AI-to-AI communication.

This module analyzes annotation nodes and extracts semantic information
for AI-to-AI communication scenarios.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from .nodes import (
    AnnotationNode, AnnotationType, AnnotatedCodeBlock, 
    ReasoningAnnotation, ImplementationAnnotation, KnowledgeAnnotation,
    VerificationAnnotation, IntentAnnotation, FeedbackAnnotation
)


class AnnotationAnalyzer:
    """
    Analyzer for annotation nodes, extracting and interpreting semantic information.
    """
    
    def __init__(self):
        """Initialize the annotation analyzer."""
        self.reasoning_chains: Dict[str, List[ReasoningAnnotation]] = {}
        self.implementation_insights: Dict[str, List[ImplementationAnnotation]] = {}
        self.knowledge_links: Dict[str, List[KnowledgeAnnotation]] = {}
        self.verification_steps: Dict[str, List[VerificationAnnotation]] = {}
        self.intent_descriptions: Dict[str, List[IntentAnnotation]] = {}
        self.feedback_items: Dict[str, List[FeedbackAnnotation]] = {}
    
    def analyze_annotations(self, annotations: List[AnnotationNode]) -> Dict[str, Any]:
        """
        Analyze a list of annotations and extract semantic information.
        
        Args:
            annotations: List of annotation nodes to analyze.
            
        Returns:
            Dictionary containing analysis results.
        """
        # Reset state for fresh analysis
        self._reset_state()
        
        # Categorize annotations by type
        self._categorize_annotations(annotations)
        
        # Perform specific analyses
        reasoning_analysis = self._analyze_reasoning_chains()
        implementation_analysis = self._analyze_implementation_insights()
        knowledge_analysis = self._analyze_knowledge_links()
        verification_analysis = self._analyze_verification_steps()
        intent_analysis = self._analyze_intent_descriptions()
        feedback_analysis = self._analyze_feedback_items()
        
        # Combine results
        return {
            "reasoning_chains": reasoning_analysis,
            "implementation_insights": implementation_analysis,
            "knowledge_links": knowledge_analysis,
            "verification_steps": verification_analysis,
            "intent_descriptions": intent_analysis,
            "feedback_items": feedback_analysis,
            "summary": self._generate_summary(
                reasoning_analysis,
                implementation_analysis,
                knowledge_analysis,
                verification_analysis,
                intent_analysis,
                feedback_analysis
            )
        }
    
    def analyze_annotated_block(self, block: AnnotatedCodeBlock) -> Dict[str, Any]:
        """
        Analyze an annotated code block.
        
        Args:
            block: The annotated code block to analyze.
            
        Returns:
            Dictionary containing analysis results for the block.
        """
        # Reset state for fresh analysis
        self._reset_state()
        
        # Categorize annotations in the block
        self._categorize_annotations(block.annotations)
        
        # Basic code metrics
        code_metrics = self._analyze_code_metrics(block.code)
        
        # Combine with annotation analysis
        block_analysis = self.analyze_annotations(block.annotations)
        block_analysis["code_metrics"] = code_metrics
        
        return block_analysis
    
    def analyze_communication_patterns(
        self, 
        annotations: List[AnnotationNode]
    ) -> Dict[str, Any]:
        """
        Analyze communication patterns between AI systems in the annotations.
        
        Args:
            annotations: List of annotation nodes to analyze.
            
        Returns:
            Dictionary containing communication pattern analysis.
        """
        # Extract sender/receiver pairs
        communication_pairs = []
        
        for annotation in annotations:
            if "sender" in annotation.metadata and "receiver" in annotation.metadata:
                communication_pairs.append({
                    "sender": annotation.metadata["sender"],
                    "receiver": annotation.metadata["receiver"],
                    "message_type": annotation.annotation_type.value,
                    "content": annotation.content
                })
        
        # Identify common communication channels
        channels = {}
        for pair in communication_pairs:
            channel_id = f"{pair['sender']}->{pair['receiver']}"
            if channel_id not in channels:
                channels[channel_id] = []
            channels[channel_id].append(pair)
        
        # Analyze message frequency and types per channel
        channel_analysis = {}
        for channel_id, messages in channels.items():
            message_types = {}
            for message in messages:
                msg_type = message["message_type"]
                if msg_type not in message_types:
                    message_types[msg_type] = 0
                message_types[msg_type] += 1
            
            channel_analysis[channel_id] = {
                "message_count": len(messages),
                "message_types": message_types
            }
        
        return {
            "communication_pairs": communication_pairs,
            "channels": channel_analysis,
            "total_messages": len(communication_pairs)
        }
    
    def _reset_state(self) -> None:
        """Reset the analyzer's internal state."""
        self.reasoning_chains = {}
        self.implementation_insights = {}
        self.knowledge_links = {}
        self.verification_steps = {}
        self.intent_descriptions = {}
        self.feedback_items = {}
    
    def _categorize_annotations(self, annotations: List[AnnotationNode]) -> None:
        """
        Categorize annotations by their type.
        
        Args:
            annotations: List of annotation nodes to categorize.
        """
        for annotation in annotations:
            # Determine category key (use component from metadata if available)
            component = annotation.metadata.get("component", "default")
            
            # Categorize by type
            if annotation.annotation_type == AnnotationType.REASONING:
                if component not in self.reasoning_chains:
                    self.reasoning_chains[component] = []
                self.reasoning_chains[component].append(annotation)
            
            elif annotation.annotation_type == AnnotationType.IMPLEMENTATION:
                if component not in self.implementation_insights:
                    self.implementation_insights[component] = []
                self.implementation_insights[component].append(annotation)
            
            elif annotation.annotation_type == AnnotationType.KNOWLEDGE:
                if component not in self.knowledge_links:
                    self.knowledge_links[component] = []
                self.knowledge_links[component].append(annotation)
            
            elif annotation.annotation_type == AnnotationType.VERIFICATION:
                if component not in self.verification_steps:
                    self.verification_steps[component] = []
                self.verification_steps[component].append(annotation)
            
            elif annotation.annotation_type == AnnotationType.INTENT:
                if component not in self.intent_descriptions:
                    self.intent_descriptions[component] = []
                self.intent_descriptions[component].append(annotation)
            
            elif annotation.annotation_type == AnnotationType.FEEDBACK:
                if component not in self.feedback_items:
                    self.feedback_items[component] = []
                self.feedback_items[component].append(annotation)
    
    def _analyze_reasoning_chains(self) -> Dict[str, Any]:
        """
        Analyze reasoning chains in the annotations.
        
        Returns:
            Dictionary containing reasoning chain analysis.
        """
        chain_analysis = {}
        
        for component, annotations in self.reasoning_chains.items():
            # Sort annotations by line number if available
            sorted_annotations = sorted(
                annotations,
                key=lambda a: a.source_position.get("line", 0) if a.source_position else 0
            )
            
            # Extract premises and conclusions
            premises = set()
            conclusions = set()
            confidence_sum = 0.0
            
            for annotation in sorted_annotations:
                if isinstance(annotation, ReasoningAnnotation):
                    # Add premises and conclusion
                    for premise in annotation.premise:
                        premises.add(premise)
                    
                    if annotation.conclusion:
                        conclusions.add(annotation.conclusion)
                    
                    # Track confidence
                    confidence_sum += annotation.confidence
            
            # Calculate average confidence
            avg_confidence = confidence_sum / len(sorted_annotations) if sorted_annotations else 0
            
            chain_analysis[component] = {
                "premises": list(premises),
                "conclusions": list(conclusions),
                "step_count": len(sorted_annotations),
                "average_confidence": avg_confidence
            }
        
        return chain_analysis
    
    def _analyze_implementation_insights(self) -> Dict[str, Any]:
        """
        Analyze implementation insights in the annotations.
        
        Returns:
            Dictionary containing implementation insight analysis.
        """
        insight_analysis = {}
        
        for component, annotations in self.implementation_insights.items():
            algorithms = set()
            complexities = set()
            alternatives = set()
            
            for annotation in annotations:
                if isinstance(annotation, ImplementationAnnotation):
                    if annotation.algorithm:
                        algorithms.add(annotation.algorithm)
                    
                    if annotation.complexity:
                        complexities.add(annotation.complexity)
                    
                    for alt in annotation.alternative_approaches:
                        alternatives.add(alt)
            
            insight_analysis[component] = {
                "algorithms": list(algorithms),
                "complexities": list(complexities),
                "alternative_approaches": list(alternatives),
                "insight_count": len(annotations)
            }
        
        return insight_analysis
    
    def _analyze_knowledge_links(self) -> Dict[str, Any]:
        """
        Analyze knowledge graph links in the annotations.
        
        Returns:
            Dictionary containing knowledge link analysis.
        """
        link_analysis = {}
        
        for component, annotations in self.knowledge_links.items():
            entities = set()
            relations = set()
            sources = set()
            
            for annotation in annotations:
                if isinstance(annotation, KnowledgeAnnotation):
                    if annotation.entity_id:
                        entities.add(annotation.entity_id)
                    
                    if annotation.relation_type:
                        relations.add(annotation.relation_type)
                    
                    if annotation.graph_source:
                        sources.add(annotation.graph_source)
            
            link_analysis[component] = {
                "entities": list(entities),
                "relations": list(relations),
                "sources": list(sources),
                "link_count": len(annotations)
            }
        
        return link_analysis
    
    def _analyze_verification_steps(self) -> Dict[str, Any]:
        """
        Analyze verification steps in the annotations.
        
        Returns:
            Dictionary containing verification step analysis.
        """
        verification_analysis = {}
        
        for component, annotations in self.verification_steps.items():
            assertions = set()
            methods = set()
            status_counts = {"verified": 0, "failed": 0, "pending": 0, "unknown": 0}
            
            for annotation in annotations:
                if isinstance(annotation, VerificationAnnotation):
                    assertions.add(annotation.assertion)
                    methods.add(annotation.verification_method)
                    
                    status = annotation.status
                    if status in status_counts:
                        status_counts[status] += 1
                    else:
                        status_counts["unknown"] += 1
            
            verification_analysis[component] = {
                "assertions": list(assertions),
                "verification_methods": list(methods),
                "status_counts": status_counts,
                "step_count": len(annotations)
            }
        
        return verification_analysis
    
    def _analyze_intent_descriptions(self) -> Dict[str, Any]:
        """
        Analyze intent descriptions in the annotations.
        
        Returns:
            Dictionary containing intent description analysis.
        """
        intent_analysis = {}
        
        for component, annotations in self.intent_descriptions.items():
            goals = set()
            rationales = set()
            alternatives = set()
            
            for annotation in annotations:
                if isinstance(annotation, IntentAnnotation):
                    goals.add(annotation.goal)
                    
                    if annotation.rationale:
                        rationales.add(annotation.rationale)
                    
                    for alt in annotation.alternatives_considered:
                        alternatives.add(alt)
            
            intent_analysis[component] = {
                "goals": list(goals),
                "rationales": list(rationales),
                "alternatives_considered": list(alternatives),
                "description_count": len(annotations)
            }
        
        return intent_analysis
    
    def _analyze_feedback_items(self) -> Dict[str, Any]:
        """
        Analyze feedback items in the annotations.
        
        Returns:
            Dictionary containing feedback item analysis.
        """
        feedback_analysis = {}
        
        for component, annotations in self.feedback_items.items():
            suggestions = set()
            areas = set()
            priority_counts = {"high": 0, "medium": 0, "low": 0}
            
            for annotation in annotations:
                if isinstance(annotation, FeedbackAnnotation):
                    suggestions.add(annotation.suggestion)
                    areas.add(annotation.improvement_area)
                    
                    priority = annotation.priority.lower()
                    if priority in priority_counts:
                        priority_counts[priority] += 1
            
            feedback_analysis[component] = {
                "suggestions": list(suggestions),
                "improvement_areas": list(areas),
                "priority_counts": priority_counts,
                "item_count": len(annotations)
            }
        
        return feedback_analysis
    
    def _analyze_code_metrics(self, code: str) -> Dict[str, Any]:
        """
        Analyze basic metrics of the code.
        
        Args:
            code: The code to analyze.
            
        Returns:
            Dictionary containing code metrics.
        """
        lines = code.split("\n")
        non_empty_lines = [line for line in lines if line.strip()]
        comment_lines = [line for line in lines if line.strip().startswith("#")]
        
        return {
            "total_lines": len(lines),
            "non_empty_lines": len(non_empty_lines),
            "comment_lines": len(comment_lines),
            "code_to_comment_ratio": len(non_empty_lines) / len(comment_lines) if comment_lines else float("inf"),
            "average_line_length": sum(len(line) for line in non_empty_lines) / len(non_empty_lines) if non_empty_lines else 0
        }
    
    def _generate_summary(self, *analyses) -> Dict[str, Any]:
        """
        Generate an overall summary from all analyses.
        
        Returns:
            Dictionary containing summary information.
        """
        # Count total annotations of each type
        total_reasoning = sum(len(chains) for chains in self.reasoning_chains.values())
        total_implementation = sum(len(insights) for insights in self.implementation_insights.values())
        total_knowledge = sum(len(links) for links in self.knowledge_links.values())
        total_verification = sum(len(steps) for steps in self.verification_steps.values())
        total_intent = sum(len(descs) for descs in self.intent_descriptions.values())
        total_feedback = sum(len(items) for items in self.feedback_items.values())
        
        total_annotations = (
            total_reasoning + total_implementation + total_knowledge +
            total_verification + total_intent + total_feedback
        )
        
        # Count components with annotations
        components = set().union(
            self.reasoning_chains.keys(),
            self.implementation_insights.keys(),
            self.knowledge_links.keys(),
            self.verification_steps.keys(),
            self.intent_descriptions.keys(),
            self.feedback_items.keys()
        )
        
        return {
            "total_annotations": total_annotations,
            "annotation_type_counts": {
                "reasoning": total_reasoning,
                "implementation": total_implementation,
                "knowledge": total_knowledge,
                "verification": total_verification,
                "intent": total_intent,
                "feedback": total_feedback
            },
            "component_count": len(components),
            "components": list(components)
        }