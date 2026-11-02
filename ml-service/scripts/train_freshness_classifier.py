"""Fine-tune MobileNetV2 for the dataset's two freshness labels."""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
from torchvision.models import MobileNet_V2_Weights

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets" / "prepared"
OUT = ROOT / "models" / "freshness_classifier"
# Keep Torch's downloaded pretrained weights inside the ignored project cache.
os.environ.setdefault("TORCH_HOME", str(ROOT / "datasets" / "raw" / "torch_cache"))
CLASSES = ["fresh", "rotten"]
SIZE = 224
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]
PREPROCESSING = {
    "resize": [SIZE, SIZE], "normalization_mean": MEAN, "normalization_std": STD,
    "evaluation_augmentation": "none",
    "training_augmentation": ["random_horizontal_flip_p=0.5", "random_rotation_degrees=8",
                               "color_jitter_brightness_contrast_saturation=0.08"],
}


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def make_loaders(batch_size: int):
    train_tf = transforms.Compose([
        transforms.Resize((SIZE, SIZE)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(8),
        transforms.ColorJitter(brightness=0.08, contrast=0.08, saturation=0.08),
        transforms.ToTensor(), transforms.Normalize(MEAN, STD),
    ])
    eval_tf = transforms.Compose([
        transforms.Resize((SIZE, SIZE)), transforms.ToTensor(), transforms.Normalize(MEAN, STD),
    ])
    folders = {}
    for split, tf in (("train", train_tf), ("val", eval_tf), ("test", eval_tf)):
        folder = DATA / split
        if not folder.is_dir():
            raise FileNotFoundError(f"Missing dataset split folder: {folder}. Prepare the dataset first.")
        ds = datasets.ImageFolder(folder, transform=tf)
        if ds.classes != CLASSES:
            raise ValueError(f"Expected class order {CLASSES}, got {ds.classes} in {folder}")
        folders[split] = ds
    expected = {"train": 2240, "val": 480, "test": 480}
    for split, ds in folders.items():
        if len(ds) != expected[split]:
            raise ValueError(f"Expected {expected[split]} images in {split}, found {len(ds)}")
    return {
        split: DataLoader(ds, batch_size=batch_size, shuffle=(split == "train"),
                          num_workers=0, pin_memory=False)
        for split, ds in folders.items()
    }


def run_epoch(model, loader, criterion, device, optimizer=None, max_batches=None):
    training = optimizer is not None
    model.train(training)
    loss_sum = correct = total = 0
    context = torch.enable_grad() if training else torch.inference_mode()
    with context:
        for batch_index, (images, labels) in enumerate(loader):
            images, labels = images.to(device), labels.to(device)
            if training:
                optimizer.zero_grad(set_to_none=True)
            logits = model(images)
            loss = criterion(logits, labels)
            if training:
                loss.backward()
                optimizer.step()
            loss_sum += loss.item() * labels.size(0)
            correct += (logits.argmax(1) == labels).sum().item()
            total += labels.size(0)
            if training and (batch_index + 1) % 20 == 0:
                print(f"  training batch {batch_index + 1}/{len(loader)}", flush=True)
            if max_batches is not None and batch_index + 1 >= max_batches:
                break
    return loss_sum / total, correct / total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=0.0001)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--patience", type=int, default=2)
    parser.add_argument("--num-threads", type=int, default=max(1, min(4, os.cpu_count() or 1)))
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    parser.add_argument("--smoke-test", action="store_true",
                        help="Train on two batches and validate on one batch; writes only under .tmp.")
    args = parser.parse_args()
    if args.epochs < 1 or args.batch_size < 1 or args.learning_rate <= 0 or args.num_threads < 1:
        parser.error("epochs, batch size, and thread count must be positive; learning rate must be greater than zero")
    seed_everything(args.seed)
    torch.set_num_threads(args.num_threads)
    device = torch.device("cuda" if args.device == "cuda" or
                          (args.device == "auto" and torch.cuda.is_available()) else "cpu")
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is not available. Use --device cpu.")
    loaders = make_loaders(args.batch_size)
    try:
        model = models.mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT)
    except Exception as exc:
        raise RuntimeError("Could not load pretrained MobileNetV2 weights. Check internet access or the Torch cache, then retry.") from exc
    model.classifier[1] = nn.Linear(model.last_channel, len(CLASSES))
    model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)
    output_dir = ROOT / ".tmp" / "freshness_smoke" if args.smoke_test else OUT
    output_dir.mkdir(parents=True, exist_ok=True)
    best_path = output_dir / "best_model.pth"
    curve_path = output_dir / "training_metrics.csv"
    best_val = float("inf")
    best_metrics = None
    stale_epochs = 0
    rows = []
    start = time.time()
    print(f"Device: {device}; classes: {CLASSES}; train/val/test: " +
          "/".join(str(len(loaders[s].dataset)) for s in ("train", "val", "test")), flush=True)
    epochs = min(args.epochs, 1) if args.smoke_test else args.epochs
    batch_limit = 2 if args.smoke_test else None
    val_batch_limit = 1 if args.smoke_test else None
    for epoch in range(1, epochs + 1):
        tr_loss, tr_acc = run_epoch(model, loaders["train"], criterion, device, optimizer, batch_limit)
        va_loss, va_acc = run_epoch(model, loaders["val"], criterion, device, max_batches=val_batch_limit)
        row = {"epoch": epoch, "train_loss": tr_loss, "train_accuracy": tr_acc,
               "val_loss": va_loss, "val_accuracy": va_acc}
        rows.append(row)
        print(f"{'SMOKE ' if args.smoke_test else ''}Epoch {epoch}/{epochs} train_loss={tr_loss:.4f} train_acc={tr_acc:.4f} "
              f"val_loss={va_loss:.4f} val_acc={va_acc:.4f}", flush=True)
        if va_loss < best_val:
            best_val, stale_epochs = va_loss, 0
            best_metrics = row.copy()
            torch.save({"state_dict": model.cpu().state_dict(), "classes": CLASSES,
                        "class_to_idx": {name: i for i, name in enumerate(CLASSES)},
                        "architecture": "torchvision.mobilenet_v2", "input_size": SIZE,
                        "mean": MEAN, "std": STD, "preprocessing": PREPROCESSING,
                        "best_validation": best_metrics,
                        "training_config": vars(args)}, best_path)
            model.to(device)
        else:
            stale_epochs += 1
        with curve_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
        if args.patience > 0 and stale_epochs >= args.patience:
            print(f"Early stopping after {epoch} epochs (validation loss did not improve).", flush=True)
            break
    metadata = {"architecture": "torchvision.mobilenet_v2", "classes": CLASSES,
                "class_to_idx": {name: i for i, name in enumerate(CLASSES)},
                "input_size": SIZE, "normalization": {"mean": MEAN, "std": STD},
                "preprocessing": PREPROCESSING,
                "training_config": vars(args), "device": str(device),
                "best_validation": best_metrics, "epochs_completed": len(rows),
                "elapsed_seconds": round(time.time() - start, 1),
                "checkpoint": best_path.name}
    (output_dir / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Best checkpoint: {best_path}; best validation: {best_metrics}; metadata: {output_dir / 'metadata.json'}", flush=True)


if __name__ == "__main__":
    main()
