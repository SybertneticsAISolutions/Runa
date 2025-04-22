import click
import os
import sys
from lexer import RunaLexer
from parser import RunaParser
from analyzer import SemanticAnalyzer
from generator import PyCodeGenerator
from advanced import transpile_advanced


@click.group()
@click.version_option(version='0.1.0')
def main():
    """Runa programming language compiler and interpreter."""
    pass


@main.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file for the generated Python code.')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output.')
@click.option('--advanced', '-a', is_flag=True, help='Enable advanced language features.')
def compile(file, output, verbose, advanced):
    """Compile a Runa file to Python code."""
    # Read the input file
    with open(file, 'r') as f:
        source = f.read()

    if advanced:
        # Use advanced transpiler
        if verbose:
            click.echo(f"Parsing {file} with advanced language features...")

        code, valid, errors, warnings = transpile_advanced(source)

        # Print any errors or warnings
        for warning in warnings:
            click.echo(f"Warning: {warning}", err=True)

        for error in errors:
            click.echo(f"Error: {error}", err=True)

        if not valid:
            click.echo("Compilation failed due to errors.", err=True)
            return 1

        if verbose:
            click.echo("Generated Python code.")
    else:
        # Use basic transpiler
        parser = RunaParser()

        if verbose:
            click.echo(f"Parsing {file}...")

        ast = parser.parse(source)

        if not ast:
            click.echo(f"Failed to parse {file}", err=True)
            return 1

        # Perform semantic analysis
        if verbose:
            click.echo("Performing semantic analysis...")

        analyzer = SemanticAnalyzer()
        valid = analyzer.analyze(ast)

        # Print any errors or warnings
        for warning in analyzer.warnings:
            click.echo(f"Warning: {warning}", err=True)

        for error in analyzer.errors:
            click.echo(f"Error: {error}", err=True)

        if not valid:
            click.echo("Compilation failed due to semantic errors.", err=True)
            return 1

        # Generate Python code
        if verbose:
            click.echo("Generating Python code...")

        generator = PyCodeGenerator()
        code = generator.generate(ast)

    # Write the output
    if output:
        with open(output, 'w') as f:
            f.write(code)
        if verbose:
            click.echo(f"Generated Python code written to {output}")
    else:
        # Use the same name as the input file but with .py extension
        output_file = os.path.splitext(file)[0] + '.py'
        with open(output_file, 'w') as f:
            f.write(code)
        if verbose:
            click.echo(f"Generated Python code written to {output_file}")

    return 0


@main.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output.')
@click.option('--advanced', '-a', is_flag=True, help='Enable advanced language features.')
def run(file, verbose, advanced):
    """Run a Runa file directly."""
    # Compile the file to Python
    output_file = os.path.splitext(file)[0] + '.py'
    result = compile.callback(file, output_file, verbose, advanced)

    if result != 0:
        return result

    # Run the compiled Python code
    if verbose:
        click.echo(f"Running {output_file}...")

    # Add the current directory to the Python path to ensure imports work
    sys.path.insert(0, os.getcwd())

    # Execute the Python file
    with open(output_file, 'r') as f:
        code = compile(f.read(), output_file, 'exec')
        exec(code)

    return 0


@main.command()
@click.option('--advanced', '-a', is_flag=True, help='Enable advanced language features.')
def repl(advanced):
    """Start an interactive Runa REPL."""
    click.echo("Runa REPL (Version 0.1.0)")
    if advanced:
        click.echo("Advanced language features enabled: pattern matching, async, functional, types")
    click.echo("Type 'exit' to quit.")

    if advanced:
        from advanced import parse_advanced, analyze_advanced, generate_advanced
        parser_func = parse_advanced
        analyzer_func = lambda ast: (analyze_advanced(ast), [])  # Returns (valid, errors)
        generator_func = generate_advanced
    else:
        parser = RunaParser()
        analyzer = SemanticAnalyzer()
        generator = PyCodeGenerator()
        parser_func = parser.parse
        analyzer_func = lambda ast: (analyzer.analyze(ast), analyzer.errors)
        generator_func = generator.generate

    while True:
        try:
            source = input(">>> ")

            if source.lower() == 'exit':
                break

            # Add a newline to ensure proper indentation
            source += '\n'

            # Parse the input
            ast = parser_func(source)

            if not ast:
                continue

            # Analyze the AST
            valid, errors = analyzer_func(ast)

            # Print any errors
            for error in errors:
                click.echo(f"Error: {error}")

            if not valid:
                continue

            # Generate Python code
            python_code = generator_func(ast)

            # Execute the Python code
            try:
                exec(python_code)
            except Exception as e:
                click.echo(f"Runtime error: {str(e)}")

        except KeyboardInterrupt:
            click.echo("\nInterrupted")
        except EOFError:
            break
        except Exception as e:
            click.echo(f"Error: {str(e)}")

    click.echo("Goodbye!")
    return 0


if __name__ == '__main__':
    main()