"""Read-only SHA-256/dHash inventory and overlap check for approved external images."""
from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

from PIL import Image

EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff"}


def dhash(path: Path) -> str:
    with Image.open(path) as im:
        px = list(im.convert("L").resize((9, 8)).getdata())
    bits = [px[y * 9 + x] > px[y * 9 + x + 1] for y in range(8) for x in range(8)]
    return f"{sum(int(value) << i for i, value in enumerate(bits)):016x}"


def band_keys(value: str):
    """Five bands ensure hashes <=4 bits apart share at least one 13-bit band."""
    number = int(value, 16)
    mask = (1 << 13) - 1
    return [(band, (number >> (band * 13)) & mask) for band in range(5)]


def near_pairs(left_rows, right_rows, max_pairs: int):
    """Return <=4-bit dHash candidates from two inventories using band lookup."""
    index = {}
    for idx, row in enumerate(right_rows):
        for key in band_keys(row["dhash64"]):
            index.setdefault(key, set()).add(idx)
    result = []
    seen = set()
    for left_idx, left in enumerate(left_rows):
        candidates = set()
        for key in band_keys(left["dhash64"]):
            candidates.update(index.get(key, ()))
        for right_idx in candidates:
            if left_rows is right_rows and right_idx <= left_idx:
                continue
            right = right_rows[right_idx]
            if left["sha256"] == right["sha256"]:
                continue  # Exact matches have their own report.
            pair_key = (left_idx, right_idx)
            if pair_key in seen:
                continue
            seen.add(pair_key)
            distance = (int(left["dhash64"], 16) ^ int(right["dhash64"], 16)).bit_count()
            if distance <= 4:
                if len(result) >= max_pairs:
                    raise SystemExit(f"Near-duplicate candidate cap ({max_pairs}) reached; no pair report written. "
                                     "Review source volume or raise --max-candidate-pairs explicitly.")
                result.append({"external_path": left["relative_path"],
                               "comparison_path": right["relative_path"],
                               "comparison_kind": right.get("record_kind", "external"),
                               "hamming_distance": distance,
                               "interpretation": "candidate only; manual visual review required"})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--inventory", required=True, type=Path, help="Local inventory CSV containing sha256")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Root for inventory relative paths")
    parser.add_argument("--max-candidate-pairs", type=int, default=2000000,
                        help="Safety cap for dHash pairs; raise explicitly if needed")
    args = parser.parse_args()
    if not args.dataset_root.is_dir():
        raise SystemExit(f"Dataset directory not found: {args.dataset_root}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for path in sorted(p for p in args.dataset_root.rglob("*") if p.is_file() and p.suffix.lower() in EXTS):
        digest = hashlib.sha256()
        with path.open("rb") as image_file:
            for chunk in iter(lambda: image_file.read(1024 * 1024), b""):
                digest.update(chunk)
        parts = path.relative_to(args.dataset_root).parts
        records.append({"relative_path": path.relative_to(args.dataset_root).as_posix(),
                        "category_from_path": parts[-3] if len(parts) >= 3 else "UNKNOWN",
                        "label_from_path": parts[-2] if len(parts) >= 2 else "UNKNOWN",
                        "sha256": digest.hexdigest(), "dhash64": dhash(path)})

    local_paths = {}
    with args.inventory.open(newline="", encoding="utf-8-sig") as f:
        local = {}
        for row in csv.DictReader(f):
            value = (row.get("sha256") or row.get("recomputed_sha256") or "").strip().lower()
            if value:
                local.setdefault(value, []).append(row.get("relative_image_path") or row.get("original_image_path") or "")
                path_value = row.get("relative_image_path") or row.get("original_image_path") or ""
                if path_value:
                    local_paths.setdefault(value, path_value)

    exact = {}
    for row in records:
        exact.setdefault(row["sha256"], []).append(row)
    duplicate_rows = [{"sha256": key, "count": len(group),
                       "paths": " | ".join(row["relative_path"] for row in group),
                       "labels": " | ".join(row["category_from_path"] + "/" + row["label_from_path"] for row in group)}
                      for key, group in exact.items() if len(group) > 1]
    overlap_rows = [{"sha256": row["sha256"], "external_path": row["relative_path"],
                     "local_paths": " | ".join(local[row["sha256"]])}
                    for row in records if row["sha256"] in local]
    local_records = []
    for sha, relpath in local_paths.items():
        path = args.project_root / relpath
        if path.is_file():
            try:
                local_records.append({"relative_path": str(relpath), "sha256": sha,
                                      "dhash64": dhash(path), "record_kind": "local"})
            except Exception:
                continue
    near_external = near_pairs(records, records, args.max_candidate_pairs)
    near_external = [row for row in near_external if row["external_path"] < row["comparison_path"]]
    near_local = near_pairs(records, local_records, args.max_candidate_pairs)
    outputs = [("image_hashes.csv", records, ["relative_path", "category_from_path", "label_from_path", "sha256", "dhash64"]),
               ("exact_duplicate_groups.csv", duplicate_rows, ["sha256", "count", "paths", "labels"]),
               ("local_exact_overlap.csv", overlap_rows, ["sha256", "external_path", "local_paths"]),
               ("near_duplicate_candidates.csv", near_external + near_local,
                ["external_path", "comparison_path", "comparison_kind", "hamming_distance", "interpretation"])]
    for name, rows, fields in outputs:
        with (args.output_dir / name).open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    print(f"Hashed {len(records)} image files; external exact groups={len(duplicate_rows)}; "
          f"local exact overlaps={len(overlap_rows)}; near-duplicate candidates="
          f"{len(near_external) + len(near_local)}. Candidates require visual review.")


if __name__ == "__main__":
    main()
