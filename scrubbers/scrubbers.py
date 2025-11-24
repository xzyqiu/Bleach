"""Metadata scrubber helpers and per-format scrubbing functions.

This module provides a small set of functions to remove metadata from
common file types. The implementations are intentionally small and
dependency-light so they can be used in CLI and tests.
"""

import logging
import os
import shutil
import subprocess
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

import exifread
import magic
from PIL import Image
from pypdf import PdfReader, PdfWriter

# Configure module logger
logger = logging.getLogger(__name__)

try:
    # optional import for docx handling
    from docx import Document
except Exception:  # pragma: no cover - optional dependency
    Document = None


def _run(cmd: Sequence[str], timeout: Optional[int] = None) -> subprocess.CompletedProcess[str]:
    """Run a subprocess and return the CompletedProcess object.
    
    Args:
        cmd: Command and arguments to run
        timeout: Optional timeout in seconds
        
    Returns:
        CompletedProcess object with stdout and stderr as text
    """
    try:
        return subprocess.run(
            list(cmd), 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=False
        )
    except subprocess.TimeoutExpired as e:
        logger.error(f"Command timed out after {timeout}s: {' '.join(cmd)}")
        raise RuntimeError(f"Command timed out: {e}")


def _check_file(path: Union[str, Path]) -> Path:
    """Validate that a file exists and return its Path object.
    
    Args:
        path: Path to the file
        
    Returns:
        Validated Path object
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If path is a directory
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if p.is_dir():
        raise ValueError(f"Path is a directory, not a file: {path}")
    return p


def _create_backup(path: Path) -> Optional[Path]:
    """Create a backup of the original file.
    
    Args:
        path: Path to file to backup
        
    Returns:
        Path to backup file or None if backup creation failed
    """
    try:
        backup_path = path.with_suffix(path.suffix + ".backup")
        shutil.copy2(path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        logger.warning(f"Failed to create backup: {e}")
        return None


@lru_cache(maxsize=128)
def get_file_type(path: Union[str, Path]) -> Dict[str, str]:
    """Return a small mime/description dict using libmagic.

    This is a convenience helper used by callers and tests.
    Results are cached for performance.
    
    Args:
        path: Path to the file
        
    Returns:
        Dict with 'mime' and 'description' keys
    """
    path_obj = _check_file(path)
    try:
        mime = magic.from_file(str(path_obj), mime=True)
        desc = magic.from_file(str(path_obj))
        return {"mime": mime, "description": desc}
    except Exception as e:
        logger.error(f"Failed to determine file type: {e}")
        raise RuntimeError(f"Unable to determine file type: {e}")


def read_image(path: Union[str, Path]) -> Dict[str, Any]:
    """Read basic image properties and EXIF tags.

    Args:
        path: Path to the image file
        
    Returns:
        Dict containing PIL info and exifread tags
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If file is not a valid image
    """
    path_obj = _check_file(path)
    metadata: Dict[str, Any] = {}
    
    try:
        with Image.open(path_obj) as img:
            metadata["format"] = img.format
            metadata["mode"] = img.mode
            metadata["size"] = img.size
            exif = img.getexif()
            if exif:
                metadata["exif"] = {k: str(v) for k, v in exif.items()}
    except Exception as e:
        logger.error(f"Failed to read image with PIL: {e}")
        raise ValueError(f"Invalid image file: {e}")

    try:
        with open(path_obj, "rb") as f:
            tags = exifread.process_file(f, details=False)
            metadata["exifread"] = {k: str(v) for k, v in tags.items()}
    except Exception as e:
        logger.warning(f"Failed to read EXIF with exifread: {e}")
        metadata["exifread"] = {}
        
    return metadata


def scrub_image(
    ipath: Union[str, Path], 
    opath: Optional[Union[str, Path]] = None,
    backup: bool = False
) -> str:
    """Create a pixel-identical image and write it to `opath` (no EXIF/XMP).

    This method creates a new image with the same pixel data but without
    any metadata, ensuring complete metadata removal.

    Args:
        ipath: Input image path
        opath: Output path (if None, creates .scrubbed variant)
        backup: Whether to create a backup of the original
        
    Returns:
        Success message with output filename
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If file is not a valid image
    """
    ipath_obj = _check_file(ipath)
    
    if backup:
        _create_backup(ipath_obj)
    
    if opath is None:
        opath_obj = ipath_obj.with_name(ipath_obj.stem + ".scrubbed" + ipath_obj.suffix)
    else:
        opath_obj = Path(opath)
    
    try:
        with Image.open(ipath_obj) as img:
            # Create new image without metadata
            clean = Image.new(img.mode, img.size)
            # Copy pixel data - use load() to avoid type issues
            img_pixels = img.load()
            clean_pixels = clean.load()
            if img_pixels and clean_pixels:
                for y in range(img.size[1]):
                    for x in range(img.size[0]):
                        clean_pixels[x, y] = img_pixels[x, y]
            clean.save(opath_obj)
        logger.info(f"Successfully scrubbed image: {ipath_obj} -> {opath_obj}")
        return f"Scrubbed: {opath_obj.name}"
    except Exception as e:
        logger.error(f"Failed to scrub image: {e}")
        raise RuntimeError(f"Image scrubbing failed: {e}")


def delete_pdf(
    path: Union[str, Path], 
    output: Optional[Union[str, Path]] = None,
    backup: bool = False
) -> str:
    """Strip PDF metadata and annotations.

    Uses `exiftool` to clear metadata, then rewrites PDF pages to remove
    annotations and forms.
    
    Args:
        path: Input PDF path
        output: Output path (if None, creates .scrubbed variant)
        backup: Whether to create a backup of the original
        
    Returns:
        Success message with output filename
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        RuntimeError: If exiftool fails or PDF processing fails
    """
    path_obj = _check_file(path)
    
    if backup:
        _create_backup(path_obj)
    
    if output is None:
        output_obj = path_obj.with_name(path_obj.stem + ".scrubbed.pdf")
    else:
        output_obj = Path(output)
    
    # Check if exiftool is available
    exiftool_result = subprocess.run(
        ["which", "exiftool"], 
        capture_output=True, 
        text=True
    )
    if exiftool_result.returncode != 0:
        logger.warning("exiftool not found, skipping EXIF removal")
    else:
        try:
            result = subprocess.run(
                ["exiftool", "-all=", "-overwrite_original", str(path_obj)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                logger.warning(f"exiftool failed: {result.stderr}")
        except Exception as e:
            logger.warning(f"Failed to run exiftool: {e}")
    
    try:
        reader = PdfReader(str(path_obj))
        writer = PdfWriter()
        
        for page in reader.pages:
            # Remove annotations
            if "/Annots" in page:
                del page["/Annots"]
            writer.add_page(page)
        
        # Clear metadata
        writer.add_metadata({
            "/Producer": "",
            "/Creator": "",
            "/Title": "",
            "/Author": "",
            "/Subject": "",
            "/Keywords": ""
        })
        
        with open(output_obj, "wb") as f:
            writer.write(f)
            
        logger.info(f"Successfully scrubbed PDF: {path_obj} -> {output_obj}")
        return f"Scrubbed: {output_obj.name}"
        
    except Exception as e:
        logger.error(f"Failed to scrub PDF: {e}")
        raise RuntimeError(f"PDF scrubbing failed: {e}")


def delete_video(
    path: Union[str, Path], 
    out: Optional[Union[str, Path]] = None, 
    reencode: bool = False, 
    inplace: bool = True,
    backup: bool = False,
    preset: str = "medium"
) -> str:
    """Remove stream metadata from video using ffmpeg.

    Args:
        path: Input video path
        out: Output path (if None, creates .scrubbed variant)
        reencode: Re-encode streams for complete metadata removal
        inplace: Replace original file with scrubbed version
        backup: Create backup before scrubbing
        preset: FFmpeg encoding preset (ultrafast, fast, medium, slow, veryslow)
        
    Returns:
        Success message with output filename
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        RuntimeError: If ffmpeg is not available or fails
    """
    p = _check_file(path)
    
    # Check if ffmpeg is available
    ffmpeg_result = subprocess.run(
        ["which", "ffmpeg"], 
        capture_output=True, 
        text=True
    )
    if ffmpeg_result.returncode != 0:
        raise RuntimeError("ffmpeg not found. Please install ffmpeg to scrub video files.")
    
    if backup:
        _create_backup(p)
    
    out_path = Path(out) if out else p.with_name(p.stem + ".scrubbed" + p.suffix)
    
    cmd: List[str] = ["ffmpeg", "-y", "-i", str(p), "-map_metadata", "-1"]
    
    if reencode:
        cmd.extend(["-c:v", "libx264", "-preset", preset, "-crf", "20", "-c:a", "aac"])
        logger.info(f"Re-encoding video with preset: {preset}")
    else:
        cmd.extend(["-c", "copy"])
        
    cmd.append(str(out_path))
    
    try:
        r = _run(cmd, timeout=600)  # 10 minute timeout
        if r.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {r.stderr.strip()}")
    except Exception as e:
        logger.error(f"Video scrubbing failed: {e}")
        raise RuntimeError(f"Failed to scrub video: {e}")
    
    # Remove extended attributes if setfattr is available
    try:
        subprocess.run(
            ["setfattr", "-h", "-x", "user.comment", str(out_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5
        )
    except Exception:
        pass  # setfattr may not be available on all systems
    
    if inplace:
        os.replace(out_path, p)
        now = time.time()
        os.utime(p, (now, now))
        logger.info(f"Successfully scrubbed video (in-place): {p}")
        return f"Scrubbed: {p.name}"
    
    logger.info(f"Successfully scrubbed video: {p} -> {out_path}")
    return f"Scrubbed: {out_path.name}"


def delete_audio(
    path: Union[str, Path], 
    out: Optional[Union[str, Path]] = None, 
    reencode: bool = False, 
    inplace: bool = True,
    backup: bool = False,
    quality: str = "2"
) -> str:
    """Remove metadata from audio files using ffmpeg.

    Args:
        path: Input audio path
        out: Output path (if None, creates .scrubbed variant)
        reencode: Re-encode audio for complete metadata removal
        inplace: Replace original file with scrubbed version
        backup: Create backup before scrubbing
        quality: Audio quality for re-encoding (0-9, lower is better)
        
    Returns:
        Success message with output filename
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        RuntimeError: If ffmpeg is not available or fails
    """
    p = _check_file(path)
    
    # Check if ffmpeg is available
    ffmpeg_result = subprocess.run(
        ["which", "ffmpeg"], 
        capture_output=True, 
        text=True
    )
    if ffmpeg_result.returncode != 0:
        raise RuntimeError("ffmpeg not found. Please install ffmpeg to scrub audio files.")
    
    if backup:
        _create_backup(p)
    
    out_path = Path(out) if out else p.with_name(p.stem + ".scrubbed" + p.suffix)
    
    cmd: List[str] = ["ffmpeg", "-y", "-i", str(p), "-map_metadata", "-1"]
    
    if reencode:
        cmd.extend(["-c:a", "libmp3lame", "-q:a", quality])
        logger.info(f"Re-encoding audio with quality: {quality}")
    else:
        cmd.extend(["-c", "copy"])
        
    cmd.append(str(out_path))
    
    try:
        r = _run(cmd, timeout=300)  # 5 minute timeout
        if r.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {r.stderr.strip()}")
    except Exception as e:
        logger.error(f"Audio scrubbing failed: {e}")
        raise RuntimeError(f"Failed to scrub audio: {e}")
    
    # Remove extended attributes if setfattr is available
    try:
        subprocess.run(
            ["setfattr", "-h", "-x", "user.comment", str(out_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=5
        )
    except Exception:
        pass  # setfattr may not be available on all systems
    
    if inplace:
        os.replace(out_path, p)
        now = time.time()
        os.utime(p, (now, now))
        logger.info(f"Successfully scrubbed audio (in-place): {p}")
        return f"Scrubbed: {p.name}"
    
    logger.info(f"Successfully scrubbed audio: {p} -> {out_path}")
    return f"Scrubbed: {out_path.name}"


def delete_raw_metadata(
    path: Union[str, Path],
    backup: bool = False
) -> str:
    """Use ExifTool to wipe RAW camera metadata in-place.
    
    Args:
        path: Path to RAW camera file
        backup: Create backup before scrubbing
        
    Returns:
        Success message with filename
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        RuntimeError: If exiftool is not available or fails
    """
    p = _check_file(path)
    
    # Check if exiftool is available
    exiftool_result = subprocess.run(
        ["which", "exiftool"], 
        capture_output=True, 
        text=True
    )
    if exiftool_result.returncode != 0:
        raise RuntimeError("exiftool not found. Please install exiftool to scrub RAW files.")
    
    if backup:
        _create_backup(p)
    
    cmd = ["exiftool", "-overwrite_original", "-all=", str(p)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f"ExifTool failed: {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("ExifTool timed out after 60 seconds")
    except Exception as e:
        logger.error(f"RAW metadata removal failed: {e}")
        raise RuntimeError(f"Failed to remove RAW metadata: {e}")
    
    # Remove ExifTool backup file if it exists
    backup_file = p.with_suffix(p.suffix + "_original")
    if backup_file.exists():
        backup_file.unlink()
        
    logger.info(f"Successfully scrubbed RAW file: {p}")
    return f"Scrubbed: {p.name}"


def delete_docx(
    path: Union[str, Path], 
    output: Optional[Union[str, Path]] = None,
    backup: bool = False
) -> str:
    """Clear core properties of a .docx file.

    Requires `python-docx`. If not installed this raises ImportError.
    
    Args:
        path: Input DOCX path
        output: Output path (if None, creates .scrubbed variant)
        backup: Create backup before scrubbing
        
    Returns:
        Success message with output filename
        
    Raises:
        ImportError: If python-docx is not installed
        FileNotFoundError: If input file doesn't exist
        RuntimeError: If DOCX processing fails
    """
    if Document is None:  # pragma: no cover - optional dependency
        raise ImportError("python-docx is required for DOCX handling. Install with: pip install python-docx")
    
    p = _check_file(path)
    
    if backup:
        _create_backup(p)
    
    if output is None:
        output_obj = p.with_name(p.stem + ".scrubbed" + p.suffix)
    else:
        output_obj = Path(output)
    
    try:
        doc = Document(str(p))
        cp = doc.core_properties
        
        # Clear all common core properties
        cp.author = ""
        cp.title = ""
        cp.comments = ""
        cp.last_modified_by = ""
        cp.subject = ""
        cp.keywords = ""
        cp.category = ""
        
        doc.save(str(output_obj))
        logger.info(f"Successfully scrubbed DOCX: {p} -> {output_obj}")
        return f"Scrubbed: {output_obj.name}"
        
    except Exception as e:
        logger.error(f"DOCX scrubbing failed: {e}")
        raise RuntimeError(f"Failed to scrub DOCX: {e}")


def scrub_text_comments(
    path: Union[str, Path], 
    output: Optional[Union[str, Path]] = None, 
    prefixes: Optional[Sequence[str]] = None,
    backup: bool = False
) -> str:
    """Remove lines that look like comments from a plain-text file.

    This is a non-destructive helper: by default writes to a `.scrubbed` file.
    Useful for removing inline annotations from exported logs or code snippets.
    
    Args:
        path: Input text file path
        output: Output path (if None, creates .scrubbed variant)
        prefixes: Comment prefixes to remove (default: ["#", "//", ";"])
        backup: Create backup before scrubbing
        
    Returns:
        Success message with output filename
        
    Raises:
        FileNotFoundError: If input file doesn't exist
    """
    p = _check_file(path)
    
    if backup:
        _create_backup(p)
    
    prefixes = prefixes or ["#", "//", ";"]
    out = Path(output) if output else p.with_name(p.stem + ".scrubbed" + p.suffix)
    
    try:
        lines_removed = 0
        with open(p, "r", encoding="utf-8", errors="ignore") as inf, \
             open(out, "w", encoding="utf-8") as outf:
            for line in inf:
                stripped = line.lstrip()
                if any(stripped.startswith(pref) for pref in prefixes):
                    lines_removed += 1
                    continue
                outf.write(line)
        
        logger.info(f"Removed {lines_removed} comment lines from {p}")
        return f"Scrubbed: {out.name} ({lines_removed} lines removed)"
        
    except Exception as e:
        logger.error(f"Text comment removal failed: {e}")
        raise RuntimeError(f"Failed to scrub text comments: {e}")

