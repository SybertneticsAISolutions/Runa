"""
Code generation for functional programming in Runa.
This module extends the Python code generator to handle functional programming nodes.
"""
from nodes import (
    LambdaExpression, PipelineExpression, PartialApplicationExpression,
    CompositionExpression, MapExpression, FilterExpression, ReduceExpression
)


def extend_generator(generator_class):
    """
    Extend a code generator class with methods for generating code for functional programming nodes.

    Args:
        generator_class: The code generator class to extend

    Returns:
        The extended code generator class
    """

    # Add generation methods for functional programming nodes

    def visit_LambdaExpression(self, node):
        """Generate code for a lambda expression."""
        param_list = ", ".join(node.parameters)
        body_code = self.generate(node.body)
        return f"lambda {param_list}: {body_code}"

    def visit_PipelineExpression(self, node):
        """Generate code for a pipeline expression."""
        # Generate code for left and right expressions
        left_code = self.generate(node.left)
        right_code = self.generate(node.right)

        # Use the pipeline function from the runtime
        return f"pipeline({left_code}, {right_code})"

    def visit_PartialApplicationExpression(self, node):
        """Generate code for a partial application expression."""
        # Generate code for the function
        func_code = self.generate(node.function)

        # Generate code for arguments
        args_code = ", ".join(self.generate(arg) for arg in node.args)
        kwargs_code = ", ".join(f"{k}={self.generate(v)}" for k, v in node.kwargs.items())

        # Combine arguments with comma if both are present
        if args_code and kwargs_code:
            args_kwargs_code = f"{args_code}, {kwargs_code}"
        else:
            args_kwargs_code = args_code + kwargs_code

        # Use the partial function from the runtime
        return f"partial({func_code}, {args_kwargs_code})"

    def visit_CompositionExpression(self, node):
        """Generate code for a function composition expression."""
        # Generate code for each function
        func_codes = [self.generate(func) for func in node.functions]

        # Join function codes with commas
        funcs_code = ", ".join(func_codes)

        # Use the compose function from the runtime
        return f"compose({funcs_code})"

    def visit_MapExpression(self, node):
        """Generate code for a map expression."""
        # Generate code for the function and collection
        func_code = self.generate(node.function)
        coll_code = self.generate(node.collection)

        # Use the map_function from the runtime
        return f"map_function({func_code}, {coll_code})"

    def visit_FilterExpression(self, node):
        """Generate code for a filter expression."""
        # Generate code for the predicate and collection
        pred_code = self.generate(node.predicate)
        coll_code = self.generate(node.collection)

        # Use the filter_function from the runtime
        return f"filter_function({pred_code}, {coll_code})"

    def visit_ReduceExpression(self, node):
        """Generate code for a reduce expression."""
        # Generate code for the function, collection, and initial value
        func_code = self.generate(node.function)
        coll_code = self.generate(node.collection)

        # Handle optional initial value
        if node.initial:
            init_code = self.generate(node.initial)
            return f"reduce_function({func_code}, {coll_code}, {init_code})"
        else:
            return f"reduce_function({func_code}, {coll_code})"

    # Add the methods to the code generator class
    generator_class.visit_LambdaExpression = visit_LambdaExpression
    generator_class.visit_PipelineExpression = visit_PipelineExpression
    generator_class.visit_PartialApplicationExpression = visit_PartialApplicationExpression
    generator_class.visit_CompositionExpression = visit_CompositionExpression
    generator_class.visit_MapExpression = visit_MapExpression
    generator_class.visit_FilterExpression = visit_FilterExpression
    generator_class.visit_ReduceExpression = visit_ReduceExpression

    return generator_class