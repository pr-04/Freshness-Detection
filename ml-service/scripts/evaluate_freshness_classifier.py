"""Evaluate the selected checkpoint once on the held-out test split."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "models" / "freshness_classifier"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=OUT / "best_model.pth")
    args = parser.parse_args()
    if not args.checkpoint.is_file():
        raise FileNotFoundError(f"Best checkpoint not found: {args.checkpoint}. Run train_freshness_classifier.py first.")
    try:
        checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=True)
    except Exception as exc:
        raise RuntimeError(f"Could not load checkpoint {args.checkpoint}: {exc}") from exc
    classes = checkpoint["classes"]
    if classes != ["fresh", "rotten"]:
        raise ValueError(f"Unexpected class order in checkpoint: {classes}")
    ds = datasets.ImageFolder(ROOT / "datasets" / "prepared" / "test", transform=transforms.Compose([
        transforms.Resize((checkpoint["input_size"], checkpoint["input_size"])),
        transforms.ToTensor(), transforms.Normalize(checkpoint["mean"], checkpoint["std"]),
    ]))
    if ds.classes != classes:
        raise ValueError(f"Test folder classes {ds.classes} do not match checkpoint {classes}")
    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = nn.Linear(model.last_channel, len(classes))
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    loader = DataLoader(ds, batch_size=32, shuffle=False, num_workers=0)
    confusion = [[0 for _ in classes] for _ in classes]
    with torch.inference_mode():
        for images, labels in loader:
            predictions = model(images).argmax(1)
            for truth, pred in zip(labels.tolist(), predictions.tolist()):
                confusion[truth][pred] += 1
    total = sum(map(sum, confusion))
    accuracy = sum(confusion[i][i] for i in range(len(classes))) / total if total else 0.0
    per_class = {}
    for i, name in enumerate(classes):
        tp = confusion[i][i]
        fp = sum(confusion[row][i] for row in range(len(classes)) if row != i)
        fn = sum(confusion[i][col] for col in range(len(classes)) if col != i)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[name] = {"precision": precision, "recall": recall, "f1_score": f1,
                           "support": sum(confusion[i])}
    macro_f1 = sum(x["f1_score"] for x in per_class.values()) / len(classes)
    report = {"evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
              "checkpoint": str(args.checkpoint), "class_order": classes,
              "positive_class_for_binary_metrics": "rotten",
              "test_images_evaluated": total, "accuracy": accuracy,
              "per_class": per_class, "macro_f1": macro_f1,
              "confusion_matrix": {"labels_in_order": classes, "rows_true_columns_predicted": confusion},
              "limitations": ["The source dataset covers eight fruit categories and only fresh/rotten labels.",
                              "No early_spoilage class or food-safety outcome is represented.",
                              "Results may not generalize to different cameras, lighting, produce varieties, or real-world settings.",
                              "Exact duplicates were separated across splits; perceptual near-duplicates were not checked."]}
    report_path = OUT / "test_evaluation.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["Held-out test evaluation", f"Images: {total}", f"Accuracy: {accuracy:.4f}",
             f"Macro F1: {macro_f1:.4f}", "Per-class (precision / recall / F1):"]
    lines += [f"  {name}: {m['precision']:.4f} / {m['recall']:.4f} / {m['f1_score']:.4f} (n={m['support']})"
              for name, m in per_class.items()]
    lines += [f"Confusion matrix (true rows, predicted columns; {classes}):", str(confusion),
              "Positive class for binary metrics: rotten", "Scores are dataset metrics, not food-safety guidance."]
    summary = "\n".join(lines) + "\n"
    (OUT / "test_evaluation.txt").write_text(summary, encoding="utf-8")
    print(summary, end="")
    print(f"Saved: {report_path}")


if __name__ == "__main__":
    main()
