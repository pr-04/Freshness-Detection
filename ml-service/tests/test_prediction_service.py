"""Unit tests for full-image MobileNetV2 inference."""

import unittest
from unittest.mock import patch

import torch
from PIL import Image

from app import prediction_service


class FakeClassifier:
    def __init__(self, logits):
        self.logits = torch.tensor([logits], dtype=torch.float32)
        self.received_shape = None

    def __call__(self, tensor):
        self.received_shape = tuple(tensor.shape)
        return self.logits


class PredictionServiceTests(unittest.TestCase):
    def run_prediction(self, logits, image_size=(80, 60), threshold=0.60):
        classifier = FakeClassifier(logits)
        transformed_images = []

        def transform(image):
            transformed_images.append((image.size, image.mode))
            return torch.zeros((3, 224, 224), dtype=torch.float32)

        with (
            patch.object(prediction_service, "get_freshness_classifier", return_value=classifier),
            patch.object(prediction_service, "get_classifier_transform", return_value=transform),
            patch.object(prediction_service, "get_classifier_classes", return_value=("fresh", "rotten")),
            Image.new("RGB", image_size, "green") as image,
        ):
            result = prediction_service.predict_freshness(image, "apple", threshold)
        return result, classifier, transformed_images

    def test_supported_fruit_selection_is_canonical_user_metadata(self):
        self.assertEqual(prediction_service.canonical_fruit("  gUaVa "), "Guava")
        self.assertIsNone(prediction_service.canonical_fruit("Grape"))
        self.assertIsNone(prediction_service.canonical_fruit("Jujube"))

    def test_direct_full_image_uses_rgb_transform_without_crop(self):
        result, classifier, transformed = self.run_prediction([3.0, 0.0])
        self.assertEqual(result["fruit"], "Apple")
        self.assertEqual(result["freshness"], "Fresh")
        self.assertEqual(classifier.received_shape, (1, 3, 224, 224))
        self.assertEqual(transformed, [((80, 60), "RGB")])
        self.assertAlmostEqual(result["probabilities"]["fresh"] + result["probabilities"]["rotten"], 1.0, places=5)

    def test_rotten_index_maps_using_checkpoint_class_order(self):
        result, _, _ = self.run_prediction([0.0, 3.0])
        self.assertEqual(result["freshness"], "Rotten")

    def test_low_top_class_score_returns_uncertain(self):
        result, _, _ = self.run_prediction([0.0, 0.0])
        self.assertTrue(result["uncertain"])
        self.assertEqual(result["freshness"], "Uncertain")
        self.assertIsNotNone(result["uncertainty_reason"])

    def test_unsupported_fruit_is_rejected_by_prediction_service(self):
        with Image.new("RGB", (20, 20), "red") as image:
            with self.assertRaisesRegex(ValueError, "Unsupported fruit"):
                prediction_service.predict_freshness(image, "Grape")


if __name__ == "__main__":
    unittest.main()
