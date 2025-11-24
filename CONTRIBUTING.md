# Contributing to Bleach

Thanks for your interest in contributing to Bleach!

## Getting Started

1. **Fork and clone the repository**:
```bash
git clone https://github.com/xzyqiu/Bleach.git
cd Bleach
```

2. **Set up development environment**:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .[dev]
```

3. **Install system dependencies**:
- **Linux**: `sudo apt-get install ffmpeg exiftool libmagic1`
- **macOS**: `brew install ffmpeg exiftool libmagic`
- **Windows**: `choco install ffmpeg exiftool`

## Development Workflow

1. **Create a branch**:
```bash
git checkout -b feature/your-feature-name
```

2. **Make changes and test**:
```bash
# Run tests
pytest --cov=scrubbers

# Format code
black scrubbers tests cli.py
isort scrubbers tests cli.py

# Lint
flake8 scrubbers tests cli.py

# Type check
mypy scrubbers --ignore-missing-imports
```

3. **Commit and push**:
```bash
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature-name
```

4. **Open a Pull Request**

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings (Google style)
- Keep functions focused and small
- Write tests for new features

## Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=scrubbers --cov-report=html

# Specific test
pytest tests/test_scrubbers.py::test_name
```

## Commit Messages

Use conventional commit format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `chore:` Maintenance

## Questions?

Open an issue or start a discussion on GitHub.
