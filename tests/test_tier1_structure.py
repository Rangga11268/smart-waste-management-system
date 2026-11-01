"""
Tier 1: Feature Coverage Test Suite for Smart Waste Management System (SWMS) - Day 1.

Verifies structural presence, file existence, image counts per class,
model file existence, and basic contracts across features F1 through F7.
"""

import ast
import json
import os
from pathlib import Path
import unittest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestTier1FeatureCoverage(unittest.TestCase):
    """Tier 1: Structural & Feature Coverage Verification."""

    # -------------------------------------------------------------------------
    # Feature 1: Monorepo Structure (ORIGINAL_REQUEST §R1, TASKS.md 1.1)
    # -------------------------------------------------------------------------
    def test_f1_backend_directory_and_structure(self):
        """F1: Verify backend module directory and required entrypoint files exist."""
        backend_dir = PROJECT_ROOT / "backend"
        self.assertTrue(backend_dir.is_dir(), f"backend/ directory missing at {backend_dir}")
        self.assertTrue((backend_dir / "app" / "main.py").is_file(), "backend/app/main.py missing")
        self.assertTrue((backend_dir / "requirements.txt").is_file(), "backend/requirements.txt missing")
        self.assertTrue((backend_dir / "README.md").is_file(), "backend/README.md missing")

    def test_f1_ml_pipeline_directory_and_structure(self):
        """F1: Verify ml_pipeline module directory and required subdirectories exist."""
        ml_dir = PROJECT_ROOT / "ml_pipeline"
        self.assertTrue(ml_dir.is_dir(), f"ml_pipeline/ directory missing at {ml_dir}")
        self.assertTrue((ml_dir / "dataset").is_dir(), "ml_pipeline/dataset/ missing")
        self.assertTrue((ml_dir / "saved_models").is_dir(), "ml_pipeline/saved_models/ missing")
        self.assertTrue((ml_dir / "artifacts").is_dir(), "ml_pipeline/artifacts/ missing")
        self.assertTrue((ml_dir / "train.py").is_file(), "ml_pipeline/train.py missing")
        self.assertTrue((ml_dir / "evaluate.py").is_file(), "ml_pipeline/evaluate.py missing")
        self.assertTrue((ml_dir / "predict.py").is_file(), "ml_pipeline/predict.py missing")

    def test_f1_web_directory_and_structure(self):
        """F1: Verify web module directory and package.json stub exist."""
        web_dir = PROJECT_ROOT / "web"
        self.assertTrue(web_dir.is_dir(), f"web/ directory missing at {web_dir}")
        self.assertTrue((web_dir / "package.json").is_file(), "web/package.json missing")
        self.assertTrue((web_dir / "README.md").is_file(), "web/README.md missing")

    def test_f1_mobile_directory_and_structure(self):
        """F1: Verify mobile module directory and pubspec.yaml stub exist."""
        mobile_dir = PROJECT_ROOT / "mobile"
        self.assertTrue(mobile_dir.is_dir(), f"mobile/ directory missing at {mobile_dir}")
        self.assertTrue((mobile_dir / "pubspec.yaml").is_file(), "mobile/pubspec.yaml missing")
        self.assertTrue((mobile_dir / "README.md").is_file(), "mobile/README.md missing")

    def test_f1_docs_directory_and_structure(self):
        """F1: Verify docs module directory and required specification files exist."""
        docs_dir = PROJECT_ROOT / "docs"
        self.assertTrue(docs_dir.is_dir(), f"docs/ directory missing at {docs_dir}")
        for doc_name in ["SPEC.md", "PRD.md", "ARCHITECTURE.md", "TASKS.md", "API_SPECS.md"]:
            self.assertTrue((docs_dir / doc_name).is_file(), f"docs/{doc_name} missing")

    def test_f1_root_configuration_files(self):
        """F1: Verify root monorepo configuration files exist."""
        self.assertTrue((PROJECT_ROOT / ".gitignore").is_file(), "Root .gitignore missing")
        self.assertTrue((PROJECT_ROOT / "README.md").is_file(), "Root README.md missing")

    # -------------------------------------------------------------------------
    # Feature 2: Dataset Curation & Partition (ORIGINAL_REQUEST §R2, TASKS.md 1.2)
    # -------------------------------------------------------------------------
    def test_f2_dataset_directory_structure(self):
        """F2: Verify ml_pipeline/dataset contains train/ and val/ partitions."""
        dataset_dir = PROJECT_ROOT / "ml_pipeline" / "dataset"
        self.assertTrue(dataset_dir.is_dir(), f"dataset dir missing at {dataset_dir}")
        self.assertTrue((dataset_dir / "train").is_dir(), "dataset/train/ directory missing")
        self.assertTrue((dataset_dir / "val").is_dir(), "dataset/val/ directory missing")

    def test_f2_train_categories_exist(self):
        """F2: Verify train partition contains organic, plastic, and paper categories."""
        train_dir = PROJECT_ROOT / "ml_pipeline" / "dataset" / "train"
        for cat in ["organic", "plastic", "paper"]:
            self.assertTrue((train_dir / cat).is_dir(), f"train category folder missing: {cat}")

    def test_f2_val_categories_exist(self):
        """F2: Verify val partition contains organic, plastic, and paper categories."""
        val_dir = PROJECT_ROOT / "ml_pipeline" / "dataset" / "val"
        for cat in ["organic", "plastic", "paper"]:
            self.assertTrue((val_dir / cat).is_dir(), f"val category folder missing: {cat}")

    def test_f2_image_files_present_in_all_partitions(self):
        """F2: Verify all 6 category folders contain valid image files."""
        dataset_dir = PROJECT_ROOT / "ml_pipeline" / "dataset"
        valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
        for split in ["train", "val"]:
            for cat in ["organic", "plastic", "paper"]:
                cat_dir = dataset_dir / split / cat
                if not cat_dir.is_dir():
                    self.fail(f"Folder missing: {cat_dir}")
                images = [f for f in cat_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_exts]
                self.assertGreater(len(images), 0, f"No images found in {split}/{cat}")

    def test_f2_total_image_count_minimum_150(self):
        """F2: Verify total dataset images across train and val is at least 150."""
        dataset_dir = PROJECT_ROOT / "ml_pipeline" / "dataset"
        valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
        total_images = 0
        for split in ["train", "val"]:
            split_dir = dataset_dir / split
            if split_dir.is_dir():
                for cat_dir in split_dir.iterdir():
                    if cat_dir.is_dir():
                        images = [f for f in cat_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_exts]
                        total_images += len(images)
        self.assertGreaterEqual(total_images, 150, f"Total dataset images {total_images} < 150 required")

    def test_f2_per_category_minimum_50_images(self):
        """F2: Verify each category (organic, plastic, paper) has at least 50 images total."""
        dataset_dir = PROJECT_ROOT / "ml_pipeline" / "dataset"
        valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
        for cat in ["organic", "plastic", "paper"]:
            cat_total = 0
            for split in ["train", "val"]:
                cat_dir = dataset_dir / split / cat
                if cat_dir.is_dir():
                    images = [f for f in cat_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_exts]
                    cat_total += len(images)
            self.assertGreaterEqual(cat_total, 50, f"Category '{cat}' has only {cat_total} images (< 50 required)")

    # -------------------------------------------------------------------------
    # Feature 3: Dataset Citations & Provenance (ORIGINAL_REQUEST §R2, SPEC.md)
    # -------------------------------------------------------------------------
    def test_f3_citations_file_exists(self):
        """F3: Verify ml_pipeline/dataset/CITATIONS.md exists."""
        citations_file = PROJECT_ROOT / "ml_pipeline" / "dataset" / "CITATIONS.md"
        self.assertTrue(citations_file.is_file(), f"CITATIONS.md missing at {citations_file}")

    def test_f3_citations_non_empty(self):
        """F3: Verify CITATIONS.md has substantive documentation content (> 100 bytes)."""
        citations_file = PROJECT_ROOT / "ml_pipeline" / "dataset" / "CITATIONS.md"
        if not citations_file.is_file():
            self.fail(f"CITATIONS.md missing at {citations_file}")
        self.assertGreater(citations_file.stat().st_size, 100, "CITATIONS.md is trivially small (< 100 bytes)")

    def test_f3_citations_organic_sources(self):
        """F3: Verify CITATIONS.md documents sources for Organic Waste."""
        citations_file = PROJECT_ROOT / "ml_pipeline" / "dataset" / "CITATIONS.md"
        if not citations_file.is_file():
            self.fail("CITATIONS.md missing")
        content = citations_file.read_text(encoding="utf-8").lower()
        self.assertIn("organic", content, "CITATIONS.md does not mention Organic Waste sources")

    def test_f3_citations_plastic_sources(self):
        """F3: Verify CITATIONS.md documents sources for Plastic Waste."""
        citations_file = PROJECT_ROOT / "ml_pipeline" / "dataset" / "CITATIONS.md"
        if not citations_file.is_file():
            self.fail("CITATIONS.md missing")
        content = citations_file.read_text(encoding="utf-8").lower()
        self.assertIn("plastic", content, "CITATIONS.md does not mention Plastic Waste sources")

    def test_f3_citations_paper_sources(self):
        """F3: Verify CITATIONS.md documents sources for Paper Waste."""
        citations_file = PROJECT_ROOT / "ml_pipeline" / "dataset" / "CITATIONS.md"
        if not citations_file.is_file():
            self.fail("CITATIONS.md missing")
        content = citations_file.read_text(encoding="utf-8").lower()
        self.assertIn("paper", content, "CITATIONS.md does not mention Paper Waste sources")

    def test_f3_citations_license_and_terms(self):
        """F3: Verify CITATIONS.md discusses licensing or public domain terms of use."""
        citations_file = PROJECT_ROOT / "ml_pipeline" / "dataset" / "CITATIONS.md"
        if not citations_file.is_file():
            self.fail("CITATIONS.md missing")
        content = citations_file.read_text(encoding="utf-8").lower()
        has_license_info = any(term in content for term in ["license", "public", "creative commons", "kaggle", "attribution", "mit", "cc0", "cc-by"])
        self.assertTrue(has_license_info, "CITATIONS.md does not document dataset licensing / terms")

    # -------------------------------------------------------------------------
    # Feature 4: ML Training Pipeline (ORIGINAL_REQUEST §R3, TASKS.md 1.3)
    # -------------------------------------------------------------------------
    def test_f4_train_script_exists(self):
        """F4: Verify ml_pipeline/train.py exists."""
        train_file = PROJECT_ROOT / "ml_pipeline" / "train.py"
        self.assertTrue(train_file.is_file(), f"ml_pipeline/train.py missing at {train_file}")

    def test_f4_train_script_syntax_valid(self):
        """F4: Verify ml_pipeline/train.py compiles cleanly without SyntaxError."""
        train_file = PROJECT_ROOT / "ml_pipeline" / "train.py"
        if not train_file.is_file():
            self.fail("ml_pipeline/train.py missing")
        source = train_file.read_text(encoding="utf-8")
        try:
            ast.parse(source)
        except SyntaxError as e:
            self.fail(f"Syntax error in train.py: {e}")

    def test_f4_train_script_references_mobilenet_v2(self):
        """F4: Verify ml_pipeline/train.py uses MobileNetV2 architecture."""
        train_file = PROJECT_ROOT / "ml_pipeline" / "train.py"
        if not train_file.is_file():
            self.fail("ml_pipeline/train.py missing")
        content = train_file.read_text(encoding="utf-8").lower()
        self.assertTrue("mobilenet" in content, "train.py does not reference MobileNetV2 architecture")

    def test_f4_train_script_references_data_augmentation(self):
        """F4: Verify ml_pipeline/train.py references image data augmentation."""
        train_file = PROJECT_ROOT / "ml_pipeline" / "train.py"
        if not train_file.is_file():
            self.fail("ml_pipeline/train.py missing")
        content = train_file.read_text(encoding="utf-8")
        has_aug = any(aug in content for aug in ["RandomHorizontalFlip", "RandomRotation", "ColorJitter", "RandomResizedCrop", "RandomAffine", "transforms"])
        self.assertTrue(has_aug, "train.py does not reference data augmentation transforms")

    def test_f4_requirements_file_exists(self):
        """F4: Verify ml_pipeline/requirements.txt lists required ML libraries."""
        req_file = PROJECT_ROOT / "ml_pipeline" / "requirements.txt"
        self.assertTrue(req_file.is_file(), f"ml_pipeline/requirements.txt missing at {req_file}")
        content = req_file.read_text(encoding="utf-8").lower()
        for pkg in ["torch", "torchvision"]:
            self.assertIn(pkg, content, f"ml_pipeline/requirements.txt does not mention {pkg}")

    # -------------------------------------------------------------------------
    # Feature 5: Model Export (`waste_model.pth`) (ORIGINAL_REQUEST §R4, TASKS.md 1.5)
    # -------------------------------------------------------------------------
    def test_f5_model_file_exists_in_saved_models(self):
        """F5: Verify ml_pipeline/saved_models/waste_model.pth exists."""
        model_file = PROJECT_ROOT / "ml_pipeline" / "saved_models" / "waste_model.pth"
        self.assertTrue(model_file.is_file(), f"Saved model weights missing at {model_file}")

    def test_f5_model_file_exists_at_root(self):
        """F5: Verify convenience export waste_model.pth exists at project root."""
        root_model = PROJECT_ROOT / "waste_model.pth"
        self.assertTrue(root_model.is_file(), f"Root model export missing at {root_model}")

    def test_f5_model_file_non_empty(self):
        """F5: Verify model weights file is non-empty (> 1 MB for MobileNetV2)."""
        model_file = PROJECT_ROOT / "ml_pipeline" / "saved_models" / "waste_model.pth"
        if not model_file.is_file():
            self.fail(f"Model file missing at {model_file}")
        size_bytes = model_file.stat().st_size
        self.assertGreater(size_bytes, 1024 * 1024, f"Model file size {size_bytes} is under 1MB; invalid weights")

    def test_f5_model_is_valid_file_format(self):
        """F5: Verify waste_model.pth starts with PyTorch / Zip / Pickle magic bytes."""
        model_file = PROJECT_ROOT / "ml_pipeline" / "saved_models" / "waste_model.pth"
        if not model_file.is_file():
            self.fail(f"Model file missing at {model_file}")
        with open(model_file, "rb") as f:
            header = f.read(4)
        # PyTorch checkpoints are either Zip archives (PK\x03\x04) or Python Pickle (\x80\x02, \x80\x03, \x80\x04)
        is_zip = header.startswith(b"PK\x03\x04")
        is_pickle = header[0] == 0x80
        self.assertTrue(is_zip or is_pickle, f"waste_model.pth header {header!r} is not a valid PyTorch/Zip/Pickle format")

    def test_f5_class_to_idx_json_exists(self):
        """F5: Verify ml_pipeline/saved_models/class_to_idx.json exists."""
        idx_file = PROJECT_ROOT / "ml_pipeline" / "saved_models" / "class_to_idx.json"
        self.assertTrue(idx_file.is_file(), f"class_to_idx.json missing at {idx_file}")

    # -------------------------------------------------------------------------
    # Feature 6: Evaluation Visualizations & Metrics (ORIGINAL_REQUEST §R4, TASKS.md 1.4)
    # -------------------------------------------------------------------------
    def test_f6_confusion_matrix_artifact_exists(self):
        """F6: Verify confusion_matrix.png exists in ml_pipeline/artifacts/."""
        cm_file = PROJECT_ROOT / "ml_pipeline" / "artifacts" / "confusion_matrix.png"
        self.assertTrue(cm_file.is_file(), f"Confusion matrix missing at {cm_file}")

    def test_f6_accuracy_curve_artifact_exists(self):
        """F6: Verify accuracy_curve.png exists in ml_pipeline/artifacts/."""
        curve_file = PROJECT_ROOT / "ml_pipeline" / "artifacts" / "accuracy_curve.png"
        self.assertTrue(curve_file.is_file(), f"Accuracy curve missing at {curve_file}")

    def test_f6_classification_report_artifact_exists(self):
        """F6: Verify classification_report.txt exists in ml_pipeline/artifacts/."""
        report_file = PROJECT_ROOT / "ml_pipeline" / "artifacts" / "classification_report.txt"
        self.assertTrue(report_file.is_file(), f"Classification report missing at {report_file}")

    def test_f6_evaluate_script_exists(self):
        """F6: Verify ml_pipeline/evaluate.py exists and compiles cleanly."""
        eval_file = PROJECT_ROOT / "ml_pipeline" / "evaluate.py"
        self.assertTrue(eval_file.is_file(), f"ml_pipeline/evaluate.py missing at {eval_file}")
        source = eval_file.read_text(encoding="utf-8")
        try:
            ast.parse(source)
        except SyntaxError as e:
            self.fail(f"Syntax error in evaluate.py: {e}")

    def test_f6_artifacts_exist_at_workspace_root(self):
        """F6: Verify convenience copies of evaluation artifacts exist at workspace root."""
        self.assertTrue((PROJECT_ROOT / "confusion_matrix.png").is_file(), "Root confusion_matrix.png missing")
        self.assertTrue((PROJECT_ROOT / "accuracy_curve.png").is_file(), "Root accuracy_curve.png missing")
        self.assertTrue((PROJECT_ROOT / "classification_report.txt").is_file(), "Root classification_report.txt missing")

    # -------------------------------------------------------------------------
    # Feature 7: Model Inference & Contract (ADR.md, API_SPECS.md)
    # -------------------------------------------------------------------------
    def test_f7_predict_script_exists(self):
        """F7: Verify ml_pipeline/predict.py exists and compiles cleanly."""
        predict_file = PROJECT_ROOT / "ml_pipeline" / "predict.py"
        self.assertTrue(predict_file.is_file(), f"ml_pipeline/predict.py missing at {predict_file}")
        source = predict_file.read_text(encoding="utf-8")
        try:
            ast.parse(source)
        except SyntaxError as e:
            self.fail(f"Syntax error in predict.py: {e}")

    def test_f7_class_to_idx_contains_all_three_classes(self):
        """F7: Verify class_to_idx.json defines mappings for all 3 waste categories."""
        idx_file = PROJECT_ROOT / "ml_pipeline" / "saved_models" / "class_to_idx.json"
        if not idx_file.is_file():
            self.fail(f"class_to_idx.json missing at {idx_file}")
        with open(idx_file, "r", encoding="utf-8") as f:
            mapping = json.load(f)
        # Check either mapped keys or values cover organic, plastic, paper
        keys_lower = [str(k).lower() for k in mapping.keys()]
        values_lower = [str(v).lower() for v in mapping.values()]
        all_terms = keys_lower + values_lower
        for cat in ["organic", "plastic", "paper"]:
            found = any(cat in term for term in all_terms)
            self.assertTrue(found, f"class_to_idx.json does not define mapping for '{cat}'")

    def test_f7_predict_script_defines_inference_class_or_function(self):
        """F7: Verify predict.py defines a predictor class or predict function."""
        predict_file = PROJECT_ROOT / "ml_pipeline" / "predict.py"
        if not predict_file.is_file():
            self.fail("ml_pipeline/predict.py missing")
        source = predict_file.read_text(encoding="utf-8")
        has_predictor = any(term in source for term in ["WastePredictor", "predict", "predict_image", "Predictor"])
        self.assertTrue(has_predictor, "predict.py does not define an inference class or function")

    def test_f7_predict_script_implements_preprocessing(self):
        """F7: Verify predict.py defines ImageNet standard normalization / resize transforms."""
        predict_file = PROJECT_ROOT / "ml_pipeline" / "predict.py"
        if not predict_file.is_file():
            self.fail("ml_pipeline/predict.py missing")
        source = predict_file.read_text(encoding="utf-8")
        has_norm = "Normalize" in source or "0.485" in source
        self.assertTrue(has_norm, "predict.py does not define standard MobileNetV2 normalization")

    def test_f7_predict_script_specifies_output_contract(self):
        """F7: Verify predict.py references required API keys (category, confidence, probabilities)."""
        predict_file = PROJECT_ROOT / "ml_pipeline" / "predict.py"
        if not predict_file.is_file():
            self.fail("ml_pipeline/predict.py missing")
        source = predict_file.read_text(encoding="utf-8")
        self.assertIn("category", source, "predict.py does not reference 'category' in output")
        self.assertIn("confidence", source, "predict.py does not reference 'confidence' in output")
        self.assertIn("probabilities", source, "predict.py does not reference 'probabilities' in output")


if __name__ == "__main__":
    unittest.main()
