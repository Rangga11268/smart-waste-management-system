# Original User Request

## Approved Task Prompt — 2026-11-01T12:07:11Z

Smart Waste Management System (SWMS) for the Bilcode Technology Fullstack Developer Technical Coding Test take-home assessment. Execute Day 1 of the implementation roadmap defined in `docs/TASKS.md`, covering monorepo setup, ML dataset curation, PyTorch MobileNetV2 transfer learning, evaluation metrics, and model export.

Working directory: D:\Ngoding\interviewWeb\BillcodeTech
Integrity mode: development

## Requirements

### R1. Monorepo Project Structure Setup
Establish the project directory structure with modules for `backend`, `ml_pipeline`, `web`, `mobile`, and `docs` as defined in `docs/TASKS.md` (Task 1.1).

### R2. Dataset Collection & Curation
Download and curate a dataset of at least 150 images across three categories: Organic Waste, Plastic Waste, and Paper Waste (minimum 50 images per category) from public sources. Organize the dataset with an 80% training and 20% validation/testing split, and document data source citations.

### R3. Machine Learning Training Pipeline
Implement a PyTorch transfer learning training script using MobileNetV2 (`ml_pipeline/train.py` or equivalent) with image data augmentation. The training pipeline must achieve an evaluation accuracy of at least 80% (target >= 85%) on the test/validation set.

### R4. Evaluation Artifacts & Model Export
Export the trained model weights to `waste_model.pth`. Generate evaluation outputs including a confusion matrix plot (`confusion_matrix.png`), training loss and accuracy curves (`accuracy_curve.png`), and a text classification report (`classification_report.txt`) showing precision, recall, and F1-score for each class.

### R5. Adherence to Technical Specifications
Follow the specifications, architecture guidelines, and standards outlined in `docs/` (`PRD.md`, `SPEC.md`, `ARCHITECTURE.md`, `ADR.md`, `RUNBOOK.md`, `TASKS.md`).

## Acceptance Criteria

### Project Structure
- [ ] Monorepo directories (`backend/`, `ml_pipeline/`, `web/`, `mobile/`, `docs/`) exist in `D:\Ngoding\interviewWeb\BillcodeTech`.

### Dataset
- [ ] Dataset contains at least 150 total images with at least 50 images for each class (`organic`, `plastic`, `paper`).
- [ ] Dataset is organized into an 80/20 train and validation/test partition.
- [ ] Dataset sources are documented with citations.

### Training & Model
- [ ] Training script executes without error using PyTorch and MobileNetV2 architecture.
- [ ] Model weights file `waste_model.pth` is exported and loadable for inference.

### Metrics & Evaluation
- [ ] Test/validation accuracy is >= 80%.
- [ ] `confusion_matrix.png` is generated and displays classification performance across all 3 categories.
- [ ] `accuracy_curve.png` (or loss/accuracy curves) is generated and saved.
- [ ] `classification_report.txt` contains precision, recall, and F1-score for each category.
