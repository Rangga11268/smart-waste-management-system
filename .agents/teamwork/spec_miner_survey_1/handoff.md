# Handoff Report: Day 1 Specification Mining Survey

**Agent:** `teamwork_spec_miner_1`  
**Working Directory:** `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\spec_miner_survey_1`  
**Milestone:** Day 1 - Repository Setup, Dataset Acquisition, and ML Pipeline  
**Target:** Orchestrator (`2fb3c008-4b2b-4b9e-88d9-91a9473b651c`)  

---

## 1. Observation

Direct observations extracted verbatim from primary project artifacts:

1. **Approved Request & Acceptance Criteria (`ORIGINAL_REQUEST.md`)**:
   - Lines 12-13: "Establish the project directory structure with modules for `backend`, `ml_pipeline`, `web`, `mobile`, and `docs` as defined in `docs/TASKS.md` (Task 1.1)."
   - Lines 15-16: "Download and curate a dataset of at least 150 images across three categories: Organic Waste, Plastic Waste, and Paper Waste (minimum 50 images per category) from public sources. Organize the dataset with an 80% training and 20% validation/testing split, and document data source citations."
   - Lines 18-19: "Implement a PyTorch transfer learning training script using MobileNetV2 (`ml_pipeline/train.py` or equivalent) with image data augmentation. The training pipeline must achieve an evaluation accuracy of at least 80% (target >= 85%) on the test/validation set."
   - Lines 21-23: "Export the trained model weights to `waste_model.pth`. Generate evaluation outputs including a confusion matrix plot (`confusion_matrix.png`), training loss and accuracy curves (`accuracy_curve.png`), and a text classification report (`classification_report.txt`) showing precision, recall, and F1-score for each class."

2. **Milestone Tasks (`docs/TASKS.md`)**:
   - Lines 18-23:
     - `Task 1.1`: "Setup struktur monorepo (`backend`, `ml_pipeline`, `web`, `mobile`, `docs`)."
     - `Task 1.2`: "Download & kurasi dataset 150+ gambar (Organic, Plastic, Paper) dengan pembagian 80% Train, 20% Val/Test."
     - `Task 1.3`: "Tulis script training PyTorch MobileNetV2 (`train.py`) dengan data augmentation."
     - `Task 1.4`: "Generate visualisasi metrik: `confusion_matrix.png`, `accuracy_curve.png`, dan `classification_report.txt` (Target Akurasi $\ge 85\%$, min $\ge 80\%$). "
     - `Task 1.5`: "Export bobot model ke `waste_model.pth`."

3. **Architecture & Decisions (`docs/ADR.md` & `docs/ARCHITECTURE.md`)**:
   - `ADR.md:27-30`: MobileNetV2 chosen for transfer learning because it is lightweight ($\approx 14\text{ MB}$), CPU-fast ($<200\text{ ms}$), and reaches $>85\%$ accuracy in 10-15 epochs with data augmentation.
   - `ADR.md:14-17`: Unified FastAPI service selected to serve both REST API and in-process PyTorch model inference (`/api/v1/predict`) loaded into memory at startup.
   - `ARCHITECTURE.md:46`: "FastAPI memuat bobot model PyTorch (`.pth`) ke dalam memory RAM saat startup (*Lifespan Handler*)."

4. **API Interface Contract (`docs/API_SPECS.md`)**:
   - Lines 90-111: `POST /api/v1/predict` accepts `multipart/form-data` with field `file` (image binary) and returns:
     ```json
     {
       "status": "success",
       "data": {
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
     }
     ```

5. **Official Employer Requirements (`Undangan Technical Coding Test – Fullstack Developer _ Bilcode Technology.eml`)**:
   - Lines 119-125: "Membuat model klasifikasi gambar sampah... Minimal 3 kategori (Organic Waste, Plastic Waste, dan Paper Waste)... Dataset minimal 150 gambar... Target akurasi minimal 80% pada data testing."
   - Lines 137-140: Deliverables include source code, `waste_model.pth`, dataset with citations, evaluation results, and 7-10 minute presentation video.

---

## 2. Logic Chain

1. **Step 1 (Source Consistency Verification)**: Across all 6 documents (`ORIGINAL_REQUEST.md`, `TASKS.md`, `PRD.md`, `SPEC.md`, `ADR.md`, and the company email `.eml`), the scope, numbers, and criteria are strictly aligned: 3 waste classes (`organic`, `plastic`, `paper`), minimum 150 total images (minimum 50 per class), 80/20 train/test split, PyTorch MobileNetV2 architecture, and evaluation target $\ge 80\%$ (target $\ge 85\%$).
2. **Step 2 (Monorepo Layout Seeding)**: Since Task 1.1 dictates the monorepo root layout (`backend`, `ml_pipeline`, `web`, `mobile`, `docs`), subsequent steps (ML training, backend inference, Next.js dashboard, Flutter app) depend on these directories existing at `D:\Ngoding\interviewWeb\BillcodeTech`.
3. **Step 3 (Dataset Structuring & Provenance)**: The dataset must be stored within `ml_pipeline/dataset/` partitioned into `train/` and `val/` (or `test/`) subdirectories containing class folders `organic/`, `plastic/`, `paper/`. A metadata citations document (`CITATIONS.md`) is mandatory to fulfill brief item 7.
4. **Step 4 (PyTorch Model & Training Execution)**: To avoid overfitting on 150+ images, MobileNetV2 with pre-trained ImageNet weights must be utilized with a custom 3-class linear classifier layer (`nn.Linear(1280, 3)`), dropout 0.2, data augmentation (`RandomResizedCrop(224)`, `RandomHorizontalFlip`, `RandomRotation(15)`), and ImageNet normalization.
5. **Step 5 (Artifact Generation & Alignment)**: Training and evaluation scripts must export `waste_model.pth` (to `ml_pipeline/saved_models/waste_model.pth` and/or root `waste_model.pth`) and output `confusion_matrix.png`, `accuracy_curve.png`, and `classification_report.txt` (to `ml_pipeline/artifacts/` and/or root) to satisfy acceptance criteria R4.
6. **Step 6 (Contract Compatibility for Day 2)**: The model class indices (`0: Organic Waste, 1: Paper Waste, 2: Plastic Waste` or mapped dictionary) must be persisted in a `class_to_idx.json` or config file so that the Day 2 FastAPI backend `POST /predict` service can consume the model seamlessly without hardcoded index mismatches.

---

## 3. Caveats

1. **Local Python ML Dependencies**: PyTorch, torchvision, scikit-learn, matplotlib, seaborn, and pillow must be available in the execution environment or virtualenv to run training and evaluation.
2. **Image Sources**: Curation of 150+ real images should balance resolution, variety, and clarity while adhering to public domain / CC0 / Open Source datasets (e.g., TrashNet, TACO, Kaggle Waste Classification subsets).
3. **File Paths for Evaluation Artifacts**: Artifacts are referenced in `SPEC.md:110-114` as residing inside `ml_pipeline/saved_models/` and `ml_pipeline/artifacts/`, while `ORIGINAL_REQUEST.md:22` mentions root filenames. It is recommended to place primary outputs in `ml_pipeline/artifacts/` and `ml_pipeline/saved_models/`, and provide symlinks or root copies if required by test runners.

---

## 4. Conclusion

All Day 1 specifications, constraints, evaluation metrics, and architectural boundaries have been mined, verified against the official employer brief, and documented in detail in:
- `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\spec_miner_survey_1\analysis.md`

The roadmap for Day 1 is fully bounded and ready for execution:
1. Initialize monorepo directory layout (`backend/`, `ml_pipeline/`, `web/`, `mobile/`, `docs/`).
2. Curate 150+ images across `organic`, `plastic`, and `paper` with 80/20 train/val split and citations.
3. Implement `ml_pipeline/train.py` and `ml_pipeline/evaluate.py` using PyTorch MobileNetV2.
4. Train to achieve $\ge 80\%$ test accuracy and export `waste_model.pth`, `confusion_matrix.png`, `accuracy_curve.png`, and `classification_report.txt`.

---

## 5. Verification Method

To verify the findings and subsequent Day 1 implementation:

1. **Inspect Mined Specifications**:
   - Inspect `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\spec_miner_survey_1\analysis.md`
   - Compare with `D:\Ngoding\interviewWeb\BillcodeTech\docs\TASKS.md` (lines 18-24) and `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\ORIGINAL_REQUEST.md` (lines 27-46).

2. **Verify Monorepo Structure**:
   ```powershell
   Get-ChildItem -Directory D:\Ngoding\interviewWeb\BillcodeTech
   ```
   Must include `backend`, `ml_pipeline`, `web`, `mobile`, `docs`.

3. **Verify Dataset Counts and Split**:
   ```powershell
   (Get-ChildItem -Recurse D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\dataset -File | Measure-Object).Count
   ```
   Must be $\ge 150$ total images, with $\ge 50$ in each class category.

4. **Verify Training & Evaluation Artifacts**:
   - Model weights: `Test-Path D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\saved_models\waste_model.pth`
   - Confusion matrix: `Test-Path D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\artifacts\confusion_matrix.png`
   - Accuracy curve: `Test-Path D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\artifacts\accuracy_curve.png`
   - Classification report: `Get-Content D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\artifacts\classification_report.txt` (verify accuracy $\ge 0.80$).
