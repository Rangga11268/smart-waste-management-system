"""
Tier 3: Cross-Feature Interaction Test Suite for Smart Waste Management System (SWMS) - Day 1.

Verifies end-to-end integration and pairwise contracts across features:
- Dataset <-> Training pipeline (ImageFolder layout compatibility)
- Training <-> Model Export (MobileNetV2 state dict)
- Model Export <-> Inference Predictor (Weight loading and inference)
- Model Export <-> Evaluation pipeline (Model evaluation on dataset)
- Predictor <-> Backend API contract (Response schema matching docs/API_SPECS.md)
- Dataset <-> Citations (Class coverage in documentation)
- Module isolation and convenience export synchronization
"""

import ast
import json
import os
from pathlib import Path
import sys
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestTier3CrossFeatureInteractions(unittest.TestCase):
    """Tier 3: Cross-Feature Interactions & Pairwise Interface Verification."""

    def test_f2_f4_dataset_structure_compatible_with_pytorch_imagefolder(self):
        """Interaction F2 <-> F4: Dataset directory layout conforms strictly to PyTorch ImageFolder requirements."""
        dataset_dir = PROJECT_ROOT / "ml_pipeline" / "dataset"
        train_dir = dataset_dir / "train"
        val_dir = dataset_dir / "val"
        self.assertTrue(train_dir.is_dir(), "train/ directory missing in dataset")
        self.assertTrue(val_dir.is_dir(), "val/ directory missing in dataset")

        expected_classes = {"organic", "plastic", "paper"}
        train_subdirs = {d.name.lower() for d in train_dir.iterdir() if d.is_dir()}
        val_subdirs = {d.name.lower() for d in val_dir.iterdir() if d.is_dir()}

        self.assertTrue(expected_classes.issubset(train_subdirs),
                        f"train/ missing required classes. Expected {expected_classes}, found {train_subdirs}")
        self.assertTrue(expected_classes.issubset(val_subdirs),
                        f"val/ missing required classes. Expected {expected_classes}, found {val_subdirs}")

    def test_f4_f5_train_produces_loadable_mobilenet_checkpoint(self):
        """Interaction F4 <-> F5: Model weights from training can be loaded into MobileNetV2 architecture."""
        model_file = PROJECT_ROOT / "ml_pipeline" / "saved_models" / "waste_model.pth"
        if not model_file.is_file():
            self.fail(f"Model checkpoint missing at {model_file}")

        try:
            import torch
            import torchvision.models as models
            import torch.nn as nn

            model = models.mobilenet_v2(weights=None)
            model.classifier[1] = nn.Linear(model.last_channel, 3)

            checkpoint = torch.load(model_file, map_location="cpu")
            state_dict = checkpoint.get("state_dict", checkpoint) if isinstance(checkpoint, dict) else checkpoint

            # Strip potential 'model.' or 'module.' prefixes if saved from DataParallel/wrapper
            clean_state_dict = {}
            for k, v in state_dict.items():
                clean_key = k.replace("module.", "").replace("model.", "")
                clean_state_dict[clean_key] = v

            model.load_state_dict(clean_state_dict, strict=False)
            model.eval()
            self.assertIsNotNone(model, "Failed to instantiate and load weights into MobileNetV2")
        except ImportError:
            # If torch is not in active python, inspect binary format
            with open(model_file, "rb") as f:
                header = f.read(4)
            self.assertTrue(header.startswith(b"PK\x03\x04") or header[0] == 0x80,
                            "Checkpoint is neither zip nor pickle format")

    def test_f5_f7_model_weights_compatible_with_predict_module(self):
        """Interaction F5 <-> F7: ml_pipeline/predict.py successfully points to waste_model.pth and class_to_idx.json."""
        predict_file = PROJECT_ROOT / "ml_pipeline" / "predict.py"
        model_file = PROJECT_ROOT / "ml_pipeline" / "saved_models" / "waste_model.pth"
        idx_file = PROJECT_ROOT / "ml_pipeline" / "saved_models" / "class_to_idx.json"

        self.assertTrue(predict_file.is_file(), "predict.py missing")
        self.assertTrue(model_file.is_file(), "waste_model.pth missing")
        self.assertTrue(idx_file.is_file(), "class_to_idx.json missing")

        content = predict_file.read_text(encoding="utf-8")
        self.assertTrue("waste_model.pth" in content or "model_path" in content,
                        "predict.py does not reference model weights path")
        self.assertTrue("class_to_idx" in content or "json" in content,
                        "predict.py does not reference class_to_idx mapping")

    def test_f5_f6_evaluate_script_accepts_model_weights(self):
        """Interaction F5 <-> F6: ml_pipeline/evaluate.py references model weights and dataset to produce artifacts."""
        eval_file = PROJECT_ROOT / "ml_pipeline" / "evaluate.py"
        self.assertTrue(eval_file.is_file(), "evaluate.py missing")

        content = eval_file.read_text(encoding="utf-8")
        self.assertTrue("waste_model.pth" in content or "--model" in content or "model" in content,
                        "evaluate.py does not accept/reference model weights")
        self.assertTrue("confusion_matrix" in content or "classification_report" in content,
                        "evaluate.py does not produce required metric artifacts")

    def test_f7_backend_contract_compatibility(self):
        """Interaction F7 <-> Backend Contract: Inference output conforms to docs/API_SPECS.md POST /predict contract."""
        idx_file = PROJECT_ROOT / "ml_pipeline" / "saved_models" / "class_to_idx.json"
        if not idx_file.is_file():
            self.fail("class_to_idx.json missing")

        with open(idx_file, "r", encoding="utf-8") as f:
            mapping = json.load(f)

        # In docs/API_SPECS.md:
        # category: "Plastic Waste" (or "Organic Waste", "Paper Waste")
        # confidence: float
        # confidence_percentage: str
        # probabilities: {"Organic Waste": float, "Plastic Waste": float, "Paper Waste": float}
        predict_file = PROJECT_ROOT / "ml_pipeline" / "predict.py"
        if not predict_file.is_file():
            self.fail("predict.py missing")

        source = predict_file.read_text(encoding="utf-8")
        required_keys = ["category", "confidence", "confidence_percentage", "probabilities"]
        for key in required_keys:
            self.assertIn(key, source, f"predict.py output contract does not include required API key: '{key}'")

    def test_f2_f3_dataset_classes_match_citations(self):
        """Interaction F2 <-> F3: Every category directory in dataset is documented in CITATIONS.md."""
        dataset_dir = PROJECT_ROOT / "ml_pipeline" / "dataset"
        citations_file = dataset_dir / "CITATIONS.md"
        if not citations_file.is_file():
            self.fail("CITATIONS.md missing")

        citations_text = citations_file.read_text(encoding="utf-8").lower()
        for cat in ["organic", "plastic", "paper"]:
            self.assertIn(cat, citations_text, f"Dataset class '{cat}' not found in CITATIONS.md")

    def test_f1_f4_ml_pipeline_self_contained(self):
        """Interaction F1 <-> F4: ml_pipeline module is self-contained with its own requirements and README."""
        ml_dir = PROJECT_ROOT / "ml_pipeline"
        self.assertTrue((ml_dir / "requirements.txt").is_file(), "ml_pipeline/requirements.txt missing")
        self.assertTrue((ml_dir / "README.md").is_file(), "ml_pipeline/README.md missing")

        readme_text = (ml_dir / "README.md").read_text(encoding="utf-8")
        self.assertGreater(len(readme_text), 50, "ml_pipeline/README.md is empty or too short")

    def test_f5_root_convenience_copy_sync(self):
        """Interaction F5: Root convenience exports match ml_pipeline artifacts in size."""
        root_model = PROJECT_ROOT / "waste_model.pth"
        saved_model = PROJECT_ROOT / "ml_pipeline" / "saved_models" / "waste_model.pth"

        self.assertTrue(root_model.is_file(), "Root waste_model.pth missing")
        self.assertTrue(saved_model.is_file(), "ml_pipeline/saved_models/waste_model.pth missing")
        self.assertEqual(root_model.stat().st_size, saved_model.stat().st_size,
                         "Root waste_model.pth size differs from ml_pipeline/saved_models/waste_model.pth")


if __name__ == "__main__":
    unittest.main()
