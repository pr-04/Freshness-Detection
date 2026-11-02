"""Inspect the raw Hugging Face Fresh Rotten Fruit dataset."""

import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from PIL import Image as PillowImage

DATASET_ID = "Project-AgML/fresh_rotten_fruit_classification"
DATASET_URL = f"https://huggingface.co/datasets/{DATASET_ID}"
CONFIG_NAME = "raw"
SPLIT_NAME = "train"
DATASET_REVISION = "65d4488931fef98c76bf996180064397fbe7da34"
RAW_PARQUET_FILES = [
    "raw/train-00000-of-00004.parquet",
    "raw/train-00001-of-00004.parquet",
    "raw/train-00002-of-00004.parquet",
    "raw/train-00003-of-00004.parquet",
]
EXPECTED_IMAGE_COUNT = 3200
EXPECTED_FRUIT_CATEGORY_COUNT = 8
DATASETS_DIR = Path(__file__).resolve().parents[1] / "datasets"
RAW_DIR = DATASETS_DIR / "raw"
# Keep this folder name short: Hugging Face builds long cache-lock filenames,
# and Windows has a legacy path-length limit. Both caches remain under raw/.
CACHE_DIR = RAW_DIR / "c"
REPORT_PATH = DATASETS_DIR / "dataset_report.json"


def load_raw_dataset():
    """Load only the raw configuration and keep image bytes undecoded."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    os.environ["HF_HOME"] = str(CACHE_DIR)
    os.environ["HF_HUB_CACHE"] = str(CACHE_DIR / "hub")
    os.environ["HF_DATASETS_CACHE"] = str(CACHE_DIR)
    # Use the regular Hub HTTP path. It is more dependable in restricted
    # networks where the optional Xet transfer can remain at zero bytes.
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

    try:
        from datasets import Image as DatasetImage
        from datasets import load_dataset
        from huggingface_hub import hf_hub_download
    except ImportError as error:
        raise RuntimeError(
            "The Hugging Face datasets package is missing. Run: pip install -r requirements.txt"
        ) from error

    try:
        # The Hub's raw config is stored as these four Parquet shards. Download
        # only those paths, then let `datasets` read the local Parquet files.
        # This avoids fetching the separate augmented directory and works around
        # the high-level remote loader stalling on this Windows environment.
        parquet_paths = [
            hf_hub_download(
                repo_id=DATASET_ID,
                filename=filename,
                repo_type="dataset",
                revision=DATASET_REVISION,
                cache_dir=str(CACHE_DIR / "hub"),
            )
            for filename in RAW_PARQUET_FILES
        ]
        dataset = load_dataset(
            "parquet",
            data_files={SPLIT_NAME: parquet_paths},
            split=SPLIT_NAME,
            cache_dir=str(CACHE_DIR),
        )
        if "image" not in dataset.column_names:
            raise RuntimeError(f"Expected an image column; found {dataset.column_names}.")
        return dataset.cast_column("image", DatasetImage(decode=False))
    except Exception as error:
        raise RuntimeError(
            f"Could not load the {CONFIG_NAME!r} dataset configuration: {error}"
        ) from error


def label_to_text(value, label_feature=None):
    """Convert a ClassLabel ID or string to a normalized freshness label."""
    if value is None:
        return None
    if hasattr(label_feature, "int2str"):
        try:
            value = label_feature.int2str(int(value))
        except (TypeError, ValueError, OverflowError):
            pass
    text = str(value).strip().lower()
    return text or None


def get_image_bytes(value):
    """Get encoded image bytes from a decoded/undecoded datasets Image value."""
    if isinstance(value, PillowImage.Image):
        buffer = BytesIO()
        image_format = value.format or "JPEG"
        value.save(buffer, format=image_format)
        return buffer.getvalue()
    if isinstance(value, dict):
        image_bytes = value.get("bytes")
        if image_bytes:
            return bytes(image_bytes)
        image_path = value.get("path")
        if image_path:
            path = Path(image_path)
            if path.is_file():
                return path.read_bytes()
    raise ValueError("The image row did not contain readable bytes or a local path.")


def inspect_image(image_bytes):
    """Fully decode an image and return dimensions and its actual format."""
    with PillowImage.open(BytesIO(image_bytes)) as image:
        image.load()
        return {
            "width": int(image.width),
            "height": int(image.height),
            "format": str(image.format or "unknown").upper(),
        }


def inspect_dataset():
    """Count rows, labels, fruit types, image formats, and image dimensions."""
    dataset = load_raw_dataset()
    features = dataset.features
    label_feature = features.get("label")
    label_counts = Counter()
    fruit_counts = Counter()
    joint_counts = defaultdict(Counter)
    format_counts = Counter()
    dimension_counts = Counter()
    unreadable = []
    missing_label_indices = []
    missing_fruit_indices = []
    invalid_label_indices = []
    widths = []
    heights = []
    usable_images = 0

    for index, row in enumerate(dataset):
        label = label_to_text(row.get("label"), label_feature)
        fruit_value = row.get("fruit_type")
        fruit = str(fruit_value).strip().lower() if fruit_value is not None else ""
        if not label:
            missing_label_indices.append(index)
        elif label not in {"fresh", "rotten"}:
            invalid_label_indices.append({"index": index, "label": label})
        else:
            label_counts[label] += 1

        if not fruit:
            missing_fruit_indices.append(index)
        else:
            fruit_counts[fruit] += 1

        if label in {"fresh", "rotten"} and fruit:
            joint_counts[fruit][label] += 1

        try:
            image_bytes = get_image_bytes(row.get("image"))
            info = inspect_image(image_bytes)
            usable_images += 1
            format_counts[info["format"]] += 1
            dimension_counts[f"{info['width']}x{info['height']}"] += 1
            widths.append(info["width"])
            heights.append(info["height"])
        except Exception as error:
            unreadable.append({"index": index, "error": str(error)})

    categories = sorted(fruit_counts)
    labels = sorted(label_counts)
    total = len(dataset)
    report = {
        "source": {
            "dataset_id": DATASET_ID,
            "url": DATASET_URL,
            "configuration": CONFIG_NAME,
            "split": SPLIT_NAME,
            "revision": DATASET_REVISION,
            "declared_license": "CC BY 4.0",
            "expected_raw_images_from_dataset_card": EXPECTED_IMAGE_COUNT,
            "expected_fruit_category_count_from_dataset_card": EXPECTED_FRUIT_CATEGORY_COUNT,
            "raw_parquet_size_bytes": 2856370960,
        },
        "inspected_at_utc": datetime.now(timezone.utc).isoformat(),
        "metadata": {
            "columns": list(dataset.column_names),
            "features": {name: str(feature) for name, feature in features.items()},
        },
        "counts": {
            "records": total,
            "usable_images": usable_images,
            "unreadable_images": len(unreadable),
            "missing_labels": len(missing_label_indices),
            "invalid_labels": len(invalid_label_indices),
            "missing_fruit_categories": len(missing_fruit_indices),
        },
        "freshness_label_counts": dict(sorted(label_counts.items())),
        "fruit_categories": categories,
        "fruit_category_counts": dict(sorted(fruit_counts.items())),
        "fruit_category_and_label_counts": {
            fruit: dict(sorted(counts.items()))
            for fruit, counts in sorted(joint_counts.items())
        },
        "category_check": {
            "actual_category_count": len(categories),
            "expected_category_count": EXPECTED_FRUIT_CATEGORY_COUNT,
            "matches_dataset_card_count": len(categories) == EXPECTED_FRUIT_CATEGORY_COUNT,
        },
        "image_formats": dict(sorted(format_counts.items())),
        "image_dimensions": {
            "unique_dimensions": len(dimension_counts),
            "most_common": [
                {"dimensions": dimensions, "count": count}
                for dimensions, count in dimension_counts.most_common(20)
            ],
            "minimum_width": min(widths) if widths else None,
            "maximum_width": max(widths) if widths else None,
            "minimum_height": min(heights) if heights else None,
            "maximum_height": max(heights) if heights else None,
        },
        "missing_label_row_indices": missing_label_indices,
        "missing_fruit_category_row_indices": missing_fruit_indices,
        "invalid_labels": invalid_label_indices,
        "unreadable_images": unreadable,
        "inspection_notes": [
            "Only the raw configuration was loaded; the augmented configuration was not requested.",
            "Image dimensions and file formats were read from and validated against the encoded image bytes.",
        ],
    }

    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nReport saved to: {REPORT_PATH}")
    return report


if __name__ == "__main__":
    try:
        inspect_dataset()
    except Exception as error:
        print(f"Dataset inspection failed: {error}", file=sys.stderr)
        raise SystemExit(1)
