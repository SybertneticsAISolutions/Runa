"""
Knowledge Graph Connectivity for Runa.

This module provides integration between Runa code and knowledge graphs,
enabling bidirectional translation between code structures and semantic knowledge.
"""

import json
from typing import Dict, List, Any, Optional, Union, Tuple, Set, Callable
from ..annotation_system import (
    AnnotationNode, KnowledgeAnnotation, AnnotationType
)


class KnowledgeEntity:
    """Represents an entity in a knowledge graph."""
    
    def __init__(
        self, 
        entity_id: str, 
        entity_type: str, 
        properties: Dict[str, Any] = None,
        source: str = None
    ):
        """
        Initialize a knowledge entity.
        
        Args:
            entity_id: Unique identifier for the entity.
            entity_type: Type of the entity.
            properties: Dictionary of entity properties.
            source: Source knowledge graph identifier.
        """
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.properties = properties or {}
        self.source = source
        self.relationships = []
    
    def add_relationship(self, relation_type: str, target_entity_id: str, properties: Dict[str, Any] = None):
        """
        Add a relationship to another entity.
        
        Args:
            relation_type: Type of relationship.
            target_entity_id: ID of the target entity.
            properties: Optional properties of the relationship.
        """
        self.relationships.append({
            "relation_type": relation_type,
            "target_entity_id": target_entity_id,
            "properties": properties or {}
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary representation."""
        return {
            "id": self.entity_id,
            "type": self.entity_type,
            "properties": self.properties,
            "source": self.source,
            "relationships": self.relationships
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeEntity':
        """Create entity from dictionary representation."""
        entity = cls(
            entity_id=data["id"],
            entity_type=data["type"],
            properties=data.get("properties", {}),
            source=data.get("source")
        )
        
        for rel in data.get("relationships", []):
            entity.add_relationship(
                relation_type=rel["relation_type"],
                target_entity_id=rel["target_entity_id"],
                properties=rel.get("properties", {})
            )
        
        return entity


class KnowledgeTriple:
    """Represents a subject-predicate-object triple in a knowledge graph."""
    
    def __init__(
        self, 
        subject_id: str, 
        predicate: str, 
        object_id: str,
        confidence: float = 1.0,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a knowledge triple.
        
        Args:
            subject_id: ID of the subject entity.
            predicate: Predicate (relationship type).
            object_id: ID of the object entity.
            confidence: Confidence score (0.0 to 1.0).
            metadata: Additional metadata about the triple.
        """
        self.subject_id = subject_id
        self.predicate = predicate
        self.object_id = object_id
        self.confidence = confidence
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert triple to dictionary representation."""
        return {
            "subject": self.subject_id,
            "predicate": self.predicate,
            "object": self.object_id,
            "confidence": self.confidence,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KnowledgeTriple':
        """Create triple from dictionary representation."""
        return cls(
            subject_id=data["subject"],
            predicate=data["predicate"],
            object_id=data["object"],
            confidence=data.get("confidence", 1.0),
            metadata=data.get("metadata", {})
        )


class KnowledgeGraphConnector:
    """
    Connector for integrating Runa code with knowledge graphs.
    """
    
    def __init__(self, graph_uri: str = None):
        """
        Initialize a knowledge graph connector.
        
        Args:
            graph_uri: URI of the knowledge graph to connect to.
        """
        self.graph_uri = graph_uri
        self.entities: Dict[str, KnowledgeEntity] = {}
        self.triples: List[KnowledgeTriple] = []
        self.api_client = None  # Would be initialized with actual client
    
    def connect(self, api_key: str = None) -> bool:
        """
        Connect to the knowledge graph.
        
        Args:
            api_key: Optional API key for authentication.
            
        Returns:
            True if connection is successful, False otherwise.
        """
        # Placeholder for actual connection logic
        self.api_client = {"connected": True, "api_key": api_key}
        return True
    
    def extract_annotations_from_code(self, code: str) -> List[KnowledgeAnnotation]:
        """
        Extract knowledge annotations from Runa code.
        
        Args:
            code: Runa source code.
            
        Returns:
            List of knowledge annotations.
        """
        from ..annotation_system import AnnotationParser
        
        parser = AnnotationParser()
        all_annotations = parser.parse_annotations(code)
        
        # Filter for knowledge annotations only
        knowledge_annotations = [
            ann for ann in all_annotations 
            if ann.annotation_type == AnnotationType.KNOWLEDGE
        ]
        
        return knowledge_annotations
    
    def create_entity_from_annotation(
        self, 
        annotation: KnowledgeAnnotation
    ) -> Optional[KnowledgeEntity]:
        """
        Create a knowledge entity from an annotation.
        
        Args:
            annotation: The knowledge annotation.
            
        Returns:
            A knowledge entity, or None if creation fails.
        """
        if not annotation.entity_id:
            return None
        
        entity_type = annotation.metadata.get("entity_type", "concept")
        properties = {
            "description": annotation.content,
            **{k: v for k, v in annotation.metadata.items() 
              if k not in ["entity_type", "source"]}
        }
        
        return KnowledgeEntity(
            entity_id=annotation.entity_id,
            entity_type=entity_type,
            properties=properties,
            source=annotation.graph_source
        )
    
    def create_triple_from_annotation(
        self, 
        annotation: KnowledgeAnnotation
    ) -> Optional[KnowledgeTriple]:
        """
        Create a knowledge triple from an annotation.
        
        Args:
            annotation: The knowledge annotation.
            
        Returns:
            A knowledge triple, or None if creation fails.
        """
        # Check for required fields
        if not (annotation.entity_id and annotation.relation_type 
                and annotation.metadata.get("target_entity_id")):
            return None
        
        return KnowledgeTriple(
            subject_id=annotation.entity_id,
            predicate=annotation.relation_type,
            object_id=annotation.metadata["target_entity_id"],
            confidence=annotation.confidence,
            metadata={k: v for k, v in annotation.metadata.items() 
                     if k != "target_entity_id"}
        )
    
    def code_to_knowledge(self, code: str) -> Tuple[List[KnowledgeEntity], List[KnowledgeTriple]]:
        """
        Convert Runa code to knowledge entities and triples.
        
        Args:
            code: Runa source code.
            
        Returns:
            Tuple of (entities, triples) extracted from the code.
        """
        annotations = self.extract_annotations_from_code(code)
        entities = []
        triples = []
        
        for annotation in annotations:
            if isinstance(annotation, KnowledgeAnnotation):
                # Create entity
                entity = self.create_entity_from_annotation(annotation)
                if entity:
                    entities.append(entity)
                
                # Create triple if relation specified
                triple = self.create_triple_from_annotation(annotation)
                if triple:
                    triples.append(triple)
        
        return entities, triples
    
    def knowledge_to_annotations(
        self, 
        entities: List[KnowledgeEntity], 
        triples: List[KnowledgeTriple]
    ) -> List[KnowledgeAnnotation]:
        """
        Convert knowledge entities and triples to annotations.
        
        Args:
            entities: List of knowledge entities.
            triples: List of knowledge triples.
            
        Returns:
            List of knowledge annotations.
        """
        annotations = []
        
        # Convert entities to annotations
        for entity in entities:
            content = entity.properties.get("description", f"Entity: {entity.entity_id}")
            
            annotation = KnowledgeAnnotation(
                annotation_type=AnnotationType.KNOWLEDGE,
                content=content,
                entity_id=entity.entity_id,
                graph_source=entity.source,
                metadata={
                    "entity_type": entity.entity_type,
                    **{k: v for k, v in entity.properties.items() if k != "description"}
                }
            )
            annotations.append(annotation)
        
        # Convert triples to annotations
        for triple in triples:
            content = triple.metadata.get("description", f"Relation: {triple.predicate}")
            
            annotation = KnowledgeAnnotation(
                annotation_type=AnnotationType.KNOWLEDGE,
                content=content,
                entity_id=triple.subject_id,
                relation_type=triple.predicate,
                confidence=triple.confidence,
                graph_source=triple.metadata.get("source"),
                metadata={
                    "target_entity_id": triple.object_id,
                    **{k: v for k, v in triple.metadata.items() 
                       if k not in ["description", "source"]}
                }
            )
            annotations.append(annotation)
        
        return annotations
    
    def query_knowledge_graph(
        self, 
        query: Union[str, Dict[str, Any]], 
        query_type: str = "sparql"
    ) -> List[Dict[str, Any]]:
        """
        Query the knowledge graph for information.
        
        Args:
            query: Query string or structured query object.
            query_type: Type of query (sparql, cypher, etc.)
            
        Returns:
            List of result objects.
        """
        # Placeholder for actual query logic
        # In a real implementation, this would call the graph API
        if isinstance(query, str) and query_type == "sparql":
            # Example response for a SPARQL query
            if "?entity" in query and "?type" in query:
                return [
                    {"entity": "concept:123", "type": "Algorithm"},
                    {"entity": "concept:456", "type": "DataStructure"}
                ]
        
        # Structured query example for entity lookup
        if isinstance(query, dict) and "entity_id" in query:
            entity_id = query["entity_id"]
            return [{"id": entity_id, "found": True}]
        
        return []
    
    def create_semantic_links(
        self, 
        code_element: Dict[str, Any], 
        entity_type: str
    ) -> List[KnowledgeAnnotation]:
        """
        Create semantic links between code elements and knowledge entities.
        
        Args:
            code_element: Dictionary describing a code element.
            entity_type: Type of entity to link to.
            
        Returns:
            List of knowledge annotations with semantic links.
        """
        # Get the name of the code element
        element_name = code_element.get("name", "")
        element_type = code_element.get("type", "unknown")
        
        if not element_name:
            return []
        
        # Placeholder for semantic matching algorithm
        # In a real implementation, this would use NLP and graph-based approaches
        matching_entities = self.query_knowledge_graph({
            "name_similar_to": element_name,
            "type": entity_type
        })
        
        annotations = []
        for entity in matching_entities:
            confidence = entity.get("match_score", 0.7)
            entity_id = entity.get("id")
            
            if entity_id:
                annotation = KnowledgeAnnotation(
                    annotation_type=AnnotationType.KNOWLEDGE,
                    content=f"{element_type} {element_name} represents {entity_type} {entity_id}",
                    entity_id=entity_id,
                    relation_type="represents",
                    confidence=confidence,
                    metadata={
                        "code_element_type": element_type,
                        "code_element_name": element_name,
                        "entity_type": entity_type
                    }
                )
                annotations.append(annotation)
        
        return annotations
    
    def serialize_to_file(self, filename: str) -> bool:
        """
        Serialize the current knowledge graph data to a file.
        
        Args:
            filename: Path to output file.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            data = {
                "entities": [entity.to_dict() for entity in self.entities.values()],
                "triples": [triple.to_dict() for triple in self.triples]
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error serializing knowledge graph: {e}")
            return False
    
    def load_from_file(self, filename: str) -> bool:
        """
        Load knowledge graph data from a file.
        
        Args:
            filename: Path to input file.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Clear existing data
            self.entities = {}
            self.triples = []
            
            # Load entities
            for entity_data in data.get("entities", []):
                entity = KnowledgeEntity.from_dict(entity_data)
                self.entities[entity.entity_id] = entity
            
            # Load triples
            for triple_data in data.get("triples", []):
                triple = KnowledgeTriple.from_dict(triple_data)
                self.triples.append(triple)
            
            return True
        except Exception as e:
            print(f"Error loading knowledge graph: {e}")
            return False


class RunaKnowledgeMapper:
    """
    Maps Runa language elements to knowledge graph concepts.
    """
    
    def __init__(self, connector: KnowledgeGraphConnector = None):
        """
        Initialize a Runa knowledge mapper.
        
        Args:
            connector: Knowledge graph connector to use.
        """
        self.connector = connector or KnowledgeGraphConnector()
        self.type_mappings = {
            "Process": "function",
            "Let": "variable",
            "Type": "type",
            "Display": "io_operation",
            "Match": "control_flow",
            "When": "condition",
            "For": "iteration",
            "While": "iteration",
            "Try": "error_handling",
            "Catch": "error_handling",
            "Async": "asynchronous",
            "Generator": "generator",
            "Context": "context_manager"
        }
    
    def map_ast_node(self, node: Dict[str, Any]) -> List[KnowledgeAnnotation]:
        """
        Map an AST node to knowledge annotations.
        
        Args:
            node: AST node dictionary.
            
        Returns:
            List of knowledge annotations.
        """
        node_type = node.get("type")
        annotations = []
        
        if not node_type:
            return annotations
        
        # Map to knowledge entity type based on Runa node type
        if node_type in self.type_mappings:
            knowledge_type = self.type_mappings[node_type]
            
            # Create annotations based on node type
            if node_type == "Process":
                # For function definitions
                function_name = node.get("name", "")
                params = node.get("parameters", [])
                param_names = [p.get("name", "") for p in params]
                
                annotations.append(KnowledgeAnnotation(
                    annotation_type=AnnotationType.KNOWLEDGE,
                    content=f"Function: {function_name}",
                    entity_id=f"function:{function_name}",
                    relation_type="defined_as",
                    metadata={
                        "entity_type": "function",
                        "parameters": param_names,
                        "async": node.get("is_async", False),
                        "generator": node.get("is_generator", False)
                    }
                ))
                
                # Add parameter annotations
                for param in params:
                    param_name = param.get("name", "")
                    if param_name:
                        annotations.append(KnowledgeAnnotation(
                            annotation_type=AnnotationType.KNOWLEDGE,
                            content=f"Parameter: {param_name}",
                            entity_id=f"parameter:{param_name}",
                            relation_type="parameter_of",
                            metadata={
                                "entity_type": "parameter",
                                "function": function_name,
                                "target_entity_id": f"function:{function_name}"
                            }
                        ))
            
            elif node_type == "Type":
                # For type definitions
                type_name = node.get("name", "")
                base_type = node.get("base_type", "")
                fields = node.get("fields", [])
                field_names = [f.get("name", "") for f in fields]
                
                annotations.append(KnowledgeAnnotation(
                    annotation_type=AnnotationType.KNOWLEDGE,
                    content=f"Type: {type_name}",
                    entity_id=f"type:{type_name}",
                    relation_type="defined_as",
                    metadata={
                        "entity_type": "type",
                        "base_type": base_type,
                        "fields": field_names
                    }
                ))
                
                # Add field annotations
                for field in fields:
                    field_name = field.get("name", "")
                    field_type = field.get("type", "")
                    if field_name:
                        annotations.append(KnowledgeAnnotation(
                            annotation_type=AnnotationType.KNOWLEDGE,
                            content=f"Field: {field_name}",
                            entity_id=f"field:{field_name}",
                            relation_type="field_of",
                            metadata={
                                "entity_type": "field",
                                "type": type_name,
                                "field_type": field_type,
                                "target_entity_id": f"type:{type_name}"
                            }
                        ))
            
            elif node_type == "Let":
                # For variable definitions
                var_name = node.get("name", "")
                var_type = node.get("type", "")
                
                annotations.append(KnowledgeAnnotation(
                    annotation_type=AnnotationType.KNOWLEDGE,
                    content=f"Variable: {var_name}",
                    entity_id=f"variable:{var_name}",
                    relation_type="defined_as",
                    metadata={
                        "entity_type": "variable",
                        "var_type": var_type
                    }
                ))
        
        # Recursively process child nodes
        for key, value in node.items():
            if isinstance(value, dict) and "type" in value:
                # Single child node
                child_annotations = self.map_ast_node(value)
                annotations.extend(child_annotations)
            elif isinstance(value, list):
                # List of child nodes
                for item in value:
                    if isinstance(item, dict) and "type" in item:
                        child_annotations = self.map_ast_node(item)
                        annotations.extend(child_annotations)
        
        return annotations
    
    def generate_knowledge_annotations(self, ast: Dict[str, Any]) -> List[KnowledgeAnnotation]:
        """
        Generate knowledge annotations from an AST.
        
        Args:
            ast: Abstract Syntax Tree as a dictionary.
            
        Returns:
            List of knowledge annotations.
        """
        return self.map_ast_node(ast)
    
    def enhance_code_with_knowledge_links(
        self, 
        code: str, 
        ast: Dict[str, Any]
    ) -> Tuple[str, List[KnowledgeAnnotation]]:
        """
        Enhance code with knowledge links.
        
        Args:
            code: Original Runa code.
            ast: Abstract Syntax Tree of the code.
            
        Returns:
            Tuple of (enhanced code, annotations)
        """
        from ..annotation_system import AnnotationGenerator
        
        # Generate knowledge annotations from AST
        annotations = self.generate_knowledge_annotations(ast)
        
        # Add additional links from external knowledge
        for annotation in annotations:
            entity_id = annotation.entity_id
            if entity_id and ":" in entity_id:
                entity_type = entity_id.split(":")[0]
                
                # Query for additional knowledge about this entity
                results = self.connector.query_knowledge_graph({
                    "entity_id": entity_id
                })
                
                if results and results[0].get("found"):
                    # Add relationship annotations
                    relations = self.connector.query_knowledge_graph({
                        "subject": entity_id
                    })
                    
                    for relation in relations:
                        rel_type = relation.get("predicate")
                        target = relation.get("object")
                        if rel_type and target:
                            annotations.append(KnowledgeAnnotation(
                                annotation_type=AnnotationType.KNOWLEDGE,
                                content=f"{entity_type} relates to {target}",
                                entity_id=entity_id,
                                relation_type=rel_type,
                                metadata={
                                    "target_entity_id": target
                                }
                            ))
        
        # Generate code with annotations
        generator = AnnotationGenerator()
        enhanced_code = generator.generate_annotations_for_code(code, annotations)
        
        return enhanced_code, annotations
