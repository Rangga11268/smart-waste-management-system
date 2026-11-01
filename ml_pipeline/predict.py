"""
Waste Image Classifier Predictor & API Contract Implementation.
Smart Waste Management System (SWMS) - Bilcode Technology Take-Home Assessment.

Features:
- Lightweight, production-ready WastePredictor class.
- MobileNetV2 pretrained weights loader with graceful CPU/CUDA device fallback.
- Standard ImageNet preprocessing (Resize 256 -> CenterCrop 224 -> Normalize [0.485, 0.456, 0.406]).
- Strict validation for image formats, extensions, and corrupted files with descriptive errors.
- Softmax probability distribution summing to 1.0.
- Output contract matching docs/API_SPECS.md:
  {
    "category": "Plastic Waste",
    "confidence": 0.9421,
    "confidence_percentage": "94.21%",
    "category_id": 2,
    "probabilities": {
      "Organic Waste": 0.0312,
      "Plastic Waste": 0.9421,
      "Paper Waste": 0.0267
    }
  }
"""

import argparse
import io
import json
import os
from pathlib import Path
from typing import Dict, Union

from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from torchvision.models import mobilenet_v2

# Supported image file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

# Domain category definitions aligning with database ERD (id 1: Organic, 2: Plastic, 3: Paper)
CATEGORY_SPECS = {
    0: {"name": "Organic Waste", "slug": "organic", "category_id": 1},
    1: {"name": "Paper Waste", "slug": "paper", "category_id": 3},
    2: {"name": "Plastic Waste", "slug": "plastic", "category_id": 2},
}


class WastePredictor:
    """Inference predictor for waste image classification using MobileNetV2."""

    def __init__(
        self,
        model_path: Union[str, Path] = None,
        class_to_idx_path: Union[str, Path] = None,
        device: str = None
    ):
        # Resolve device
        if device is not None:
            self.device = torch.device(device)
        else:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Resolve model path
        self.model_path = self._resolve_model_path(model_path)
        self.class_to_idx_path = self._resolve_class_to_idx_path(class_to_idx_path)

        # Load class index mapping
        self.class_to_idx = self._load_class_to_idx()
        self.idx_to_class = {v: k for k, v in self.class_to_idx.items()}

        # Build transform pipeline with ImageNet normalization
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

        # Load MobileNetV2 model
        self.model = self._load_model()

    def _resolve_model_path(self, model_path: Union[str, Path]) -> Path:
        """Find waste_model.pth across canonical paths."""
        if model_path is not None:
            p = Path(model_path).resolve()
            if p.is_file():
                return p

        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent

        candidates = [
            script_dir / "saved_models" / "waste_model.pth",
            project_root / "waste_model.pth",
            Path("ml_pipeline/saved_models/waste_model.pth").resolve(),
            Path("waste_model.pth").resolve()
        ]
        for cand in candidates:
            if cand.is_file():
                return cand

        # Default fallback path even if not yet created
        return script_dir / "saved_models" / "waste_model.pth"

    def _resolve_class_to_idx_path(self, class_to_idx_path: Union[str, Path]) -> Path:
        """Find class_to_idx.json across canonical paths."""
        if class_to_idx_path is not None:
            p = Path(class_to_idx_path).resolve()
            if p.is_file():
                return p

        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent

        candidates = [
            script_dir / "saved_models" / "class_to_idx.json",
            project_root / "class_to_idx.json",
            Path("ml_pipeline/saved_models/class_to_idx.json").resolve(),
        ]
        for cand in candidates:
            if cand.is_file():
                return cand

        return script_dir / "saved_models" / "class_to_idx.json"

    def _load_class_to_idx(self) -> dict:
        """Load class_to_idx mapping or initialize standard fallback."""
        if self.class_to_idx_path.is_file():
            try:
                with open(self.class_to_idx_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "Organic Waste": 0,
            "Paper Waste": 1,
            "Plastic Waste": 2
        }

    def _load_model(self) -> nn.Module:
        """Instantiate MobileNetV2 architecture and load checkpoint weights."""
        num_classes = len(self.class_to_idx)
        model = mobilenet_v2(weights=None)
        model.classifier = nn.Sequential(
            nn.Dropout(p=0.2),
            nn.Linear(model.last_channel, num_classes)
        )

        if self.model_path.is_file():
            checkpoint = torch.load(self.model_path, map_location=self.device)
            state_dict = checkpoint.get("state_dict", checkpoint) if isinstance(checkpoint, dict) else checkpoint

            clean_state_dict = {}
            for k, v in state_dict.items():
                clean_key = k.replace("module.", "").replace("model.", "")
                clean_state_dict[clean_key] = v

            model.load_state_dict(clean_state_dict, strict=False)

        model = model.to(self.device)
        model.eval()
        return model

    def _prepare_image(self, image_input: Union[str, Path, bytes, io.BytesIO, Image.Image]) -> Image.Image:
        """Validate and open image with strict error handling for corrupted or unsupported inputs."""
        if isinstance(image_input, (str, Path)):
            path = Path(image_input)
            if not path.is_file():
                raise FileNotFoundError(f"Image file not found: {path}")

            ext = path.suffix.lower()
            if ext not in ALLOWED_EXTENSIONS:
                raise ValueError(
                    f"Unsupported image extension '{ext}'. Allowed extensions: {sorted(ALLOWED_EXTENSIONS)}"
                )

            try:
                # Open and verify integrity
                with open(path, "rb") as f:
                    data = f.read()
                img = Image.open(io.BytesIO(data))
                img.verify()
                # Reopen to load image buffer
                img = Image.open(io.BytesIO(data))
            except Exception as e:
                raise ValueError(f"Corrupted or invalid image file: {e}")

        elif isinstance(image_input, (bytes, bytearray)):
            try:
                img = Image.open(io.BytesIO(image_input))
                img.verify()
                img = Image.open(io.BytesIO(image_input))
            except Exception as e:
                raise ValueError(f"Corrupted or invalid image bytes: {e}")

        elif isinstance(image_input, io.BytesIO):
            try:
                img = Image.open(image_input)
                img.verify()
                image_input.seek(0)
                img = Image.open(image_input)
            except Exception as e:
                raise ValueError(f"Corrupted or invalid BytesIO image: {e}")

        elif isinstance(image_input, Image.Image):
            img = image_input
        else:
            raise TypeError(f"Unsupported image input type: {type(image_input)}")

        # Convert to RGB mode to handle grayscale, RGBA, CMYK gracefully
        if img.mode != "RGB":
            img = img.convert("RGB")

        return img

    def predict(self, image_input: Union[str, Path, bytes, io.BytesIO, Image.Image]) -> Dict:
        """
        Execute waste classification inference on an input image.

        Returns:
            dict matching docs/API_SPECS.md contract:
            {
                "category": "Plastic Waste",
                "confidence": 0.9421,
                "confidence_percentage": "94.21%",
                "category_id": 2,
                "probabilities": {
                    "Organic Waste": 0.0312,
                    "Plastic Waste": 0.9421,
                    "Paper Waste": 0.0267
                }
            }
        """
        # 1. Validate and prepare image
        image = self._prepare_image(image_input)

        # 2. Preprocessing & tensor creation
        input_tensor = self.transform(image).unsqueeze(0).to(self.device)

        # 3. Model inference
        with torch.no_grad():
            logits = self.model(input_tensor)
            probabilities = F.softmax(logits, dim=1)[0]

        probs_np = probabilities.cpu().numpy()

        # 4. Argmax selection
        best_idx = int(torch.argmax(probabilities).item())
        confidence = float(probs_np[best_idx])
        confidence_percentage = f"{confidence * 100:.2f}%"

        # 5. Build class probabilities dictionary
        prob_dict = {}
        for idx in range(len(probs_np)):
            spec = CATEGORY_SPECS.get(idx, {"name": f"Category_{idx}", "category_id": idx + 1})
            prob_dict[spec["name"]] = round(float(probs_np[idx]), 4)

        best_spec = CATEGORY_SPECS.get(best_idx, {"name": f"Category_{best_idx}", "category_id": best_idx + 1})

        result = {
            "category": best_spec["name"],
            "confidence": round(confidence, 4),
            "confidence_percentage": confidence_percentage,
            "category_id": best_spec["category_id"],
            "probabilities": prob_dict
        }
        return result

    def __call__(self, image_input: Union[str, Path, bytes, io.BytesIO, Image.Image]) -> Dict:
        """Make class instance directly callable."""
        return self.predict(image_input)


# Module-level convenience functions
_default_predictor = None


def get_default_predictor() -> WastePredictor:
    """Retrieve or lazily initialize the singleton predictor."""
    global _default_predictor
    if _default_predictor is None:
        _default_predictor = WastePredictor()
    return _default_predictor


def predict(image_input: Union[str, Path, bytes, io.BytesIO, Image.Image], **kwargs) -> Dict:
    """Convenience module-level predict function."""
    if kwargs:
        predictor = WastePredictor(**kwargs)
        return predictor.predict(image_input)
    return get_default_predictor().predict(image_input)


def predict_image(image_input: Union[str, Path, bytes, io.BytesIO, Image.Image], **kwargs) -> Dict:
    """Alias for predict function."""
    return predict(image_input, **kwargs)


def main():
    parser = argparse.ArgumentParser(description="Waste Image Classification Inference")
    parser.add_argument("image", type=str, help="Path to input image file")
    parser.add_argument("--model", type=str, default=None, help="Path to waste_model.pth")
    args = parser.parse_args()

    predictor = WastePredictor(model_path=args.model)
    result = predictor.predict(args.image)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
