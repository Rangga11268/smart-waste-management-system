# Handoff Report: Milestone M2 (Dataset Collection & Curation)

**Agent**: `teamwork_worker_m2_dataset_1`  
**Milestone**: M2 (Dataset Collection & Curation)  
**Date**: 2026-11-01  
**Target Project**: `D:\Ngoding\interviewWeb\BillcodeTech`  
**Working Directory**: `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m2_dataset_1`  
**Recipient**: Orchestrator (`2fb3c008-4b2b-4b9e-88d9-91a9473b651c`)

---

## 1. Observation

### 1.1 Source Dataset Extraction
- **Archive Source**: Mostafa Abla's 12-Class Garbage Classification dataset on Hugging Face:  
  `https://huggingface.co/datasets/UdaraChamidu/Garbage-Classification-with-12-classes/resolve/main/garbage_classification.zip`
- Total entries in source archive: 15,533 files.
- Available class pool:
  - `biological`: 985 files
  - `plastic`: 865 files
  - `paper`: 1,050 files

### 1.2 Created Files and Directory Layout
- `ml_pipeline/download_dataset.py` (310 lines, executable curation script).
- `ml_pipeline/dataset/CITATIONS.md` (75 lines, provenance, CC-BY 4.0 license, mapping rationale, distribution table).
- Extracted images:
  - `ml_pipeline/dataset/train/organic/`: 56 images (`organic_001.jpg` to `organic_056.jpg`)
  - `ml_pipeline/dataset/train/plastic/`: 56 images (`plastic_001.jpg` to `plastic_056.jpg`)
  - `ml_pipeline/dataset/train/paper/`: 56 images (`paper_001.jpg` to `paper_056.jpg`)
  - `ml_pipeline/dataset/val/organic/`: 14 images (`organic_001.jpg` to `organic_014.jpg`)
  - `ml_pipeline/dataset/val/plastic/`: 14 images (`plastic_001.jpg` to `plastic_014.jpg`)
  - `ml_pipeline/dataset/val/paper/`: 14 images (`paper_001.jpg` to `paper_014.jpg`)
- Total image count: **210 genuine photographic images** (168 train, 42 val). Exactly 80.0% train / 20.0% val split.

### 1.3 Audit & Verification Command Outputs
1. Curation Script Output (`python ml_pipeline/download_dataset.py`):
   ```text
   Dataset already curated and complete on disk:
     organic: 56 train, 14 val
     plastic: 56 train, 14 val
     paper: 56 train, 14 val
   Verification complete: checked 210 images across all classes. Status: OK

   Dataset verified and ready for model training!
   ```
2. PIL Image Quality & Mode Audit:
   ```text
   train / organic : 56 images | modes={'RGB'} | dim range=(183x129) to (389x275)
   train / plastic : 56 images | modes={'RGB'} | dim range=(183x177) to (512x384)
   train / paper   : 56 images | modes={'RGB'} | dim range=(183x140) to (512x384)
   val   / organic : 14 images | modes={'RGB'} | dim range=(183x137) to (367x275)
   val   / plastic : 14 images | modes={'RGB'} | dim range=(183x168) to (512x384)
   val   / paper   : 14 images | modes={'RGB'} | dim range=(194x146) to (512x384)

   Total images verified: 210
   Train images: 168 (80.0%)
   Val images:   42 (20.0%)
   ```
3. Test Suite Verification:
   - `python -m unittest tests.test_tier1_structure -k test_f2`: Ran 6 tests in 0.067s — **OK**
   - `python -m unittest tests.test_tier1_structure -k test_f3`: Ran 6 tests in 0.004s — **OK**
   - `python -m unittest tests.test_tier2_validation -k test_f2`: Ran 6 tests in 0.198s — **OK**
   - `python -m unittest tests.test_tier3_interaction -k test_f2`: Ran 2 tests in 0.002s — **OK**
   - Total dataset-specific tests passing: **20 of 20 tests (100% pass rate)**.

---

## 2. Logic Chain

1. **Requirement R2 Specification**:
   `ORIGINAL_REQUEST.md` §R2 and `PROJECT.md` mandate >=150 real waste images across Organic Waste, Plastic Waste, and Paper Waste with >=50 images/class and an 80/20 train/val partition, accompanied by source documentation in `CITATIONS.md`.
2. **Deterministic Sampling**:
   To eliminate class imbalance and randomness across runs, `ml_pipeline/download_dataset.py` uses seed `42` to select exactly 70 images per category from the 12-class dataset (70 * 3 = 210 images, comfortably exceeding 150).
3. **Partitioning**:
   70 images per class partitions cleanly into 56 training images (80.0%) and 14 validation images (20.0%). Across three categories, this yields 168 training images and 42 validation images (total 210 images).
4. **Category Mapping Rationale**:
   The source dataset labels food scraps and fruit/vegetable matter as `biological`. This directly represents the compostable organic waste stream. Therefore, `biological` is mapped to `organic`, while `plastic` and `paper` map directly.
5. **Quality Assurance**:
   Every image was inspected with `PIL.Image.open().verify()` and converted to 3-channel RGB. No zero-byte, corrupted, or unsupported images exist in the dataset directory.
6. **E2E Test Compliance**:
   All 20 unit tests across Tiers 1-3 that validate dataset structure, counts, split ratios, non-zero file sizes, image decodability, and citation documentation execute and pass cleanly.

---

## 3. Caveats

- The source dataset is photographic imagery originally collected for research benchmarks. Although lighting and backgrounds vary naturally, items are centered and isolated on realistic indoor/outdoor surfaces, which is optimal for transfer learning feature extraction in MobileNetV2.
- The 239.5 MB source zip archive was downloaded, curated, and then removed from disk to avoid bloating the repository and git tree, adhering to `docs/SPEC.md` §6 ("Never Do: Mengunggah file dataset berukuran ratusan megabyte langsung ke git tracking"). If a user or evaluator deletes `train/` and `val/` and runs `python ml_pipeline/download_dataset.py`, the script automatically re-downloads the archive and regenerates the exact same partition deterministically.

---

## 4. Conclusion

Milestone M2 (Dataset Collection & Curation) is **100% COMPLETE**. All acceptance criteria for Requirement R2 are fully satisfied:
- 210 genuine, non-corrupted waste images curated into `ml_pipeline/dataset/`.
- 3 categories: `organic` (70 images), `plastic` (70 images), `paper` (70 images) — exceeding >=50/class.
- Exact 80/20 split: 168 train (56/class) and 42 val (14/class).
- Comprehensive citations, licenses, and mapping rationale recorded in `ml_pipeline/dataset/CITATIONS.md`.
- Automated curation and validation script delivered in `ml_pipeline/download_dataset.py`.
- 100% pass on all 20 dataset unit tests in the project test suite.

The dataset is ready for immediate consumption by Worker M3 (ML Pipeline & PyTorch MobileNetV2 Training).

---

## 5. Verification Method

To independently verify this milestone:

1. **Run dataset self-verification**:
   ```powershell
   cd D:\Ngoding\interviewWeb\BillcodeTech
   python ml_pipeline/download_dataset.py
   ```
   *Expected output*: `Verification complete: checked 210 images across all classes. Status: OK` and `Dataset verified and ready for model training!`.

2. **Run E2E test suite for dataset and citation modules**:
   ```powershell
   cd D:\Ngoding\interviewWeb\BillcodeTech
   python -m unittest tests.test_tier1_structure -k "test_f2 or test_f3"
   python -m unittest tests.test_tier2_validation -k "test_f2"
   python -m unittest tests.test_tier3_interaction -k "test_f2"
   ```
   *Expected output*: All 20 tests pass with `OK`.

3. **Inspect file layout and citation documentation**:
   ```powershell
   Get-ChildItem -Path D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\dataset -Recurse -File | Group-Object Directory
   Get-Content D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\dataset\CITATIONS.md
   ```
