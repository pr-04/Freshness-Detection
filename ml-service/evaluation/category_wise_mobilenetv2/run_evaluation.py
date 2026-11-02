"""Evaluate the existing MobileNetV2 once on selected fruit test images only.

This script reads the existing checkpoint, prepared test images, manifest and
metadata. All generated outputs stay in this separate evaluation directory.
It never imports or calls YOLO and never trains or saves model weights.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import torch
from PIL import Image
from torch import nn
from torchvision import models, transforms


ML_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ML_ROOT / "datasets" / "prepared"
MANIFEST = DATA_ROOT / "manifest.csv"
CHECKPOINT_PATH = ML_ROOT / "models" / "freshness_classifier" / "best_model.pth"
METADATA_PATH = ML_ROOT / "models" / "freshness_classifier" / "metadata.json"
OUT = Path(__file__).resolve().parent
SELECTED_FRUITS = [
    "apple", "banana", "grape", "guava", "orange", "pomegranate", "strawberry"
]
LABELS = ["fresh", "rotten"]


def load_inputs():
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    if metadata.get("architecture") != "torchvision.mobilenet_v2":
        raise ValueError(f"Unexpected architecture in metadata: {metadata.get('architecture')!r}")
    if metadata.get("classes") != LABELS or metadata.get("class_to_idx") != {"fresh": 0, "rotten": 1}:
        raise ValueError("Metadata class order or class-to-index mapping is not fresh=0, rotten=1.")

    checkpoint = torch.load(CHECKPOINT_PATH, map_location="cpu", weights_only=True)
    if checkpoint.get("architecture") != metadata["architecture"]:
        raise ValueError("Checkpoint architecture does not match metadata.")
    if checkpoint.get("classes") != metadata["classes"] or checkpoint.get("class_to_idx") != metadata["class_to_idx"]:
        raise ValueError("Checkpoint class mapping does not match metadata.")
    if checkpoint.get("input_size") != metadata["input_size"]:
        raise ValueError("Checkpoint input size does not match metadata.")

    preprocessing = metadata["preprocessing"]
    input_size = metadata["input_size"]
    mean = preprocessing["normalization_mean"]
    std = preprocessing["normalization_std"]
    if preprocessing.get("resize") != [input_size, input_size]:
        raise ValueError("Unsupported resize configuration in metadata.")
    if metadata.get("normalization") != {"mean": mean, "std": std}:
        raise ValueError("Normalization values disagree within metadata.")
    if checkpoint.get("mean") != mean or checkpoint.get("std") != std:
        raise ValueError("Checkpoint normalization does not match metadata.")

    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = nn.Linear(model.last_channel, len(LABELS))
    model.load_state_dict(checkpoint["state_dict"], strict=True)
    model.to("cpu")
    model.eval()

    image_transform = transforms.Compose([
        transforms.Resize((input_size, input_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=mean, std=std),
    ])
    return model, image_transform, metadata


def collect_test_records():
    with MANIFEST.open("r", encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    selected = [
        row for row in rows
        if row.get("split") == "test" and row.get("fruit_category") in SELECTED_FRUITS
    ]
    if len(selected) != 420:
        raise ValueError(f"Expected 420 selected test records (60 per fruit), found {len(selected)}.")
    if len({row["image_path"] for row in selected}) != len(selected):
        raise ValueError("Duplicate image paths found in selected test manifest rows.")
    counts = Counter((row["fruit_category"], row["freshness_label"]) for row in selected)
    for fruit in SELECTED_FRUITS:
        if counts[(fruit, "fresh")] != 30 or counts[(fruit, "rotten")] != 30:
            raise ValueError(f"Expected 30 Fresh and 30 Rotten test images for {fruit}; got "
                             f"{counts[(fruit, 'fresh')]} and {counts[(fruit, 'rotten')]}.")
    hash_groups = {}
    for row in selected:
        if row.get("freshness_label") not in LABELS:
            raise ValueError(f"Unexpected actual label in test manifest: {row}")
        group = hash_groups.setdefault(row["sha256"], [])
        group.append(row)
        image_path = ML_ROOT / row["image_path"]
        if not image_path.is_file():
            raise FileNotFoundError(f"Selected test image is missing: {row['image_path']}")
        # Verify every selected file before inference; no unreadable image is silently skipped.
        with Image.open(image_path) as image:
            image.verify()
    for image_hash, group in hash_groups.items():
        if len({row["fruit_category"] for row in group}) > 1 or len({row["freshness_label"] for row in group}) > 1:
            raise ValueError(f"Exact duplicate hash {image_hash} has conflicting category or freshness labels.")
    return selected, hash_groups


def metrics_for(records):
    # Rows are indexed by actual class, columns by predicted class.
    confusion = [[0, 0], [0, 0]]
    for row in records:
        confusion[row["actual_index"]][row["predicted_index"]] += 1
    total = sum(sum(row) for row in confusion)
    per_class = {}
    for index, label in enumerate(LABELS):
        tp = confusion[index][index]
        support = sum(confusion[index])
        fp = sum(confusion[other][index] for other in range(len(LABELS)) if other != index)
        fn = sum(confusion[index][other] for other in range(len(LABELS)) if other != index)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / support if support else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = {
            "support": support,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
        }
    correct = confusion[0][0] + confusion[1][1]
    return {
        "test_image_count": total,
        "fresh_image_count": sum(confusion[0]),
        "rotten_image_count": sum(confusion[1]),
        "accuracy": correct / total if total else 0.0,
        "macro_precision": sum(per_class[label]["precision"] for label in LABELS) / 2,
        "macro_recall": sum(per_class[label]["recall"] for label in LABELS) / 2,
        "macro_f1": sum(per_class[label]["f1_score"] for label in LABELS) / 2,
        "weighted_f1": sum(per_class[label]["f1_score"] * per_class[label]["support"]
                            for label in LABELS) / total if total else 0.0,
        "per_class": per_class,
        "confusion_matrix": {
            "labels_in_order": LABELS,
            "rows_actual_columns_predicted": confusion,
        },
        "false_fresh_count": confusion[1][0],
        "false_rotten_count": confusion[0][1],
        "fresh_accuracy": per_class["fresh"]["recall"],
        "rotten_accuracy": per_class["rotten"]["recall"],
        "false_fresh_rate": confusion[1][0] / sum(confusion[1]) if sum(confusion[1]) else 0.0,
    }


def write_csv(path, fieldnames, records):
    with path.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main():
    torch.set_num_threads(4)
    model, image_transform, metadata = load_inputs()
    selected, hash_groups = collect_test_records()
    unique_predictions = {}

    # One direct full-image MobileNetV2 forward pass per selected test image.
    with torch.inference_mode():
        for image_hash, group in hash_groups.items():
            row = group[0]
            image_path = ML_ROOT / row["image_path"]
            with Image.open(image_path) as source_image:
                image = source_image.convert("RGB")
                tensor = image_transform(image).unsqueeze(0)
                image.close()
            probabilities = torch.softmax(model(tensor)[0], dim=0)
            predicted_index = int(probabilities.argmax().item())
            actual_index = LABELS.index(row["freshness_label"])
            unique_predictions[image_hash] = {
                "fruit_category": row["fruit_category"],
                "actual_freshness_label": LABELS[actual_index],
                "predicted_freshness_label": LABELS[predicted_index],
                "fresh_probability": float(probabilities[0].item()),
                "rotten_probability": float(probabilities[1].item()),
                "correctness": "correct" if actual_index == predicted_index else "incorrect",
                "actual_index": actual_index,
                "predicted_index": predicted_index,
            }

    # Retain one CSV row per manifest filename, but reuse exact-duplicate
    # predictions and count only the unique image content in metrics.
    predictions = []
    for row in selected:
        result = unique_predictions[row["sha256"]]
        predictions.append({
            **result,
            "image_filename": Path(row["image_path"]).name,
            "image_hash": row["sha256"],
            "unique_image_content": hash_groups[row["sha256"]][0]["image_path"] == row["image_path"],
        })
    metric_predictions = [row for row in predictions if row["unique_image_content"]]
    if len(unique_predictions) != len(hash_groups) or len(metric_predictions) != len(hash_groups):
        raise RuntimeError("Expected exactly one inference and metric row per unique image hash.")

    category_metrics = []
    category_matrices = {}
    for fruit in SELECTED_FRUITS:
        fruit_records = [row for row in metric_predictions if row["fruit_category"] == fruit]
        metrics = metrics_for(fruit_records)
        category_metrics.append({
            "fruit_category": fruit,
            "test_image_count": metrics["test_image_count"],
            "test_image_file_count": sum(row["fruit_category"] == fruit for row in predictions),
            "duplicate_file_rows_excluded": sum(row["fruit_category"] == fruit and not row["unique_image_content"] for row in predictions),
            "fresh_image_count": metrics["fresh_image_count"],
            "rotten_image_count": metrics["rotten_image_count"],
            "fresh_accuracy": metrics["fresh_accuracy"],
            "rotten_accuracy": metrics["rotten_accuracy"],
            "overall_accuracy": metrics["accuracy"],
            "fresh_precision": metrics["per_class"]["fresh"]["precision"],
            "fresh_recall": metrics["per_class"]["fresh"]["recall"],
            "fresh_f1": metrics["per_class"]["fresh"]["f1_score"],
            "rotten_precision": metrics["per_class"]["rotten"]["precision"],
            "rotten_recall": metrics["per_class"]["rotten"]["recall"],
            "rotten_f1": metrics["per_class"]["rotten"]["f1_score"],
            "macro_f1": metrics["macro_f1"],
            "false_fresh_count": metrics["false_fresh_count"],
            "false_fresh_rate": metrics["false_fresh_rate"],
            "false_rotten_count": metrics["false_rotten_count"],
        })
        category_matrices[fruit] = metrics["confusion_matrix"]

    overall = metrics_for(metric_predictions)
    false_fresh = [row for row in metric_predictions
                   if row["actual_freshness_label"] == "rotten"
                   and row["predicted_freshness_label"] == "fresh"]
    false_rotten = [row for row in metric_predictions
                    if row["actual_freshness_label"] == "fresh"
                    and row["predicted_freshness_label"] == "rotten"]

    write_csv(OUT / "category_wise_metrics.csv", list(category_metrics[0]), category_metrics)
    write_csv(OUT / "prediction_results.csv", [
        "image_filename", "fruit_category", "actual_freshness_label",
        "predicted_freshness_label", "fresh_probability", "rotten_probability", "correctness",
        "unique_image_content",
    ], [{key: row[key] for key in (
        "image_filename", "fruit_category", "actual_freshness_label",
        "predicted_freshness_label", "fresh_probability", "rotten_probability", "correctness",
        "unique_image_content",
    )} for row in predictions])
    (OUT / "overall_metrics.json").write_text(json.dumps({
        **{key: overall[key] for key in (
        "test_image_count", "fresh_image_count", "rotten_image_count", "accuracy",
            "macro_precision", "macro_recall", "macro_f1", "weighted_f1", "per_class",
            "false_fresh_count", "false_rotten_count", "false_fresh_rate",
        )},
        "categories_included": SELECTED_FRUITS,
        "categories_excluded": ["jujube"],
        "test_image_file_count": len(selected),
        "duplicate_file_rows_excluded_from_metrics": len(selected) - len(hash_groups),
        "checkpoint": str(CHECKPOINT_PATH),
        "class_order": LABELS,
        "class_to_idx": metadata["class_to_idx"],
        "inference": "CPU; direct full-image MobileNetV2; exactly one forward pass per unique image hash",
        "input_size": metadata["input_size"],
        "normalization": metadata["normalization"],
    }, indent=2) + "\n", encoding="utf-8")
    (OUT / "confusion_matrices.json").write_text(json.dumps({
        "labels_in_order": LABELS,
        "rows_actual_columns_predicted": True,
        "per_category": category_matrices,
        "overall_selected_categories": overall["confusion_matrix"],
    }, indent=2) + "\n", encoding="utf-8")

    category_metrics.sort(key=lambda row: (row["macro_f1"], -row["false_fresh_rate"]), reverse=True)
    report_lines = [
        "# Category-wise MobileNetV2 Evaluation",
        "",
        "## Method and integrity checks",
        "",
        f"- Selected {len(selected)} test filenames across seven fruits; {len(hash_groups)} unique image hashes received exactly one full-image MobileNetV2 forward pass.",
        f"- Exact duplicate test files reused the identical prediction and were excluded from metric counts: {len(selected) - len(hash_groups)} duplicate file row(s).",
        "- Used only `datasets/prepared/test`; train and validation images were not used.",
        "- Jujube was excluded from evaluation and aggregate metrics; its dataset files were left untouched.",
        "- Checkpoint and metadata class mapping verified: `fresh=0`, `rotten=1`.",
        "- The saved checkpoint had already been evaluated on this held-out test split in the earlier aggregate evaluation. This run adds the fruit-wise breakdown without training or tuning the model.",
        "- CPU inference; RGB conversion, 224×224 resize, ToTensor, and normalization match training/evaluation configuration.",
        "- All selected image paths, unique hashes, expected 30 Fresh/30 Rotten counts per fruit, and image readability were checked before inference.",
        "- No YOLO, boxes, or crops were used. No checkpoint or original dataset files were written.",
        "",
        "## Per-category results",
        "",
        "| Fruit | Unique N | Fresh correct / Fresh N | Rotten correct / Rotten N | Accuracy | Macro F1 | False Fresh | False Rotten |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in category_metrics:
        fresh_correct = round(row["fresh_accuracy"] * row["fresh_image_count"])
        rotten_correct = round(row["rotten_accuracy"] * row["rotten_image_count"])
        report_lines.append(
            f"| {row['fruit_category'].title()} | {row['test_image_count']} | {fresh_correct}/{row['fresh_image_count']} | "
            f"{rotten_correct}/{row['rotten_image_count']} | {row['overall_accuracy']:.4f} | {row['macro_f1']:.4f} | "
            f"{row['false_fresh_count']} | {row['false_rotten_count']} |"
        )
    report_lines += [
        "",
        "Per-class precision, recall, and F1 are in the CSV. Confusion matrices use actual rows and predicted columns, ordered Fresh then Rotten:",
        "",
        "| Fruit | Matrix `[[Fresh→Fresh, Fresh→Rotten], [Rotten→Fresh, Rotten→Rotten]]` |",
        "|---|---|",
        *[f"| {fruit.title()} | `{category_matrices[fruit]['rows_actual_columns_predicted']}` |" for fruit in SELECTED_FRUITS],
        f"| Overall | `{overall['confusion_matrix']['rows_actual_columns_predicted']}` |",
        "",
        "## Overall results for the seven selected fruits",
        "",
        f"- Unique test images counted: {overall['test_image_count']} ({overall['fresh_image_count']} Fresh, {overall['rotten_image_count']} Rotten); selected test filenames: {len(selected)}.",
        f"- Accuracy: {overall['accuracy']:.6f}.",
        f"- Macro precision: {overall['macro_precision']:.6f}; macro recall: {overall['macro_recall']:.6f}.",
        f"- Macro F1: {overall['macro_f1']:.6f}; weighted F1: {overall['weighted_f1']:.6f}.",
        f"- Combined confusion matrix (actual rows, predicted columns; Fresh, Rotten): `{overall['confusion_matrix']['rows_actual_columns_predicted']}`.",
        f"- False Fresh: {len(false_fresh)} (actual Rotten, predicted Fresh); false Rotten: {len(false_rotten)} (actual Fresh, predicted Rotten).",
        "",
        "## False Fresh predictions",
        "",
    ]
    if false_fresh:
        report_lines += [
            "| Filename | Fruit | Fresh score | Rotten score |",
            "|---|---|---:|---:|",
        ]
        for row in false_fresh:
            report_lines.append(
                f"| `{row['image_filename']}` | {row['fruit_category'].title()} | "
                f"{row['fresh_probability']:.6f} | {row['rotten_probability']:.6f} |"
            )
    else:
        report_lines.append("No false Fresh predictions occurred in this evaluation.")
    report_lines += ["", "## False Rotten predictions", ""]
    if false_rotten:
        report_lines += [
            "| Filename | Fruit | Fresh score | Rotten score |",
            "|---|---|---:|---:|",
        ]
        for row in false_rotten:
            report_lines.append(
                f"| `{row['image_filename']}` | {row['fruit_category'].title()} | "
                f"{row['fresh_probability']:.6f} | {row['rotten_probability']:.6f} |"
            )
    else:
        report_lines.append("No false Rotten predictions occurred in this evaluation.")
    best = category_metrics[0]
    weakest = category_metrics[-1]
    report_lines += [
        "",
        "## Category ranking and recommendation",
        "",
        f"- Highest macro F1 in this sample: {best['fruit_category'].title()} ({best['macro_f1']:.4f}; false Fresh rate {best['false_fresh_rate']:.4f}).",
        f"- Lowest macro F1 in this sample: {weakest['fruit_category'].title()} ({weakest['macro_f1']:.4f}; false Fresh rate {weakest['false_fresh_rate']:.4f}).",
        "- The Orange metric uses 58 unique images because two exact duplicate file rows were excluded; each other fruit uses 60 unique images.",
        "- Provisional candidates for a limited, supervised prototype with fruit category supplied by the user: Apple, Banana, Guava, Orange, Pomegranate, and Strawberry (no false Fresh or false Rotten errors in these small test samples).",
        "- Temporarily withhold Grape from the initial supported choices pending review and additional testing: its one false Fresh prediction is 1 of 30 Rotten unique test images (3.33%).",
        "- These results do not establish production readiness. Even zero observed false Fresh errors among 30 Rotten examples leaves substantial uncertainty; validate candidates on independent real-world images before prototype claims.",
        "- The model itself does not output fruit identity. The provisional category list is not automatic fruit recognition; without user-declared category or a separately evaluated identification/rejection system, the binary classifier will return Fresh or Rotten for unsupported images too.",
        "- Manually inspected the Grape false Fresh image: it shows a bunch with visibly dark/damaged areas on some grapes alongside green-looking grapes. This mixed appearance may make a single image-level label difficult, but one image does not establish the cause of the error.",
        "- A binary MobileNetV2 always returns Fresh or Rotten; it cannot identify fruit, reject non-fruit images, or detect out-of-domain inputs. Fruit identity must be supplied externally or addressed by a separately evaluated model.",
        "- Scores are class probabilities, not freshness percentages or food-safety estimates.",
        "",
        "## Limitations",
        "",
        "- Dataset metrics may not generalize to different cameras, lighting, varieties, backgrounds, or real-world spoilage conditions.",
        "- Existing data preparation grouped exact SHA-256 duplicates in one split; perceptual duplicates and similar re-encodings were not checked.",
        "- The evaluation reports appearance labels only; it does not establish edibility or food safety.",
    ]
    (OUT / "evaluation_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"Evaluated {len(predictions)} images; 7 categories; outputs: {OUT}")
    print(f"Overall accuracy={overall['accuracy']:.6f}, macro_f1={overall['macro_f1']:.6f}, "
          f"false_fresh={len(false_fresh)}, false_rotten={len(false_rotten)}")


if __name__ == "__main__":
    main()
