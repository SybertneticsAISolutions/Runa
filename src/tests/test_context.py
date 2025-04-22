"""
Tests for the context-aware interpretation system.
"""
import pytest
import os
import numpy as np
from src.runa.parser import RunaParser
from src.runa.context import integrate_context_awareness
from src.runa.context.embeddings import get_embedding, get_similarity, get_most_similar
from src.runa.context.disambiguator import Disambiguator
from src.runa.context.learner import PrecedentLearner


def test_embeddings():
    """Test the vector embeddings functionality."""
    # Test embedding generation
    code1 = "Let x be 10"
    embedding1 = get_embedding(code1)

    # Check that embedding is a numpy array
    assert isinstance(embedding1, np.ndarray)

    # Check that embedding has the expected shape
    assert embedding1.shape[0] > 0

    # Check that the same code produces the same embedding
    embedding2 = get_embedding(code1)
    assert np.array_equal(embedding1, embedding2)

    # Check that different code produces different embeddings
    code2 = "Set x to 20"
    embedding3 = get_embedding(code2)
    assert not np.array_equal(embedding1, embedding3)

    # Test similarity calculation
    similarity = get_similarity(code1, code2)
    assert 0 <= similarity <= 1

    # Check that identical code has perfect similarity
    identical_similarity = get_similarity(code1, code1)
    assert identical_similarity == 1.0

    # Test most similar function
    candidates = ["Let y be 10", "Set x to 20", "Let z be 30"]
    most_similar, similarity = get_most_similar(code1, candidates)
    assert most_similar == "Let y be 10"


def test_disambiguator():
    """Test the disambiguation system."""
    # Create a disambiguator without a learner
    disambiguator = Disambiguator()

    # Test variable disambiguation
    name = "x"
    candidates = [
        {"name": "x", "type": "Integer", "scope": "global"},
        {"name": "x", "type": "String", "scope": "local"}
    ]
    current_statement = "Set x to 10"

    # Add some context
    disambiguator.add_to_context("Let x be 5")
    disambiguator.add_to_context("Set x to x plus 1")

    # Disambiguate variable
    result = disambiguator.disambiguate_variable(name, candidates, current_statement)

    # Should return the first candidate as default
    assert result == candidates[0]

    # Test function disambiguation
    name = "calculate"
    candidates = [
        {"name": "calculate", "parameters": ["Integer", "Integer"], "return_type": "Integer"},
        {"name": "calculate", "parameters": ["String", "String"], "return_type": "String"}
    ]
    current_statement = "calculate with num1 as 5 and num2 as 10"

    # Add some context
    disambiguator.add_to_context("Process called \"calculate\" that takes a and b")
    disambiguator.add_to_context("Return a plus b")

    # Disambiguate function
    result = disambiguator.disambiguate_function(name, candidates, current_statement)

    # Should return the first candidate as default
    assert result == candidates[0]

    # Test syntax disambiguation
    partial_statement = "Let x be"
    possible_completions = ["Let x be 10", "Let x be \"hello\"", "Let x be true"]

    # Disambiguate syntax
    result = disambiguator.disambiguate_syntax(partial_statement, possible_completions)

    # Should return one of the completions
    assert result in possible_completions


def test_precedent_learner():
    """Test the precedent-based learning system."""
    # Create a temporary file for persistence
    temp_file = "temp_precedents.json"

    # Create a learner
    learner = PrecedentLearner(persistence_file=temp_file)

    # Test variable disambiguation learning
    name = "x"
    candidates = [
        {"name": "x", "type": "Integer", "scope": "global"},
        {"name": "x", "type": "String", "scope": "local"}
    ]
    chosen_candidate = candidates[1]
    context = ["Let x be \"hello\"", "Display x"]

    # Learn from a decision
    learner.learn_variable_disambiguation(name, candidates, chosen_candidate, context)

    # Check that the precedent was stored
    assert name in learner.variable_precedents
    assert len(learner.variable_precedents[name]) == 1

    # Save and load precedents
    learner.save_precedents()

    new_learner = PrecedentLearner(persistence_file=temp_file)
    new_learner.load_precedents()

    # Check that the precedent was loaded
    assert name in new_learner.variable_precedents
    assert len(new_learner.variable_precedents[name]) == 1

    # Cleanup
    if os.path.exists(temp_file):
        os.remove(temp_file)


def test_context_aware_parser():
    """Test the context-aware parser."""
    # Create a context-aware parser
    parser_class = RunaParser
    context_aware_parser_class = integrate_context_awareness(parser_class)

    # Create an instance of the context-aware parser
    parser = context_aware_parser_class()

    # Parse a simple program
    source = """
    Let x be 10
    Let y be 20
    Set x to x plus y
    Display x
    """

    # Parse the program
    ast = parser.parse(source)

    # Check that the AST was created
    assert ast is not None

    # Check that statements were tracked in the context
    assert len(parser.disambiguator.context_history) > 0
    assert len(parser.disambiguator.global_context) > 0