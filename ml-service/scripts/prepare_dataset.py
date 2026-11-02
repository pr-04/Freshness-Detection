"""Validate the raw dataset and export reproducible train/val/test folders."""

import argparse
import csv
import hashlib
import json
import random
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

from inspect_dataset import (
    DATASETS_DIR,
    EXPECTED_FRUIT_CATEGORY_COUNT,
    REPORT_PATH,
    get_image_bytes,
    inspect_image,
    label_to_text,
    load_raw_dataset,
)

PROJECT_DIR = Path(__file__).resolve().parents[1]
PREPARED_DIR = DATASETS_DIR / "prepared"
MANIFEST_PATH = PREPARED_DIR / "manifest.csv"
RANDOM_SEED = 42
SPLIT_RATIOS = {"train": 0.70, "val": 0.15, "test": 0.15}
VALID_LABELS = {"fresh", "rotten"}


def get_extension(image_format):
    """Map the decoded image format to a conventional filename extension."""
    return {
        "JPEG": ".jpg",
        "JPG": ".jpg",
        "PNG": ".png",
        "WEBP": ".webp",
        "BMP": ".bmp",
        "GIF": ".gif",
        "TIFF": ".tiff",
    }.get(image_format.upper(), ".img")


def allocate_split_targets(row_count):
    """Get integer row targets close to 70/15/15 for one stratum."""
    train_count = round(row_count * SPLIT_RATIOS["train"])
    val_count = round(row_count * SPLIT_RATIOS["val"])
    if train_count + val_count > row_count:
        val_count = row_count - train_count
    return {
        "train": train_count,
        "val": val_count,
        "test": row_count - train_count - val_count,
    }


def assign_group_splits(records, seed=RANDOM_SEED):
    """Assign exact-byte duplicate groups to one split, stratifying by fruit/label."""
    rows_by_hash = defaultdict(list)
    for record in records:
        rows_by_hash[record["sha256"]].append(record)

    groups_by_stratum = defaultdict(list)
    duplicate_label_conflicts = []
    duplicate_category_conflicts = []
    for image_hash, group in rows_by_hash.items():
        strata = Counter((item["fruit_category"], item["freshness_label"]) for item in group)
        primary_stratum = sorted(strata, key=lambda value: (-strata[value], value))[0]
        groups_by_stratum[primary_stratum].append(image_hash)

        if len({item["freshness_label"] for item in group}) > 1:
            duplicate_label_conflicts.append(image_hash)
        if len({item["fruit_category"] for item in group}) > 1:
            duplicate_category_conflicts.append(image_hash)

    rng = random.Random(seed)
    group_splits = {}
    stratum_targets = {}
    stratum_actual = defaultdict(Counter)

    for stratum in sorted(groups_by_stratum):
        image_hashes = groups_by_stratum[stratum]
        rng.shuffle(image_hashes)
        row_count = sum(len(rows_by_hash[image_hash]) for image_hash in image_hashes)
        targets = allocate_split_targets(row_count)
        stratum_targets[f"{stratum[0]}|{stratum[1]}"] = targets

        for image_hash in image_hashes:
            group_size = len(rows_by_hash[image_hash])

            def split_cost(candidate):
                cost = 0.0
                for split in SPLIT_RATIOS:
                    projected = stratum_actual[stratum][split]
                    if split == candidate:
                        projected += group_size
                    target = targets[split]
                    scale = max(1, target)
                    cost += ((projected - target) / scale) ** 2
                return cost

            chosen_split = min(SPLIT_RATIOS, key=split_cost)
            group_splits[image_hash] = chosen_split
            stratum_actual[stratum][chosen_split] += group_size

    row_splits = {
        record["source_row_index"]: group_splits[record["sha256"]]
        for record in records
    }
    return rows_by_hash, group_splits, row_splits, {
        "exact_duplicate_groups": sum(1 for group in rows_by_hash.values() if len(group) > 1),
        "duplicate_rows_beyond_first": sum(len(group) - 1 for group in rows_by_hash.values()),
        "duplicate_groups_with_conflicting_labels": duplicate_label_conflicts,
        "duplicate_groups_with_conflicting_fruit_categories": duplicate_category_conflicts,
        "hashes_crossing_splits": 0,
        "stratum_target_counts": stratum_targets,
        "stratum_actual_counts": {
            f"{fruit}|{label}": dict(counts)
            for (fruit, label), counts in sorted(stratum_actual.items())
        },
    }


def prepare_dataset(force=False):
    """Create image folders and a CSV manifest without training any model."""
    if not REPORT_PATH.is_file():
        raise RuntimeError(
            "Run `python scripts/inspect_dataset.py` first to inspect and verify the raw configuration."
        )
    inspection_report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    if inspection_report.get("source", {}).get("configuration") != "raw":
        raise RuntimeError("The inspection report does not describe the raw configuration.")

    if PREPARED_DIR.exists() and any(PREPARED_DIR.iterdir()):
        if not force:
            raise RuntimeError(
                f"{PREPARED_DIR} already contains files. Use --force to replace the prepared output."
            )
        shutil.rmtree(PREPARED_DIR)

    dataset = load_raw_dataset()
    label_feature = dataset.features.get("label")
    records = []
    skipped = []

    for index, row in enumerate(dataset):
        label = label_to_text(row.get("label"), label_feature)
        fruit_value = row.get("fruit_type")
        fruit_category = str(fruit_value).strip().lower() if fruit_value is not None else ""
        if label not in VALID_LABELS:
            skipped.append({"source_row_index": index, "reason": "missing_or_invalid_label", "label": label})
            continue
        if not fruit_category:
            skipped.append({"source_row_index": index, "reason": "missing_fruit_category"})
            continue

        try:
            image_bytes = get_image_bytes(row.get("image"))
            image_info = inspect_image(image_bytes)
        except Exception as error:
            skipped.append({"source_row_index": index, "reason": "unreadable_image", "error": str(error)})
            continue

        records.append({
            "source_row_index": index,
            "freshness_label": label,
            "fruit_category": fruit_category,
            "sha256": hashlib.sha256(image_bytes).hexdigest(),
            "extension": get_extension(image_info["format"]),
        })

    if not records:
        raise RuntimeError("No valid labeled images were found to prepare.")

    _, _, row_splits, duplicate_report = assign_group_splits(records)
    for split in SPLIT_RATIOS:
        for label in sorted(VALID_LABELS):
            (PREPARED_DIR / split / label).mkdir(parents=True, exist_ok=True)

    manifest_rows = []
    split_label_counts = {split: Counter() for split in SPLIT_RATIOS}
    split_fruit_label_counts = {
        split: defaultdict(Counter) for split in SPLIT_RATIOS
    }
    for record in records:
        index = record["source_row_index"]
        split = row_splits[index]
        # Re-read the already-cached row instead of holding gigabytes of image
        # bytes in memory while assigning the splits.
        image_bytes = get_image_bytes(dataset[index]["image"])
        if hashlib.sha256(image_bytes).hexdigest() != record["sha256"]:
            raise RuntimeError(f"Image bytes changed while preparing source row {index}.")

        filename = (
            f"{record['fruit_category']}_{index:05d}_{record['sha256'][:12]}"
            f"{record['extension']}"
        )
        output_path = PREPARED_DIR / split / record["freshness_label"] / filename
        output_path.write_bytes(image_bytes)
        relative_path = output_path.relative_to(PROJECT_DIR).as_posix()
        manifest_rows.append({
            "image_path": relative_path,
            "freshness_label": record["freshness_label"],
            "fruit_category": record["fruit_category"],
            "split": split,
            "source_row_index": index,
            "sha256": record["sha256"],
        })
        split_label_counts[split][record["freshness_label"]] += 1
        split_fruit_label_counts[split][record["fruit_category"]][record["freshness_label"]] += 1

    fieldnames = [
        "image_path",
        "freshness_label",
        "fruit_category",
        "split",
        "source_row_index",
        "sha256",
    ]
    with MANIFEST_PATH.open("w", newline="", encoding="utf-8") as manifest_file:
        writer = csv.DictWriter(manifest_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest_rows)

    paths = [row["image_path"] for row in manifest_rows]
    path_duplicates = len(paths) - len(set(paths))
    hash_splits = defaultdict(set)
    for row in manifest_rows:
        hash_splits[row["sha256"]].add(row["split"])
    hash_leaks = sum(1 for splits in hash_splits.values() if len(splits) > 1)
    missing_output_files = [
        row["image_path"]
        for row in manifest_rows
        if not (PROJECT_DIR / Path(row["image_path"])).is_file()
    ]
    invalid_output_paths = [
        row["image_path"]
        for row in manifest_rows
        if Path(row["image_path"]).parent.as_posix()
        != f"datasets/prepared/{row['split']}/{row['freshness_label']}"
    ]
    written_file_counts = Counter(
        path.parent.parent.name for path in PREPARED_DIR.rglob("*") if path.is_file()
    )
    expected_file_counts = Counter({
        split: sum(split_label_counts[split].values()) for split in SPLIT_RATIOS
    })
    verification = {
        "manifest_rows": len(manifest_rows),
        "missing_output_files": len(missing_output_files),
        "invalid_output_paths": len(invalid_output_paths),
        "missing_labels": sum(not row["freshness_label"] for row in manifest_rows),
        "duplicate_manifest_paths": path_duplicates,
        "exact_hashes_crossing_splits": hash_leaks,
        "folder_counts_match_manifest": written_file_counts == expected_file_counts,
    }
    if (
        verification["manifest_rows"] != len(records)
        or verification["missing_output_files"]
        or verification["invalid_output_paths"]
        or verification["missing_labels"]
        or verification["duplicate_manifest_paths"]
        or verification["exact_hashes_crossing_splits"]
        or not verification["folder_counts_match_manifest"]
    ):
        raise RuntimeError(f"Prepared output verification failed: {verification}")

    preparation_report = {
        "random_seed": RANDOM_SEED,
        "requested_split_ratios": SPLIT_RATIOS,
        "source_records": len(dataset),
        "valid_records_exported": len(manifest_rows),
        "skipped_records": len(skipped),
        "skipped_record_reasons": dict(Counter(item["reason"] for item in skipped)),
        "split_counts": {
            split: {
                "total": sum(split_label_counts[split].values()),
                "freshness_labels": dict(sorted(split_label_counts[split].items())),
                "fruit_category_and_label_counts": {
                    fruit: dict(sorted(counts.items()))
                    for fruit, counts in sorted(split_fruit_label_counts[split].items())
                },
            }
            for split in SPLIT_RATIOS
        },
        "duplicate_check": {
            **duplicate_report,
            "hashes_crossing_splits": hash_leaks,
            "duplicate_manifest_image_paths": path_duplicates,
            "method": "SHA-256 of encoded image bytes; exact duplicates are assigned together.",
            "comprehensive": False,
            "limitation": "Perceptual duplicates and visually similar re-encodings were not checked.",
        },
        "missing_labels_in_exported_manifest": sum(
            1 for row in manifest_rows if not row["freshness_label"]
        ),
        "verification": verification,
        "manifest": MANIFEST_PATH.relative_to(PROJECT_DIR).as_posix(),
        "skipped_records_detail": skipped,
        "training_performed": False,
    }

    inspection_report["preparation"] = preparation_report
    inspection_report["dataset_coverage_note"] = (
        f"Freshness labels are limited to {', '.join(sorted(VALID_LABELS))}. "
        f"The dataset contains {len(inspection_report.get('fruit_categories', []))} observed fruit categories; "
        f"the card declared {EXPECTED_FRUIT_CATEGORY_COUNT}."
    )
    REPORT_PATH.write_text(
        json.dumps(inspection_report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(preparation_report, indent=2, ensure_ascii=False))
    print(f"\nPrepared images saved under: {PREPARED_DIR}")
    print(f"Manifest saved to: {MANIFEST_PATH}")
    print(f"Dataset report updated: {REPORT_PATH}")
    return preparation_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace the existing prepared output directory before exporting.",
    )
    arguments = parser.parse_args()
    try:
        prepare_dataset(force=arguments.force)
    except Exception as error:
        print(f"Dataset preparation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
