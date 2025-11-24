.PHONY: help install install-dev test test-cov lint format type-check clean build publish

help:
	@echo "Bleach - Metadata Scrubber"
	@echo ""
	@echo "Available commands:"
	@echo "  install       Install package"
	@echo "  install-dev   Install with development dependencies"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage report"
	@echo "  lint          Run linting checks"
	@echo "  format        Format code with black and isort"
	@echo "  type-check    Run type checking with mypy"
	@echo "  clean         Remove build artifacts"
	@echo "  build         Build distribution packages"
	@echo "  publish       Publish to PyPI (requires credentials)"

install:
	pip install -e .

install-dev:
	pip install -e .[dev]

test:
	pytest -v

test-cov:
	pytest --cov=scrubbers --cov-report=html --cov-report=term-missing

lint:
	flake8 scrubbers tests cli.py --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 scrubbers tests cli.py --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics

format:
	black scrubbers tests cli.py
	isort scrubbers tests cli.py

type-check:
	mypy scrubbers --ignore-missing-imports

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

build: clean
	python -m build

publish: build
	twine upload dist/*

check: format lint type-check test

all: check
