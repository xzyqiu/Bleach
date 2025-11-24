# 🧼 Bleach

[![CI](https://github.com/xzyqiu/Bleach/workflows/CI/badge.svg)](https://github.com/xzyqiu/Bleach/actions)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Bleach** is a powerful, privacy-focused metadata scrubber that removes digital fingerprints from various file types. Built for security researchers, privacy advocates, and anyone who values anonymity online.

## 🎯 Why Bleach?

Metadata is the invisible ink of the digital world—your location, camera model, software version, and device ID can all be embedded in your files. Bleach purges this data completely, leaving only what matters: your content.

## ✨ Features

- 🖼️ **Images**: Remove EXIF, XMP, and IPTC metadata from JPEG, PNG, TIFF, and more
- 📄 **PDFs**: Strip author info, tracking data, annotations, and forms
- 🎬 **Videos**: Clean metadata streams with optional re-encoding (H.264)
- 🎵 **Audio**: Remove ID3 tags and metadata from MP3, AAC, and other formats
- 📷 **RAW Files**: Wipe metadata from camera RAW formats (NEF, CR2, ARW, DNG, etc.)
- 📝 **Documents**: Clear properties from DOCX files
- 💬 **Text**: Remove comment lines from plain text files
- 🔒 **100% Offline**: No network access required—your files stay local
- ⚡ **Fast & Efficient**: Optimized with caching and parallel processing
- 🛡️ **Safe**: Automatic backups, non-destructive by default

## 📦 Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install bleach-metadata
```

### Option 2: Install from Source

```bash
git clone https://github.com/xzyqiu/Bleach.git
cd Bleach
pip install -e .
```

### System Dependencies

Some features require external tools:

**Linux (Ubuntu/Debian)**:
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

## 🚀 Quick Start

### Command Line Interface

```bash
# Scrub an image (creates .scrubbed variant)
bleach image photo.jpg

# Scrub with backup
bleach image photo.jpg --backup

# Specify output file
bleach image photo.jpg output.jpg

# Scrub a PDF
bleach pdf document.pdf

# Scrub video with re-encoding for complete removal
bleach video movie.mp4 --reencode --preset fast

# Scrub audio (in-place by default)
bleach audio song.mp3

# Prevent in-place modification
bleach audio song.mp3 --no-inplace

# Scrub RAW camera file
bleach raw photo.NEF --backup

# Scrub DOCX file
bleach docx document.docx

# Remove comments from text file
bleach text script.py --prefixes "#,//"

# Verbose mode
bleach image photo.jpg --verbose
```

### Python API

```python
from scrubbers import scrub_image, delete_pdf, delete_video

# Scrub an image
result = scrub_image("photo.jpg", "clean_photo.jpg", backup=True)
print(result)  # "Scrubbed: clean_photo.jpg"

# Clean a PDF
result = delete_pdf("document.pdf", "clean_doc.pdf")

# Scrub video with re-encoding
result = delete_video(
    "video.mp4",
    reencode=True,
    preset="fast",
    inplace=False
)

# Read image metadata before scrubbing
from scrubbers import read_image
metadata = read_image("photo.jpg")
print(metadata["exif"])  # View EXIF tags
```

## 📋 Supported File Types

| Type | Extensions | Metadata Removed |
|------|-----------|------------------|
| Images | `.jpg`, `.jpeg`, `.png`, `.tiff`, `.webp`, `.bmp` | EXIF, XMP, IPTC |
| PDF | `.pdf` | Author, Creator, Producer, Annotations, Forms |
| Video | `.mp4`, `.mov`, `.avi`, `.mkv`, `.flv` | Stream metadata, XMP |
| Audio | `.mp3`, `.m4a`, `.aac`, `.flac`, `.ogg` | ID3, Vorbis comments |
| RAW | `.nef`, `.cr2`, `.arw`, `.dng`, `.raf` | All metadata tags |
| Documents | `.docx` | Core properties, author, comments |
| Text | `.txt`, `.py`, `.sh`, `.log` | Comment lines |

## ⚙️ Advanced Usage

### Configuration Options

**Image Scrubbing**:
- `--backup`: Create backup before modification
- Custom output path

**Video/Audio Scrubbing**:
- `--reencode`: Re-encode for complete metadata removal
- `--preset`: Encoding speed (ultrafast to veryslow)
- `--quality`: Audio quality (0-9 for MP3)
- `--no-inplace`: Keep original file

**Text Scrubbing**:
- `--prefixes`: Custom comment prefixes (default: `#,//,;`)

### Batch Processing

```bash
# Scrub all images in a directory
for img in *.jpg; do
    bleach image "$img" --backup
done

# Scrub all PDFs
find . -name "*.pdf" -exec bleach pdf {} \;
```

### Python Batch Processing

```python
from pathlib import Path
from scrubbers import scrub_image

# Scrub all images in a directory
for img_path in Path("photos").glob("*.jpg"):
    output = img_path.with_name(f"{img_path.stem}_clean{img_path.suffix}")
    scrub_image(img_path, output, backup=True)
    print(f"Scrubbed: {img_path.name}")
```

## 🧪 Development

### Setup Development Environment

```bash
git clone https://github.com/xzyqiu/Bleach.git
cd Bleach
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .[dev]
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=scrubbers --cov-report=html

# Run specific test
pytest tests/test_scrubbers.py::TestImageScrubbing::test_scrub_image_creates_file
```

### Code Quality

```bash
# Format code
black scrubbers tests cli.py

# Check imports
isort scrubbers tests cli.py

# Lint
flake8 scrubbers tests cli.py

# Type check
mypy scrubbers
```

## 📖 Documentation

- [Contributing Guidelines](CONTRIBUTING.md)
- [Project Status](PROJECT_STATUS.md)

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Priorities

- [ ] Add support for more document formats (ODT, RTF, EPUB)
- [ ] Batch processing mode with progress tracking
- [ ] GUI application
- [ ] Metadata verification/comparison tool
- [ ] Container format support (ZIP, TAR)

## 🔒 Security

Bleach is designed with security and privacy in mind:

- ✅ 100% offline operation
- ✅ No telemetry or tracking
- ✅ Open source and auditable
- ✅ Safe defaults (backups, non-destructive)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Pillow](https://python-pillow.org/) - Image processing
- [PyPDF](https://github.com/py-pdf/pypdf) - PDF manipulation
- [FFmpeg](https://ffmpeg.org/) - Video/audio processing
- [ExifTool](https://exiftool.org/) - Metadata extraction/removal

## 📞 Support

- 🐛 [Report bugs](https://github.com/xzyqiu/Bleach/issues)
- 💡 [Request features](https://github.com/xzyqiu/Bleach/issues)

---

**⚠️ Disclaimer**: While Bleach removes metadata to the best of its ability, complete anonymity cannot be guaranteed. Always verify scrubbed files before sharing sensitive content.
