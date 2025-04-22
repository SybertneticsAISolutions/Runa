#!/usr/bin/env python3
"""
AI Annotations Example for Runa

This example demonstrates the use of AI annotations and knowledge graph
connectivity features in the Runa programming language.
"""

import os
import sys
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.runa.annotation_system import (
    AnnotationParser, AnnotationAnalyzer, AnnotationGenerator,
    KnowledgeAnnotation, ReasoningAnnotation, AnnotationType
)
from src.runa.ai import (
    KnowledgeGraphConnector, RunaKnowledgeMapper, AIParser
)

# Example Runa code with AI annotations
EXAMPLE_CODE = """
# @knowledge(entity="algorithm:quicksort", relation="implements", confidence=0.95): 
# This function implements the QuickSort algorithm
Process called "quick_sort" that takes arr:
    # @reasoning(premise=["len(arr) <= 1"], conclusion="array is already sorted"): Base case check
    If length of arr is less than or equal to 1:
        Return arr
    
    # @implementation(algorithm="partition", complexity="O(n)"): Select pivot and partition
    Let pivot be arr at index 0
    Let left be list containing
    Let right be list containing
    
    # @reasoning: Elements are compared with the pivot to determine their position
    For each x in arr starting from index 1:
        If x is less than pivot:
            Add x to left
        Otherwise:
            Add x to right
    
    # @reasoning(premise=["partition complete"], conclusion="recursively sort partitions"): 
    # After partitioning, sort the sub-arrays
    # @knowledge(entity="concept:divide_and_conquer", relation="uses"): Using divide and conquer pattern
    Return quick_sort(left) followed by list containing pivot followed by quick_sort(right)

# @knowledge(entity="algorithm:merge_sort", relation="implements"): 
# Implementation of merge sort algorithm
Process called "merge_sort" that takes arr:
    # Base case
    If length of arr is less than or equal to 1:
        Return arr
    
    # @reasoning: Divide the array into two halves
    Let middle be length of arr divided by 2
    Let left be arr from index 0 to middle
    Let right be arr from index middle to end
    
    # @implementation(algorithm="recursive_merge_sort", complexity="O(n log n)"): 
    # Recursively sort and merge
    Let sorted_left be merge_sort with arr as left
    Let sorted_right be merge_sort with arr as right
    
    Return merge with left as sorted_left and right as sorted_right

# @knowledge(entity="algorithm:merge", relation="implements", entity_type="function"): 
# Helper function for merge sort
Process called "merge" that takes left and right:
    Let result be list containing
    Let i be 0
    Let j be 0
    
    # @implementation(complexity="O(n)"): Merge two sorted arrays
    While i is less than length of left and j is less than length of right:
        If left at index i is less than or equal to right at index j:
            Add left at index i to result
            Set i to i plus 1
        Otherwise:
            Add right at index j to result
            Set j to j plus 1
    
    # Add remaining elements
    While i is less than length of left:
        Add left at index i to result
        Set i to i plus 1
    
    While j is less than length of right:
        Add right at index j to result
        Set j to j plus 1
    
    Return result
"""

def main():
    """Run the AI annotations example."""
    print("Runa AI Annotations Example")
    print("=========================\n")
    
    # Parse annotations from Runa code
    print("Parsing AI annotations from code...")
    parser = AnnotationParser()
    annotations = parser.parse_annotations(EXAMPLE_CODE)
    
    print(f"Found {len(annotations)} annotations\n")
    
    # Analyze annotations
    print("Analyzing annotations...")
    analyzer = AnnotationAnalyzer()
    analysis = analyzer.analyze_annotations(annotations)
    
    print("Summary of analysis:")
    summary = analysis["summary"]
    print(f"- Total annotations: {summary['total_annotations']}")
    print(f"- Annotation types: {json.dumps(summary['annotation_type_counts'], indent=2)}")
    print(f"- Components: {', '.join(summary['components'])}\n")
    
    # Extract knowledge links
    print("Extracting knowledge links...")
    knowledge_annotations = [a for a in annotations if a.annotation_type == AnnotationType.KNOWLEDGE]
    
    print(f"Found {len(knowledge_annotations)} knowledge annotations:")
    for i, ka in enumerate(knowledge_annotations):
        print(f"{i+1}. {ka.content}")
        print(f"   Entity: {ka.entity_id}")
        if ka.relation_type:
            print(f"   Relation: {ka.relation_type}")
        print()
    
    # Create a knowledge graph connector
    print("Creating knowledge graph from annotations...")
    kg_connector = KnowledgeGraphConnector()
    entities, triples = kg_connector.code_to_knowledge(EXAMPLE_CODE)
    
    print(f"Created {len(entities)} entities and {len(triples)} triples\n")
    
    # Generate enhanced code with additional annotations
    print("Generating enhanced code...")
    mapper = RunaKnowledgeMapper(kg_connector)
    
    # Create dummy AST node for demonstration
    dummy_ast = {
        "type": "Module",
        "body": [
            {
                "type": "Process",
                "name": "quick_sort",
                "parameters": [
                    {"name": "arr", "type": None}
                ]
            },
            {
                "type": "Process",
                "name": "merge_sort",
                "parameters": [
                    {"name": "arr", "type": None}
                ]
            }
        ]
    }
    
    # Enhance with knowledge links
    ai_parser = AIParser()
    ai_annotations = ai_parser.extract_ai_annotations(EXAMPLE_CODE)
    
    print(f"Found {len(ai_annotations)} AI-specific annotations")
    
    # Generate code with annotations
    generator = AnnotationGenerator()
    enhanced_code = generator.generate_annotations_for_code(
        "# Example enhanced code\n",
        [
            KnowledgeAnnotation(
                annotation_type=AnnotationType.KNOWLEDGE,
                content="Shows relation between sorting algorithms",
                entity_id="concept:sorting_algorithms",
                relation_type="compares",
                metadata={"target_entity_id": "algorithm:quicksort"}
            ),
            ReasoningAnnotation(
                annotation_type=AnnotationType.REASONING,
                content="QuickSort is faster than MergeSort for small arrays",
                premise=["QuickSort has less overhead", "MergeSort always divides equally"],
                conclusion="Choose QuickSort for small arrays"
            )
        ]
    )
    
    print("\nEnhanced code sample:")
    print(enhanced_code)

if __name__ == "__main__":
    main() 