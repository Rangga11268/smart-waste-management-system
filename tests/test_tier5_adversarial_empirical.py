"""
Tier 5: Adversarial & Empirical Validation Test Suite for Smart Waste Management System (SWMS).
Challenger 2 Empirical Verification:
1. Model Weight Integrity & Checkpoint Inspection (non-zero, non-NaN, non-Inf, layer dimensions, hash parity)
2. Determinism and Repeatability across 10 consecutive inference runs
3. Probability Distribution Axioms (sum=1.0000, bounds [0,1], argmax alignment, confidence calibration)
4. Batch Latency & CPU Memory Profile (50 runs, mean/p95 latency, RSS memory, leak check)
5. Independent 42-Image Validation Accuracy & Confusion Matrix Audit (verifying reported 92.86%)
6. Adversarial Input Robustness (black/white/noise, extreme aspect ratios, RGBA/CMYK/grayscale, corrupt files)
"""

import hashlib
import io
import json
import os
from pathlib import Path
import time
import tracemalloc
import unittest

import numpy as np
from PIL import Image
import psutil
from sklearn.metrics import classification_report, confusion_matrix
import torch
import torch.nn as nn

PROJECT_ROOT = Path(__file__).resolve().parent.parent

from ml_pipeline.predict import WastePredictor, CATEGORY_SPECS


class TestTier5EmpiricalChallenger(unittest.TestCase):
    """Empirical verification and adversarial stress-testing harness."""

    @classmethod
    def setUpClass(cls):
        cls.root_model_path = PROJECT_ROOT / "waste_model.pth"
        cls.saved_model_path = PROJECT_ROOT / "ml_pipeline" / "saved_models" / "waste_model.pth"
        cls.val_dir = PROJECT_ROOT / "ml_pipeline" / "dataset" / "val"
        cls.predictor = WastePredictor(model_path=cls.root_model_path, device="cpu")

    # =========================================================================
    # Test 1: Model Weights Integrity & Checkpoint Inspection
    # =========================================================================
    def test_01_checkpoint_files_exist_and_hash_parity(self):
        """Verify both root and saved_models checkpoints exist, are > 1MB, and match SHA256."""
        self.assertTrue(self.root_model_path.is_file(), f"Missing {self.root_model_path}")
        self.assertTrue(self.saved_model_path.is_file(), f"Missing {self.saved_model_path}")

        root_size = self.root_model_path.stat().st_size
        saved_size = self.saved_model_path.stat().st_size
        self.assertGreater(root_size, 1_000_000, f"Root model suspicious size: {root_size} bytes")
        self.assertEqual(root_size, saved_size, "Model file sizes do not match between root and saved_models")

        h1 = hashlib.sha256(self.root_model_path.read_bytes()).hexdigest()
        h2 = hashlib.sha256(self.saved_model_path.read_bytes()).hexdigest()
        self.assertEqual(h1, h2, f"SHA256 mismatch between root ({h1}) and saved_models ({h2})")

    def test_02_model_weights_numerical_integrity(self):
        """Verify all model weights are non-zero, non-NaN, non-Inf, and have correct dimensions."""
        checkpoint = torch.load(self.root_model_path, map_location="cpu")
        state_dict = checkpoint.get("state_dict", checkpoint) if isinstance(checkpoint, dict) else checkpoint

        self.assertGreater(len(state_dict), 20, "Suspiciously few state_dict parameters for MobileNetV2")

        total_params = 0
        zero_tensors = 0
        for name, tensor in state_dict.items():
            if not isinstance(tensor, torch.Tensor):
                continue
            total_params += tensor.numel()
            # Non-NaN assertion
            self.assertFalse(torch.isnan(tensor).any().item(), f"Tensor '{name}' contains NaN values!")
            # Non-Inf assertion
            self.assertFalse(torch.isinf(tensor).any().item(), f"Tensor '{name}' contains Inf values!")
            # Non-zero assertion (tensor is not completely zero)
            is_all_zero = (tensor == 0).all().item()
            if is_all_zero:
                zero_tensors += 1
            self.assertFalse(is_all_zero, f"Tensor '{name}' is completely zero!")

        self.assertEqual(zero_tensors, 0, "Found all-zero parameter tensors")
        self.assertGreater(total_params, 2_000_000, f"Total parameter count {total_params} too low for MobileNetV2")

        # Verify classifier head dimensions: (3, 1280) and bias (3,)
        classifier_weight_key = "classifier.1.weight"
        classifier_bias_key = "classifier.1.bias"
        # Handle prefix if present
        if classifier_weight_key not in state_dict:
            matches = [k for k in state_dict.keys() if "classifier.1.weight" in k]
            self.assertTrue(len(matches) > 0, "Cannot find classifier.1.weight in state_dict")
            classifier_weight_key = matches[0]
            classifier_bias_key = [k for k in state_dict.keys() if "classifier.1.bias" in k][0]

        clf_weight = state_dict[classifier_weight_key]
        clf_bias = state_dict[classifier_bias_key]

        self.assertEqual(clf_weight.shape, torch.Size([3, 1280]), f"Unexpected classifier weight shape: {clf_weight.shape}")
        self.assertEqual(clf_bias.shape, torch.Size([3]), f"Unexpected classifier bias shape: {clf_bias.shape}")

        # Statistical sanity checks for classifier weights
        w_min = clf_weight.min().item()
        w_max = clf_weight.max().item()
        w_mean = clf_weight.mean().item()
        w_std = clf_weight.std().item()

        self.assertTrue(-2.0 < w_min < 0.0, f"Classifier weight min ({w_min}) out of expected range")
        self.assertTrue(0.0 < w_max < 2.0, f"Classifier weight max ({w_max}) out of expected range")
        self.assertTrue(abs(w_mean) < 0.1, f"Classifier weight mean ({w_mean}) drifted far from 0")
        self.assertTrue(0.01 < w_std < 0.5, f"Classifier weight std ({w_std}) outside expected distribution")

    # =========================================================================
    # Test 2: Inference Repeatability & Determinism
    # =========================================================================
    def test_03_inference_repeatability_10_runs(self):
        """Run 10 consecutive inferences on the exact same image and verify deterministic outputs."""
        sample_img = self.val_dir / "organic" / "organic_001.jpg"
        self.assertTrue(sample_img.is_file(), f"Sample image {sample_img} not found")

        runs = []
        for i in range(10):
            res = self.predictor.predict(sample_img)
            runs.append(res)

        first_res = runs[0]
        for idx, run_res in enumerate(runs[1:], start=2):
            self.assertEqual(run_res["category"], first_res["category"], f"Run {idx} category diverged")
            self.assertEqual(run_res["category_id"], first_res["category_id"], f"Run {idx} category_id diverged")
            self.assertAlmostEqual(run_res["confidence"], first_res["confidence"], places=6,
                                   msg=f"Run {idx} confidence diverged")
            self.assertEqual(run_res["confidence_percentage"], first_res["confidence_percentage"],
                             f"Run {idx} confidence percentage diverged")
            for k in first_res["probabilities"]:
                self.assertAlmostEqual(run_res["probabilities"][k], first_res["probabilities"][k], places=6,
                                       msg=f"Run {idx} probability for {k} diverged")

    # =========================================================================
    # Test 3: Probability Distribution Axioms & Calibration
    # =========================================================================
    def test_04_probability_distribution_axioms(self):
        """Verify mathematical axioms on all 42 validation images: sum=1.0, bounds [0,1], argmax alignment."""
        val_images = list(self.val_dir.glob("*/*.jpg"))
        self.assertEqual(len(val_images), 42, f"Expected 42 validation images, found {len(val_images)}")

        for img_path in val_images:
            res = self.predictor.predict(img_path)

            # Contract schema check
            self.assertIn("category", res)
            self.assertIn("confidence", res)
            self.assertIn("confidence_percentage", res)
            self.assertIn("category_id", res)
            self.assertIn("probabilities", res)

            probs = res["probabilities"]
            self.assertEqual(len(probs), 3, "Expected 3 category probabilities")

            # Probability sum axiom
            prob_sum = sum(probs.values())
            self.assertAlmostEqual(prob_sum, 1.0, delta=0.0005,
                                   msg=f"Probability sum {prob_sum} deviates from 1.0 on {img_path.name}")

            # Probability range axiom
            for cname, pval in probs.items():
                self.assertGreaterEqual(pval, 0.0, f"Probability for {cname} < 0.0 ({pval}) on {img_path.name}")
                self.assertLessEqual(pval, 1.0, f"Probability for {cname} > 1.0 ({pval}) on {img_path.name}")

            # Confidence equals max probability
            max_prob_key = max(probs, key=probs.get)
            max_prob_val = probs[max_prob_key]
            self.assertEqual(res["category"], max_prob_key,
                             f"Category '{res['category']}' does not match argmax '{max_prob_key}'")
            self.assertAlmostEqual(res["confidence"], max_prob_val, delta=0.0002,
                                   msg=f"Confidence {res['confidence']} != max prob {max_prob_val}")

            # Category ID mapping alignment
            if res["category"] == "Organic Waste":
                self.assertEqual(res["category_id"], 1)
            elif res["category"] == "Plastic Waste":
                self.assertEqual(res["category_id"], 2)
            elif res["category"] == "Paper Waste":
                self.assertEqual(res["category_id"], 3)
            else:
                self.fail(f"Unrecognized category name: {res['category']}")

            # Confidence percentage formatting
            expected_pct = f"{res['confidence'] * 100:.2f}%"
            self.assertEqual(res["confidence_percentage"], expected_pct,
                             f"Confidence percentage format mismatch: {res['confidence_percentage']} vs {expected_pct}")

    # =========================================================================
    # Test 4: Batch Latency and CPU Memory Consumption
    # =========================================================================
    def test_05_batch_latency_and_cpu_memory_benchmark(self):
        """Measure 50 consecutive CPU predictions: latency (mean, median, p95) and RAM usage."""
        val_images = list(self.val_dir.glob("*/*.jpg"))
        # Sample 50 images with wrap-around
        test_inputs = [val_images[i % len(val_images)] for i in range(50)]

        # Warm-up (5 runs)
        for i in range(5):
            self.predictor.predict(test_inputs[i])

        process = psutil.Process(os.getpid())
        ram_before_mb = process.memory_info().rss / (1024 * 1024)
        tracemalloc.start()

        latencies = []
        for img_path in test_inputs:
            t0 = time.perf_counter()
            self.predictor.predict(img_path)
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0)  # ms

        current_trace, peak_trace = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        ram_after_mb = process.memory_info().rss / (1024 * 1024)

        lat_arr = np.array(latencies)
        mean_lat = float(np.mean(lat_arr))
        median_lat = float(np.median(lat_arr))
        p95_lat = float(np.percentile(lat_arr, 95))
        min_lat = float(np.min(lat_arr))
        max_lat = float(np.max(lat_arr))
        throughput = 1000.0 / mean_lat
        peak_trace_mb = peak_trace / (1024 * 1024)
        rss_delta_mb = ram_after_mb - ram_before_mb

        print(f"\n[BENCHMARK] 50 CPU Predictions Summary:")
        print(f"  Mean Latency:    {mean_lat:.2f} ms")
        print(f"  Median Latency:  {median_lat:.2f} ms")
        print(f"  P95 Latency:     {p95_lat:.2f} ms")
        print(f"  Min / Max:       {min_lat:.2f} ms / {max_lat:.2f} ms")
        print(f"  Throughput:      {throughput:.1f} images/sec")
        print(f"  RAM Before/After:{ram_before_mb:.1f} MB -> {ram_after_mb:.1f} MB (Delta: {rss_delta_mb:+.2f} MB)")
        print(f"  Peak Traced RAM: {peak_trace_mb:.2f} MB")

        # SLAs: CPU inference mean latency < 350 ms, no runaway memory leak (< 100 MB delta)
        self.assertLess(mean_lat, 350.0, f"Mean latency {mean_lat:.2f}ms exceeds 350ms SLA")
        self.assertLess(rss_delta_mb, 100.0, f"Excessive memory growth: {rss_delta_mb:.2f} MB")

    # =========================================================================
    # Test 5: Independent 42-Image Validation Accuracy Audit
    # =========================================================================
    def test_06_independent_validation_accuracy_audit(self):
        """Independently evaluate all 42 images and verify exact match with reported 92.86%."""
        class_dirs = {
            "organic": "Organic Waste",
            "paper": "Paper Waste",
            "plastic": "Plastic Waste"
        }

        y_true = []
        y_pred = []
        results_log = []

        for folder_name, true_class in class_dirs.items():
            folder_path = self.val_dir / folder_name
            images = sorted(list(folder_path.glob("*.jpg")))
            self.assertEqual(len(images), 14, f"Expected 14 images in {folder_name}, found {len(images)}")

            for img in images:
                res = self.predictor.predict(img)
                y_true.append(true_class)
                y_pred.append(res["category"])
                results_log.append({
                    "file": img.name,
                    "true_class": true_class,
                    "predicted_class": res["category"],
                    "confidence": res["confidence"],
                    "probabilities": res["probabilities"],
                    "is_correct": (true_class == res["category"])
                })

        # Calculate metrics
        correct_count = sum(1 for r in results_log if r["is_correct"])
        total_count = len(results_log)
        accuracy = correct_count / total_count

        cm = confusion_matrix(y_true, y_pred, labels=["Organic Waste", "Paper Waste", "Plastic Waste"])
        report = classification_report(y_true, y_pred, labels=["Organic Waste", "Paper Waste", "Plastic Waste"], output_dict=True)

        print(f"\n[AUDIT] Independent Validation Results (42 images):")
        print(f"  Correct: {correct_count} / {total_count}")
        print(f"  Accuracy: {accuracy * 100:.2f}% ({accuracy:.4f})")
        print(f"  Confusion Matrix (Organic, Paper, Plastic):\n{cm}")

        misclassified = [r for r in results_log if not r["is_correct"]]
        print(f"\n  Misclassified images ({len(misclassified)}):")
        for m in misclassified:
            print(f"    - {m['file']} (True: {m['true_class']}) -> Predicted: {m['predicted_class']} (Confidence: {m['confidence']})")

        # Assertions
        self.assertEqual(total_count, 42, "Total validation count is not 42")
        self.assertEqual(correct_count, 39, f"Expected 39 correct classifications, got {correct_count}")
        self.assertAlmostEqual(accuracy, 39 / 42, places=4, msg=f"Accuracy {accuracy} != 39/42 (0.9286)")

        # Verify exact reported confusion matrix:
        # Organic: 14 TP, 0 FP, 0 FN (14/14 correct)
        self.assertEqual(cm[0, 0], 14, "Organic Waste should have 14 correct")
        self.assertEqual(cm[0, 1], 0)
        self.assertEqual(cm[0, 2], 0)

        # Paper: 14 TP, 3 FP (from plastic), 0 FN (14/14 correct recall)
        self.assertEqual(cm[1, 0], 0)
        self.assertEqual(cm[1, 1], 14, "Paper Waste should have 14 correct")
        self.assertEqual(cm[1, 2], 0)

        # Plastic: 11 TP, 3 FN (misclassified as Paper), 0 FP
        self.assertEqual(cm[2, 0], 0)
        self.assertEqual(cm[2, 1], 3, "Plastic Waste misclassifications into Paper should be 3")
        self.assertEqual(cm[2, 2], 11, "Plastic Waste correct should be 11")

        # Verify precision, recall, f1 match classification_report.txt
        self.assertAlmostEqual(report["Organic Waste"]["precision"], 1.0000, places=3)
        self.assertAlmostEqual(report["Organic Waste"]["recall"], 1.0000, places=3)
        self.assertAlmostEqual(report["Organic Waste"]["f1-score"], 1.0000, places=3)

        self.assertAlmostEqual(report["Paper Waste"]["recall"], 1.0000, places=3)
        self.assertAlmostEqual(report["Paper Waste"]["precision"], 14 / 17, places=3)  # ~0.8235

        self.assertAlmostEqual(report["Plastic Waste"]["precision"], 1.0000, places=3)
        self.assertAlmostEqual(report["Plastic Waste"]["recall"], 11 / 14, places=3)  # ~0.7857

    # =========================================================================
    # Test 6: Adversarial & Edge Case Robustness
    # =========================================================================
    def test_07_extreme_aspect_ratios_and_resolutions(self):
        """Stress-test predictor with extreme aspect ratios, high resolution, and tiny images."""
        test_cases = [
            ("panoramic", (1200, 60)),
            ("tall_vertical", (60, 1200)),
            ("high_res", (3000, 3000)),
            ("tiny", (16, 16)),
            ("standard_rect", (640, 480)),
        ]

        for name, size in test_cases:
            img = Image.new("RGB", size, color=(128, 128, 128))
            res = self.predictor.predict(img)
            self.assertIn("category", res)
            self.assertAlmostEqual(sum(res["probabilities"].values()), 1.0, delta=0.0005,
                                   msg=f"Axiom broken on aspect ratio {name} {size}")

    def test_08_synthetic_degenerate_images(self):
        """Stress-test predictor with all-black, all-white, and random noise images."""
        # 1. All black
        black_img = Image.new("RGB", (224, 224), color=(0, 0, 0))
        res_black = self.predictor.predict(black_img)
        self.assertAlmostEqual(sum(res_black["probabilities"].values()), 1.0, delta=0.0005)

        # 2. All white
        white_img = Image.new("RGB", (224, 224), color=(255, 255, 255))
        res_white = self.predictor.predict(white_img)
        self.assertAlmostEqual(sum(res_white["probabilities"].values()), 1.0, delta=0.0005)

        # 3. Random noise
        noise_arr = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
        noise_img = Image.fromarray(noise_arr)
        res_noise = self.predictor.predict(noise_img)
        self.assertAlmostEqual(sum(res_noise["probabilities"].values()), 1.0, delta=0.0005)

    def test_09_color_space_handling(self):
        """Verify proper conversion for RGBA, Grayscale (L), and CMYK images."""
        # RGBA
        rgba_img = Image.new("RGBA", (224, 224), color=(200, 100, 50, 128))
        res_rgba = self.predictor.predict(rgba_img)
        self.assertIn("category", res_rgba)

        # Grayscale
        gray_img = Image.new("L", (224, 224), color=128)
        res_gray = self.predictor.predict(gray_img)
        self.assertIn("category", res_gray)

        # CMYK
        cmyk_img = Image.new("CMYK", (224, 224), color=(0, 100, 100, 0))
        res_cmyk = self.predictor.predict(cmyk_img)
        self.assertIn("category", res_cmyk)

    def test_10_error_handling_invalid_and_corrupt_inputs(self):
        """Verify strict error raising on missing files, unsupported formats, and corrupt bytes."""
        # 1. Non-existent file
        with self.assertRaises(FileNotFoundError):
            self.predictor.predict("non_existent_file_xyz_12345.jpg")

        # 2. Unsupported extension
        dummy_txt = PROJECT_ROOT / "temp_dummy_test_unsupported.txt"
        dummy_txt.write_text("not an image", encoding="utf-8")
        try:
            with self.assertRaises(ValueError) as ctx:
                self.predictor.predict(dummy_txt)
            self.assertIn("Unsupported image extension", str(ctx.exception))
        finally:
            if dummy_txt.is_file():
                dummy_txt.unlink()

        # 3. Corrupt image file
        corrupt_jpg = PROJECT_ROOT / "temp_corrupt_test.jpg"
        corrupt_jpg.write_bytes(b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00garbage_data_not_valid_jpeg")
        try:
            with self.assertRaises(ValueError) as ctx:
                self.predictor.predict(corrupt_jpg)
            self.assertIn("Corrupted or invalid", str(ctx.exception))
        finally:
            if corrupt_jpg.is_file():
                corrupt_jpg.unlink()

        # 4. Corrupt bytes
        with self.assertRaises(ValueError):
            self.predictor.predict(b"completely invalid byte sequence")

        # 5. Invalid type
        with self.assertRaises(TypeError):
            self.predictor.predict(12345)


if __name__ == "__main__":
    unittest.main(verbosity=2)
