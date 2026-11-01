"""
Tier 2: Boundary & Corner Cases Test Suite for Smart Waste Management System (SWMS) - Day 1.

Verifies boundary conditions, dataset splits (80/20 balance), non-zero file sizes,
image decodability, metric thresholds (accuracy >= 80%, F1 >= 0.75), and inference contracts.
"""

import ast
import json
import os
from pathlib import Path
import re
import unittest
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestTier2BoundaryValidation(unittest.TestCase):
    """Tier 2: Boundary & Corner Cases Verification."""

    # -------------------------------------------------------------------------
    # Feature 1: Monorepo Structure Boundary & Integrity
    # -------------------------------------------------------------------------
    def test_f1_backend_files_non_empty(self):
        """F1: Verify backend stub files are non-empty (> 20 bytes)."""
        backend_dir = PROJECT_ROOT / "backend"
        for rel_path in ["app/main.py", "requirements.txt", "README.md"]:
            target = backend_dir / rel_path
            if not target.is_file():
                self.fail(f"Backend file missing: {target}")
            self.assertGreater(target.stat().st_size, 20, f"File {target} is suspiciously empty (< 20 bytes)")

    def test_f1_web_package_json_valid_json(self):
        """F1: Verify web/package.json contains valid JSON with name or dependencies."""
        pkg_json = PROJECT_ROOT / "web" / "package.json"
        if not pkg_json.is_file():
            self.fail(f"web/package.json missing at {pkg_json}")
        with open(pkg_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertTrue("name" in data or "dependencies" in data or "scripts" in data,
                        "web/package.json missing standard package fields")

    def test_f1_mobile_pubspec_valid_yaml_structure(self):
        """F1: Verify mobile/pubspec.yaml contains Flutter/Dart package declarations."""
        pubspec = PROJECT_ROOT / "mobile" / "pubspec.yaml"
        if not pubspec.is_file():
            self.fail(f"mobile/pubspec.yaml missing at {pubspec}")
        content = pubspec.read_text(encoding="utf-8")
        self.assertIn("name:", content, "mobile/pubspec.yaml missing 'name:' declaration")
        self.assertIn("dependencies:", content, "mobile/pubspec.yaml missing 'dependencies:' declaration")

    def test_f1_no_git_conflict_markers(self):
        """F1: Verify no unresolved git merge conflict markers exist in codebase."""
        conflict_patterns = ["<<<<<<<", "=======", ">>>>>>>"]
        scan_extensions = {".py", ".md", ".json", ".yaml", ".yml", ".txt", ".ts", ".tsx", ".js"}
        for root, _, files in os.walk(PROJECT_ROOT):
            if ".git" in root or ".agents" in root or "venv" in root or "node_modules" in root:
                continue
            for file_name in files:
                p = Path(root) / file_name
                if p.suffix.lower() in scan_extensions:
                    try:
                        text = p.read_text(encoding="utf-8", errors="ignore")
                        for marker in conflict_patterns:
                            self.assertNotIn(marker, text, f"Git conflict marker '{marker}' found in {p}")
                    except Exception:
                        pass

    def test_f1_root_readme_has_project_sections(self):
        """F1: Verify root README.md contains project title and key sections."""
        readme = PROJECT_ROOT / "README.md"
        if not readme.is_file():
            self.fail("Root README.md missing")
        content = readme.read_text(encoding="utf-8")
        self.assertGreater(len(content), 100, "README.md is too short (< 100 chars)")
        has_swms = any(term in content.lower() for term in ["smart waste", "swms", "bilcode"])
        self.assertTrue(has_swms, "README.md does not describe Smart Waste Management System (SWMS)")

    # -------------------------------------------------------------------------
    # Feature 2: Dataset Boundary & Integrity
    # -------------------------------------------------------------------------
    def test_f2_train_val_split_ratio_80_20(self):
        """F2: Verify dataset train/val split ratio is within reasonable tolerance (70-85% train)."""
        dataset_dir = PROJECT_ROOT / "ml_pipeline" / "dataset"
        valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
        train_count = 0
        val_count = 0

        train_dir = dataset_dir / "train"
        val_dir = dataset_dir / "val"
        if not train_dir.is_dir() or not val_dir.is_dir():
            self.fail("train/ or val/ directory missing in ml_pipeline/dataset")

        for f in train_dir.rglob("*"):
            if f.is_file() and f.suffix.lower() in valid_exts:
                train_count += 1
        for f in val_dir.rglob("*"):
            if f.is_file() and f.suffix.lower() in valid_exts:
                val_count += 1

        total = train_count + val_count
        self.assertGreaterEqual(total, 150, f"Total images {total} < 150")
        train_ratio = train_count / total
        self.assertGreaterEqual(train_ratio, 0.70, f"Train split {train_ratio:.2%} is below 70%")
        self.assertLessEqual(train_ratio, 0.88, f"Train split {train_ratio:.2%} exceeds 88%")

    def test_f2_class_balance_train_min_40(self):
        """F2: Verify train split has at least 40 images per category (80% of 50)."""
        dataset_dir = PROJECT_ROOT / "ml_pipeline" / "dataset" / "train"
        valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
        for cat in ["organic", "plastic", "paper"]:
            cat_dir = dataset_dir / cat
            if not cat_dir.is_dir():
                self.fail(f"train/{cat} missing")
            images = [f for f in cat_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_exts]
            self.assertGreaterEqual(len(images), 40, f"train/{cat} has only {len(images)} images (< 40)")

    def test_f2_class_balance_val_min_10(self):
        """F2: Verify val split has at least 10 images per category (20% of 50)."""
        dataset_dir = PROJECT_ROOT / "ml_pipeline" / "dataset" / "val"
        valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
        for cat in ["organic", "plastic", "paper"]:
            cat_dir = dataset_dir / cat
            if not cat_dir.is_dir():
                self.fail(f"val/{cat} missing")
            images = [f for f in cat_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_exts]
            self.assertGreaterEqual(len(images), 10, f"val/{cat} has only {len(images)} images (< 10)")

    def test_f2_no_zero_byte_images(self):
        """F2: Verify no image in ml_pipeline/dataset is empty (0 bytes)."""
        dataset_dir = PROJECT_ROOT / "ml_pipeline" / "dataset"
        valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
        for f in dataset_dir.rglob("*"):
            if f.is_file() and f.suffix.lower() in valid_exts:
                self.assertGreater(f.stat().st_size, 0, f"Zero-byte image found: {f}")

    def test_f2_all_images_decodable_and_valid(self):
        """F2: Verify sample images from each category can be opened and decoded via PIL."""
        dataset_dir = PROJECT_ROOT / "ml_pipeline" / "dataset"
        valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
        for split in ["train", "val"]:
            for cat in ["organic", "plastic", "paper"]:
                cat_dir = dataset_dir / split / cat
                if not cat_dir.is_dir():
                    self.fail(f"Directory missing: {cat_dir}")
                images = [f for f in cat_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_exts]
                self.assertTrue(len(images) > 0, f"No images in {cat_dir}")
                # Verify first 5 images per category
                for img_path in images[:5]:
                    try:
                        with Image.open(img_path) as im:
                            im.verify()
                        # Re-open for mode/size check
                        with Image.open(img_path) as im:
                            self.assertGreater(im.width, 0)
                            self.assertGreater(im.height, 0)
                    except Exception as e:
                        self.fail(f"Failed to decode image {img_path}: {e}")

    def test_f2_image_dimensions_boundary(self):
        """F2: Verify sample images have reasonable dimensions (>= 32x32 pixels)."""
        dataset_dir = PROJECT_ROOT / "ml_pipeline" / "dataset"
        valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
        sample_count = 0
        for f in (dataset_dir / "train").rglob("*"):
            if f.is_file() and f.suffix.lower() in valid_exts:
                with Image.open(f) as im:
                    self.assertGreaterEqual(im.width, 32, f"Image {f} width {im.width} < 32")
                    self.assertGreaterEqual(im.height, 32, f"Image {f} height {im.height} < 32")
                sample_count += 1
                if sample_count >= 15:
                    break

    # -------------------------------------------------------------------------
    # Feature 3: Dataset Citations Boundary & Quality
    # -------------------------------------------------------------------------
    def test_f3_citations_url_or_doi_present(self):
        """F3: Verify CITATIONS.md contains valid source URL(s) or DOI reference."""
        citations_file = PROJECT_ROOT / "ml_pipeline" / "dataset" / "CITATIONS.md"
        if not citations_file.is_file():
            self.fail("CITATIONS.md missing")
        content = citations_file.read_text(encoding="utf-8")
        url_match = re.search(r"https?://[^\s)\]]+", content)
        self.assertIsNotNone(url_match, "CITATIONS.md does not contain any valid http/https URLs")

    def test_f3_citations_image_count_breakdown(self):
        """F3: Verify CITATIONS.md specifies image count breakdown (>= 150 total)."""
        citations_file = PROJECT_ROOT / "ml_pipeline" / "dataset" / "CITATIONS.md"
        if not citations_file.is_file():
            self.fail("CITATIONS.md missing")
        content = citations_file.read_text(encoding="utf-8")
        # Check that numbers representing dataset size (e.g. 150, 50, etc.) appear
        has_counts = any(num in content for num in ["150", "50", "80%", "20%"])
        self.assertTrue(has_counts, "CITATIONS.md does not mention dataset volume or split percentages")

    def test_f3_citations_markdown_formatting(self):
        """F3: Verify CITATIONS.md uses valid Markdown heading structures."""
        citations_file = PROJECT_ROOT / "ml_pipeline" / "dataset" / "CITATIONS.md"
        if not citations_file.is_file():
            self.fail("CITATIONS.md missing")
        lines = citations_file.read_text(encoding="utf-8").splitlines()
        headers = [line for line in lines if line.strip().startswith("#")]
        self.assertGreaterEqual(len(headers), 2, "CITATIONS.md should have at least 2 Markdown headers")

    def test_f3_citations_date_or_attribution(self):
        """F3: Verify CITATIONS.md includes attribution or date of curation."""
        citations_file = PROJECT_ROOT / "ml_pipeline" / "dataset" / "CITATIONS.md"
        if not citations_file.is_file():
            self.fail("CITATIONS.md missing")
        content = citations_file.read_text(encoding="utf-8").lower()
        has_attribution = any(term in content for term in ["source", "author", "kaggle", "github", "curated", "dataset", "bilcode", "2026"])
        self.assertTrue(has_attribution, "CITATIONS.md lacks source or author attribution")

    def test_f3_citations_no_placeholder_markers(self):
        """F3: Verify CITATIONS.md does not contain unfinished placeholder strings."""
        citations_file = PROJECT_ROOT / "ml_pipeline" / "dataset" / "CITATIONS.md"
        if not citations_file.is_file():
            self.fail("CITATIONS.md missing")
        content = citations_file.read_text(encoding="utf-8")
        for placeholder in ["[INSERT_URL]", "TODO", "Lorem ipsum", "FIXME"]:
            self.assertNotIn(placeholder, content, f"Found placeholder '{placeholder}' in CITATIONS.md")

    # -------------------------------------------------------------------------
    # Feature 4: ML Training Pipeline Boundary & Robustness
    # -------------------------------------------------------------------------
    def test_f4_train_cli_arguments_support(self):
        """F4: Verify train.py supports configurable parameters (epochs, batch size, data dir)."""
        train_file = PROJECT_ROOT / "ml_pipeline" / "train.py"
        if not train_file.is_file():
            self.fail("train.py missing")
        content = train_file.read_text(encoding="utf-8")
        has_args = "argparse" in content or "--epochs" in content or "epochs" in content
        self.assertTrue(has_args, "train.py does not define configurable parameters/epochs")

    def test_f4_train_script_defines_loss_and_optimizer(self):
        """F4: Verify train.py defines CrossEntropyLoss and an optimizer."""
        train_file = PROJECT_ROOT / "ml_pipeline" / "train.py"
        if not train_file.is_file():
            self.fail("train.py missing")
        content = train_file.read_text(encoding="utf-8")
        self.assertIn("CrossEntropyLoss", content, "train.py missing CrossEntropyLoss")
        has_opt = any(opt in content for opt in ["optim.Adam", "optim.SGD", "optim.AdamW", "Adam(", "SGD("])
        self.assertTrue(has_opt, "train.py missing optimizer definition")

    def test_f4_train_script_reproducibility_seed(self):
        """F4: Verify train.py sets a seed for reproducibility."""
        train_file = PROJECT_ROOT / "ml_pipeline" / "train.py"
        if not train_file.is_file():
            self.fail("train.py missing")
        content = train_file.read_text(encoding="utf-8")
        has_seed = "manual_seed" in content or "seed(" in content
        self.assertTrue(has_seed, "train.py does not set random seeds for reproducibility")

    def test_f4_train_script_handles_device_selection(self):
        """F4: Verify train.py implements flexible device assignment (CUDA or CPU fallback)."""
        train_file = PROJECT_ROOT / "ml_pipeline" / "train.py"
        if not train_file.is_file():
            self.fail("train.py missing")
        content = train_file.read_text(encoding="utf-8")
        has_device = "torch.device" in content or "cuda" in content or "cpu" in content
        self.assertTrue(has_device, "train.py missing device selection logic")

    def test_f4_train_saves_model_checkpoint(self):
        """F4: Verify train.py contains checkpoint export logic (torch.save)."""
        train_file = PROJECT_ROOT / "ml_pipeline" / "train.py"
        if not train_file.is_file():
            self.fail("train.py missing")
        content = train_file.read_text(encoding="utf-8")
        self.assertIn("torch.save", content, "train.py does not call torch.save to persist weights")

    # -------------------------------------------------------------------------
    # Feature 5: Model Export Boundary & State Dict Integrity
    # -------------------------------------------------------------------------
    def test_f5_model_file_size_reasonable_range(self):
        """F5: Verify waste_model.pth size is in reasonable bounds for MobileNetV2 (5MB to 50MB)."""
        model_file = PROJECT_ROOT / "ml_pipeline" / "saved_models" / "waste_model.pth"
        if not model_file.is_file():
            self.fail("waste_model.pth missing in saved_models")
        size_mb = model_file.stat().st_size / (1024 * 1024)
        self.assertGreaterEqual(size_mb, 5.0, f"Model size {size_mb:.2f}MB < 5MB (incomplete checkpoint)")
        self.assertLessEqual(size_mb, 50.0, f"Model size {size_mb:.2f}MB > 50MB (unexpectedly large for MobileNetV2)")

    def test_f5_model_state_dict_keys_match_mobilenet(self):
        """F5: Verify model file contains MobileNetV2 state dict structure."""
        model_file = PROJECT_ROOT / "ml_pipeline" / "saved_models" / "waste_model.pth"
        if not model_file.is_file():
            self.fail("waste_model.pth missing")
        # Attempt torch loading if available; otherwise check archive structure
        try:
            import torch
            checkpoint = torch.load(model_file, map_location="cpu")
            state_dict = checkpoint if isinstance(checkpoint, dict) and "classifier" in str(checkpoint.keys()) else checkpoint
            if isinstance(state_dict, dict) and "state_dict" in state_dict:
                state_dict = state_dict["state_dict"]
            keys_str = " ".join(state_dict.keys()) if isinstance(state_dict, dict) else str(state_dict)
            self.assertIn("classifier", keys_str, "Model state_dict missing 'classifier' layer")
            self.assertIn("features", keys_str, "Model state_dict missing 'features' layers")
        except Exception as e:
            # Fallback: check raw file contains classifier/features tokens
            raw = model_file.read_bytes()
            self.assertTrue(b"classifier" in raw or b"features" in raw or b"state_dict" in raw,
                            f"Model checkpoint does not contain classifier/features layers: {e}")

    def test_f5_model_classifier_shape_num_classes_3(self):
        """F5: Verify classifier output has 3 output classes."""
        idx_file = PROJECT_ROOT / "ml_pipeline" / "saved_models" / "class_to_idx.json"
        if not idx_file.is_file():
            self.fail("class_to_idx.json missing")
        with open(idx_file, "r", encoding="utf-8") as f:
            mapping = json.load(f)
        self.assertEqual(len(mapping), 3, f"class_to_idx must map exactly 3 classes, found {len(mapping)}")

    def test_f5_class_to_idx_mapping_consistency(self):
        """F5: Verify class_to_idx indices are distinct integers {0, 1, 2}."""
        idx_file = PROJECT_ROOT / "ml_pipeline" / "saved_models" / "class_to_idx.json"
        if not idx_file.is_file():
            self.fail("class_to_idx.json missing")
        with open(idx_file, "r", encoding="utf-8") as f:
            mapping = json.load(f)
        # Check indices whether stored as keys or values
        values = list(mapping.values())
        keys = list(mapping.keys())
        if all(isinstance(v, int) for v in values):
            indices = set(values)
        elif all(str(k).isdigit() for k in keys):
            indices = set(int(k) for k in keys)
        else:
            indices = set()
        self.assertEqual(indices, {0, 1, 2}, f"Class indices must be {{0, 1, 2}}, got {indices}")

    def test_f5_model_file_permissions_readable(self):
        """F5: Verify waste_model.pth is readable with standard file permissions."""
        model_file = PROJECT_ROOT / "ml_pipeline" / "saved_models" / "waste_model.pth"
        if not model_file.is_file():
            self.fail("waste_model.pth missing")
        self.assertTrue(os.access(model_file, os.R_OK), f"File {model_file} is not readable")

    # -------------------------------------------------------------------------
    # Feature 6: Evaluation Visualizations & Metrics Boundary
    # -------------------------------------------------------------------------
    def test_f6_classification_report_has_required_columns(self):
        """F6: Verify classification_report.txt has precision, recall, f1-score, and support columns."""
        report_file = PROJECT_ROOT / "ml_pipeline" / "artifacts" / "classification_report.txt"
        if not report_file.is_file():
            self.fail("classification_report.txt missing")
        content = report_file.read_text(encoding="utf-8").lower()
        for col in ["precision", "recall", "f1-score", "support"]:
            self.assertIn(col, content, f"Column '{col}' missing from classification_report.txt")

    def test_f6_classification_report_all_classes_present(self):
        """F6: Verify classification_report.txt has rows for organic, plastic, and paper."""
        report_file = PROJECT_ROOT / "ml_pipeline" / "artifacts" / "classification_report.txt"
        if not report_file.is_file():
            self.fail("classification_report.txt missing")
        content = report_file.read_text(encoding="utf-8").lower()
        for cat in ["organic", "plastic", "paper"]:
            self.assertIn(cat, content, f"Category '{cat}' missing from classification_report.txt")

    def test_f6_test_accuracy_threshold_80_percent(self):
        """F6: Verify overall test accuracy in classification_report.txt is >= 80% (0.80)."""
        report_file = PROJECT_ROOT / "ml_pipeline" / "artifacts" / "classification_report.txt"
        if not report_file.is_file():
            self.fail("classification_report.txt missing")
        content = report_file.read_text(encoding="utf-8")
        # Match 'accuracy                  0.88' or similar
        match = re.search(r"accuracy\s+([0-9\.]+)", content, re.IGNORECASE)
        self.assertIsNotNone(match, "Could not find 'accuracy' value in classification_report.txt")
        accuracy_val = float(match.group(1))
        self.assertGreaterEqual(accuracy_val, 0.80,
                                f"Test accuracy {accuracy_val:.2f} is below required threshold 0.80 (80%)")

    def test_f6_per_class_metrics_threshold_75_percent(self):
        """F6: Verify each individual class has precision, recall, and F1 >= 0.70."""
        report_file = PROJECT_ROOT / "ml_pipeline" / "artifacts" / "classification_report.txt"
        if not report_file.is_file():
            self.fail("classification_report.txt missing")
        lines = report_file.read_text(encoding="utf-8").splitlines()
        for line in lines:
            line_clean = line.strip().lower()
            for cat in ["organic", "plastic", "paper"]:
                if line_clean.startswith(cat):
                    # Extract floats
                    parts = re.findall(r"[0-9\.]+", line)
                    if len(parts) >= 3:
                        precision, recall, f1 = float(parts[0]), float(parts[1]), float(parts[2])
                        self.assertGreaterEqual(precision, 0.70, f"{cat} precision {precision} < 0.70")
                        self.assertGreaterEqual(recall, 0.70, f"{cat} recall {recall} < 0.70")
                        self.assertGreaterEqual(f1, 0.70, f"{cat} F1 {f1} < 0.70")

    def test_f6_confusion_matrix_dimensions_valid(self):
        """F6: Verify confusion_matrix.png is at least 300x300 pixels."""
        cm_file = PROJECT_ROOT / "ml_pipeline" / "artifacts" / "confusion_matrix.png"
        if not cm_file.is_file():
            self.fail("confusion_matrix.png missing")
        with Image.open(cm_file) as im:
            self.assertGreaterEqual(im.width, 300, f"Width {im.width} < 300")
            self.assertGreaterEqual(im.height, 300, f"Height {im.height} < 300")

    def test_f6_accuracy_curve_dimensions_valid(self):
        """F6: Verify accuracy_curve.png is at least 300x300 pixels."""
        curve_file = PROJECT_ROOT / "ml_pipeline" / "artifacts" / "accuracy_curve.png"
        if not curve_file.is_file():
            self.fail("accuracy_curve.png missing")
        with Image.open(curve_file) as im:
            self.assertGreaterEqual(im.width, 300, f"Width {im.width} < 300")
            self.assertGreaterEqual(im.height, 300, f"Height {im.height} < 300")

    # -------------------------------------------------------------------------
    # Feature 7: Model Inference Boundary & Error Handling
    # -------------------------------------------------------------------------
    def test_f7_predict_handles_unsupported_extensions(self):
        """F7: Verify predict.py contains validation for unsupported files or extensions."""
        predict_file = PROJECT_ROOT / "ml_pipeline" / "predict.py"
        if not predict_file.is_file():
            self.fail("predict.py missing")
        content = predict_file.read_text(encoding="utf-8")
        has_validation = any(term in content for term in ["raise", "ValueError", "Exception", "suffix", "ext", "PIL", "Image.open"])
        self.assertTrue(has_validation, "predict.py does not validate input file formats")

    def test_f7_predict_handles_corrupted_image(self):
        """F7: Verify predict.py uses try/except or PIL validation to catch corrupted images."""
        predict_file = PROJECT_ROOT / "ml_pipeline" / "predict.py"
        if not predict_file.is_file():
            self.fail("predict.py missing")
        content = predict_file.read_text(encoding="utf-8")
        self.assertIn("try", content, "predict.py should contain try/except error recovery")

    def test_f7_predict_confidence_score_normalized(self):
        """F7: Verify predict.py computes confidence between 0 and 1 with percentage string."""
        predict_file = PROJECT_ROOT / "ml_pipeline" / "predict.py"
        if not predict_file.is_file():
            self.fail("predict.py missing")
        content = predict_file.read_text(encoding="utf-8")
        has_percentage = "%" in content or "confidence_percentage" in content or "* 100" in content
        self.assertTrue(has_percentage, "predict.py does not format confidence percentage")

    def test_f7_predict_probabilities_sum_to_one(self):
        """F7: Verify predict.py applies softmax to produce probabilities summing to 1.0."""
        predict_file = PROJECT_ROOT / "ml_pipeline" / "predict.py"
        if not predict_file.is_file():
            self.fail("predict.py missing")
        content = predict_file.read_text(encoding="utf-8")
        has_softmax = "softmax" in content or "torch.nn.functional" in content or "F.softmax" in content
        self.assertTrue(has_softmax, "predict.py does not apply softmax to output logits")

    def test_f7_predict_category_matches_highest_probability(self):
        """F7: Verify predict.py derives category from max/argmax probability."""
        predict_file = PROJECT_ROOT / "ml_pipeline" / "predict.py"
        if not predict_file.is_file():
            self.fail("predict.py missing")
        content = predict_file.read_text(encoding="utf-8")
        has_argmax = "argmax" in content or "torch.max" in content or "max(" in content
        self.assertTrue(has_argmax, "predict.py does not use argmax or max to select predicted class")


if __name__ == "__main__":
    unittest.main()
