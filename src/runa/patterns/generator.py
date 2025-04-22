"""
Code generation for pattern matching in Runa.
This module extends the Python code generator to handle pattern matching nodes.
"""
import ast as py_ast
from src.runa.patterns.nodes import (
    WildcardPattern, LiteralPattern, VariablePattern,
    ListPattern, DictionaryPattern, RestPattern, TypePattern,
    MatchCase, MatchExpression
)


def extend_generator(generator_class):
    """
    Extend a code generator class with methods for generating code for pattern matching nodes.

    Args:
        generator_class: The code generator class to extend

    Returns:
        The extended code generator class
    """

    # Add generation methods for pattern matching nodes

    def visit_MatchExpression(self, node):
        """Generate code for a match expression."""
        # Generate code for the value to match
        value_code = self.generate(node.value)

        # Generate a unique temporary variable name for the value
        temp_var = f"_match_value_{id(node) % 10000:04d}"

        # Generate the match statement
        match_code = [f"{temp_var} = {value_code}"]

        # Process each case
        has_wildcard = False
        for i, case in enumerate(node.cases):
            # Check if this is a wildcard pattern (catch-all)
            is_wildcard = (
                    isinstance(case.pattern, WildcardPattern) or
                    (isinstance(case.pattern, VariablePattern) and case.pattern.name == '_')
            )

            if is_wildcard:
                has_wildcard = True

            # Generate the condition for this case
            if i == 0:
                if is_wildcard:
                    condition = "True"
                else:
                    condition = self._generate_pattern_condition(case.pattern, temp_var)
                match_code.append(f"if {condition}:")
            else:
                if is_wildcard:
                    condition = "True"
                else:
                    condition = self._generate_pattern_condition(case.pattern, temp_var)
                match_code.append(f"elif {condition}:")

            # Generate the bindings for this case
            bindings = self._generate_pattern_bindings(case.pattern, temp_var)

            # Generate the body for this case
            indent_body = ["    " + self.generate(stmt) for stmt in case.body]

            # Add bindings before the body
            body = ["    " + binding for binding in bindings] + indent_body

            # Add the body to the match statement
            match_code.extend(body)

        # Add default case if no wildcard pattern found
        if not has_wildcard:
            match_code.append("else:")
            match_code.append("    pass  # No pattern matched")

        return "\n".join(match_code)

    def _generate_pattern_condition(self, pattern, value_var):
        """Generate a condition for matching a pattern."""
        if isinstance(pattern, WildcardPattern):
            # Wildcard always matches
            return "True"

        elif isinstance(pattern, LiteralPattern):
            # Literal matches if values are equal
            lit_code = self.generate(pattern.value)
            return f"{value_var} == {lit_code}"

        elif isinstance(pattern, VariablePattern):
            # Variable pattern always matches
            return "True"

        elif isinstance(pattern, ListPattern):
            # Check if value is a list and has the right length or structure
            elements = pattern.elements

            # Check for rest pattern
            has_rest = any(isinstance(e, RestPattern) for e in elements)

            if not has_rest:
                # Fixed length list pattern
                length_check = f"len({value_var}) == {len(elements)}"

                # If no elements, just check length
                if not elements:
                    return length_check

                # Check each element
                element_checks = []
                for i, elem in enumerate(elements):
                    elem_check = self._generate_pattern_condition(elem, f"{value_var}[{i}]")
                    element_checks.append(elem_check)

                # Combine checks: is list, right length, and each element matches
                return f"isinstance({value_var}, list) and {length_check} and " + " and ".join(element_checks)
            else:
                # Variable length list pattern with rest
                # First check if it's a list
                list_check = f"isinstance({value_var}, list)"

                # Count elements before and after rest
                rest_index = next(i for i, e in enumerate(elements) if isinstance(e, RestPattern))
                before_rest = elements[:rest_index]
                after_rest = elements[rest_index + 1:]

                # Minimum length check
                min_length = len(before_rest) + len(after_rest)
                length_check = f"len({value_var}) >= {min_length}"

                # Check elements before rest
                before_checks = []
                for i, elem in enumerate(before_rest):
                    elem_check = self._generate_pattern_condition(elem, f"{value_var}[{i}]")
                    before_checks.append(elem_check)

                # Check elements after rest
                after_checks = []
                for i, elem in enumerate(after_rest):
                    elem_check = self._generate_pattern_condition(
                        elem, f"{value_var}[len({value_var}) - {len(after_rest) + i}]"
                    )
                    after_checks.append(elem_check)

                # Combine checks
                all_checks = [list_check, length_check]
                all_checks.extend(before_checks)
                all_checks.extend(after_checks)

                return " and ".join(all_checks)

        elif isinstance(pattern, DictionaryPattern):
            # Check if value is a dictionary and has the required keys
            entries = pattern.entries

            # If no entries, check if it's an empty dict
            if not entries:
                return f"isinstance({value_var}, dict) and len({value_var}) == 0"

            # Check if it's a dictionary
            dict_check = f"isinstance({value_var}, dict)"

            # Check each key exists and its value matches
            key_checks = []
            for entry in entries:
                key_code = self.generate(entry.key)
                key_check = f"{key_code} in {value_var}"

                # Add check for the corresponding value
                value_check = self._generate_pattern_condition(entry.value, f"{value_var}[{key_code}]")
                key_checks.append(f"{key_check} and {value_check}")

            # Combine all checks
            return f"{dict_check} and " + " and ".join(key_checks)

        elif isinstance(pattern, RestPattern):
            # Rest pattern always matches
            return "True"

        elif isinstance(pattern, TypePattern):
            # Type pattern matches if value is of the specified type
            return f"isinstance({value_var}, {pattern.type_name})"

        # Default case
        return "False"

    def _generate_pattern_bindings(self, pattern, value_var):
        """Generate variable bindings for a pattern."""
        bindings = []

        if isinstance(pattern, VariablePattern) and pattern.name != '_':
            # Bind the variable to the value
            bindings.append(f"{pattern.name} = {value_var}")

        elif isinstance(pattern, ListPattern):
            # Bind variables in the list pattern
            elements = pattern.elements

            # Check for rest pattern
            rest_index = next((i for i, e in enumerate(elements) if isinstance(e, RestPattern)), None)

            if rest_index is not None:
                # Handle list pattern with rest
                before_rest = elements[:rest_index]
                after_rest = elements[rest_index + 1:]

                # Bind elements before rest
                for i, elem in enumerate(before_rest):
                    elem_bindings = self._generate_pattern_bindings(elem, f"{value_var}[{i}]")
                    bindings.extend(elem_bindings)

                # Bind rest element if named
                rest_pattern = elements[rest_index]
                if isinstance(rest_pattern, RestPattern) and rest_pattern.name:
                    start = len(before_rest)
                    end = len(after_rest)
                    if end > 0:
                        rest_expr = f"{value_var}[{start}:len({value_var}) - {end}]"
                    else:
                        rest_expr = f"{value_var}[{start}:]"
                    bindings.append(f"{rest_pattern.name} = {rest_expr}")

                # Bind elements after rest
                for i, elem in enumerate(after_rest):
                    index_expr = f"len({value_var}) - {len(after_rest) + i}"
                    elem_bindings = self._generate_pattern_bindings(elem, f"{value_var}[{index_expr}]")
                    bindings.extend(elem_bindings)
            else:
                # Handle fixed length list pattern
                for i, elem in enumerate(elements):
                    elem_bindings = self._generate_pattern_bindings(elem, f"{value_var}[{i}]")
                    bindings.extend(elem_bindings)

        elif isinstance(pattern, DictionaryPattern):
            # Bind variables in the dictionary pattern
            for entry in pattern.entries:
                key_code = self.generate(entry.key)
                entry_bindings = self._generate_pattern_bindings(entry.value, f"{value_var}[{key_code}]")
                bindings.extend(entry_bindings)

        return bindings

    # Add the methods to the code generator class
    generator_class.visit_MatchExpression = visit_MatchExpression
    generator_class._generate_pattern_condition = _generate_pattern_condition
    generator_class._generate_pattern_bindings = _generate_pattern_bindings

    return generator_class