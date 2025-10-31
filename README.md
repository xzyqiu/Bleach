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
