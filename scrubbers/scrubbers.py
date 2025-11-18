"""Metadata scrubber helpers and per-format scrubbing functions.

This module provides a small set of functions to remove metadata from
common file types. The implementations are intentionally small and
dependency-light so they can be used in CLI and tests.
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Optional, Sequence
import exifread
import magic
from PIL import Image
from pypdf import PdfReader, PdfWriter

try:
    # optional import for docx handling
    from docx import Document
except Exception:  # pragma: no cover - optional dependency
    Document = None


def _run(cmd: Sequence[str]) -> subprocess.CompletedProcess:
    """Run a subprocess and return the CompletedProcess object."""
    return subprocess.run(list(cmd), capture_output=True, text=True)


def _check_file(path: Path) -> Path:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return p


def get_file_type(path: Path) -> Dict[str, str]:
    """Return a small mime/description dict using libmagic.

    This is a convenience helper used by callers and tests.
    """
    path = _check_file(path)
    mime = magic.from_file(str(path), mime=True)
    desc = magic.from_file(str(path))
    return {"mime": mime, "description": desc}


def read_image(path: Path) -> Dict:
    """Read basic image properties and EXIF tags.

    Returns a dict containing PIL info and exifread tags.
    """
    path = _check_file(path)
    metadata: Dict = {}
    with Image.open(path) as img:
        metadata["format"] = img.format
        metadata["mode"] = img.mode
        metadata["size"] = img.size
        exif = img.getexif()
        if exif:
            metadata["exif"] = {k: str(v) for k, v in exif.items()}

    with open(path, "rb") as f:
        tags = exifread.process_file(f, details=False)
        metadata["exifread"] = {k: str(v) for k, v in tags.items()}
    return metadata


def scrub_image(ipath: Path, opath: Optional[Path] = None) -> str:
    """Create a pixel-identical image and write it to `opath` (no EXIF/XMP).

    If `opath` is not provided a new file with suffix `.scrubbed` is created
    next to the original file.
    """
    ipath = _check_file(ipath)
    opath = Path(opath) if opath else Path(ipath).with_name(Path(ipath).stem + ".scrubbed" + Path(ipath).suffix)
    with Image.open(ipath) as img:
        data = list(img.getdata())
        clean = Image.new(img.mode, img.size)
        clean.putdata(data)
        clean.save(opath)
    return f"Scrubbed: {opath.name}"


def delete_pdf(path: Path, output: Optional[Path] = None) -> str:
    """Strip PDF metadata and annotations.

    Uses `exiftool` to clear metadata, then rewrites PDF pages to remove
    annotations and forms. Returns the output filename.
    """
    path = _check_file(path)
    output = Path(output) if output else Path(path).with_name(Path(path).stem + ".scrubbed.pdf")
    subprocess.run(["exiftool", "-all=", "-overwrite_original", str(path)], stdout=subprocess.DEVNULL)
    reader = PdfReader(path)
    writer = PdfWriter()
    for page in reader.pages:
        page.pop("/Annots", None)
        writer.add_page(page)
    if " /AcroForm" in str(reader.trailer.get("/Root", {})):
        reader.trailer["/Root"].pop("/AcroForm", None)
    writer.add_metadata({"/Producer": "", "/Creator": "", "/Title": "", "/Author": ""})
    with open(output, "wb") as f:
        writer.write(f)
    return f"Scrubbed: {output.name}"


def delete_video(path: Path, out: Optional[Path] = None, reencode: bool = False, inplace: bool = True) -> str:
    """Remove stream metadata from video using ffmpeg.

    If `reencode` is True the streams are re-encoded for extra safety. By
    default the scrubbed file replaces the original (inplace=True).
    """
    p = _check_file(path)
    out = Path(out) if out else p.with_name(p.stem + ".scrubbed" + p.suffix)
    cmd = ["ffmpeg", "-y", "-i", str(p), "-map_metadata", "-1"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "20", "-c:a", "aac"] if reencode else ["-c", "copy"]
    cmd.append(str(out))
    r = _run(cmd)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {r.stderr.strip()}")
    # Remove common extended attributes if possible
    subprocess.run(["setfattr", "-h", "-x", "user.comment", str(out)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if inplace:
        os.replace(out, p)
        now = time.time()
        os.utime(p, (now, now))
        return f"Scrubbed: {p.name}"
    return f"Scrubbed: {out.name}"


def delete_audio(path: Path, out: Optional[Path] = None, reencode: bool = False, inplace: bool = True) -> str:
    """Remove metadata from audio files using ffmpeg.

    Similar contract to `delete_video`.
    """
    p = _check_file(path)
    out = Path(out) if out else p.with_name(p.stem + ".scrubbed" + p.suffix)
    cmd = ["ffmpeg", "-y", "-i", str(p), "-map_metadata", "-1"]
    cmd += ["-c:a", "libmp3lame", "-q:a", "2"] if reencode else ["-c", "copy"]
    cmd.append(str(out))
    r = _run(cmd)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {r.stderr.strip()}")
    subprocess.run(["setfattr", "-h", "-x", "user.comment", str(out)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if inplace:
        os.replace(out, p)
        now = time.time()
        os.utime(p, (now, now))
        return f"Scrubbed: {p.name}"
    return f"Scrubbed: {out.name}"


def delete_raw_metadata(path: Path) -> str:
    """Use ExifTool to wipe RAW camera metadata in-place."""
    p = _check_file(path)
    cmd = ["exiftool", "-overwrite_original", "-all=", str(p)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ExifTool failed: {result.stderr.strip()}")
    # Remove ExifTool backup file if it exists
    backup = p.with_suffix(p.suffix + "_original")
    if backup.exists():
        backup.unlink()
    return f"Scrubbed: {p.name}"


def delete_docx(path: Path, output: Optional[Path] = None) -> str:
    """Clear core properties of a .docx file.

    Requires `python-docx`. If not installed this raises ImportError.
    """
    if Document is None:  # pragma: no cover - optional dependency
        raise ImportError("python-docx is required for DOCX handling")
    p = _check_file(path)
    output = Path(output) if output else p.with_name(p.stem + ".scrubbed" + p.suffix)
    doc = Document(str(p))
    cp = doc.core_properties
    # clear common core properties
    cp.author = ""
    cp.title = ""
    cp.comments = ""
    cp.last_modified_by = ""
    cp.subject = ""
    doc.save(str(output))
    return f"Scrubbed: {output.name}"


def scrub_text_comments(path: Path, output: Optional[Path] = None, prefixes: Optional[Sequence[str]] = None) -> str:
    """Remove lines that look like comments from a plain-text file.

    This is a non-destructive helper: by default writes to a `.scrubbed` file.
    Useful for removing inline annotations from exported logs or code snippets.
    """
    p = _check_file(path)
    prefixes = prefixes or ["#", "//", ";"]
    out = Path(output) if output else p.with_name(p.stem + ".scrubbed" + p.suffix)
    with open(p, "r", encoding="utf-8", errors="ignore") as inf, open(out, "w", encoding="utf-8") as outf:
        for line in inf:
            stripped = line.lstrip()
            if any(stripped.startswith(pref) for pref in prefixes):
                continue
            outf.write(line)
    return f"Scrubbed: {out.name}"

