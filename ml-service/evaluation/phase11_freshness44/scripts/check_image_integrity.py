"""Read-only Pillow integrity/dimension scan for an already-approved extracted image tree."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from PIL import Image, ImageStat

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", required=True, type=Path, help="Extracted dataset root (read-only)")
    parser.add_argument("--output-csv", required=True, type=Path)
    args = parser.parse_args()
    if not args.dataset_root.is_dir():
        raise SystemExit(f"Dataset root does not exist: {args.dataset_root}")

    rows = []
    for path in sorted(p for p in args.dataset_root.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS):
        row = {"relative_path": str(path.relative_to(args.dataset_root)), "bytes": path.stat().st_size,
               "readable": False, "width": "", "height": "", "format": "", "blank_candidate": "", "error": ""}
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                image.load()
                row.update(readable=True, width=image.width, height=image.height, format=image.format or "")
                thumb = image.convert("L").resize((64, 64))
                stat = ImageStat.Stat(thumb)
                pixels = list(thumb.getdata())
                row["blank_candidate"] = stat.stddev[0] < 5 and (max(pixels) - min(pixels)) < 15
        except Exception as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
        rows.append(row)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = ["relative_path", "bytes", "readable", "width", "height", "format", "blank_candidate", "error"]
    with args.output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    good = sum(bool(row["readable"]) for row in rows)
    print(f"Images scanned: {len(rows)}; readable: {good}; unreadable: {len(rows) - good}")


if __name__ == "__main__":
    main()
