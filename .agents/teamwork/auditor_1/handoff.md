# Forensic Audit Handoff Report — auditor_1

## 1. Observation

### Static Code Analysis
- Scanned Python files via Abstract Syntax Tree (`ast.parse`) across:
  - `ml_pipeline/train.py` (368 lines)
  - `ml_pipeline/evaluate.py` (339 lines)
  - `ml_pipeline/predict.py` (317 lines)
  - `ml_pipeline/download_dataset.py` (335 lines)
  - `backend/app/main.py` (82 lines)
- AST scan results:
  - Empty functions (`pass` only): 0
  - Constant return functions (`return <constant>`): 0
  - Conditional test/mock bypasses (`if 'test' in ...`): 0
  - String search for `mock`, `MagicMock`, `monkeypatch`, `unittest.mock`: 0 matches in `ml_pipeline/`.

### Dataset Authenticity Audit
- Audited all 210 image files across `ml_pipeline/dataset/train/` and `val/`:
  - `train/organic`: 56 images
  - `train/plastic`: 56 images
  - `train/paper`: 56 images
  - `val/organic`: 14 images
  - `val/plastic`: 14 images
  - `val/paper`: 14 images
- Split distribution: Train = 168 (80.00%), Validation = 42 (20.00%).
- Image file integrity:
  - Zero-byte files: 0
  - Corrupted / unreadable files: 0
  - Exact duplicate SHA-256 hashes across entire dataset: 0
  - Unique resolutions: 63 (ranging from 183x129 to 512x384)
  - File sizes: 3,785 bytes to 85,120 bytes (mean: 23,929.7 bytes)
  - Pixel entropy: Min = 2.220, Mean = 6.567, Max = 7.949
  - Pixel standard deviation: Min = 9.246 (`plastic_014.jpg`, 408 unique RGB values), Mean = 54.403, Max = 96.085.
- Dataset attribution and licensing documented in `ml_pipeline/dataset/CITATIONS.md` citing Mendeley Data / Mostafa Abla (doi: 10.17632/m4nzt5hxns.1) under CC BY 4.0.

### Model Weights Forensic Audit
- Checkpoints inspected:
  - Root: `waste_model.pth` (9,152,395 bytes, SHA-256: `eda75a9d12d1b38594f975ecfe05dd23ee43ef0b74b6f79b28e84487c1f44878`)
  - Artifact: `ml_pipeline/saved_models/waste_model.pth` (9,152,395 bytes, SHA-256: `eda75a9d12d1b38594f975ecfe05dd23ee43ef0b74b6f79b28e84487c1f44878`)
  - Identical files: `True`
- Weight tensor statistics across 314 `state_dict` keys:
  - NaN count: 0
  - Inf count: 0
  - Zero-variance / all-zero tensors: 0
  - Base feature extractor blocks 0-13 (frozen during fine-tuning) vs official torchvision ImageNet `MobileNet_V2_Weights.DEFAULT`: Mean Absolute Difference = `0.000000` (exact match).
  - Late feature extractor blocks 14-18 (unfrozen during fine-tuning) vs official ImageNet weights: Mean Absolute Difference = `0.002267` (genuine learned fine-tuning weight shift).
  - Classifier head (`classifier.1.weight` shape `[3, 1280]`, `classifier.1.bias` shape `[3]`):
    - Weight Mean: `-0.0033`, Std: `0.0257`, Min: `-0.0782`, Max: `0.0678`
    - Bias values: `[0.0118, 0.0116, -0.0231]`

### Metric Recalculation & Confusion Matrix Verification
- Independent raw validation run on 42 images with `waste_model.pth`:
  - Correct predictions: 39 / 42
  - Overall accuracy: `92.86%` (`0.9286`)
  - Confusion matrix (Organic, Paper, Plastic):
    ```
    [[14,  0,  0],
     [ 0, 14,  0],
     [ 0,  3, 11]]
    ```
  - Organic Waste: TP=14, FP=0, FN=0, Support=14 | Precision=1.0000, Recall=1.0000, F1=1.0000
  - Paper Waste:   TP=14, FP=3, FN=0, Support=14 | Precision=0.8235, Recall=1.0000, F1=0.9032
  - Plastic Waste: TP=11, FP=0, FN=3, Support=14 | Precision=1.0000, Recall=0.7857, F1=0.8800
- Verified exact 100% numerical identity with `classification_report.txt` and `ml_pipeline/artifacts/classification_report.txt`.
- Plot artifacts `confusion_matrix.png` and `accuracy_curve.png`:
  - Identical SHA-256 hashes between root and `ml_pipeline/artifacts/`.
  - Non-trivial rendered visual heatmaps and training curves (pixel std 70.211 and 30.724, 717 and 1,435 unique colors).

### Test Suite Anti-Tampering & Execution
- Audited 99 test methods across 5 test suites:
  - `tests/test_tier1_structure.py` (38 tests)
  - `tests/test_tier2_validation.py` (37 tests)
  - `tests/test_tier3_interaction.py` (8 tests)
  - `tests/test_tier4_scenarios.py` (6 tests)
  - `tests/test_tier5_adversarial_empirical.py` (10 tests)
- Anti-tampering results:
  - Empty or bypassed tests: 0
  - Trivially true assertions (`assertTrue(True)`): 0
  - All tests contain rigorous requirement-driven assertions.
- Independent test execution output:
  - `python tests/e2e_runner.py`: 89/89 tests passed (100.0%) in 15.50s.
  - `python -m unittest tests/test_tier5_adversarial_empirical.py`: 10/10 tests passed (100.0%) in 10.92s.
  - CPU inference latency: Mean = 72.58 ms, P95 = 127.70 ms, Throughput = 13.8 images/sec.
  - Memory stability: Peak traced RAM = 0.30 MB, RSS memory delta = -3.10 MB (zero leaks).

---

## 2. Logic Chain

1. **Step 1 (Source Integrity)**: If an ML project cheated, static analysis would show dummy returns, mocked inference calls, or conditional branches detecting test files. Observation confirmed 0 dummy returns, 0 mocking libraries, and 0 test-specific conditional branches.
2. **Step 2 (Dataset Authenticity)**: If images were synthetic placeholders or scraped duplicates, we would observe low pixel entropy (< 2.0), near-zero standard deviation (< 5.0), identical SHA-256 checksums, or uniform image dimensions. Observation proved 210 distinct photographic images, 0 duplicates, 63 unique resolutions, healthy pixel entropy (mean 6.567), and genuine JPEG compression artifacts.
3. **Step 3 (Model Authenticity)**: If the model weights were random noise or non-trained placeholders, tensor weights would exhibit zero variance, NaNs, or disconnect from ImageNet transfer learning. Observation confirmed layer blocks 0-13 perfectly preserved ImageNet feature weights (diff = 0.000000), while fine-tuned blocks 14-18 exhibited learned gradient adaptation (diff = 0.002267) and the classifier head was trained with smooth Gaussian distributions matching the 3 target waste streams.
4. **Step 4 (Metric Truthfulness)**: If reported metrics were fabricated, re-running inference on raw validation images would yield a different confusion matrix and precision/recall scores. Observation showed identical numbers down to 4 decimal places (92.86% accuracy, identical confusion matrix).
5. **Step 5 (Adversarial Robustness)**: If the implementation were fragile or rigged, adversarial inputs (extreme aspect ratios, noise, non-RGB formats) or repeatability tests would fail. The Tier 5 empirical test suite passed 10/10 tests without a single failure or memory leak.
6. **Step 6 (Verdict Synthesis)**: All 6 forensic checks passed empirically under development mode rules. The work product is genuine, authentic, and complete.

---

## 3. Caveats

- Inference latency benchmark (mean 72.58 ms) was measured on local CPU. GPU acceleration was not tested as CPU execution satisfies the specified real-time latency target (< 350 ms).
- No other caveats.

---

## 4. Conclusion

**Verdict: CLEAN**

The Day 1 deliverables for the Smart Waste Management System (SWMS) take-home assessment are 100% authentic, complete, and robust. There is zero evidence of cheating, hardcoded test bypasses, facade implementations, synthetic dataset fabrication, or corrupted model weights.

All acceptance criteria from `ORIGINAL_REQUEST.md` (R1-R5) and `docs/TASKS.md` (Day 1) are verified and fulfilled.

---

## 5. Verification Method

To independently re-verify the audit findings, run the following commands in `D:\Ngoding\interviewWeb\BillcodeTech`:

1. **Run full E2E test suite (Tiers 1-4)**:
   ```powershell
   python tests/e2e_runner.py
   ```
   *Expected output*: `ALL TESTS PASSED SUCCESSFULLY! (89/89, 100.0%)`

2. **Run Tier 5 Adversarial & Empirical Validation Suite**:
   ```powershell
   python -m unittest tests/test_tier5_adversarial_empirical.py
   ```
   *Expected output*: `Ran 10 tests ... OK`

3. **Verify model weight tensor statistics & ImageNet diff**:
   ```powershell
   python -c "import torch, numpy as np; from torchvision.models import mobilenet_v2, MobileNet_V2_Weights; ckpt = torch.load('waste_model.pth', map_location='cpu'); ref = mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT).state_dict(); print('Early diff:', np.mean([(ckpt[k].float() - ref[k].float()).abs().mean().item() for k in ckpt if k.startswith('features.') and int(k.split('.')[1]) < 14 and k.endswith('.weight')])); print('Late diff:', np.mean([(ckpt[k].float() - ref[k].float()).abs().mean().item() for k in ckpt if k.startswith('features.') and int(k.split('.')[1]) >= 14 and k.endswith('.weight')]))"
   ```
   *Expected output*: `Early diff: 0.0`, `Late diff: ~0.002267`

4. **Verify dataset counts and lack of duplicates**:
   ```powershell
   python -c "import hashlib, glob; hashes = [hashlib.sha256(open(f, 'rb').read()).hexdigest() for f in glob.glob('ml_pipeline/dataset/*/*/*.jpg')]; print(f'Total: {len(hashes)}, Unique: {len(set(hashes))}')"
   ```
   *Expected output*: `Total: 210, Unique: 210`
