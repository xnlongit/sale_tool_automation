# Makefile for ER Sports Automation Tool

.PHONY: help install install-dev test clean run build dist

# Default target
help:
	@echo "ER Sports Automation Tool - Available commands:"
	@echo ""
	@echo "  install     - Install package and dependencies"
	@echo "  install-dev - Install package in development mode"
	@echo "  test        - Run tests"
	@echo "  clean       - Clean build artifacts"
	@echo "  run         - Run the application"
	@echo "  build       - Build package"
	@echo "  dist        - Create distribution package"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo ""

# Install package and dependencies
install:
	pip install -r requirements.txt
	pip install -e .

# Install in development mode
install-dev:
	pip install -r requirements.txt
	pip install -e .[dev]

# Run tests
test:
	python -m pytest tests/ -v

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run the application
run:
	python src/main.py

# Build package
build:
	python setup.py build

# Create distribution package
dist: clean
	python setup.py sdist bdist_wheel

# Run linting
lint:
	flake8 src/ tests/
	mypy src/

# Format code
format:
	black src/ tests/

# Install ChromeDriver
install-chromedriver:
	python -c "from webdriver_manager.chrome import ChromeDriverManager; ChromeDriverManager().install()"

# Create virtual environment
venv:
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  Windows: venv\\Scripts\\activate"
	@echo "  Unix/MacOS: source venv/bin/activate"

# Full setup for development
setup-dev: venv
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install -e .[dev]
	@echo "Development environment ready!"
