"""FastAPI route tests using the local classifier checkpoint and generated fixtures."""

import unittest
from io import BytesIO
from unittest.mock import patch

from PIL import Image
import torch
from fastapi.testclient import TestClient

from app import main

class MainApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Keep the CPU-only integration test responsive on high-core-count hosts.
        torch.set_num_threads(1)
        cls.client_context = TestClient(main.app)
        cls.client = cls.client_context.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client_context.__exit__(None, None, None)

    def image_bytes(self, color):
        image_data = BytesIO()
        Image.new("RGB", (96, 72), color).save(image_data, format="JPEG")
        return image_data.getvalue()

    def test_health_reports_classifier_loading_state(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["model_loaded"])
        self.assertTrue(data["models"]["classifier"]["loaded"])

    def test_valid_image_runs_full_image_prediction(self):
        image_bytes = self.image_bytes("green")
        response = self.client.post(
            "/predict",
            data={"fruit": "Apple"},
            files={"file": ("sample.jpg", image_bytes, "image/jpeg")},
        )
        self.assertEqual(response.status_code, 200, response.text)
        data = response.json()
        self.assertFalse(data["mock"])
        self.assertEqual(data["prediction"]["fruit"], "Apple")
        prediction = data["prediction"]
        self.assertIn(prediction["freshness"], {"Fresh", "Rotten", "Uncertain"})
        self.assertEqual(prediction["model"], "MobileNetV2")
        self.assertAlmostEqual(sum(prediction["probabilities"].values()), 1.0, places=5)

    def test_unsupported_mime_is_rejected(self):
        response = self.client.post(
            "/predict", data={"fruit": "Apple"},
            files={"file": ("note.txt", b"not an image", "text/plain")},
        )
        self.assertEqual(response.status_code, 400)

    def test_corrupted_image_is_rejected(self):
        response = self.client.post(
            "/predict", data={"fruit": "Apple"},
            files={"file": ("broken.jpg", b"broken jpeg bytes", "image/jpeg")},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("valid readable image", response.json()["detail"])

    def test_missing_fruit_selection_is_rejected(self):
        response = self.client.post(
            "/predict", files={"file": ("sample.jpg", self.image_bytes("green"), "image/jpeg")},
        )
        self.assertEqual(response.status_code, 422)

    def test_unsupported_fruit_selection_is_rejected(self):
        response = self.client.post(
            "/predict", data={"fruit": "Grape"},
            files={"file": ("sample.jpg", self.image_bytes("green"), "image/jpeg")},
        )
        self.assertEqual(response.status_code, 400)

    def test_low_confidence_response_is_uncertain(self):
        uncertain = {
            "fruit": "Apple", "freshness": "Uncertain", "uncertain": True,
            "uncertainty_reason": "Low score", "probabilities": {"fresh": 0.51, "rotten": 0.49},
            "model": "MobileNetV2",
        }
        with patch.object(main, "predict_freshness", return_value=uncertain):
            response = self.client.post(
                "/predict", data={"fruit": "Apple"},
                files={"file": ("sample.jpg", self.image_bytes("green"), "image/jpeg")},
            )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertTrue(response.json()["prediction"]["uncertain"])
        self.assertEqual(response.json()["prediction"]["freshness"], "Uncertain")

    def test_oversized_image_is_rejected(self):
        response = self.client.post(
            "/predict", data={"fruit": "Apple"},
            files={"file": ("large.jpg", b"x" * (main.MAX_FILE_SIZE + 1), "image/jpeg")},
        )
        self.assertEqual(response.status_code, 413)


if __name__ == "__main__":
    unittest.main()
