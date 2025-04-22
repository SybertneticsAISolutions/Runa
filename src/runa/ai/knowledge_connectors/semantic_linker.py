"""
Semantic Linker for Runa knowledge graph integration.

This module provides functionality to connect code elements to knowledge graph
concepts using semantic similarity and other linking strategies.
"""

import re
import os
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from enum import Enum
import numpy as np

from ..knowledge import KnowledgeEntity, KnowledgeTriple, KnowledgeGraphConnector


class LinkingStrategy(Enum):
    """Strategies for linking code elements to knowledge graph concepts."""
    EXACT_MATCH = "exact_match"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    PATTERN_MATCHING = "pattern_matching"
    TYPE_BASED = "type_based"
    CONTEXT_BASED = "context_based"
    HYBRID = "hybrid"


class LinkConfidence(Enum):
    """Confidence levels for semantic links."""
    DEFINITE = 1.0
    HIGH = 0.8
    MEDIUM = 0.6
    LOW = 0.4
    SPECULATIVE = 0.2


class SemanticLink:
    """Represents a semantic link between a code element and a knowledge entity."""
    
    def __init__(
        self, 
        code_element_id: str,
        entity_id: str,
        link_type: str,
        confidence: float,
        strategy: LinkingStrategy,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a semantic link.
        
        Args:
            code_element_id: Identifier for the code element (e.g., function name)
            entity_id: Identifier for the knowledge entity
            link_type: Type of link (e.g., "implements", "relates_to")
            confidence: Confidence score for the link (0.0 to 1.0)
            strategy: Strategy used to establish the link
            metadata: Additional information about the link
        """
        self.code_element_id = code_element_id
        self.entity_id = entity_id
        self.link_type = link_type
        self.confidence = confidence
        self.strategy = strategy
        self.metadata = metadata or {}
    
    def to_triple(self) -> KnowledgeTriple:
        """Convert the semantic link to a knowledge triple."""
        return KnowledgeTriple(
            subject_id=self.code_element_id,
            predicate=self.link_type,
            object_id=self.entity_id,
            confidence=self.confidence,
            metadata=self.metadata
        )
    
    def __repr__(self) -> str:
        return (
            f"SemanticLink(code_element='{self.code_element_id}', "
            f"entity='{self.entity_id}', type='{self.link_type}', "
            f"confidence={self.confidence:.2f}, strategy={self.strategy.value})"
        )


class SemanticLinker:
    """Links code elements to knowledge graph concepts using semantic analysis."""
    
    def __init__(
        self, 
        connector: KnowledgeGraphConnector,
        embedding_provider: Any = None,
        min_confidence: float = 0.6,
        default_strategy: LinkingStrategy = LinkingStrategy.HYBRID
    ):
        """
        Initialize the semantic linker.
        
        Args:
            connector: Knowledge graph connector for accessing entities
            embedding_provider: Provider for generating embeddings 
                               (e.g., OpenAI embedding API)
            min_confidence: Minimum confidence threshold for links
            default_strategy: Default linking strategy to use
        """
        self.connector = connector
        self.embedding_provider = embedding_provider
        self.min_confidence = min_confidence
        self.default_strategy = default_strategy
        self.entity_cache = {}
        self.embedding_cache = {}
    
    def link_code_element(
        self,
        code_element: Dict[str, Any],
        candidates: Optional[List[KnowledgeEntity]] = None,
        strategy: Optional[LinkingStrategy] = None
    ) -> List[SemanticLink]:
        """
        Link a code element to knowledge graph entities.
        
        Args:
            code_element: Dictionary representing the code element
                         (must have 'id' and 'name' keys)
            candidates: Optional list of candidate entities to link to
                       (if None, will search the knowledge graph)
            strategy: Linking strategy to use (defaults to self.default_strategy)
            
        Returns:
            List of semantic links established
        """
        if strategy is None:
            strategy = self.default_strategy
            
        element_id = code_element.get('id')
        name = code_element.get('name')
        element_type = code_element.get('type')
        
        if not element_id or not name:
            raise ValueError("Code element must have 'id' and 'name' attributes")
        
        # Get candidates if not provided
        if candidates is None:
            candidates = self._find_candidate_entities(name, element_type)
        
        links = []
        
        # Apply the selected strategy to find links
        if strategy == LinkingStrategy.EXACT_MATCH:
            links = self._link_by_exact_match(code_element, candidates)
        elif strategy == LinkingStrategy.SEMANTIC_SIMILARITY:
            links = self._link_by_semantic_similarity(code_element, candidates)
        elif strategy == LinkingStrategy.PATTERN_MATCHING:
            links = self._link_by_pattern_matching(code_element, candidates)
        elif strategy == LinkingStrategy.TYPE_BASED:
            links = self._link_by_type(code_element, candidates)
        elif strategy == LinkingStrategy.CONTEXT_BASED:
            links = self._link_by_context(code_element, candidates)
        elif strategy == LinkingStrategy.HYBRID:
            # Combine multiple strategies
            exact_links = self._link_by_exact_match(code_element, candidates)
            semantic_links = self._link_by_semantic_similarity(code_element, candidates)
            pattern_links = self._link_by_pattern_matching(code_element, candidates)
            type_links = self._link_by_type(code_element, candidates)
            
            # Combine and deduplicate links
            all_links = exact_links + semantic_links + pattern_links + type_links
            links = self._deduplicate_links(all_links)
        
        # Filter by confidence threshold
        return [link for link in links if link.confidence >= self.min_confidence]
    
    def _find_candidate_entities(
        self, 
        name: str, 
        element_type: Optional[str] = None
    ) -> List[KnowledgeEntity]:
        """
        Find candidate entities in the knowledge graph.
        
        Args:
            name: Name of the code element
            element_type: Type of the code element
            
        Returns:
            List of candidate entities
        """
        # Check cache first
        cache_key = f"{name}:{element_type or 'any'}"
        if cache_key in self.entity_cache:
            return self.entity_cache[cache_key]
            
        # Query candidates from knowledge graph
        query = {}
        
        if element_type:
            # Use structured query with type
            query = {
                "name_similar_to": name,
                "type": self._map_code_type_to_entity_type(element_type)
            }
        else:
            # Use name-based query
            query = {
                "name_similar_to": name
            }
            
        results = self.connector.query_knowledge_graph(query)
        
        # Convert results to entities
        candidates = []
        for result in results:
            entity_id = result.get("id")
            if entity_id:
                # Get full entity if available
                entity = self.connector.entities.get(entity_id)
                if entity:
                    candidates.append(entity)
                else:
                    # Create entity from result
                    entity = KnowledgeEntity(
                        entity_id=entity_id,
                        entity_type=result.get("type", "concept"),
                        properties={
                            "name": result.get("name", name),
                            "match_score": result.get("match_score", 0.0)
                        }
                    )
                    candidates.append(entity)
        
        # Cache results
        self.entity_cache[cache_key] = candidates
        
        return candidates
    
    def _map_code_type_to_entity_type(self, code_type: str) -> str:
        """Map code element type to knowledge entity type."""
        mapping = {
            "function": "Function",
            "method": "Method",
            "class": "Class",
            "module": "Module",
            "variable": "Variable",
            "parameter": "Parameter",
            "type": "Type",
            "interface": "Interface",
            # Add more mappings as needed
        }
        
        return mapping.get(code_type.lower(), "Concept")
    
    def _link_by_exact_match(
        self,
        code_element: Dict[str, Any],
        candidates: List[KnowledgeEntity]
    ) -> List[SemanticLink]:
        """Link by exact name matching."""
        links = []
        element_id = code_element.get('id')
        name = code_element.get('name').lower()
        
        for entity in candidates:
            entity_name = entity.properties.get('name', '').lower()
            
            if name == entity_name:
                # Exact match
                links.append(SemanticLink(
                    code_element_id=element_id,
                    entity_id=entity.entity_id,
                    link_type="exact_match",
                    confidence=LinkConfidence.DEFINITE.value,
                    strategy=LinkingStrategy.EXACT_MATCH,
                    metadata={"match_type": "exact"}
                ))
            elif name in entity_name or entity_name in name:
                # Partial match
                confidence = 0.7 if name in entity_name else 0.6
                links.append(SemanticLink(
                    code_element_id=element_id,
                    entity_id=entity.entity_id,
                    link_type="similar_to",
                    confidence=confidence,
                    strategy=LinkingStrategy.EXACT_MATCH,
                    metadata={"match_type": "partial"}
                ))
                
        return links
    
    def _link_by_semantic_similarity(
        self,
        code_element: Dict[str, Any],
        candidates: List[KnowledgeEntity]
    ) -> List[SemanticLink]:
        """Link by semantic similarity using embeddings."""
        if not self.embedding_provider:
            return []
            
        links = []
        element_id = code_element.get('id')
        name = code_element.get('name')
        description = code_element.get('description', '')
        
        # Generate an embedding for the code element
        element_text = f"{name}: {description}" if description else name
        try:
            element_embedding = self._get_embedding(element_text)
            
            for entity in candidates:
                entity_name = entity.properties.get('name', '')
                entity_desc = entity.properties.get('description', '')
                
                entity_text = f"{entity_name}: {entity_desc}" if entity_desc else entity_name
                entity_embedding = self._get_embedding(entity_text)
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(element_embedding, entity_embedding)
                
                # Determine confidence and link type based on similarity
                if similarity > 0.9:
                    confidence = LinkConfidence.DEFINITE.value
                    link_type = "semantically_equivalent"
                elif similarity > 0.75:
                    confidence = LinkConfidence.HIGH.value
                    link_type = "strongly_related"
                elif similarity > 0.6:
                    confidence = LinkConfidence.MEDIUM.value
                    link_type = "related"
                else:
                    confidence = LinkConfidence.LOW.value
                    link_type = "weakly_related"
                
                links.append(SemanticLink(
                    code_element_id=element_id,
                    entity_id=entity.entity_id,
                    link_type=link_type,
                    confidence=confidence,
                    strategy=LinkingStrategy.SEMANTIC_SIMILARITY,
                    metadata={"similarity": similarity}
                ))
        except Exception as e:
            print(f"Error calculating semantic similarity: {e}")
            
        return links
    
    def _link_by_pattern_matching(
        self,
        code_element: Dict[str, Any],
        candidates: List[KnowledgeEntity]
    ) -> List[SemanticLink]:
        """Link by pattern matching in names and descriptions."""
        links = []
        element_id = code_element.get('id')
        name = code_element.get('name').lower()
        description = code_element.get('description', '').lower()
        
        # Extract keywords from name
        keywords = self._extract_keywords(name)
        
        for entity in candidates:
            entity_name = entity.properties.get('name', '').lower()
            entity_desc = entity.properties.get('description', '').lower()
            
            # Extract entity keywords
            entity_keywords = self._extract_keywords(entity_name)
            
            # Calculate keyword overlap
            shared_keywords = keywords.intersection(entity_keywords)
            
            if shared_keywords:
                # Determine confidence based on overlap
                overlap_ratio = len(shared_keywords) / max(len(keywords), len(entity_keywords))
                
                if overlap_ratio > 0.8:
                    confidence = LinkConfidence.HIGH.value
                elif overlap_ratio > 0.5:
                    confidence = LinkConfidence.MEDIUM.value
                else:
                    confidence = LinkConfidence.LOW.value
                
                links.append(SemanticLink(
                    code_element_id=element_id,
                    entity_id=entity.entity_id,
                    link_type="shares_keywords",
                    confidence=confidence,
                    strategy=LinkingStrategy.PATTERN_MATCHING,
                    metadata={
                        "shared_keywords": list(shared_keywords),
                        "overlap_ratio": overlap_ratio
                    }
                ))
                
            # Pattern-based checks in description
            if description and entity_desc:
                # Check if entity name appears in code description
                if entity_name in description:
                    links.append(SemanticLink(
                        code_element_id=element_id,
                        entity_id=entity.entity_id,
                        link_type="references",
                        confidence=LinkConfidence.HIGH.value,
                        strategy=LinkingStrategy.PATTERN_MATCHING,
                        metadata={"match_location": "description"}
                    ))
                
                # Check if code name appears in entity description
                if name in entity_desc:
                    links.append(SemanticLink(
                        code_element_id=element_id,
                        entity_id=entity.entity_id,
                        link_type="referenced_by",
                        confidence=LinkConfidence.MEDIUM.value,
                        strategy=LinkingStrategy.PATTERN_MATCHING,
                        metadata={"match_location": "entity_description"}
                    ))
                
        return links
    
    def _link_by_type(
        self,
        code_element: Dict[str, Any],
        candidates: List[KnowledgeEntity]
    ) -> List[SemanticLink]:
        """Link based on type compatibility."""
        links = []
        element_id = code_element.get('id')
        element_type = code_element.get('type')
        
        if not element_type:
            return links
            
        mapped_type = self._map_code_type_to_entity_type(element_type)
        
        for entity in candidates:
            entity_type = entity.entity_type
            
            # Check for type compatibility
            if entity_type == mapped_type:
                links.append(SemanticLink(
                    code_element_id=element_id,
                    entity_id=entity.entity_id,
                    link_type="same_type",
                    confidence=LinkConfidence.HIGH.value,
                    strategy=LinkingStrategy.TYPE_BASED,
                    metadata={"type": mapped_type}
                ))
            elif self._are_types_related(mapped_type, entity_type):
                links.append(SemanticLink(
                    code_element_id=element_id,
                    entity_id=entity.entity_id,
                    link_type="related_type",
                    confidence=LinkConfidence.MEDIUM.value,
                    strategy=LinkingStrategy.TYPE_BASED,
                    metadata={
                        "code_type": mapped_type,
                        "entity_type": entity_type
                    }
                ))
                
        return links
    
    def _link_by_context(
        self,
        code_element: Dict[str, Any],
        candidates: List[KnowledgeEntity]
    ) -> List[SemanticLink]:
        """Link based on contextual information."""
        links = []
        element_id = code_element.get('id')
        context = code_element.get('context', {})
        
        if not context:
            return links
            
        # Extract useful context
        module = context.get('module')
        parent = context.get('parent')
        imports = context.get('imports', [])
        neighbors = context.get('neighbors', [])
        
        for entity in candidates:
            entity_id = entity.entity_id
            
            # Check if entity is related to the module
            if module and module.lower() in entity.entity_id.lower():
                links.append(SemanticLink(
                    code_element_id=element_id,
                    entity_id=entity_id,
                    link_type="belongs_to",
                    confidence=LinkConfidence.MEDIUM.value,
                    strategy=LinkingStrategy.CONTEXT_BASED,
                    metadata={"context_type": "module"}
                ))
            
            # Check if entity is related to parent
            if parent and parent.lower() in entity.entity_id.lower():
                links.append(SemanticLink(
                    code_element_id=element_id,
                    entity_id=entity_id,
                    link_type="part_of",
                    confidence=LinkConfidence.MEDIUM.value,
                    strategy=LinkingStrategy.CONTEXT_BASED,
                    metadata={"context_type": "parent"}
                ))
            
            # Check imports
            for imp in imports:
                if imp.lower() in entity.entity_id.lower():
                    links.append(SemanticLink(
                        code_element_id=element_id,
                        entity_id=entity_id,
                        link_type="uses",
                        confidence=LinkConfidence.MEDIUM.value,
                        strategy=LinkingStrategy.CONTEXT_BASED,
                        metadata={"context_type": "import"}
                    ))
            
            # Check neighbors
            for neighbor in neighbors:
                if neighbor.lower() in entity.entity_id.lower():
                    links.append(SemanticLink(
                        code_element_id=element_id,
                        entity_id=entity_id,
                        link_type="related_to",
                        confidence=LinkConfidence.LOW.value,
                        strategy=LinkingStrategy.CONTEXT_BASED,
                        metadata={"context_type": "neighbor"}
                    ))
                    
        return links
    
    def _deduplicate_links(self, links: List[SemanticLink]) -> List[SemanticLink]:
        """Deduplicate links, keeping the highest confidence link for each entity."""
        # Group by entity ID
        grouped = {}
        for link in links:
            if link.entity_id not in grouped or grouped[link.entity_id].confidence < link.confidence:
                grouped[link.entity_id] = link
                
        return list(grouped.values())
    
    def _are_types_related(self, type1: str, type2: str) -> bool:
        """Check if two types are related."""
        # Type hierarchy and relations
        type_relations = {
            "Function": ["Method", "Procedure", "Algorithm"],
            "Class": ["Type", "Interface", "AbstractClass"],
            "Module": ["Package", "Library", "Framework"],
            "Variable": ["Parameter", "Property", "Field"],
            # Add more relations as needed
        }
        
        # Check both directions
        return type2 in type_relations.get(type1, []) or type1 in type_relations.get(type2, [])
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text by splitting camelCase, snake_case, etc."""
        # Split camelCase
        camel_words = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', text)
        
        # Split snake_case
        snake_words = []
        for word in text.split('_'):
            if word:
                snake_words.append(word)
                
        # Combine and lowercase all words
        all_words = set()
        for word in camel_words + snake_words:
            all_words.add(word.lower())
            
        return all_words
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get an embedding for text, with caching."""
        if not text:
            return []
            
        # Check cache
        if text in self.embedding_cache:
            return self.embedding_cache[text]
            
        # Generate embedding using provider
        try:
            embedding = self.embedding_provider.get_embedding(text)
            self.embedding_cache[text] = embedding
            return embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
            
        # Convert to numpy arrays for efficient calculation
        a = np.array(vec1)
        b = np.array(vec2)
        
        # Calculate cosine similarity
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)


class BatchLinker:
    """Handles batch linking of code elements to knowledge entities."""
    
    def __init__(self, linker: SemanticLinker):
        """
        Initialize the batch linker.
        
        Args:
            linker: The semantic linker to use for individual linking
        """
        self.linker = linker
        self.connector = linker.connector
    
    def link_batch(
        self,
        code_elements: List[Dict[str, Any]],
        strategy: Optional[LinkingStrategy] = None
    ) -> List[SemanticLink]:
        """
        Link a batch of code elements to knowledge entities.
        
        Args:
            code_elements: List of code elements to link
            strategy: Linking strategy to use
            
        Returns:
            List of semantic links
        """
        all_links = []
        
        # Pre-cache candidates for all elements
        unique_names = {element.get('name', '') for element in code_elements}
        candidates_map = {}
        
        for name in unique_names:
            if name:
                candidates = self.linker._find_candidate_entities(name)
                candidates_map[name] = candidates
        
        # Link each code element
        for element in code_elements:
            name = element.get('name', '')
            if not name:
                continue
                
            candidates = candidates_map.get(name, [])
            links = self.linker.link_code_element(
                element, 
                candidates=candidates,
                strategy=strategy
            )
            
            all_links.extend(links)
        
        return all_links
    
    def link_codebase(
        self,
        code_elements: List[Dict[str, Any]],
        strategy: Optional[LinkingStrategy] = None,
        batch_size: int = 100
    ) -> List[SemanticLink]:
        """
        Link an entire codebase to knowledge entities.
        
        Args:
            code_elements: List of all code elements in the codebase
            strategy: Linking strategy to use
            batch_size: Size of batches for processing
            
        Returns:
            List of semantic links
        """
        all_links = []
        
        # Process in batches
        for i in range(0, len(code_elements), batch_size):
            batch = code_elements[i:i + batch_size]
            batch_links = self.link_batch(batch, strategy)
            all_links.extend(batch_links)
            
            # Print progress
            progress = min(100, 100 * (i + len(batch)) / len(code_elements))
            print(f"Linking progress: {progress:.1f}% ({len(all_links)} links found)")
        
        return all_links
    
    def store_links(self, links: List[SemanticLink]) -> int:
        """
        Store semantic links in the knowledge graph.
        
        Args:
            links: List of semantic links to store
            
        Returns:
            Number of successfully stored links
        """
        success_count = 0
        
        for link in links:
            triple = link.to_triple()
            if self.connector.store_triple(triple):
                success_count += 1
                
        return success_count 