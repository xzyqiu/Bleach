# 🧼 Bleach

Bleach is a small, offline-first metadata scrubber for common file types. It
focuses on removing EXIF/XMP, PDF annotations, and stream/file metadata from
images, PDFs, audio/video, RAW camera files, and common document formats.

Highlights
- Remove EXIF/XMP from images (`.jpg`, `.png`, `.tiff`, etc.)
- Strip author and tracking data from PDFs and remove annotations
- Clean hidden tags from videos and audio using `ffmpeg` (optional re-encode)
- Wipe metadata from RAW camera files using `exiftool`
- Support for `.docx` core-property scrubbing and removing comment lines from text files

Quick install
1. Create a virtual environment and install Python dependencies:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

2. Ensure these system tools are available on your PATH:
- `ffmpeg` (video/audio handling)
- `exiftool` (PDF/RAW metadata removal)
- `setfattr` (optional; used to clear extended attributes on Linux)

Usage examples

```sh
python cli.py image path/to/photo.jpg
python cli.py pdf path/to/document.pdf
python cli.py video path/to/movie.mp4 --reencode
python cli.py audio path/to/song.mp3
python cli.py raw path/to/file.NEF
python cli.py docx path/to/file.docx [output.docx]
python cli.py text path/to/log.txt [output.txt] --prefixes "#,//"
```

Notes and recommendations
- Tests: run `pytest -q` after installing dev deps.
- The CLI defaults create cleaned files next to the input. For video/audio the
  original file is replaced in-place by default when scrubbing; this can be
  made optional later via CLI flags.
- Some functionality requires system binaries described above; the code will
  raise helpful errors if they are missing.

Contributing
- Open issues and PRs are welcome. Consider adding tests for new file types.

License
- See `LICENSE` for license terms.
# 🧼 Bleach

**Bleach** is a cross-format metadata scrubber built for privacy and anonymity.  
It erases digital fingerprints from files such as photos, videos, PDFs, and more without damaging content.

## Features
- Remove EXIF and XMP metadata from images (`.jpg`, `.png`, `.tiff`, etc.)
- Strip author and tracking data from PDFs
- Clean hidden tags from videos and audio files using `ffmpeg`
- Wipe sensitive fields from RAW camera formats
- Works entirely offline no network access required

## Why Bleach?
Metadata is the invisible ink of the digital world  your location, camera model, software name, and even your device ID can hide in it. Bleach purges that data, leaving only what’s essential.

## Supported types:
- image
- pdf
- video
- audio
- raw

## Installation

Install requirements: 
```bash
pip install -r requirements.txt
```

Clone the repo:
```bash
git clone https://github.com/xzyqiu/Bleach.git
cd Bleach
```

## Dependencies
Make sure you have ffmpeg and exiftool installed.

## Usage
```bash
python cli.py image path/to/image.jpg
python cli.py pdf path/to/file.pdf
python cli.py video path/to/video.mp4
python cli.py audio path/to/audio.mp3
python cli.py raw path/to/photo.nef
```
