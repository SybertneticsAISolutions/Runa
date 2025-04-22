"""
Disambiguation system for resolving ambiguities in code interpretation.

This module provides classes and functions for resolving ambiguities
in code interpretation based on semantic similarity and context.
"""
from src.runa.context.embeddings import get_similarity, get_most_similar


class Disambiguator:
    """
    Class for resolving ambiguities in code interpretation.
    """

    def __init__(self, learner=None):
        """
        Initialize a disambiguator.

        Args:
            learner: Optional precedent learner for improving disambiguation over time
        """
        self.learner = learner
        self.context_history = []  # List of previous statements in the current scope
        self.global_context = []  # List of all statements seen so far
        self.similarity_threshold = 0.7  # Threshold for considering a match

    def add_to_context(self, statement, scope_level=0):
        """
        Add a statement to the context.

        Args:
            statement: The statement to add
            scope_level: The scope level (0 for global, >0 for nested scopes)
        """
        # Add to global context
        self.global_context.append(statement)

        # Add to current context if in the same scope
        if scope_level == 0:
            self.context_history.append(statement)

    def clear_local_context(self):
        """Clear the local context when exiting a scope."""
        self.context_history = []

    def disambiguate_variable(self, name, candidates, current_statement):
        """
        Disambiguate a variable reference.

        Args:
            name: The variable name
            candidates: List of possible variables (with scope and type information)
            current_statement: The statement containing the reference

        Returns:
            The most likely variable from the candidates
        """
        if not candidates:
            return None

        if len(candidates) == 1:
            return candidates[0]

        # Find declarations involving this variable in the context
        variable_contexts = []
        for stmt in self.context_history:
            if name in stmt:
                variable_contexts.append(stmt)

        # No relevant context found, use the most recent declaration
        if not variable_contexts:
            return candidates[0]  # Assume the first candidate is the most recent

        # Calculate similarity to each context
        weighted_scores = []
        for candidate in candidates:
            # Combine candidate's scope and type into a context representation
            candidate_info = f"Let {name} be {candidate.get('type', 'value')}"

            # Calculate similarity to each context statement
            similarities = [get_similarity(candidate_info, context) for context in variable_contexts]

            # Weight more recent contexts higher
            weighted_similarity = sum(sim * (i + 1) for i, sim in enumerate(similarities)) / sum(
                range(1, len(similarities) + 2))

            weighted_scores.append((candidate, weighted_similarity))

        # Return the candidate with the highest score
        best_candidate, _ = max(weighted_scores, key=lambda x: x[1])

        # Learn from this disambiguation if a learner is available
        if self.learner:
            self.learner.learn_variable_disambiguation(name, candidates, best_candidate, variable_contexts)

        return best_candidate

    def disambiguate_function(self, name, candidates, current_statement, args=None):
        """
        Disambiguate a function call.

        Args:
            name: The function name
            candidates: List of possible functions (with parameter and return type information)
            current_statement: The statement containing the call
            args: Optional list of argument types

        Returns:
            The most likely function from the candidates
        """
        if not candidates:
            return None

        if len(candidates) == 1:
            return candidates[0]

        # If we have argument types, filter by compatible functions
        if args:
            compatible_candidates = []
            for candidate in candidates:
                if 'parameters' in candidate:
                    # Check if the number of parameters matches
                    if len(candidate['parameters']) == len(args):
                        # Check if parameter types are compatible
                        if all(self._is_type_compatible(arg_type, param_type)
                               for arg_type, param_type in zip(args, candidate['parameters'])):
                            compatible_candidates.append(candidate)

            # If we found compatible candidates, update the candidates list
            if compatible_candidates:
                candidates = compatible_candidates

        # Find function calls in the context
        function_contexts = []
        for stmt in self.global_context:
            if name in stmt and "with" in stmt:  # Simple heuristic for function calls
                function_contexts.append(stmt)

        # No relevant context found, use the first candidate
        if not function_contexts:
            return candidates[0]

        # Calculate similarity to each context
        weighted_scores = []
        for candidate in candidates:
            # Combine candidate's parameters into a context representation
            if 'parameters' in candidate:
                param_str = " and ".join(f"{p}" for p in candidate['parameters'])
                candidate_info = f"Process called \"{name}\" that takes {param_str}"
            else:
                candidate_info = f"Process called \"{name}\""

            # Calculate similarity to each context statement
            similarities = [get_similarity(candidate_info, context) for context in function_contexts]

            # Weight more recent contexts higher
            weighted_similarity = sum(sim * (i + 1) for i, sim in enumerate(similarities)) / sum(
                range(1, len(similarities) + 2))

            weighted_scores.append((candidate, weighted_similarity))

        # Return the candidate with the highest score
        best_candidate, _ = max(weighted_scores, key=lambda x: x[1])

        # Learn from this disambiguation if a learner is available
        if self.learner:
            self.learner.learn_function_disambiguation(name, candidates, best_candidate, function_contexts)

        return best_candidate

    def disambiguate_syntax(self, partial_statement, possible_completions):
        """
        Disambiguate ambiguous syntax based on context.

        Args:
            partial_statement: The partial or ambiguous statement
            possible_completions: List of possible interpretations

        Returns:
            The most likely completion
        """
        if not possible_completions:
            return None

        if len(possible_completions) == 1:
            return possible_completions[0]

        # If we have context history, use it to disambiguate
        if self.context_history:
            # Find the most similar completion to the context
            context_representation = " ".join(self.context_history[-3:])  # Use last 3 statements
            most_similar, similarity = get_most_similar(context_representation, possible_completions)

            # If the similarity is above the threshold, use this completion
            if similarity > self.similarity_threshold:
                # Learn from this disambiguation if a learner is available
                if self.learner:
                    self.learner.learn_syntax_disambiguation(
                        partial_statement, possible_completions, most_similar, self.context_history
                    )
                return most_similar

        # If no context or similarity is below threshold, check with the learner
        if self.learner:
            learner_suggestion = self.learner.suggest_syntax_disambiguation(
                partial_statement, possible_completions
            )
            if learner_suggestion:
                return learner_suggestion

        # Default to the first completion if no other methods work
        return possible_completions[0]

    def _is_type_compatible(self, type1, type2):
        """
        Check if two types are compatible.

        Args:
            type1: First type
            type2: Second type

        Returns:
            Whether the types are compatible
        """
        # Simple compatibility check, can be enhanced with full type system
        if type1 == type2:
            return True

        # Any type is compatible with any other type
        if type1 == "Any" or type2 == "Any":
            return True

        # Numeric types are compatible
        if type1 in ["Integer", "Float"] and type2 in ["Integer", "Float"]:
            return True

        # Check for list types
        if type1.startswith("List[") and type2.startswith("List["):
            # Extract element types
            elem_type1 = type1[5:-1]
            elem_type2 = type2[5:-1]
            return self._is_type_compatible(elem_type1, elem_type2)

        # Check for dictionary types
        if type1.startswith("Dictionary[") and type2.startswith("Dictionary["):
            # Extract key and value types
            key_value1 = type1[11:-1].split(", ")
            key_value2 = type2[11:-1].split(", ")

            if len(key_value1) == 2 and len(key_value2) == 2:
                key_type1, value_type1 = key_value1
                key_type2, value_type2 = key_value2

                return (self._is_type_compatible(key_type1, key_type2) and
                        self._is_type_compatible(value_type1, value_type2))

        # Default to not compatible
        return False