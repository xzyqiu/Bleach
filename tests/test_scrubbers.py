import os
import tempfile
from pathlib import Path

import pytest

from scrubbers import scrub_image, scrub_text_comments, delete_docx


def test_scrub_image_creates_file():
    # create a small RGB image
    from PIL import Image

    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "test.png"
        img = Image.new("RGB", (10, 10), color=(123, 222, 111))
        img.save(p)

        out = Path(td) / "test.scrubbed.png"
        result = scrub_image(p, out)
        assert out.exists()
        assert "Scrubbed" in result


def test_scrub_text_comments_removes_prefixes():
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "sample.txt"
        p.write_text("# comment line\nactual\n// another comment\nkeep\n")
        out = Path(td) / "sample.scrubbed.txt"
        res = scrub_text_comments(p, out, prefixes=["#", "//"]) 
        assert out.exists()
        content = out.read_text()
        assert "comment" not in content
        assert "actual" in content
        assert "keep" in content


def test_delete_docx_clears_core_properties(tmp_path):
    # skip if python-docx is missing
    try:
        from docx import Document
    except Exception:
        pytest.skip("python-docx not installed")

    p = tmp_path / "test.docx"
    doc = Document()
    doc.add_paragraph("hello")
    doc.core_properties.author = "Jane"
    doc.core_properties.title = "Title"
    doc.save(str(p))

    out = tmp_path / "test.scrubbed.docx"
    result = delete_docx(p, out)
    assert out.exists()
    new = Document(str(out))
    assert (new.core_properties.author or "") == ""
    assert (new.core_properties.title or "") == ""
