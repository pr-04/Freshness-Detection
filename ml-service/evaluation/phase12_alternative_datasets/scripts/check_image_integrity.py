"""Read-only Pillow integrity and basic quality scan for an approved extracted image tree."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from PIL import Image, ImageStat

EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    args = parser.parse_args()
    if not args.dataset_root.is_dir():
        raise SystemExit(f"Dataset directory not found: {args.dataset_root}")

    rows = []
    for path in sorted(p for p in args.dataset_root.rglob("*") if p.is_file() and p.suffix.lower() in EXTS):
        row = {"relative_path": path.relative_to(args.dataset_root).as_posix(), "bytes": path.stat().st_size,
               "format": "", "width": "", "height": "", "readable": False,
               "blank_candidate": "", "error": ""}
        try:
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:
                im.load()
                row.update(format=im.format or "", width=im.width, height=im.height, readable=True)
                thumb = im.convert("L").resize((64, 64))
                pixels = list(thumb.getdata())
                row["blank_candidate"] = ImageStat.Stat(thumb).stddev[0] < 5 and max(pixels) - min(pixels) < 15
        except Exception as exc:
            row["error"] = f"{type(exc).__name__}: {exc}"
        rows.append(row)

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = ["relative_path", "bytes", "format", "width", "height", "readable", "blank_candidate", "error"]
    with args.output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Scanned {len(rows)} images; readable={sum(bool(r['readable']) for r in rows)}; "
          f"unreadable={sum(not r['readable'] for r in rows)}")


if __name__ == "__main__":
    main()
