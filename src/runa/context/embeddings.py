"""
Vector embeddings for code semantics.

This module provides functions for converting code snippets and
concepts into vector embeddings for semantic analysis.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re

# Initialize TF-IDF vectorizer for preprocessing
_vectorizer = TfidfVectorizer(
    analyzer='word',
    token_pattern=r'[a-zA-Z_][a-zA-Z0-9_]*|[+\-*/]|[<>=!]=?|[(){}\[\],.]|\'[^\']*\'|\"[^\"]*\"',
    lowercase=True,
    max_features=1000
)

# Common code samples to build the vocabulary
_common_samples = [
    "Let x be 10",
    "Set x to 20",
    "Process called \"add\" that takes a and b",
    "Return a plus b",
    "If condition is true",
    "For each item in items",
    "Match value",
    "When pattern",
    "Display message"
]

# Pre-fit the vectorizer with common code samples
_vectorizer.fit(_common_samples)

# In-memory cache for embeddings to avoid recomputation
_embedding_cache = {}


def _preprocess_code(code):
    """
    Preprocess code for embedding.

    Args:
        code: The code string to preprocess

    Returns:
        The preprocessed code
    """
    # Remove comments
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)

    # Normalize whitespace
    code = re.sub(r'\s+', ' ', code).strip()

    return code


def get_embedding(code):
    """
    Get vector embedding for a code snippet.

    Args:
        code: The code snippet to embed

    Returns:
        A numpy array containing the embedding vector
    """
    # Check cache first
    if code in _embedding_cache:
        return _embedding_cache[code]

    # Preprocess the code
    preprocessed = _preprocess_code(code)

    # Create embedding using TF-IDF
    tfidf_vector = _vectorizer.transform([preprocessed])

    # Convert to dense numpy array
    embedding = tfidf_vector.toarray()[0]

    # Normalize the vector
    norm = np.linalg.norm(embedding)
    if norm > 0:
        embedding = embedding / norm

    # Cache the result
    _embedding_cache[code] = embedding

    return embedding


def get_similarity(code1, code2):
    """
    Calculate semantic similarity between two code snippets.

    Args:
        code1: First code snippet
        code2: Second code snippet

    Returns:
        A float value between 0 and 1, where higher values indicate greater similarity
    """
    # Get embeddings
    embedding1 = get_embedding(code1)
    embedding2 = get_embedding(code2)

    # Calculate cosine similarity
    similarity = np.dot(embedding1, embedding2)

    # Ensure the similarity is between 0 and 1
    similarity = max(0, min(1, similarity))

    return similarity


def get_most_similar(code, candidates):
    """
    Find the most semantically similar candidate to the given code.

    Args:
        code: The reference code snippet
        candidates: A list of candidate code snippets

    Returns:
        The most similar candidate and its similarity score
    """
    if not candidates:
        return None, 0.0

    # Calculate similarity scores
    similarities = [(candidate, get_similarity(code, candidate)) for candidate in candidates]

    # Find the candidate with the highest similarity
    most_similar_candidate, highest_similarity = max(similarities, key=lambda x: x[1])

    return most_similar_candidate, highest_similarity