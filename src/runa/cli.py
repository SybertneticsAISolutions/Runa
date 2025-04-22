import click
import os
import sys
from src.runa.lexer import RunaLexer
from src.runa.parser import RunaParser
from src.runa.analyzer import SemanticAnalyzer
from src.runa.generator import PyCodeGenerator
from src.runa.advanced import transpile_advanced
from src.runa.transpiler import Transpiler


@click.group()
@click.version_option(version='0.1.0')
def main():
    """Runa programming language compiler and interpreter."""
    pass


@main.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file for the generated code.')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output.')
@click.option('--advanced', '-a', is_flag=True, help='Enable advanced language features.')
@click.option('--target', '-t', default='python', help='Target language (python, javascript).')
def compile(file, output, verbose, advanced, target):
    """Compile a Runa file to the target language code."""
    # Read the input file
    with open(file, 'r') as f:
        source = f.read()

    # Check if the target language is supported
    try:
        transpiler = Transpiler(target=target, advanced=advanced)
    except ValueError as e:
        click.echo(f"Error: {str(e)}", err=True)
        return 1

    if verbose:
        click.echo(
            f"Parsing {file}" + (" with advanced language features" if advanced else "") + f" targeting {target}...")

    # Transpile the source code
    code, valid, errors, warnings = transpiler.transpile(source)

    # Print any errors or warnings
    for warning in warnings:
        click.echo(f"Warning: {warning}", err=True)

    for error in errors:
        click.echo(f"Error: {error}", err=True)

    if not valid:
        click.echo("Compilation failed due to errors.", err=True)
        return 1

    if verbose:
        click.echo(f"Generated {target} code.")

    # Determine the file extension for the target language
    ext_map = {
        'python': '.py',
        'javascript': '.js',
        'js': '.js'
    }
    file_ext = ext_map.get(target.lower(), '.txt')

    # Write the output
    if output:
        with open(output, 'w') as f:
            f.write(code)
        if verbose:
            click.echo(f"Generated {target} code written to {output}")
    else:
        # Use the same name as the input file but with the appropriate extension
        output_file = os.path.splitext(file)[0] + file_ext
        with open(output_file, 'w') as f:
            f.write(code)
        if verbose:
            click.echo(f"Generated {target} code written to {output_file}")

    return 0


@main.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output.')
@click.option('--advanced', '-a', is_flag=True, help='Enable advanced language features.')
@click.option('--target', '-t', default='python', help='Target language (python, javascript).')
def run(file, verbose, advanced, target):
    """Run a Runa file directly."""
    # Currently, we can only run Python targets
    if target.lower() not in ('python', 'py'):
        click.echo(f"Error: Can only run Python targets. Use 'compile' for {target}.", err=True)
        return 1

    # Compile the file to Python
    output_file = os.path.splitext(file)[0] + '.py'
    result = compile.callback(file, output_file, verbose, advanced, target)

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
@click.option('--target', '-t', default='python', help='Target language (python, javascript).')
def repl(advanced, target):
    """Start an interactive Runa REPL."""
    # Currently, we can only run Python targets in REPL
    if target.lower() not in ('python', 'py'):
        click.echo(f"Error: REPL only supports Python targets. Use 'compile' for {target}.", err=True)
        return 1

    click.echo("Runa REPL (Version 0.1.0)")
    if advanced:
        click.echo("Advanced language features enabled: pattern matching, async, functional, types")
    click.echo(f"Target language: {target}")
    click.echo("Type 'exit' to quit.")

    # Create appropriate parser and generator based on options
    try:
        transpiler = Transpiler(target=target, advanced=advanced)
    except ValueError as e:
        click.echo(f"Error: {str(e)}", err=True)
        return 1

    if advanced:
        from src.runa.advanced import parse_advanced, analyze_advanced, generate_advanced
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


@main.command()
def targets():
    """List supported target languages."""
    target_list = Transpiler.supported_targets()
    click.echo("Supported target languages:")
    for target in target_list:
        click.echo(f"  - {target}")
    return 0


if __name__ == '__main__':
    main()