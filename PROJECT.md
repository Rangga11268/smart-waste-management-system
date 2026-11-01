# Project: Smart Waste Management System (SWMS) - Day 1

## Architecture
- Monorepo containing `backend/`, `ml_pipeline/`, `web/`, `mobile/`, and `docs/`.
- `ml_pipeline` houses the dataset (`ml_pipeline/dataset/`), models (`ml_pipeline/saved_models/`), reports (`ml_pipeline/artifacts/`), and scripts (`train.py`, `evaluate.py`, `predict.py`).
- Root files contain root `.gitignore`, `README.md`, and convenience exports (`waste_model.pth`, `confusion_matrix.png`, `accuracy_curve.png`, `classification_report.txt`) to satisfy both `docs/SPEC.md` and `ORIGINAL_REQUEST.md`.

## Code Layout
- `backend/`: FastAPI application stub (`app/main.py`, `requirements.txt`, `README.md`)
- `web/`: Next.js 14 web dashboard stub (`package.json`, `README.md`)
- `mobile/`: Flutter mobile application stub (`pubspec.yaml`, `README.md`)
- `ml_pipeline/`:
  - `dataset/`:
    - `train/`: `organic/` (>=40), `plastic/` (>=40), `paper/` (>=40)
    - `val/`: `organic/` (>=10), `plastic/` (>=10), `paper/` (>=10)
    - `CITATIONS.md`: Dataset source documentation, licensing, and citations
  - `saved_models/`: `waste_model.pth`, `class_to_idx.json`
  - `artifacts/`: `confusion_matrix.png`, `accuracy_curve.png`, `classification_report.txt`
  - `train.py`: PyTorch MobileNetV2 transfer learning with data augmentation
  - `evaluate.py`: Generates confusion matrix, accuracy curves, and classification report
  - `predict.py`: Inference helper class for single image classification
  - `download_dataset.py`: Reproducible dataset download and curation script
  - `requirements.txt`: Python package requirements for ML pipeline
  - `README.md`: ML pipeline execution guide
- Root:
  - `waste_model.pth`: copy of trained weights
  - `confusion_matrix.png`: copy of confusion matrix plot
  - `accuracy_curve.png`: copy of loss/accuracy curve plot
  - `classification_report.txt`: copy of classification report
  - `.gitignore`: root monorepo ignore rules
  - `README.md`: monorepo overview

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Monorepo Structure | Setup `backend`, `ml_pipeline`, `web`, `mobile`, `docs` directories and stubs | M1 | TASKS.md 1.1, ORIGINAL_REQUEST R1 |
| 2 | Dataset Curation | Download and organize >=150 images (>=50/class) across organic, plastic, paper with 80/20 train/val split | M2 | TASKS.md 1.2, ORIGINAL_REQUEST R2 |
| 3 | Dataset Citations | Document dataset provenance, licenses, and sources in `CITATIONS.md` | M2 | ORIGINAL_REQUEST R2, SPEC.md |
| 4 | PyTorch Environment Setup | Ensure clean PyTorch CPU and torchvision installation | M3 | explorer_env_1, SPEC.md |
| 5 | MobileNetV2 Transfer Learning | Implement `train.py` with MobileNetV2 pretrained weights, custom classifier (1280->3), data augmentation | M3 | TASKS.md 1.3, ORIGINAL_REQUEST R3 |
| 6 | Model Weights Export | Export trained model weights to `waste_model.pth` | M3 | TASKS.md 1.5, ORIGINAL_REQUEST R4 |
| 7 | Metric Visualizations & Reports | Generate `confusion_matrix.png`, `accuracy_curve.png`, and `classification_report.txt` (Accuracy >= 80%, target >= 85%) | M4 | TASKS.md 1.4, ORIGINAL_REQUEST R4 |
| 8 | Inference Script & Class Mapping | Provide `predict.py` and `class_to_idx.json` for Day 2 FastAPI backend compatibility | M4 | ADR.md, API_SPECS.md |
| 9 | 100% E2E Test Suite Pass | Verify all Day 1 requirements against requirement-driven opaque-box test suite | M5 | Project Pattern Final Milestone |
| 10| Adversarial Hardening | Test edge cases (corrupted images, non-waste images, wrong shapes) | M5 | Project Pattern Tier 5 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M0| Survey & Infra Planning | Complete codebase, spec, and environment survey | none | DONE |
| M1| Monorepo Project Structure Setup | Root `.gitignore`, `README.md`, `backend/`, `web/`, `mobile/` stubs | none | DONE |
| M2| Dataset Collection & Curation | Curate 150+ images (50+ per class) in 80/20 split and write `CITATIONS.md` | none | DONE |
| M3| ML Pipeline & MobileNetV2 Training | `requirements.txt`, PyTorch environment, `train.py`, train model, export `waste_model.pth` | M2 | DONE |
| M4| Evaluation Artifacts & Inference Contract | `evaluate.py`, `predict.py`, `confusion_matrix.png`, `accuracy_curve.png`, `classification_report.txt`, `class_to_idx.json` | M3 | DONE |
| M5| Final Milestone (E2E Verification & Hardening) | Pass 100% E2E test suite (Tiers 1-4) + Adversarial hardening (Tier 5) | M1, M2, M3, M4, TEST_READY | DONE |

## Interface Contracts
### Dataset ↔ Training Pipeline
- Input: `ml_pipeline/dataset/train/` and `ml_pipeline/dataset/val/`
- Classes: `organic/`, `plastic/`, `paper/`
- Format: `.jpg`, `.jpeg`, `.png`, standard RGB images

### ML Pipeline ↔ Backend (Day 2 Contract)
- Model: `waste_model.pth` (MobileNetV2 state_dict, classifier: `Dropout(p=0.2)`, `Linear(in_features=1280, out_features=3)`)
- Classes map: `class_to_idx.json` mapping indices `0, 1, 2` to `"Organic Waste"`, `"Paper Waste"`, `"Plastic Waste"`
- Preprocessing: `Resize(256)`, `CenterCrop(224)`, `ToTensor()`, `Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])`
- Inference return: predicted category, confidence score, confidence percentage, class probabilities dictionary
