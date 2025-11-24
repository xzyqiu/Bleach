"""Bleach - Privacy-oriented metadata scrubber.

This package provides tools to remove metadata from various file types
including images, PDFs, videos, audio files, and documents.
"""

__version__ = "1.0.0"
__author__ = "xzyqiu"
__license__ = "MIT"

from .scrubbers import (
    delete_audio,
    delete_docx,
    delete_pdf,
    delete_raw_metadata,
    delete_video,
    get_file_type,
    read_image,
    scrub_image,
    scrub_text_comments,
)

__all__ = [
    "scrub_image",
    "delete_pdf",
    "delete_video",
    "delete_audio",
    "delete_raw_metadata",
    "delete_docx",
    "scrub_text_comments",
    "read_image",
    "get_file_type",
]
