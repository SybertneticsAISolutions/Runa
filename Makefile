.PHONY: install test clean lint format

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Testing
test:
	pytest

test-verbose:
	pytest -v

coverage:
	pytest --cov=runa

# Code quality
lint:
	black src tests
	flake8 src tests

format:
	black src tests

# Cleanup
clean:
	rm -rf build dist *.egg-info
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete
	find . -name '.coverage' -delete
	find . -name '*.so' -delete
	find . -name '*.c' -delete
	find . -name '*.html' -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov

# Running
run-example:
	python -m runa.cli run tests/examples/hello_world.runa

repl:
	python -m runa.cli repl