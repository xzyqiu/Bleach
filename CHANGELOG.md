# Changelog

All notable changes to Bleach will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-24

### 🎉 Major Release - Complete Project Overhaul

This release represents a complete rewrite and modernization of Bleach, transforming it from a basic script into a professional, production-ready metadata scrubber.

### Added

#### Core Features
- **Comprehensive Type Hints**: Full type annotation coverage for better IDE support and type safety
- **Structured Logging**: Built-in logging with configurable verbosity levels
- **Progress Tracking**: Real-time progress bars using tqdm for better user feedback
- **Backup Support**: Optional automatic backups before scrubbing operations
- **Caching**: LRU cache for file type detection to improve performance
- **Error Handling**: Robust error handling with detailed, actionable error messages

#### CLI Improvements
- **Better UX**: Emoji indicators (✓ for success, ❌ for errors)
- **Verbose Mode**: `-v/--verbose` flag for detailed operation logging
- **Version Command**: `--version` flag to display version information
- **Enhanced Options**:
  - `--backup`: Create backups before scrubbing
  - `--no-inplace`: Prevent in-place modifications for video/audio
  - `--preset`: Choose FFmpeg encoding preset (ultrafast to veryslow)
  - `--quality`: Set audio encoding quality (0-9)
- **Improved Help**: Better formatted help text with examples

#### Testing
- **Comprehensive Test Suite**: 15+ tests covering core functionality
- **Test Coverage**: 45% coverage with clear targets for improvement
- **Multiple Test Classes**: Organized tests by functionality
- **Edge Case Testing**: Tests for error conditions and invalid inputs
- **CI/CD Integration**: GitHub Actions workflow for automated testing

#### Development
- **Package Configuration**: Complete `pyproject.toml` with metadata and dependencies
- **Development Tools**: Integration with black, flake8, isort, mypy
- **Pre-commit Hooks**: Code quality checks before commits
- **Contributing Guide**: Detailed CONTRIBUTING.md with development workflow

#### Documentation
- **Professional README**: Complete rewrite with badges, examples, and better structure
- **Contributing Guidelines**: Comprehensive guide for contributors
- **Code Documentation**: Improved docstrings with Google-style formatting
- **API Examples**: Python API usage examples in README

### Changed

#### Breaking Changes
- **CLI Command Name**: Changed from `python cli.py` to `bleach` command
- **Function Signatures**: Updated all scrubbing functions with Union types for path parameters
- **Error Types**: Changed some exceptions to be more specific (RuntimeError instead of generic Exception)

#### Improvements
- **Image Scrubbing**: Rewritten to avoid type errors and use pixel-by-pixel copy
- **PDF Scrubbing**: Better error handling and graceful fallback if exiftool unavailable
- **Video/Audio**: Added timeout support and better FFmpeg error reporting
- **File Validation**: Enhanced validation with directory detection and better error messages
- **Performance**: Added caching for file type detection
- **Code Quality**: Refactored for better readability and maintainability

### Fixed
- **Type Errors**: Resolved PIL image data type issues
- **Import Issues**: Fixed missing imports and optional dependency handling
- **Path Handling**: Better cross-platform path handling with pathlib
- **Timeout Issues**: Added timeouts for long-running external commands
- **Backup Creation**: Fixed backup file path generation

### Security
- **Safe Defaults**: Non-destructive operations by default
- **Backup Protection**: Automatic backup creation option
- **No Network**: Confirmed 100% offline operation
- **Error Exposure**: Sanitized error messages to prevent information leakage

### Performance
- **Caching**: File type detection results cached with LRU cache
- **Batch Processing**: Documentation for efficient batch operations
- **Optimized Imports**: Lazy imports for optional dependencies

### Documentation
- **README.md**: Complete rewrite with professional formatting
- **CONTRIBUTING.md**: New comprehensive contribution guide
- **PROJECT_STATUS.md**: Updated status and roadmap
- **Code Comments**: Improved inline documentation
- **Type Hints**: Self-documenting function signatures

### Infrastructure
- **GitHub Actions**: CI/CD pipeline for automated testing
- **Multi-Platform**: Testing on Ubuntu, macOS, and Windows
- **Python Versions**: Support for Python 3.8-3.12+
- **Package Distribution**: PyPI-ready package configuration

## [0.1.0] - 2025-11-18

### Initial Release
- Basic image metadata scrubbing
- PDF annotation removal
- Video/audio metadata stripping
- RAW file support
- DOCX property clearing
- Text comment removal

---

## Upgrade Guide

### From 0.x to 1.0

#### CLI Changes
```bash
# Old
python cli.py image photo.jpg

# New
bleach image photo.jpg
```

#### Python API Changes
```python
# Old
from scrubbers import scrub_image
scrub_image("photo.jpg")  # Path as str

# New - Still compatible, but with added features
from scrubbers import scrub_image
scrub_image("photo.jpg", backup=True)  # New backup option
```

#### Installation Changes
```bash
# Old
pip install -r requirements.txt

# New - Proper package installation
pip install -e .
# or from PyPI (when published)
pip install bleach-metadata
```

---

[1.0.0]: https://github.com/xzyqiu/Bleach/releases/tag/v1.0.0
[0.1.0]: https://github.com/xzyqiu/Bleach/releases/tag/v0.1.0
