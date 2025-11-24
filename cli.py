#!/usr/bin/env python3
"""Command-line interface for Bleach metadata scrubber.

This module provides a user-friendly CLI for removing metadata from various file types.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import NoReturn, Optional

from tqdm import tqdm

from scrubbers import (
    delete_audio,
    delete_docx,
    delete_pdf,
    delete_raw_metadata,
    delete_video,
    scrub_image,
    scrub_text_comments,
)

# Version information
__version__ = "1.0.0"

# Configure logging
def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=level
    )

logger = logging.getLogger(__name__)

def error_exit(message: str) -> NoReturn:
    """Print error message and exit with code 1."""
    print(f"❌ Error: {message}", file=sys.stderr)
    sys.exit(1)


def success_message(message: str) -> None:
    """Print success message."""
    print(f"✓ {message}")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="bleach",
        description="🧼 Bleach - Privacy-oriented metadata scrubber for various file types.",
        epilog="Examples:\n"
               "  bleach image photo.jpg --backup\n"
               "  bleach video movie.mp4 --reencode --preset fast\n"
               "  bleach pdf document.pdf --output clean.pdf\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"Bleach {__version__}"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    subparsers = parser.add_subparsers(dest="type", required=True, help="File type to scrub")

    # Common arguments for all subcommands
    def add_common_args(subparser: argparse.ArgumentParser) -> None:
        """Add common arguments to a subparser."""
        subparser.add_argument(
            "--backup",
            action="store_true",
            help="Create a backup of the original file before scrubbing"
        )
    
    # Image scrubber
    img_parser = subparsers.add_parser(
        "image", 
        help="Scrub metadata from an image",
        description="Remove EXIF, XMP, and other metadata from image files"
    )
    img_parser.add_argument("input", type=Path, help="Path to input image")
    img_parser.add_argument("output", type=Path, nargs="?", help="Output path (optional)")
    add_common_args(img_parser)

    # PDF scrubber
    pdf_parser = subparsers.add_parser(
        "pdf", 
        help="Scrub metadata from a PDF",
        description="Remove author, tracking data, and annotations from PDF files"
    )
    pdf_parser.add_argument("input", type=Path, help="Path to input PDF")
    pdf_parser.add_argument("output", type=Path, nargs="?", help="Output path (optional)")
    add_common_args(pdf_parser)

    # Video scrubber
    vid_parser = subparsers.add_parser(
        "video", 
        help="Scrub metadata from a video file",
        description="Remove hidden metadata from video files using ffmpeg"
    )
    vid_parser.add_argument("input", type=Path, help="Path to input video")
    vid_parser.add_argument(
        "--reencode", 
        action="store_true", 
        help="Re-encode video for complete metadata removal (slower)"
    )
    vid_parser.add_argument(
        "--preset",
        type=str,
        default="medium",
        choices=["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"],
        help="FFmpeg encoding preset (default: medium)"
    )
    vid_parser.add_argument(
        "--no-inplace",
        action="store_true",
        help="Don't replace the original file (creates .scrubbed variant)"
    )
    add_common_args(vid_parser)

    # Audio scrubber
    aud_parser = subparsers.add_parser(
        "audio", 
        help="Scrub metadata from an audio file",
        description="Remove ID3 tags and other metadata from audio files"
    )
    aud_parser.add_argument("input", type=Path, help="Path to input audio")
    aud_parser.add_argument(
        "--reencode", 
        action="store_true", 
        help="Re-encode audio for complete metadata removal"
    )
    aud_parser.add_argument(
        "--quality",
        type=str,
        default="2",
        choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
        help="Audio quality for re-encoding (0=best, 9=worst, default: 2)"
    )
    aud_parser.add_argument(
        "--no-inplace",
        action="store_true",
        help="Don't replace the original file (creates .scrubbed variant)"
    )
    add_common_args(aud_parser)

    # RAW scrubber
    raw_parser = subparsers.add_parser(
        "raw", 
        help="Scrub metadata from a raw camera file",
        description="Remove metadata from RAW camera files (.NEF, .CR2, .ARW, etc.)"
    )
    raw_parser.add_argument("input", type=Path, help="Path to input raw image (e.g., .NEF, .CR2, .ARW)")
    add_common_args(raw_parser)

    # DOCX scrubber
    docx_parser = subparsers.add_parser(
        "docx", 
        help="Scrub metadata from a Microsoft Word .docx file",
        description="Remove author, title, and other properties from DOCX files"
    )
    docx_parser.add_argument("input", type=Path, help="Path to input .docx file")
    docx_parser.add_argument("output", type=Path, nargs="?", help="Output path (optional)")
    add_common_args(docx_parser)

    # Text scrubber
    text_parser = subparsers.add_parser(
        "text", 
        help="Remove comment lines from a text file",
        description="Strip comment lines from plain text files"
    )
    text_parser.add_argument("input", type=Path, help="Path to input text file")
    text_parser.add_argument("output", type=Path, nargs="?", help="Output path (optional)")
    text_parser.add_argument(
        "--prefixes", 
        type=str, 
        help="Comma-separated comment prefixes (default: '#,//,;')"
    )
    add_common_args(text_parser)

    args = parser.parse_args()
    
    # Setup logging based on verbosity
    setup_logging(args.verbose)
    
    # Validate input file exists
    if not args.input.exists():
        error_exit(f"Input file not found: {args.input}")
    
    if args.input.is_dir():
        error_exit(f"Input path is a directory, not a file: {args.input}")

    try:
        # Get backup flag if available
        backup = getattr(args, 'backup', False)
        
        with tqdm(total=100, desc=f"Scrubbing {args.input.name}", unit="%", disable=not sys.stdout.isatty()) as pbar:
            pbar.update(10)  # Starting
            
            if args.type == "image":
                result = scrub_image(args.input, args.output, backup=backup)
                pbar.update(90)
                success_message(result)

            elif args.type == "pdf":
                result = delete_pdf(args.input, args.output, backup=backup)
                pbar.update(90)
                success_message(result)

            elif args.type == "video":
                inplace = not getattr(args, 'no_inplace', False)
                preset = getattr(args, 'preset', 'medium')
                result = delete_video(
                    args.input, 
                    reencode=args.reencode,
                    inplace=inplace,
                    backup=backup,
                    preset=preset
                )
                pbar.update(90)
                success_message(result)

            elif args.type == "audio":
                inplace = not getattr(args, 'no_inplace', False)
                quality = getattr(args, 'quality', '2')
                result = delete_audio(
                    args.input, 
                    reencode=args.reencode,
                    inplace=inplace,
                    backup=backup,
                    quality=quality
                )
                pbar.update(90)
                success_message(result)

            elif args.type == "raw":
                result = delete_raw_metadata(args.input, backup=backup)
                pbar.update(90)
                success_message(result)

            elif args.type == "docx":
                result = delete_docx(args.input, args.output, backup=backup)
                pbar.update(90)
                success_message(result)

            elif args.type == "text":
                prefixes = args.prefixes.split(",") if args.prefixes else None
                result = scrub_text_comments(args.input, args.output, prefixes, backup=backup)
                pbar.update(90)
                success_message(result)

            else:
                parser.print_help()
                sys.exit(1)

    except KeyboardInterrupt:
        error_exit("Operation cancelled by user")
    except FileNotFoundError as e:
        error_exit(str(e))
    except RuntimeError as e:
        error_exit(str(e))
    except Exception as e:
        if args.verbose:
            logger.exception("Unexpected error occurred")
        error_exit(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
