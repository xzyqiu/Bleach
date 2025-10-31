import argparse
import sys
from pathlib import Path

from scrubbers import (
    delete_pdf,
    delete_video,
    delete_audio,
    delete_raw_metadata,
    scrub_image,
)

def main():
    parser = argparse.ArgumentParser(
        prog="scrubber",
        description="Privacy-oriented metadata scrubber for various file types.",
        epilog="Example: scrubber video myclip.mp4 --reencode",
    )

    subparsers = parser.add_subparsers(dest="type", required=True, help="File type to scrub")

    img_parser = subparsers.add_parser("image", help="Scrub metadata from an image")
    img_parser.add_argument("input", type=Path, help="Path to input image")
    img_parser.add_argument("output", type=Path, nargs="?", help="Output path (optional)")

    pdf_parser = subparsers.add_parser("pdf", help="Scrub metadata from a PDF")
    pdf_parser.add_argument("input", type=Path, help="Path to input PDF")
    pdf_parser.add_argument("output", type=Path, nargs="?", help="Output path (optional)")

    vid_parser = subparsers.add_parser("video", help="Scrub metadata from a video file")
    vid_parser.add_argument("input", type=Path, help="Path to input video")
    vid_parser.add_argument("--reencode", action="store_true", help="Re-encode to remove hidden metadata")

    aud_parser = subparsers.add_parser("audio", help="Scrub metadata from an audio file")
    aud_parser.add_argument("input", type=Path, help="Path to input audio")
    aud_parser.add_argument("--reencode", action="store_true", help="Re-encode audio for clean removal")

    raw_parser = subparsers.add_parser("raw", help="Scrub metadata from a raw camera file")
    raw_parser.add_argument("input", type=Path, help="Path to input raw image (e.g., .NEF, .CR2, .ARW)")

    args = parser.parse_args()

    try:
        if args.type == "image":
            out = args.output or args.input.with_name(args.input.stem + "_clean" + args.input.suffix)
            scrub_image(args.input, out)
            print(f"Image scrubbed: {out}")

        elif args.type == "pdf":
            out = args.output or args.input.with_name(args.input.stem + "_clean.pdf")
            delete_pdf(args.input, out)
            print(f"PDF scrubbed: {out}")

        elif args.type == "video":
            delete_video(args.input, reencode=args.reencode)
            print(f"Video scrubbed: {args.input}")

        elif args.type == "audio":
            delete_audio(args.input, reencode=args.reencode)
            print(f"Audio scrubbed: {args.input}")

        elif args.type == "raw":
            delete_raw_metadata(args.input)
            print(f"RAW file scrubbed: {args.input}")

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
