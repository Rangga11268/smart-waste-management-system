"""Tier 1 and Tier 2 Machine Learning Inference Test Suite for SWMS - Day 2.

Covers POST /api/v1/predict endpoint:
- Tier 1 (Feature Coverage):
  1. Valid JPEG image inference returning 200 OK, category, confidence, probabilities
  2. Valid PNG image inference
  3. Valid WebP image inference
  4. Probabilities dictionary completeness (3 classes: Organic, Plastic, Paper) and normalization (sum ~= 1.0)
  5. Public accessibility without Authorization header
  6. Authenticated accessibility with Bearer token
- Tier 2 (Boundary & Corner Cases):
  1. Unsupported file extension (.txt file) returning 400 Bad Request
  2. Unsupported file extension (.pdf file) returning 400 Bad Request
  3. Corrupted image bytes returning 400 Bad Request
  4. Empty file (0 bytes) returning 400 or 422
  5. Missing 'file' multipart form field returning 422 Unprocessable Entity
  6. Extreme dimension image handling (1x1 pixel image)
  7. Large dimension image handling (1000x1000 pixels)
  8. Grayscale (single-channel) image converted without runtime shape mismatch
"""

import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image


class TestTier1PredictFeatureCoverage:
    """Tier 1: Feature coverage for ML inference happy paths and contract conformance."""

    def test_predict_valid_jpeg_happy_path(self, client: TestClient, dummy_image_bytes: bytes):
        """Tier 1: Verify valid JPEG image classification returns full predicted schema."""
        files = {
            "file": ("evidence.jpg", dummy_image_bytes, "image/jpeg"),
        }

        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        body = response.json()
        assert body["status"] == "success"
        data = body["data"]

        # Validate predicted category and ID
        assert data["category"] in {"Organic Waste", "Plastic Waste", "Paper Waste"}
        assert data["category_id"] in {1, 2, 3}

        # Validate confidence score and percentage string
        assert isinstance(data["confidence"], (int, float))
        assert 0.0 <= data["confidence"] <= 1.0
        assert data["confidence_percentage"].endswith("%")

        # Validate probabilities mapping
        probs = data["probabilities"]
        assert "Organic Waste" in probs
        assert "Plastic Waste" in probs
        assert "Paper Waste" in probs

    def test_predict_valid_png_image(self, client: TestClient, dummy_png_bytes: bytes):
        """Tier 1: Verify valid PNG image inference succeeds with 200 OK."""
        files = {
            "file": ("waste_sample.png", dummy_png_bytes, "image/png"),
        }

        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()["data"]
        assert data["category"] in {"Organic Waste", "Plastic Waste", "Paper Waste"}

    def test_predict_valid_webp_image(self, client: TestClient, dummy_webp_bytes: bytes):
        """Tier 1: Verify valid WebP image inference succeeds with 200 OK."""
        files = {
            "file": ("sample.webp", dummy_webp_bytes, "image/webp"),
        }

        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()["data"]
        assert data["category"] in {"Organic Waste", "Plastic Waste", "Paper Waste"}

    def test_predict_probabilities_normalization_and_keys(self, client: TestClient, dummy_image_bytes: bytes):
        """Tier 1: Verify probabilities dictionary sum equals approximately 1.0 (Softmax output)."""
        files = {
            "file": ("test_norm.jpg", dummy_image_bytes, "image/jpeg"),
        }

        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 200
        probs = response.json()["data"]["probabilities"]

        total_prob = sum(probs.values())
        assert abs(total_prob - 1.0) < 0.05, f"Probabilities sum {total_prob} deviated from 1.0"
        for class_name, prob in probs.items():
            assert 0.0 <= prob <= 1.0

    def test_predict_public_accessibility_without_token(self, client: TestClient, dummy_image_bytes: bytes):
        """Tier 1: Verify /predict endpoint is publicly accessible without Authorization header."""
        files = {
            "file": ("public_test.jpg", dummy_image_bytes, "image/jpeg"),
        }

        response = client.post("/api/v1/predict", files=files)
        # Endpoint should not return 401 Unauthorized
        assert response.status_code == 200

    def test_predict_authenticated_accessibility_with_token(
        self, client: TestClient, dummy_image_bytes: bytes, user_headers
    ):
        """Tier 1: Verify /predict endpoint also accepts requests with Bearer token."""
        files = {
            "file": ("auth_test.jpg", dummy_image_bytes, "image/jpeg"),
        }

        response = client.post("/api/v1/predict", files=files, headers=user_headers)
        assert response.status_code == 200


class TestTier2PredictBoundaryAndCornerCases:
    """Tier 2: Boundary cases, unsupported extensions, corrupted files, and dimension stress."""

    def test_predict_unsupported_extension_txt_rejected(self, client: TestClient):
        """Tier 2: Verify uploading a plain text file returns 400 Bad Request."""
        text_content = b"This is a text file, not an image of waste."
        files = {
            "file": ("notes.txt", text_content, "text/plain"),
        }

        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
        assert "detail" in response.json()

    def test_predict_unsupported_extension_pdf_rejected(self, client: TestClient):
        """Tier 2: Verify uploading a PDF document returns 400 Bad Request."""
        pdf_content = b"%PDF-1.5 %fake binary PDF stream"
        files = {
            "file": ("document.pdf", pdf_content, "application/pdf"),
        }

        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"

    def test_predict_corrupt_image_bytes_rejected(self, client: TestClient, corrupt_image_bytes: bytes):
        """Tier 2: Verify uploading corrupted image bytes returns 400 Bad Request."""
        files = {
            "file": ("corrupt.jpg", corrupt_image_bytes, "image/jpeg"),
        }

        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"

    def test_predict_empty_file_zero_bytes_rejected(self, client: TestClient, empty_file_bytes: bytes):
        """Tier 2: Verify uploading 0-byte file returns 400 Bad Request or 422 Unprocessable Entity."""
        files = {
            "file": ("empty.jpg", empty_file_bytes, "image/jpeg"),
        }

        response = client.post("/api/v1/predict", files=files)
        assert response.status_code in (400, 422), f"Expected 400 or 422, got {response.status_code}"

    def test_predict_missing_file_form_field(self, client: TestClient):
        """Tier 2: Verify request without required 'file' form field returns 422 Unprocessable Entity."""
        # Send multipart request with wrongly named field
        files = {
            "wrong_field_name": ("test.jpg", b"dummy", "image/jpeg"),
        }

        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 422

    def test_predict_extreme_small_dimension_1x1(self, client: TestClient):
        """Tier 2: Verify inference handles extreme 1x1 pixel image without division or resize errors."""
        img = Image.new("RGB", (1, 1), color=(100, 100, 100))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        bytes_1x1 = buf.getvalue()

        files = {
            "file": ("tiny_1x1.jpg", bytes_1x1, "image/jpeg"),
        }

        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 200
        assert "category" in response.json()["data"]

    def test_predict_large_dimension_image(self, client: TestClient):
        """Tier 2: Verify inference handles larger 1000x1000 image smoothly within memory budget."""
        img = Image.new("RGB", (1000, 1000), color=(200, 150, 50))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=80)
        bytes_large = buf.getvalue()

        files = {
            "file": ("large_1000x1000.jpg", bytes_large, "image/jpeg"),
        }

        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 200
        assert "category" in response.json()["data"]

    def test_predict_grayscale_mode_image(self, client: TestClient):
        """Tier 2: Verify 1-channel Grayscale image is converted to 3-channel RGB without crashing."""
        img = Image.new("L", (128, 128), color=128)  # Mode 'L' = 8-bit grayscale
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        bytes_gray = buf.getvalue()

        files = {
            "file": ("grayscale.png", bytes_gray, "image/png"),
        }

        response = client.post("/api/v1/predict", files=files)
        assert response.status_code == 200
        assert "category" in response.json()["data"]
