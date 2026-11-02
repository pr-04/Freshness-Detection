"""Hash and validate an already-approved extracted image tree; never downloads or edits data."""
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

from PIL import Image, ImageStat

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def dhash(path: Path) -> str:
    """Return a 64-bit difference hash for manual near-duplicate triage."""
    with Image.open(path) as im:
        gray = im.convert("L").resize((9, 8))
        px = list(gray.getdata())
    bits = [px[y * 9 + x] > px[y * 9 + x + 1] for y in range(8) for x in range(8)]
    return f"{sum(int(bit) << i for i, bit in enumerate(bits)):016x}"


def distance(a: str, b: str) -> int:
    return (int(a, 16) ^ int(b, 16)).bit_count()


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", required=True, type=Path, help="Extracted dataset root (read-only)")
    parser.add_argument("--inventory", required=True, type=Path, help="Existing local inventory CSV with sha256 column")
    parser.add_argument("--output-dir", required=True, type=Path, help="New output directory for reports")
    parser.add_argument("--near-distance", type=int, default=4, help="Maximum dHash Hamming distance for candidate pairs")
    args = parser.parse_args()

    if not args.dataset_root.is_dir():
        raise SystemExit(f"Dataset root does not exist: {args.dataset_root}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    for path in sorted(p for p in args.dataset_root.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS):
        rel = path.relative_to(args.dataset_root)
        parts = rel.parts
        category = parts[-3] if len(parts) >= 3 else "UNKNOWN"
        label = parts[-2] if len(parts) >= 2 else "UNKNOWN"
        row = {"relative_path": str(rel), "category_from_path": category, "label_from_path": label,
               "bytes": path.stat().st_size, "sha256": "", "dhash64": "", "width": "", "height": "",
               "format": "", "readable": False, "error": ""}
        try:
            row["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:
                im.load()
                row.update(width=im.width, height=im.height, format=im.format or "")
                small = im.convert("L").resize((64, 64))
                stat = ImageStat.Stat(small)
                row["blank_candidate"] = stat.stddev[0] < 5 and (max(small.getdata()) - min(small.getdata())) < 15
            row["dhash64"] = dhash(path)
            row["readable"] = True
        except Exception as exc:  # Keep damaged files in the report.
            row["error"] = f"{type(exc).__name__}: {exc}"
            row["blank_candidate"] = ""
        records.append(row)

    fields = ["relative_path", "category_from_path", "label_from_path", "bytes", "sha256", "dhash64",
              "width", "height", "format", "readable", "blank_candidate", "error"]
    write_csv(args.output_dir / "image_integrity_report.csv", records, fields)

    local_hashes: dict[str, list[str]] = {}
    with args.inventory.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            sha = (row.get("sha256") or row.get("recomputed_sha256") or "").strip().lower()
            if sha:
                local_hashes.setdefault(sha, []).append(row.get("relative_image_path") or row.get("original_image_path") or "")
    exact_groups: dict[str, list[dict]] = {}
    for row in records:
        if row["sha256"]:
            exact_groups.setdefault(row["sha256"], []).append(row)
    duplicates = [{"sha256": sha, "count": len(group), "paths": " | ".join(r["relative_path"] for r in group),
                   "labels": " | ".join(f'{r["category_from_path"]}/{r["label_from_path"]}' for r in group)}
                  for sha, group in exact_groups.items() if len(group) > 1]
    write_csv(args.output_dir / "exact_duplicate_groups.csv", duplicates, ["sha256", "count", "paths", "labels"])

    overlaps = [{"sha256": row["sha256"], "external_path": row["relative_path"],
                 "local_paths": " | ".join(local_hashes[row["sha256"]])}
                for row in records if row["sha256"] in local_hashes]
    write_csv(args.output_dir / "local_exact_overlap.csv", overlaps, ["sha256", "external_path", "local_paths"])

    readable = [r for r in records if r["readable"] and r["dhash64"]]
    # Index 5 disjoint hash bands. Any pair at Hamming distance <= 4 must
    # share at least one band, avoiding a quadratic scan over every image pair.
    buckets: dict[tuple[int, int], set[int]] = {}
    mask = (1 << 13) - 1
    for idx, row in enumerate(readable):
        value = int(row["dhash64"], 16)
        for band in range(5):
            chunk = (value >> (band * 13)) & mask
            buckets.setdefault((band, chunk), set()).add(idx)
    candidate_pairs: set[tuple[int, int]] = set()
    for indices in buckets.values():
        ordered = sorted(indices)
        for i, left_idx in enumerate(ordered):
            for right_idx in ordered[i + 1:]:
                candidate_pairs.add((left_idx, right_idx))
    pairs = []
    for left_idx, right_idx in candidate_pairs:
        left, right = readable[left_idx], readable[right_idx]
        d = distance(left["dhash64"], right["dhash64"])
        if d <= args.near_distance:
            pairs.append({"left_path": left["relative_path"], "right_path": right["relative_path"],
                          "hamming_distance": d, "left_label": f'{left["category_from_path"]}/{left["label_from_path"]}',
                          "right_label": f'{right["category_from_path"]}/{right["label_from_path"]}',
                          "interpretation": "candidate only; manual visual review required"})
    write_csv(args.output_dir / "near_duplicate_candidates.csv", pairs,
              ["left_path", "right_path", "hamming_distance", "left_label", "right_label", "interpretation"])
    print(f"Images scanned: {len(records)}; readable: {sum(bool(r['readable']) for r in records)}; "
          f"exact duplicate groups: {len(duplicates)}; exact local overlaps: {len(overlaps)}; "
          f"near-duplicate candidates: {len(pairs)}")


if __name__ == "__main__":
    main()
