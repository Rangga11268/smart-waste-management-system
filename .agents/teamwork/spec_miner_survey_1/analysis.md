# Day 1 Specification Analysis: Smart Waste Management System (SWMS)

**Author:** `teamwork_spec_miner_1`  
**Date:** 2026-11-01  
**Scope:** Day 1 Implementation Roadmap (Monorepo Setup, Dataset Curation, PyTorch MobileNetV2 Transfer Learning, Evaluation Metrics, Model Export)  
**Authoritative Sources:**
- `ORIGINAL_REQUEST.md` (Approved prompt & acceptance criteria)
- `docs/TASKS.md` (Task 1.1 through 1.5)
- `docs/PRD.md` (FR-ML-01 to FR-ML-05, NFR-01, Delivery Checklist)
- `docs/SPEC.md` (§1, §2.A, §3, §5, §6, §7)
- `docs/ARCHITECTURE.md` (C4 diagrams, ML integration, Unified FastAPI)
- `docs/RUNBOOK.md` (§2.A, §3 demo scenario)
- `docs/ADR.md` (ADR-001, ADR-002, ADR-004)
- `docs/API_SPECS.md` (§2 `/predict` endpoint contract)
- `docs/ERD.md` (Database schema & categories master data)
- `docs/FLOWS.md` (ML inference sequence & edge cases)
- `Undangan Technical Coding Test – Fullstack Developer _ Bilcode Technology.eml`

---

## 1. Executive Summary & Objective

The objective of Day 1 is to establish the solid foundation for the Smart Waste Management System (SWMS), an AI-assisted multi-platform municipal waste management solution for the Bilcode Technology Fullstack Developer Technical Assessment.

Day 1 delivers:
1. Complete monorepo directory skeleton (`backend/`, `ml_pipeline/`, `web/`, `mobile/`, `docs/`).
2. High-quality curated dataset of $\ge 150$ images (minimum 50 per category) for 3 classes: Organic Waste, Plastic Waste, and Paper Waste, split 80% training and 20% validation/testing, with documented provenance citations.
3. PyTorch transfer learning training pipeline using MobileNetV2 with robust data augmentation and hyperparameter tuning.
4. Model evaluation achieving $\ge 80\%$ test accuracy (target $\ge 85\%$).
5. Exported model weights (`waste_model.pth`) and required visual/textual metric artifacts (`confusion_matrix.png`, `accuracy_curve.png`, `classification_report.txt`).
6. Compatibility with the unified backend inference contract (`POST /api/v1/predict`) and database architecture baseline.

---

## 2. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Repository | Monorepo Structure Setup (Task 1.1) | Clean, modular monorepo layout containing `backend/`, `ml_pipeline/`, `web/`, `mobile/`, and `docs/` directories. | Local filesystem path `D:\Ngoding\interviewWeb\BillcodeTech` | Directory structure with respective `.gitignore`, configuration, and module roots | Missing parent paths or permission errors | `TASKS.md:19`, `ORIGINAL_REQUEST.md:12-13`, `SPEC.md:94-138` |
| 2 | Dataset | Multi-Class Dataset Acquisition (Task 1.2) | Collection of $\ge 150$ total waste images with $\ge 50$ images across 3 mandatory classes: `organic`, `plastic`, `paper`. | Public domain image datasets / web image corpora | Image files in JPEG/PNG format organized in class subfolders | Corrupt images, unreadable formats, insufficient counts (<50/class) | `ORIGINAL_REQUEST.md:15-17`, `PRD.md:32-33`, `TASKS.md:20`, `EML:119-121` |
| 3 | Dataset | Train/Val Partitioning & Structuring | Organization of dataset into an 80% train and 20% validation/test split. | Raw image folders per category | Stratified directory structure: `dataset/train/{organic,plastic,paper}` and `dataset/val/{organic,plastic,paper}` | Class imbalance in split, data leakage across splits | `ORIGINAL_REQUEST.md:16, 34`, `TASKS.md:20`, `SPEC.md:42-45` |
| 4 | Dataset | Provenance & Citations Metadata | Documentation recording dataset sources, licensing, class definitions, and image counts. | Source URLs, attribution licenses, dataset metadata | `ml_pipeline/dataset/README.md` or `CITATIONS.md` containing full source citations | Missing attribution or unclear commercial/academic license | `ORIGINAL_REQUEST.md:16, 35`, `PRD.md:80`, `EML:138` |
| 5 | ML Pipeline | MobileNetV2 Transfer Learning Architecture (Task 1.3) | Pre-trained MobileNetV2 backbone (ImageNet weights) with custom classifier head adapted to 3 waste classes. | Pre-trained weights, RGB images resized to 224x224 | Model object with trainable classification layer (Linear 1280 -> 3) | Weight download network failure, input tensor dimension mismatch | `SPEC.md:14, 41-43`, `ADR.md:21-31`, `PRD.md:34` |
| 6 | ML Pipeline | Image Data Augmentation Pipeline | Training data transformations: RandomResizedCrop(224), RandomHorizontalFlip, RandomRotation(15°), ColorJitter, and ImageNet normalization. | Raw PIL images of varying dimensions | Transformed PyTorch tensors of shape `[B, 3, 224, 224]` | Non-RGB color modes (RGBA, Grayscale) failing transforms | `SPEC.md:41-43`, `TASKS.md:21`, `ORIGINAL_REQUEST.md:19` |
| 7 | ML Pipeline | Model Training Script (`ml_pipeline/train.py`) | Configurable training loop with CrossEntropyLoss, Adam/SGD optimizer, learning rate scheduler, checkpointing, and epoch tracking. | CLI args (`--epochs 15`, `--batch-size 16`, `--lr 0.001`, `--data-dir`) | Trained model weights in memory/disk, loss/accuracy logs per epoch | Out of memory (CUDA/RAM), vanishing/exploding gradients, zero epochs | `SPEC.md:41-43`, `TASKS.md:21`, `RUNBOOK.md:57` |
| 8 | ML Pipeline | Accuracy Target Fulfillment | Training pipeline convergence to achieve $\ge 80\%$ test/validation accuracy (target $\ge 85\%$). | Validation/Test dataset | Test accuracy metric $\ge 0.80$ ($\ge 80\%$) logged to stdout | Overfitting on small dataset or underfitting (<80% accuracy) | `ORIGINAL_REQUEST.md:19, 42`, `PRD.md:34`, `SPEC.md:204-205`, `EML:123` |
| 9 | Artifacts | Model Weights Export (Task 1.5) | Serialized PyTorch state dictionary or full model saved to `waste_model.pth`. | Trained PyTorch model | Saved weights file: `ml_pipeline/saved_models/waste_model.pth` (or root `waste_model.pth`) $\approx 14\text{ MB}$ | Disk write error, unpicklable lambda functions, missing target dir | `ORIGINAL_REQUEST.md:22, 39`, `TASKS.md:23`, `PRD.md:79`, `SPEC.md:113` |
| 10 | Artifacts | Confusion Matrix Visualization (Task 1.4) | Heatmap plot showing true vs. predicted counts/proportions across the 3 classes. | Model predictions and ground-truth validation labels | `ml_pipeline/artifacts/confusion_matrix.png` (or root `confusion_matrix.png`) | Matplotlib backend GUI errors on headless environments (must use Agg) | `ORIGINAL_REQUEST.md:22, 43`, `TASKS.md:22`, `PRD.md:35, 81`, `SPEC.md:206` |
| 11 | Artifacts | Loss & Accuracy Curves (Task 1.4) | Dual-line plot illustrating train vs. validation loss and accuracy progression across epochs. | Epoch history arrays (train_loss, val_loss, train_acc, val_acc) | `ml_pipeline/artifacts/accuracy_curve.png` (or root `accuracy_curve.png`) | NaN values in loss array, plotting dimension mismatch | `ORIGINAL_REQUEST.md:22, 44`, `TASKS.md:22`, `PRD.md:35, 81` |
| 12 | Artifacts | Text Classification Report (Task 1.4) | Formatted report detailing precision, recall, F1-score, and support for each class plus macro/weighted averages. | Ground-truth labels and model prediction classes | `ml_pipeline/artifacts/classification_report.txt` (or root `classification_report.txt`) | Zero division warnings when a class is never predicted | `ORIGINAL_REQUEST.md:22, 45`, `TASKS.md:22`, `PRD.md:35, 81`, `SPEC.md:207` |
| 13 | Evaluation | Standalone Evaluation Script (`ml_pipeline/evaluate.py`) | Independent evaluation utility to load saved `waste_model.pth`, run inference on test partition, and generate all metric artifacts. | CLI args (`--model`, `--test-dir`, `--output-dir`) | Console evaluation summary + written artifact files | Missing model file, mismatched class index mapping | `SPEC.md:44-46, 203-207`, `RUNBOOK.md:57` |
| 14 | Architecture | Inference Engine Interface Alignment | Exported model and preprocessing transformations directly loadable by FastAPI `POST /api/v1/predict`. | Multipart binary image (`image/jpeg`, `image/png`, `image/webp`) | JSON: `{ status: "success", data: { category: string, confidence: float, probabilities: dict } }` | Latency >800ms, corrupt image payload, dimension mismatch | `API_SPECS.md:90-112`, `PRD.md:36`, `ARCHITECTURE.md:46`, `ADR.md:15-17` |
| 15 | Architecture | Database & Category Mapping Baseline | Class indices (0, 1, 2) mapped to database master categories (`organic`, `plastic`, `paper`) with UI hex colors. | Class label from model | Database category ID (1: organic, 2: plastic, 3: paper) and hex badges | Mismatched label index causing incorrect category ID storage | `ERD.md:91-105`, `STYLING_GUIDE.md:41-47` |

---

## 3. Edge Cases & Handling

| # | Feature | Input / Condition | Observed / Documented Behavior | Mitigated Handling Strategy |
|---|---------|-------------------|--------------------------------|-----------------------------|
| 1 | Image Preprocessing | Grayscale or RGBA Image | PyTorch `transforms.ToTensor()` on 1-channel or 4-channel image fails ImageNet normalization expecting 3 channels `[3, 224, 224]`. | Enforce `image.convert("RGB")` via PIL before feeding into torchvision transforms. |
| 2 | Image Quality | Low Resolution / Blurry Image | Sub-300px image or heavy compression artifacts leading to low model confidence (<50%). | Model outputs confidence probabilities; system contract specifies falling back to manual user selection if confidence < 0.50 (`FLOWS.md:167-173`). |
| 3 | Matplotlib Plotting | Headless / Non-GUI OS Execution | `plt.show()` or default backend on Windows server / headless terminal throws `UserWarning` or fails to save figure. | Explicitly invoke `matplotlib.use('Agg')` prior to importing `pyplot`. |
| 4 | Data Augmentation | Overly Aggressive Crop or Rotation | Small images cropped to empty background or excessive black padding from rotation. | Use moderate rotation (`degrees=15`), gentle scale bounds (`scale=(0.8, 1.0)`), and bilinear interpolation. |
| 5 | Small Dataset Overfitting | 150-200 images trained for excessive epochs | Training accuracy reaches 100% while validation accuracy drops below 75%. | Freeze MobileNetV2 base feature extractor, train only final classifier first, use dropout (p=0.2), apply weight decay (1e-4), and use early stopping / learning rate scheduler. |
| 6 | Class Label Indexing | Mismatched class-to-index order between `ImageFolder` and DB | Alphabetical sorting in `ImageFolder` yields: 0=`organic`, 1=`paper`, 2=`plastic`, whereas DB categories might be 1=`organic`, 2=`plastic`, 3=`paper`. | Explicitly define and persist `class_to_idx.json` and verify mapping across pipeline and API inference. |
| 7 | Zero Division in Metrics | Imbalanced class testing predictions | Precision or F1 score calculation throws `ZeroDivisionError` or generates warning if model predicts 0 instances for a rare class. | Set `zero_division=0` in `scikit-learn.metrics.classification_report`. |
| 8 | Model Serialization | Serializing full class vs. state_dict | Saving full model instance (`torch.save(model)`) breaks if module path changes between `ml_pipeline` and `backend`. | Save `model.state_dict()` into `waste_model.pth` along with model metadata (architecture, class names, mean/std normalization values). |

---

## 4. Detailed Specification Breakdown

### 4.1 Monorepo Architecture & Conventions (Task 1.1)
- Root folder: `D:\Ngoding\interviewWeb\BillcodeTech`
- Primary directory modules:
  - `backend/`: FastAPI REST backend, SQLAlchemy ORM, Alembic migrations, PyTorch in-process inference service.
  - `ml_pipeline/`: Machine learning dataset, preprocessing scripts, training script (`train.py`), evaluation script (`evaluate.py`), saved weights (`saved_models/`), and evaluation plots (`artifacts/`).
  - `web/`: Next.js 14+ App Router, Tailwind CSS, Lucide Icons web admin and citizen dashboard.
  - `mobile/`: Flutter Android/iOS application with camera, geotagging, and API integration.
  - `docs/`: Technical documents (PRD, SPEC, ARCHITECTURE, ADR, ERD, FLOWS, API_SPECS, STYLING_GUIDE, TASKS, RUNBOOK).

### 4.2 Dataset Requirements & Curation (Task 1.2)
- **Minimum Count**: $\ge 150$ total images.
- **Per-Class Threshold**: $\ge 50$ images per category.
- **Classes**:
  1. `organic` (Organic Waste: food scraps, leaves, vegetables, fruit peels).
  2. `plastic` (Plastic Waste: plastic bottles, bags, sachets, cups, straws).
  3. `paper` (Paper Waste: cardboard, newspapers, cartons, paper sheets).
- **Split Ratio**: Stratified 80% Training ($\ge 120$ images), 20% Validation/Testing ($\ge 30$ images).
- **Format**: RGB images (JPEG, PNG, WebP).
- **Documentation**: Source URLs, dataset license (Creative Commons / Open Access), and metadata file.

### 4.3 ML Training Pipeline Specification (Task 1.3)
- **Framework**: PyTorch (`torch`, `torchvision`).
- **Base Architecture**: `models.mobilenet_v2(weights=MobileNet_V2_Weights.DEFAULT)`.
- **Classification Head**:
  - Input features: `1280`
  - Dropout: `0.2`
  - Output features: `3` (Linear layer `in_features=1280, out_features=3`).
- **Image Preprocessing**:
  - Resolution: $224 \times 224$ pixels.
  - ImageNet normalization: Mean `[0.485, 0.456, 0.406]`, Std `[0.229, 0.224, 0.225]`.
- **Data Augmentation**:
  - `RandomResizedCrop(224, scale=(0.8, 1.0))`
  - `RandomHorizontalFlip(p=0.5)`
  - `RandomRotation(degrees=15)`
  - `ColorJitter(brightness=0.1, contrast=0.1)`
- **Optimization**:
  - Loss function: `nn.CrossEntropyLoss()`
  - Optimizer: `optim.Adam(model.classifier.parameters(), lr=0.001)` or `optim.SGD(momentum=0.9)`
  - Learning rate scheduler: `StepLR(step_size=5, gamma=0.5)`
  - Epochs: 10–15 epochs.
  - Batch size: 16 (or 32 depending on memory).

### 4.4 Model Performance & Evaluation Targets (Task 1.4)
- **Test/Validation Accuracy**: $\ge 80\%$ minimum passing threshold, target $\ge 85\%$.
- **Generated Artifacts**:
  1. `confusion_matrix.png`: Multi-class confusion matrix plot with labeled axes and counts.
  2. `accuracy_curve.png`: Plots showing training vs. validation loss and training vs. validation accuracy across epochs.
  3. `classification_report.txt`: Formatted report containing Precision, Recall, and F1-Score per class, plus overall accuracy and Macro/Weighted averages.

### 4.5 Model Export & Deployment Artifacts (Task 1.5)
- **Weights File**: `waste_model.pth` exported to `ml_pipeline/saved_models/` and accessible to root/backend.
- **Model Footprint**: Approximately 14 MB (MobileNetV2 state dict).
- **Inference Latency**: Under 200ms on CPU (<800ms NFR requirement).
- **Inference Contract**: Compatible with FastAPI payload structure:
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

### 4.6 Alignment with Day 2 - Day 5 Dependencies
- **Day 2 (Backend)**: `backend/app/services/ml_service.py` requires `waste_model.pth` to be loaded at startup using FastAPI lifespan context.
- **Day 4 (Mobile)**: Flutter app calls `/predict` to pre-fill waste category and confidence.
- **Day 5 (Submission & Video Demo)**: Minutes 01:30–03:30 of the presentation require demonstrating `train.py`, `evaluate.py`, `confusion_matrix.png`, and `classification_report.txt`.

---

## 5. Verification Checklist for Day 1

- [ ] Directory layout contains `backend/`, `ml_pipeline/`, `web/`, `mobile/`, `docs/`.
- [ ] Dataset has $\ge 150$ verified images ($\ge 50$ per class: organic, plastic, paper).
- [ ] Train/val split is 80/20.
- [ ] Provenance citations file is present in `ml_pipeline/dataset/`.
- [ ] PyTorch training script runs with data augmentation.
- [ ] Evaluation accuracy is $\ge 80\%$ (target $\ge 85\%$).
- [ ] Model weights `waste_model.pth` exported and loadable with `torch.load()`.
- [ ] `confusion_matrix.png` is generated.
- [ ] `accuracy_curve.png` is generated.
- [ ] `classification_report.txt` is generated with per-class metrics.
