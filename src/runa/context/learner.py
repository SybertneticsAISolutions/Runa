"""
Precedent-based learning for context-aware interpretation.

This module provides classes and functions for learning from past
disambiguation decisions to improve future interpretations.
"""
import json
import os
import copy
from collections import defaultdict
from src.runa.context.embeddings import get_embedding, get_similarity


class PrecedentLearner:
    """
    Class for learning from past interpretation decisions.
    """

    def __init__(self, persistence_file=None):
        """
        Initialize a precedent learner.

        Args:
            persistence_file: Optional file path for saving/loading learned precedents
        """
        self.persistence_file = persistence_file

        # Dictionary to store variable disambiguation precedents
        # Key: variable name, Value: list of (context, chosen_candidate) pairs
        self.variable_precedents = defaultdict(list)

        # Dictionary to store function disambiguation precedents
        # Key: function name, Value: list of (context, chosen_candidate) pairs
        self.function_precedents = defaultdict(list)

        # Dictionary to store syntax disambiguation precedents
        # Key: partial statement pattern, Value: list of (context, chosen_completion) pairs
        self.syntax_precedents = defaultdict(list)

        # Load previous precedents if available
        if persistence_file and os.path.exists(persistence_file):
            self.load_precedents()

    def learn_variable_disambiguation(self, name, candidates, chosen_candidate, context):
        """
        Learn from a variable disambiguation decision.

        Args:
            name: The variable name
            candidates: The list of candidate interpretations
            chosen_candidate: The chosen interpretation
            context: The context in which the decision was made
        """
        # Create a simplified context representation
        context_repr = " ".join(context[-3:]) if context else ""

        # Create a deep copy of the chosen candidate to avoid reference issues
        chosen_copy = copy.deepcopy(chosen_candidate)

        # Add to precedents
        self.variable_precedents[name].append((context_repr, chosen_copy))

        # Save precedents if persistence is enabled
        if self.persistence_file:
            self.save_precedents()

    def learn_function_disambiguation(self, name, candidates, chosen_candidate, context):
        """
        Learn from a function disambiguation decision.

        Args:
            name: The function name
            candidates: The list of candidate interpretations
            chosen_candidate: The chosen interpretation
            context: The context in which the decision was made
        """
        # Create a simplified context representation
        context_repr = " ".join(context[-3:]) if context else ""

        # Create a deep copy of the chosen candidate to avoid reference issues
        chosen_copy = copy.deepcopy(chosen_candidate)

        # Add to precedents
        self.function_precedents[name].append((context_repr, chosen_copy))

        # Save precedents if persistence is enabled
        if self.persistence_file:
            self.save_precedents()

    def learn_syntax_disambiguation(self, partial_statement, completions, chosen_completion, context):
        """
        Learn from a syntax disambiguation decision.

        Args:
            partial_statement: The partial or ambiguous statement
            completions: The list of possible completions
            chosen_completion: The chosen completion
            context: The context in which the decision was made
        """
        # Create a simplified context representation
        context_repr = " ".join(context[-3:]) if context else ""

        # Simplify the partial statement to a pattern
        pattern = self._simplify_to_pattern(partial_statement)

        # Add to precedents
        self.syntax_precedents[pattern].append((context_repr, chosen_completion))

        # Save precedents if persistence is enabled
        if self.persistence_file:
            self.save_precedents()

    def suggest_variable_disambiguation(self, name, candidates, current_context):
        """
        Suggest a disambiguation for a variable based on precedents.

        Args:
            name: The variable name
            candidates: The list of candidate interpretations
            current_context: The current context

        Returns:
            The suggested candidate, or None if no suggestion can be made
        """
        # Check if we have precedents for this variable
        if name not in self.variable_precedents or not self.variable_precedents[name]:
            return None

        # Create a simplified context representation
        context_repr = " ".join(current_context[-3:]) if current_context else ""

        # Find the most similar precedent
        best_similarity = -1
        best_suggestion = None

        for prec_context, prec_candidate in self.variable_precedents[name]:
            similarity = get_similarity(context_repr, prec_context)

            if similarity > best_similarity:
                best_similarity = similarity
                best_suggestion = prec_candidate

        # Only suggest if similarity is high enough
        if best_similarity > 0.6:
            return best_suggestion

        return None

    def suggest_function_disambiguation(self, name, candidates, current_context, args=None):
        """
        Suggest a disambiguation for a function based on precedents.

        Args:
            name: The function name
            candidates: The list of candidate interpretations
            current_context: The current context
            args: Optional list of argument types

        Returns:
            The suggested candidate, or None if no suggestion can be made
        """
        # Check if we have precedents for this function
        if name not in self.function_precedents or not self.function_precedents[name]:
            return None

        # Create a simplified context representation
        context_repr = " ".join(current_context[-3:]) if current_context else ""

        # Find the most similar precedent
        best_similarity = -1
        best_suggestion = None

        for prec_context, prec_candidate in self.function_precedents[name]:
            similarity = get_similarity(context_repr, prec_context)

            # If we have args, adjust similarity based on parameter match
            if args and 'parameters' in prec_candidate:
                param_match = self._parameter_match_score(args, prec_candidate['parameters'])
                similarity = (similarity + param_match) / 2

            if similarity > best_similarity:
                best_similarity = similarity
                best_suggestion = prec_candidate

        # Only suggest if similarity is high enough
        if best_similarity > 0.6:
            return best_suggestion

        return None

    def suggest_syntax_disambiguation(self, partial_statement, completions):
        """
        Suggest a disambiguation for syntax based on precedents.

        Args:
            partial_statement: The partial or ambiguous statement
            completions: The list of possible completions

        Returns:
            The suggested completion, or None if no suggestion can be made
        """
        # Simplify the partial statement to a pattern
        pattern = self._simplify_to_pattern(partial_statement)

        # Check if we have precedents for this pattern
        if pattern not in self.syntax_precedents or not self.syntax_precedents[pattern]:
            return None

        # Count occurrences of each completion
        completion_counts = defaultdict(int)

        for _, completion in self.syntax_precedents[pattern]:
            # Find the most similar completion in the current list
            best_match = None
            best_match_similarity = -1

            for curr_completion in completions:
                similarity = get_similarity(completion, curr_completion)
                if similarity > best_match_similarity:
                    best_match_similarity = similarity
                    best_match = curr_completion

            # Only count if we found a good match
            if best_match_similarity > 0.7:
                completion_counts[best_match] += 1

        # If we have counts, return the most frequent completion
        if completion_counts:
            return max(completion_counts.items(), key=lambda x: x[1])[0]

        return None

    def save_precedents(self):
        """Save learned precedents to the persistence file."""
        if not self.persistence_file:
            return

        # Prepare data for serialization
        precedents_data = {
            'variables': {k: [(c, self._make_serializable(v)) for c, v in vs]
                          for k, vs in self.variable_precedents.items()},
            'functions': {k: [(c, self._make_serializable(v)) for c, v in fs]
                          for k, fs in self.function_precedents.items()},
            'syntax': dict(self.syntax_precedents)
        }

        # Save to file
        with open(self.persistence_file, 'w') as f:
            json.dump(precedents_data, f, indent=2)

    def load_precedents(self):
        """Load learned precedents from the persistence file."""
        if not self.persistence_file or not os.path.exists(self.persistence_file):
            return

        try:
            # Load from file
            with open(self.persistence_file, 'r') as f:
                precedents_data = json.load(f)

            # Restore variable precedents
            if 'variables' in precedents_data:
                for var_name, precedents in precedents_data['variables'].items():
                    self.variable_precedents[var_name] = [(c, v) for c, v in precedents]

            # Restore function precedents
            if 'functions' in precedents_data:
                for func_name, precedents in precedents_data['functions'].items():
                    self.function_precedents[func_name] = [(c, v) for c, v in precedents]

            # Restore syntax precedents
            if 'syntax' in precedents_data:
                for pattern, precedents in precedents_data['syntax'].items():
                    self.syntax_precedents[pattern] = precedents

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading precedents: {e}")

    def _simplify_to_pattern(self, statement):
        """
        Simplify a statement to a pattern for syntax precedent matching.

        Args:
            statement: The statement to simplify

        Returns:
            A simplified pattern
        """
        # Replace specific identifiers with placeholders
        import re

        # Replace string literals
        pattern = re.sub(r'\"[^\"]*\"', '"STRING"', statement)
        pattern = re.sub(r'\'[^\']*\'', "'STRING'", pattern)

        # Replace number literals
        pattern = re.sub(r'\b\d+\b', 'NUMBER', pattern)

        # Replace specific identifiers if not at the beginning of a token
        tokens = re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*|\S', pattern)

        # Keep common keywords and operators
        keywords = {'Let', 'Set', 'If', 'Otherwise', 'For', 'each', 'in', 'Return',
                    'Process', 'called', 'that', 'takes', 'with', 'as', 'and',
                    'is', 'equal', 'to', 'not', 'plus', 'minus', 'multiplied', 'divided',
                    'be', 'Display', 'Import', 'Module', 'Match', 'When'}

        # Replace specific identifiers but keep structure
        simplified_tokens = []
        for token in tokens:
            if token in keywords or len(token) == 1:
                simplified_tokens.append(token)
            elif re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', token):
                simplified_tokens.append('IDENTIFIER')
            else:
                simplified_tokens.append(token)

        return ' '.join(simplified_tokens)

    def _parameter_match_score(self, args, parameters):
        """
        Calculate a score for how well argument types match parameter types.

        Args:
            args: List of argument types
            parameters: List of parameter types

        Returns:
            A match score between 0 and 1
        """
        if len(args) != len(parameters):
            return 0.0

        if not args:
            return 1.0

        # Count matching parameters
        matches = sum(1 for a, p in zip(args, parameters) if a == p or a == "Any" or p == "Any")

        return matches / len(args)

    def _make_serializable(self, obj):
        """
        Make an object serializable by converting it to a simple dict.

        Args:
            obj: The object to make serializable

        Returns:
            A serializable representation of the object
        """
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(v) for v in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            # For custom objects, convert to dict
            return {k: self._make_serializable(v) for k, v in obj.__dict__.items()
                    if not k.startswith('_')}