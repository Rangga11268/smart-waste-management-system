"""
Tier 4: Real-World Scenarios Test Suite for Smart Waste Management System (SWMS) - Day 1.

Exercises end-to-end user workflows:
1. Full Model Load & Classify Organic Waste Image
2. Full Model Load & Classify Plastic Waste Image
3. Full Model Load & Classify Paper Waste Image
4. Model Robustness Across Varied Aspect Ratios & Dimensions (Mobile Camera Simulation)
5. Classification Report Metric Integrity & Bilcode Acceptance Audit
6. Monorepo Stubs Syntax & Framework Readiness (FastAPI, Next.js, Flutter)
"""

import ast
import io
import json
import os
from pathlib import Path
import re
import unittest
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestTier4RealWorldScenarios(unittest.TestCase):
    """Tier 4: Realistic Application Scenarios Verification."""

    def _get_predictor(self):
        """Helper to load WastePredictor from ml_pipeline/predict.py if available."""
        predict_file = PROJECT_ROOT / "ml_pipeline" / "predict.py"
        if not predict_file.is_file():
            self.fail("ml_pipeline/predict.py missing")

        import importlib.util
        spec = importlib.util.spec_from_file_location("predict_module", str(predict_file))
        if spec is None or spec.loader is None:
            self.fail("Failed to load spec for predict.py")
        module = importlib.util.module_from_spec(spec)
        sys_path_added = False
        try:
            sys_path_str = str(PROJECT_ROOT / "ml_pipeline")
            if sys_path_str not in os.sys.path:
                os.sys.path.insert(0, sys_path_str)
                sys_path_added = True
            spec.loader.exec_module(module)
        except Exception as e:
            self.fail(f"Failed to import predict.py: {e}")
        finally:
            if sys_path_added and sys_path_str in os.sys.path:
                os.sys.path.remove(sys_path_str)

        # Look for WastePredictor class or predict function
        predictor_cls = getattr(module, "WastePredictor", None)
        if predictor_cls is not None:
            return predictor_cls()
        predict_fn = getattr(module, "predict", getattr(module, "predict_image", None))
        if predict_fn is not None:
            return predict_fn
        self.fail("predict.py does not define WastePredictor or predict()")

    def _run_prediction_on_image(self, predictor, image_path):
        """Invoke predictor callable or class method."""
        if hasattr(predictor, "predict"):
            return predictor.predict(str(image_path))
        elif callable(predictor):
            return predictor(str(image_path))
        self.fail("Predictor is neither callable nor has .predict() method")

    def test_scenario_1_organic_waste_image_inference(self):
        """Scenario 1: End-to-end inference on an actual Organic Waste sample image."""
        dataset_dir = PROJECT_ROOT / "ml_pipeline" / "dataset"
        organic_dir = dataset_dir / "val" / "organic"
        if not organic_dir.is_dir():
            organic_dir = dataset_dir / "train" / "organic"
        self.assertTrue(organic_dir.is_dir(), "No organic waste image directory found in dataset")

        images = [f for f in organic_dir.iterdir() if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
        self.assertGreater(len(images), 0, "No organic waste images found for inference")
        sample_img = images[0]

        # Verify image is readable
        with Image.open(sample_img) as im:
            self.assertGreater(im.width, 0)
            self.assertGreater(im.height, 0)

        # Execute prediction if predictor is available
        predictor = self._get_predictor()
        result = self._run_prediction_on_image(predictor, sample_img)

        self.assertIsInstance(result, dict, f"Inference result should be dict, got {type(result)}")
        self.assertIn("category", result, "Result missing 'category'")
        self.assertIn("confidence", result, "Result missing 'confidence'")
        self.assertIn("probabilities", result, "Result missing 'probabilities'")

        self.assertIsInstance(result["confidence"], (float, int))
        self.assertGreaterEqual(result["confidence"], 0.0)
        self.assertLessEqual(result["confidence"], 1.0)

    def test_scenario_2_plastic_waste_image_inference(self):
        """Scenario 2: End-to-end inference on an actual Plastic Waste sample image."""
        dataset_dir = PROJECT_ROOT / "ml_pipeline" / "dataset"
        plastic_dir = dataset_dir / "val" / "plastic"
        if not plastic_dir.is_dir():
            plastic_dir = dataset_dir / "train" / "plastic"
        self.assertTrue(plastic_dir.is_dir(), "No plastic waste image directory found in dataset")

        images = [f for f in plastic_dir.iterdir() if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
        self.assertGreater(len(images), 0, "No plastic waste images found for inference")
        sample_img = images[0]

        predictor = self._get_predictor()
        result = self._run_prediction_on_image(predictor, sample_img)

        self.assertIsInstance(result, dict)
        self.assertIn("category", result)
        self.assertIn("confidence", result)
        self.assertIn("probabilities", result)

    def test_scenario_3_paper_waste_image_inference(self):
        """Scenario 3: End-to-end inference on an actual Paper Waste sample image."""
        dataset_dir = PROJECT_ROOT / "ml_pipeline" / "dataset"
        paper_dir = dataset_dir / "val" / "paper"
        if not paper_dir.is_dir():
            paper_dir = dataset_dir / "train" / "paper"
        self.assertTrue(paper_dir.is_dir(), "No paper waste image directory found in dataset")

        images = [f for f in paper_dir.iterdir() if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}]
        self.assertGreater(len(images), 0, "No paper waste images found for inference")
        sample_img = images[0]

        predictor = self._get_predictor()
        result = self._run_prediction_on_image(predictor, sample_img)

        self.assertIsInstance(result, dict)
        self.assertIn("category", result)
        self.assertIn("confidence", result)
        self.assertIn("probabilities", result)

    def test_scenario_4_different_aspect_ratios_and_sizes(self):
        """Scenario 4: Mobile camera simulation with varied aspect ratios (portrait, landscape, square)."""
        aspect_ratios = [
            (1080, 1920),  # Portrait 9:16 mobile camera
            (1920, 1080),  # Landscape 16:9
            (600, 600),    # Square 1:1
            (120, 120),    # Small thumbnail
        ]

        predictor = self._get_predictor()
        tmp_dir = PROJECT_ROOT / "ml_pipeline" / "artifacts"
        tmp_dir.mkdir(parents=True, exist_ok=True)

        for w, h in aspect_ratios:
            # Create synthetic RGB test image
            img = Image.new("RGB", (w, h), color=(120, 150, 180))
            test_path = tmp_dir / f"test_aspect_{w}x{h}.jpg"
            img.save(test_path, "JPEG")
            try:
                result = self._run_prediction_on_image(predictor, test_path)
                self.assertIsInstance(result, dict, f"Failed prediction on {w}x{h}")
                self.assertIn("category", result)
                self.assertIn("confidence", result)
            finally:
                if test_path.is_file():
                    test_path.unlink()

    def test_scenario_5_classification_report_metrics_parsing_and_audit(self):
        """Scenario 5: Audit metrics in classification_report.txt against Bilcode standards."""
        report_file = PROJECT_ROOT / "ml_pipeline" / "artifacts" / "classification_report.txt"
        if not report_file.is_file():
            self.fail("classification_report.txt missing")

        content = report_file.read_text(encoding="utf-8")

        # 1. Check overall accuracy >= 80% (0.80)
        acc_match = re.search(r"accuracy\s+([0-9\.]+)", content, re.IGNORECASE)
        self.assertIsNotNone(acc_match, "Accuracy row missing from classification report")
        accuracy = float(acc_match.group(1))
        self.assertGreaterEqual(accuracy, 0.80, f"Accuracy {accuracy:.2f} < 0.80")

        # 2. Check macro avg F1 >= 0.75
        macro_match = re.search(r"macro avg\s+([0-9\.]+)\s+([0-9\.]+)\s+([0-9\.]+)", content, re.IGNORECASE)
        if macro_match:
            macro_f1 = float(macro_match.group(3))
            self.assertGreaterEqual(macro_f1, 0.75, f"Macro Avg F1 {macro_f1:.2f} < 0.75")

        # 3. Check weighted avg F1 >= 0.75
        weighted_match = re.search(r"weighted avg\s+([0-9\.]+)\s+([0-9\.]+)\s+([0-9\.]+)", content, re.IGNORECASE)
        if weighted_match:
            weighted_f1 = float(weighted_match.group(3))
            self.assertGreaterEqual(weighted_f1, 0.75, f"Weighted Avg F1 {weighted_f1:.2f} < 0.75")

    def test_scenario_6_monorepo_stubs_syntax_and_readiness(self):
        """Scenario 6: Monorepo stubs readiness for Day 2 (FastAPI), Day 3 (Next.js), and Day 4 (Flutter)."""
        # FastAPI
        backend_main = PROJECT_ROOT / "backend" / "app" / "main.py"
        if not backend_main.is_file():
            self.fail("backend/app/main.py missing")
        source = backend_main.read_text(encoding="utf-8")
        try:
            ast.parse(source)
        except SyntaxError as e:
            self.fail(f"Syntax error in backend/app/main.py: {e}")
        self.assertIn("FastAPI", source, "backend/app/main.py does not instantiate FastAPI")

        # Next.js
        pkg_json = PROJECT_ROOT / "web" / "package.json"
        if not pkg_json.is_file():
            self.fail("web/package.json missing")
        with open(pkg_json, "r", encoding="utf-8") as f:
            web_data = json.load(f)
        deps = {**web_data.get("dependencies", {}), **web_data.get("devDependencies", {})}
        self.assertTrue("next" in deps or "react" in deps, "web/package.json missing Next.js / React dependencies")

        # Flutter
        pubspec = PROJECT_ROOT / "mobile" / "pubspec.yaml"
        if not pubspec.is_file():
            self.fail("mobile/pubspec.yaml missing")
        pub_text = pubspec.read_text(encoding="utf-8")
        self.assertIn("flutter", pub_text.lower(), "mobile/pubspec.yaml missing Flutter declaration")


if __name__ == "__main__":
    unittest.main()
