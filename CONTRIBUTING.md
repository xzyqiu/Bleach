# Contributing to Bleach

Thank you for your interest in contributing to Bleach! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- FFmpeg and ExifTool (for full functionality)

### Development Setup

1. **Fork and clone the repository**:
```bash
git clone https://github.com/yourusername/Bleach.git
cd Bleach
```

2. **Create a virtual environment**:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install development dependencies**:
```bash
pip install -e .[dev]
```

4. **Install system dependencies**:

**Linux**:
```bash
sudo apt-get install ffmpeg exiftool libmagic1
```

**macOS**:
```bash
brew install ffmpeg exiftool libmagic
```

**Windows**:
```bash
choco install ffmpeg exiftool
```

## 📝 Development Workflow

### Before Making Changes

1. Create a new branch for your feature or bugfix:
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bugfix-name
```

2. Make sure all tests pass:
```bash
pytest
```

### Making Changes

1. **Write clean, readable code**:
   - Follow PEP 8 style guidelines
   - Add type hints to function signatures
   - Write descriptive docstrings
   - Keep functions focused and modular

2. **Add tests for new features**:
   - Place tests in the `tests/` directory
   - Aim for >80% code coverage
   - Test edge cases and error conditions

3. **Update documentation**:
   - Update README.md if adding features
   - Add docstrings to new functions/classes
   - Update CHANGELOG.md

### Code Quality

Run these checks before committing:

```bash
# Format code
black scrubbers tests cli.py

# Sort imports
isort scrubbers tests cli.py

# Lint code
flake8 scrubbers tests cli.py

# Type check
mypy scrubbers --ignore-missing-imports

# Run tests
pytest --cov=scrubbers --cov-report=term-missing
```

Or use the convenience script:
```bash
# Run all quality checks
./scripts/check.sh  # (if available)
```

### Commit Messages

Write clear, descriptive commit messages:

```
feat: Add support for EPUB metadata scrubbing
fix: Handle edge case in image scrubbing
docs: Update installation instructions
test: Add tests for PDF scrubbing
refactor: Simplify video encoding logic
```

Use conventional commit prefixes:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scrubbers --cov-report=html

# Run specific test file
pytest tests/test_scrubbers.py

# Run specific test
pytest tests/test_scrubbers.py::TestImageScrubbing::test_scrub_image_creates_file

# Run with verbose output
pytest -v
```

### Writing Tests

Create test files in the `tests/` directory:

```python
# tests/test_new_feature.py
import pytest
from pathlib import Path
from scrubbers import your_function

class TestNewFeature:
    """Tests for new feature."""
    
    def test_basic_functionality(self, tmp_path):
        """Test basic functionality works."""
        # Arrange
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        # Act
        result = your_function(test_file)
        
        # Assert
        assert result is not None
        assert "expected" in str(result)
```

## 📋 Pull Request Process

1. **Update your branch**:
```bash
git fetch upstream
git rebase upstream/main
```

2. **Push your changes**:
```bash
git push origin feature/your-feature-name
```

3. **Create a Pull Request**:
   - Use a clear, descriptive title
   - Reference any related issues
   - Describe what changed and why
   - Add screenshots for UI changes
   - Ensure all CI checks pass

4. **PR Template**:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] All tests pass locally
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
```

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Minimal steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**:
   - OS and version
   - Python version
   - Bleach version
   - Relevant system tools (ffmpeg, exiftool versions)
6. **Logs/Screenshots**: Any relevant error messages or screenshots

## 💡 Suggesting Features

We welcome feature suggestions! Please:

1. Check if the feature already exists or is planned
2. Clearly describe the feature and its use case
3. Explain why it would be valuable
4. Consider implementation complexity
5. Be open to discussion and feedback

## 🎯 Areas for Contribution

Looking for where to start? Here are some areas:

### High Priority
- [ ] Support for additional document formats (ODT, RTF, EPUB)
- [ ] Batch processing with progress tracking
- [ ] Improved error messages and handling
- [ ] Performance optimizations
- [ ] More comprehensive tests

### Medium Priority
- [ ] GUI application
- [ ] Configuration file support (.bleachrc)
- [ ] Metadata comparison/verification tool
- [ ] Support for container formats (ZIP, TAR)
- [ ] Plugin system for custom scrubbers

### Documentation
- [ ] API documentation improvements
- [ ] More usage examples
- [ ] Video tutorials
- [ ] Translations

## 📚 Code Style Guide

### Python Style

- Follow PEP 8
- Use Black for formatting (line length: 100)
- Use isort for import sorting
- Add type hints to all function signatures
- Write descriptive docstrings (Google style)

### Example Function:

```python
def scrub_metadata(
    path: Union[str, Path],
    output: Optional[Union[str, Path]] = None,
    backup: bool = False
) -> str:
    """Remove metadata from a file.
    
    This function removes all metadata from the specified file,
    optionally creating a backup before modification.
    
    Args:
        path: Path to input file
        output: Optional output path (creates .scrubbed variant if None)
        backup: Whether to create a backup of the original file
        
    Returns:
        Success message with output filename
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        RuntimeError: If scrubbing fails
        
    Example:
        >>> scrub_metadata("photo.jpg", backup=True)
        'Scrubbed: photo.scrubbed.jpg'
    """
    # Implementation
    pass
```

### Documentation Style

- Use clear, concise language
- Include code examples
- Add usage warnings where appropriate
- Keep documentation up-to-date with code

## 🤝 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Unprofessional conduct

## 📧 Contact

- GitHub Issues: [Report bugs or request features](https://github.com/xzyqiu/Bleach/issues)
- Discussions: [Ask questions or discuss ideas](https://github.com/xzyqiu/Bleach/discussions)

## 📜 License

By contributing to Bleach, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Bleach! Your efforts help make digital privacy more accessible to everyone. 🧼
