"""Load and reuse the trained MobileNetV2 freshness classifier on CPU."""

import logging
from pathlib import Path

CLASSIFIER_NAME = "MobileNetV2"
MODELS_DIR = Path(__file__).resolve().parents[1] / "models"
CLASSIFIER_DIR = MODELS_DIR / "freshness_classifier"
CLASSIFIER_PATH = CLASSIFIER_DIR / "best_model.pth"
CLASSIFIER_METADATA_PATH = CLASSIFIER_DIR / "metadata.json"

logger = logging.getLogger(__name__)
_classifier = None
_classifier_error = None
_classifier_classes = None
_classifier_transform = None


def load_freshness_classifier():
    """Load the saved architecture, mapping, weights and preprocessing once."""
    global _classifier, _classifier_error, _classifier_classes, _classifier_transform
    if _classifier is not None:
        return True

    try:
        import json

        import torch
        from torch import nn
        from torchvision import models, transforms

        if not CLASSIFIER_PATH.is_file():
            raise FileNotFoundError(f"Classifier checkpoint not found: {CLASSIFIER_PATH}")
        if not CLASSIFIER_METADATA_PATH.is_file():
            raise FileNotFoundError(f"Classifier metadata not found: {CLASSIFIER_METADATA_PATH}")

        metadata = json.loads(CLASSIFIER_METADATA_PATH.read_text(encoding="utf-8"))
        architecture = metadata.get("architecture")
        if architecture != "torchvision.mobilenet_v2":
            raise ValueError(f"Unsupported classifier architecture in metadata: {architecture!r}")
        classes = metadata.get("classes")
        class_to_idx = metadata.get("class_to_idx")
        expected_mapping = {label: index for index, label in enumerate(classes or [])}
        if classes != ["fresh", "rotten"] or class_to_idx != expected_mapping:
            raise ValueError("Metadata must map fresh=0 and rotten=1 in that class order.")

        preprocessing = metadata.get("preprocessing")
        normalization = metadata.get("normalization")
        input_size = metadata.get("input_size")
        if not isinstance(preprocessing, dict) or not isinstance(input_size, int) or input_size <= 0:
            raise ValueError("Classifier metadata is missing valid preprocessing/input_size values.")
        mean = preprocessing.get("normalization_mean")
        std = preprocessing.get("normalization_std")
        resize = preprocessing.get("resize")
        if not isinstance(mean, list) or not isinstance(std, list) or len(mean) != 3 or len(std) != 3:
            raise ValueError("Classifier metadata must contain three-channel normalization values.")
        if normalization != {"mean": mean, "std": std}:
            raise ValueError("Classifier normalization metadata fields do not agree.")
        if resize != [input_size, input_size]:
            raise ValueError(f"Unsupported classifier resize metadata: {resize!r}")

        checkpoint = torch.load(CLASSIFIER_PATH, map_location="cpu", weights_only=True)
        if checkpoint.get("architecture") != architecture:
            raise ValueError("Checkpoint architecture does not match metadata.")
        if checkpoint.get("classes") != classes or checkpoint.get("class_to_idx") != class_to_idx:
            raise ValueError("Checkpoint class mapping does not match metadata.")
        if checkpoint.get("input_size") != input_size or checkpoint.get("mean") != mean or checkpoint.get("std") != std:
            raise ValueError("Checkpoint preprocessing does not match metadata.")

        model = models.mobilenet_v2(weights=None)
        model.classifier[1] = nn.Linear(model.last_channel, len(classes))
        model.load_state_dict(checkpoint["state_dict"], strict=True)
        model.to("cpu")
        model.eval()

        _classifier_transform = transforms.Compose([
            transforms.Resize(tuple(resize)),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ])
        _classifier = model
        _classifier_classes = tuple(classes)
        _classifier_error = None
        logger.info("Loaded %s on CPU with class mapping %s", CLASSIFIER_NAME, class_to_idx)
        return True
    except Exception as error:
        _classifier = None
        _classifier_error = str(error) or error.__class__.__name__
        logger.exception("Could not load %s: %s", CLASSIFIER_NAME, _classifier_error)
        return False


def get_freshness_classifier():
    return _classifier


def get_classifier_error():
    return _classifier_error


def get_classifier_classes():
    return _classifier_classes


def get_classifier_transform():
    return _classifier_transform
