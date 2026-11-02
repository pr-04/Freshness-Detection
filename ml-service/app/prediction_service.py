"""Classify one complete uploaded fruit image with the loaded MobileNetV2."""

import torch
from PIL import Image

from app.model_service import (
    CLASSIFIER_NAME,
    get_classifier_classes,
    get_classifier_transform,
    get_freshness_classifier,
)

SUPPORTED_FRUITS = {
    "apple": "Apple",
    "banana": "Banana",
    "guava": "Guava",
    "orange": "Orange",
    "pomegranate": "Pomegranate",
    "strawberry": "Strawberry",
}


def canonical_fruit(value: str) -> str | None:
    """Return the canonical user-selected category, or None if unsupported."""
    if not isinstance(value, str):
        return None
    return SUPPORTED_FRUITS.get(value.strip().casefold())


def predict_freshness(image: Image.Image, fruit: str, low_confidence_threshold: float = 0.60):
    """Run one direct full-image inference and return Fresh/Rotten scores.

    ``fruit`` is validated user metadata. MobileNetV2 does not identify the
    fruit or reject non-fruit images.
    """
    selected_fruit = canonical_fruit(fruit)
    if selected_fruit is None:
        raise ValueError("Unsupported fruit selection.")

    classifier = get_freshness_classifier()
    transform = get_classifier_transform()
    classes = get_classifier_classes()
    if classifier is None or transform is None or classes is None:
        raise RuntimeError("The MobileNetV2 classifier is unavailable. Check the service startup log.")
    if tuple(classes) != ("fresh", "rotten"):
        raise RuntimeError(f"Unexpected MobileNetV2 class mapping: {classes!r}")

    # The supplied whole image is converted and resized exactly as at training.
    with image.convert("RGB") as rgb_image:
        tensor = transform(rgb_image).unsqueeze(0)
    with torch.inference_mode():
        scores = torch.softmax(classifier(tensor), dim=1)[0]

    fresh_probability = float(scores[classes.index("fresh")].item())
    rotten_probability = float(scores[classes.index("rotten")].item())
    predicted_class = "Fresh" if fresh_probability >= rotten_probability else "Rotten"
    low_score = max(fresh_probability, rotten_probability) < low_confidence_threshold
    return {
        "fruit": selected_fruit,
        "freshness": "Uncertain" if low_score else predicted_class,
        "uncertain": low_score,
        "uncertainty_reason": (
            "The highest model class score is below the configured threshold."
            if low_score else None
        ),
        "probabilities": {
            "fresh": round(fresh_probability, 6),
            "rotten": round(rotten_probability, 6),
        },
        "model": CLASSIFIER_NAME,
    }
