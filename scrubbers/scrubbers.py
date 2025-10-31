import os, time, subprocess, magic, exifread
from pathlib import Path
from PIL import Image
from pypdf import PdfReader, PdfWriter

# helper
def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

def extract_meta(path):
    return subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(path)],
        capture_output=True, text=True
    ).stdout

def check_file(path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return p

# identify
def get_file_type(path):
    mime = magic.from_file(path, mime=True)
    desc = magic.from_file(path)
    return {"mime": mime, "description": desc}

# image
def read_image(path):
    path = check_file(path)
    metadata = {}
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

def scrub_image(ipath, opath=None):
    ipath = check_file(ipath)
    opath = Path(opath) if opath else Path(ipath).with_name(Path(ipath).stem + ".scrubbed" + Path(ipath).suffix)
    with Image.open(ipath) as img:
        data = list(img.getdata())
        clean = Image.new(img.mode, img.size)
        clean.putdata(data)
        clean.save(opath)
    return f"Scrubbed: {opath.name}"

# PDF
def delete_pdf(path, output=None):
    path = check_file(path)
    output = Path(output) if output else Path(path).with_name(Path(path).stem + ".scrubbed.pdf")
    subprocess.run(["exiftool", "-all=", "-overwrite_original", str(path)], stdout=subprocess.DEVNULL)
    reader = PdfReader(path)
    writer = PdfWriter()
    for page in reader.pages:
        page.pop("/Annots", None)
        writer.add_page(page)
    if "/AcroForm" in reader.trailer["/Root"]:
        reader.trailer["/Root"].pop("/AcroForm", None)
    writer.add_metadata({"/Producer": "", "/Creator": "", "/Title": "", "/Author": ""})
    with open(output, "wb") as f:
        writer.write(f)
    return f"Scrubbed: {output.name}"

# Video
def delete_video(path, out=None, reencode=False):
    p = check_file(path)
    out = Path(out) if out else p.with_name(p.stem + ".scrubbed" + p.suffix)
    cmd = ["ffmpeg", "-y", "-i", str(p), "-map_metadata", "-1"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "20", "-c:a", "aac"] if reencode else ["-c", "copy"]
    cmd.append(str(out))
    r = run(cmd)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {r.stderr.strip()}")
    subprocess.run(["setfattr", "-h", "-x", "user.comment", str(out)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.replace(out, p)
    now = time.time()
    os.utime(p, (now, now))
    return f"Scrubbed: {p.name}"

# Audio
def delete_audio(path, out=None, reencode=False):
    p = check_file(path)
    out = Path(out) if out else p.with_name(p.stem + ".scrubbed" + p.suffix)
    cmd = ["ffmpeg", "-y", "-i", str(p), "-map_metadata", "-1"]
    cmd += ["-c:a", "libmp3lame", "-q:a", "2"] if reencode else ["-c", "copy"]
    cmd.append(str(out))
    r = run(cmd)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {r.stderr.strip()}")
    subprocess.run(["setfattr", "-h", "-x", "user.comment", str(out)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.replace(out, p)
    now = time.time()
    os.utime(p, (now, now))
    return f"Scrubbed: {p.name}"

# RAW
def delete_raw_metadata(path):
    p = check_file(path)
    cmd = ["exiftool", "-overwrite_original", "-all=", str(p)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ExifTool failed: {result.stderr.strip()}")
    backup = p.with_suffix(p.suffix + "_original")
    if backup.exists():
        backup.unlink()
    return f"Scrubbed: {p.name}"
