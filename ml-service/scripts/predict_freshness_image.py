"""Run one local image through a trained freshness checkpoint (no service changes)."""
import argparse
from pathlib import Path

import torch
from PIL import Image
from torch import nn
from torchvision import models, transforms

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHECKPOINT = ROOT / "models" / "freshness_classifier" / "best_model.pth"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    args = parser.parse_args()
    if not args.image.is_file():
        raise FileNotFoundError(f"Image not found: {args.image}")
    if not args.checkpoint.is_file():
        raise FileNotFoundError(f"Checkpoint not found: {args.checkpoint}")
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=True)
    classes = checkpoint["classes"]
    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = nn.Linear(model.last_channel, len(classes))
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()
    pipeline = transforms.Compose([
        transforms.Resize((checkpoint["input_size"], checkpoint["input_size"])),
        transforms.ToTensor(), transforms.Normalize(checkpoint["mean"], checkpoint["std"]),
    ])
    with Image.open(args.image) as image:
        tensor = pipeline(image.convert("RGB")).unsqueeze(0)
    with torch.inference_mode():
        probabilities = torch.softmax(model(tensor)[0], dim=0)
    idx = int(probabilities.argmax())
    print(f"Dataset class: {classes[idx]}")
    print(f"Model score (not a freshness percentage): {probabilities[idx].item():.4f}")
    print("This two-class dataset output is not food-safety or edibility advice.")


if __name__ == "__main__":
    main()
