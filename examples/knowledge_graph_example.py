#!/usr/bin/env python3
"""
Knowledge Graph Connectivity Example for Runa

This example demonstrates how to use the knowledge graph connectors
to interact with knowledge graphs from Runa code.
"""

import os
import sys
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.runa.ai.knowledge import (
    KnowledgeEntity, KnowledgeTriple, KnowledgeGraphConnector
)
from src.runa.ai.knowledge_connectors import (
    RDFConnector, create_connector, get_connector_for_uri
)
from src.runa.annotation_system import (
    KnowledgeAnnotation, AnnotationType, AnnotationParser, AnnotationGenerator
)


def create_sample_knowledge():
    """Create sample knowledge entities and triples."""
    entities = [
        KnowledgeEntity(
            entity_id="algorithm:quicksort",
            entity_type="Algorithm",
            properties={
                "name": "QuickSort",
                "description": "A divide-and-conquer sorting algorithm",
                "complexity": "O(n log n) average case"
            }
        ),
        KnowledgeEntity(
            entity_id="algorithm:mergesort",
            entity_type="Algorithm",
            properties={
                "name": "MergeSort",
                "description": "A divide-and-conquer sorting algorithm that always has O(n log n) complexity",
                "complexity": "O(n log n)"
            }
        ),
        KnowledgeEntity(
            entity_id="concept:divide_and_conquer",
            entity_type="Concept",
            properties={
                "name": "Divide and Conquer",
                "description": "A problem-solving approach that breaks a problem into smaller subproblems"
            }
        ),
        KnowledgeEntity(
            entity_id="paradigm:functional_programming",
            entity_type="ProgrammingParadigm",
            properties={
                "name": "Functional Programming",
                "description": "A programming paradigm that treats computation as the evaluation of mathematical functions"
            }
        )
    ]
    
    triples = [
        KnowledgeTriple(
            subject_id="algorithm:quicksort",
            predicate="uses",
            object_id="concept:divide_and_conquer"
        ),
        KnowledgeTriple(
            subject_id="algorithm:mergesort",
            predicate="uses",
            object_id="concept:divide_and_conquer"
        ),
        KnowledgeTriple(
            subject_id="algorithm:quicksort",
            predicate="has_property",
            object_id="property:in_place",
            confidence=0.9,
            metadata={"context": "typical implementations"}
        ),
        KnowledgeTriple(
            subject_id="algorithm:mergesort",
            predicate="compatible_with",
            object_id="paradigm:functional_programming",
            confidence=1.0
        )
    ]
    
    return entities, triples


def demonstate_rdf_connector():
    """Demonstrate use of the RDF connector."""
    print("\n--- RDF Connector Example ---")
    
    # Create an RDF connector
    connector = RDFConnector()
    print("Created RDF connector")
    
    # Add a custom namespace
    connector.add_namespace("alg", "http://example.org/algorithms#")
    
    # Connect to the graph (in-memory for this example)
    connected = connector.connect()
    if connected:
        print("Connected to in-memory RDF graph")
    
    # Create sample knowledge
    entities, triples = create_sample_knowledge()
    
    # Import knowledge
    imported = connector.import_knowledge(entities, triples)
    if imported:
        print(f"Imported {len(entities)} entities and {len(triples)} triples")
    
    # Query all sorting algorithms
    print("\nSPARQL Query Results (All Algorithms):")
    results = connector.query_knowledge_graph("""
        SELECT ?entity ?name ?description
        WHERE {
            ?entity rdf:type <http://runa-lang.org/ontology#Algorithm> .
            ?entity <http://runa-lang.org/ontology#name> ?name .
            ?entity <http://runa-lang.org/ontology#description> ?description .
        }
    """, "sparql")
    
    for result in results:
        print(f"- {result['name']}: {result['description']}")
    
    # Use structured query to find algorithms using divide and conquer
    print("\nStructured Query Results (Algorithms using Divide and Conquer):")
    subject_results = connector.query_knowledge_graph({
        "subject": "concept:divide_and_conquer"
    })
    
    for algorithm in subject_results:
        if algorithm["predicate"] == "uses":
            print(f"- {algorithm['object']} uses divide and conquer")
    
    # Save the graph to a file
    file_path = os.path.join(os.path.dirname(__file__), "knowledge_graph.ttl")
    saved = connector.save_to_file(file_path)
    if saved:
        print(f"\nSaved RDF graph to {file_path}")
    
    return file_path


def demonstrate_factory():
    """Demonstrate use of the connector factory."""
    print("\n--- Connector Factory Example ---")
    
    # Create different types of connectors using the factory
    rdf_connector = create_connector("rdf")
    print("Created RDF connector via factory")
    
    # Get connector based on URI
    ttl_file = "knowledge_graph.ttl"
    connector = get_connector_for_uri(ttl_file)
    print(f"Got appropriate connector for {ttl_file}: {connector.__class__.__name__}")
    
    neo4j_uri = "bolt://localhost:7687"
    connector = get_connector_for_uri(neo4j_uri)
    print(f"Got appropriate connector for {neo4j_uri}: {connector.__class__.__name__}")


def demonstrate_code_integration(ttl_file):
    """Demonstrate integration with Runa code."""
    print("\n--- Runa Code Integration Example ---")
    
    # Load the RDF graph from file
    connector = RDFConnector(graph_uri=ttl_file)
    connector.connect()
    
    # Export entities and triples
    entities, triples = connector.export_knowledge()
    print(f"Loaded {len(entities)} entities and {len(triples)} triples from file")
    
    # Runa code with knowledge annotations
    runa_code = """
# Implementation of sorting algorithms
Process called "quick_sort" that takes arr:
    # Base case
    If length of arr is less than or equal to 1:
        Return arr
    
    Let pivot be arr at index 0
    Let left be list containing
    Let right be list containing
    
    For each x in arr starting from index 1:
        If x is less than pivot:
            Add x to left
        Otherwise:
            Add x to right
    
    Return quick_sort(left) followed by list containing pivot followed by quick_sort(right)

Process called "merge_sort" that takes arr:
    # Base case
    If length of arr is less than or equal to 1:
        Return arr
    
    Let middle be length of arr divided by 2
    Let left be arr from index 0 to middle
    Let right be arr from index middle to end
    
    Let sorted_left be merge_sort with arr as left
    Let sorted_right be merge_sort with arr as right
    
    Return merge with left as sorted_left and right as sorted_right
"""
    
    # Create knowledge annotations
    annotations = []
    
    # Add annotations based on knowledge graph
    for entity in entities:
        if entity.entity_id == "algorithm:quicksort":
            annotations.append(
                KnowledgeAnnotation(
                    annotation_type=AnnotationType.KNOWLEDGE,
                    content=entity.properties.get("description", ""),
                    entity_id=entity.entity_id,
                    relation_type="implements",
                    metadata={"function": "quick_sort"}
                )
            )
        elif entity.entity_id == "algorithm:mergesort":
            annotations.append(
                KnowledgeAnnotation(
                    annotation_type=AnnotationType.KNOWLEDGE,
                    content=entity.properties.get("description", ""),
                    entity_id=entity.entity_id,
                    relation_type="implements",
                    metadata={"function": "merge_sort"}
                )
            )
    
    # Add relationship annotations
    for triple in triples:
        if triple.subject_id in ["algorithm:quicksort", "algorithm:mergesort"] and triple.predicate == "uses":
            # Get the entity for the object
            object_entity = next((e for e in entities if e.entity_id == triple.object_id), None)
            if object_entity:
                subject_name = "quick_sort" if triple.subject_id == "algorithm:quicksort" else "merge_sort"
                annotations.append(
                    KnowledgeAnnotation(
                        annotation_type=AnnotationType.KNOWLEDGE,
                        content=f"{subject_name} uses {object_entity.properties.get('name', '')}",
                        entity_id=triple.subject_id,
                        relation_type=triple.predicate,
                        metadata={"target_entity_id": triple.object_id}
                    )
                )
    
    # Generate annotated code
    generator = AnnotationGenerator()
    enhanced_code = generator.generate_annotations_for_code(runa_code, annotations)
    
    print("\nRuna Code with Knowledge Graph Annotations:")
    print("=" * 60)
    print(enhanced_code)
    print("=" * 60)
    
    # Create a file with the enhanced code
    output_file = os.path.join(os.path.dirname(__file__), "enhanced_sorting.rn")
    with open(output_file, "w") as f:
        f.write(enhanced_code)
    
    print(f"\nSaved enhanced code to {output_file}")


def main():
    """Run the knowledge graph example."""
    print("Runa Knowledge Graph Example")
    print("===========================")
    
    # Demonstrate RDF connector
    ttl_file = demonstate_rdf_connector()
    
    # Demonstrate factory
    demonstrate_factory()
    
    # Demonstrate integration with Runa code
    demonstrate_code_integration(ttl_file)
    
    print("\nExample complete!")


if __name__ == "__main__":
    main() 