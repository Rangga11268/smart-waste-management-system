# SWMS Machine Learning Pipeline

## Overview
This directory contains the complete Machine Learning pipeline for the **Smart Waste Management System (SWMS)**, built for the Bilcode Technology Fullstack Developer Technical Coding Test take-home assessment.

The pipeline performs transfer learning with a pretrained **MobileNetV2** backbone on a curated dataset of waste images, classifying inputs into three categories:
- **Organic Waste** (Leaves, food leftovers, fruits, vegetables)
- **Plastic Waste** (Bottles, plastic bags, packaging, containers)
- **Paper Waste** (Cardboard, paper sheets, newspapers, books)

---

## Directory Structure
```text
ml_pipeline/
├── dataset/
│   ├── train/                 # 80% partition (56 images/class = 168 images)
│   │   ├── organic/
│   │   ├── paper/
│   │   └── plastic/
│   ├── val/                   # 20% partition (14 images/class = 42 images)
│   │   ├── organic/
│   │   ├── paper/
│   │   └── plastic/
│   └── CITATIONS.md           # Dataset sources, provenance, and license documentation
├── saved_models/
│   ├── waste_model.pth        # Trained PyTorch model weights (state_dict)
│   └── class_to_idx.json      # Class index mapping dictionary
├── artifacts/
│   ├── confusion_matrix.png   # Seaborn heatmap of test evaluation
│   ├── accuracy_curve.png     # Training & validation loss/accuracy curves
│   ├── classification_report.txt # Detailed precision, recall, F1-score metrics
│   └── training_history.json  # Epoch metrics log
├── train.py                   # Transfer learning training pipeline
├── evaluate.py                # Evaluation & metric visualizations generator
├── predict.py                 # Production-grade inference helper class
├── download_dataset.py        # Automated reproducible dataset acquisition script
├── requirements.txt           # Python dependency specification
└── README.md                  # This documentation file
```

---

## Requirements & Setup

### 1. Environment Setup
Create and activate a Python 3.10+ virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

---

## Training the Model

The training script applies data augmentation (`RandomResizedCrop(224)`, `RandomHorizontalFlip()`, `RandomRotation(15)`, `ColorJitter`) to prevent overfitting on small datasets, using a two-stage transfer learning schedule (classifier warm-up followed by selective top-feature fine-tuning).

### Command:
```bash
python ml_pipeline/train.py --epochs 15 --batch-size 16 --lr 0.001 --seed 42
```

### Hyperparameters:
| Parameter | Default | Description |
|---|---|---|
| `--epochs` | 15 | Total number of training epochs |
| `--batch-size` | 16 | Mini-batch size for DataLoader |
| `--lr` | 0.001 | Initial learning rate for Adam optimizer |
| `--seed` | 42 | Random seed for deterministic reproducibility |
| `--data-dir` | `./dataset` | Path to curated dataset directory |
| `--save-dir` | `./saved_models` | Directory to save checkpoint weights |

### Outputs Generated:
- `saved_models/waste_model.pth` and workspace root `waste_model.pth`
- `saved_models/class_to_idx.json`
- `artifacts/training_history.json`
- `artifacts/accuracy_curve.png` and workspace root `accuracy_curve.png`

---

## Evaluating the Model

The evaluation script runs the saved model against the validation/test set to compute standard metrics and export visual artifacts.

### Command:
```bash
python ml_pipeline/evaluate.py --model ml_pipeline/saved_models/waste_model.pth --data-dir ml_pipeline/dataset/val
```

### Outputs Generated:
- `artifacts/confusion_matrix.png` (and workspace root `confusion_matrix.png`)
- `artifacts/accuracy_curve.png` (and workspace root `accuracy_curve.png`)
- `artifacts/classification_report.txt` (and workspace root `classification_report.txt`)

### Acceptance Criteria:
- Overall Validation Accuracy $\ge 80\%$ (Target $\ge 85\%$).
- Per-class Precision, Recall, and F1-score $\ge 0.70$.

---

## Running Inference

The `predict.py` module exposes a clean `WastePredictor` class conforming strictly to the `docs/API_SPECS.md` contract for integration with the Day 2 FastAPI backend.

### Python Code Usage:
```python
from ml_pipeline.predict import WastePredictor

predictor = WastePredictor()
result = predictor.predict("path/to/image.jpg")

print(result)
```

### Response Schema:
```json
{
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
```

### CLI Usage:
```bash
python ml_pipeline/predict.py path/to/sample_image.jpg
```
