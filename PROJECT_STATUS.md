# Project status

Last updated: 2025-11-18

Status: Active development (early stage)

Completed
- Basic scrubbing functionality for images, PDFs, audio, video, and RAW files.
- Refactored `scrubbers/scrubbers.py` to add clearer helpers and docstrings.
- Added CLI commands in `cli.py` for: `image`, `pdf`, `video`, `audio`, `raw`.
- Added support for `docx` core property scrubbing and `text` comment-line removal.
- Added unit tests for image/text/docx handling under `tests/`.

In progress
- Running tests in CI and improving test coverage.
- Making `inplace` behavior configurable via CLI flags.

Next steps
- Add GitHub Actions workflow to run `pytest` on push/PR.
- Expand support for other document formats (ODT, RTF) if needed.
- Add integration tests for ffmpeg/exiftool flows (requires system binaries in CI).
- Add optional `--backup` flag to keep originals when scrubbing.

Known issues / constraints
- Some functionality depends on external binaries (`ffmpeg`, `exiftool`, `setfattr`).
- Tests that require `python-docx` will skip if the dependency is not installed.
- Running heavy re-encodes in CI can be slow and may require smaller fixtures.

How to run locally
1. Create a virtualenv and install requirements:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

2. Run tests:

```sh
pytest -q
```
