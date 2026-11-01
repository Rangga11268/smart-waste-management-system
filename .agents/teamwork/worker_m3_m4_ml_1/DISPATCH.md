# Dispatch: Worker M3 & M4 (ML Pipeline, MobileNetV2 Training, Evaluation & Export)

## Objective
Implement the complete PyTorch transfer learning training pipeline using MobileNetV2 (`ml_pipeline/train.py`), train the model on the curated dataset to achieve >=80% evaluation accuracy (target >=85%), export `waste_model.pth`, generate evaluation metric artifacts (`confusion_matrix.png`, `accuracy_curve.png`, `classification_report.txt`), provide `class_to_idx.json`, and implement `ml_pipeline/predict.py`.

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Working Directory
`D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m3_m4_ml_1`

## Inputs
- `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\ORIGINAL_REQUEST.md`
- `D:\Ngoding\interviewWeb\BillcodeTech\PROJECT.md`
- `D:\Ngoding\interviewWeb\BillcodeTech\TEST_READY.md`
- `D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\dataset/` (210 curated images in `train/` and `val/`)
- `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\explorer_env_1\analysis.md` (PyTorch installation details & hyperparameter guidance)

## File Ownership
- Exclusively owns:
  - `D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline/train.py`
  - `D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline/evaluate.py`
  - `D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline/predict.py`
  - `D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline/requirements.txt`
  - `D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline/README.md`
  - `D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline/saved_models/**`
  - `D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline/artifacts/**`
  - Root convenience exports:
    - `D:\Ngoding\interviewWeb\BillcodeTech\waste_model.pth`
    - `D:\Ngoding\interviewWeb\BillcodeTech\confusion_matrix.png`
    - `D:\Ngoding\interviewWeb\BillcodeTech\accuracy_curve.png`
    - `D:\Ngoding\interviewWeb\BillcodeTech\classification_report.txt`

## Instructions
1. Setup Python ML Environment:
   - Run `python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu` if PyTorch CPU is not cleanly importable. Verify `import torch, torchvision` succeeds.
   - Author `ml_pipeline/requirements.txt` listing exact dependencies.
2. Implement `ml_pipeline/train.py`:
   - Architecture: MobileNetV2 pretrained (`weights=MobileNet_V2_Weights.DEFAULT`).
   - Classifier: `nn.Sequential(nn.Dropout(p=0.2), nn.Linear(1280, 3))`.
   - Data augmentation for training: `RandomResizedCrop(224)`, `RandomHorizontalFlip()`, `RandomRotation(15)`, `ColorJitter(brightness=0.1, contrast=0.1)`, `ToTensor()`, `Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])`.
   - Validation transform: `Resize(256)`, `CenterCrop(224)`, `ToTensor()`, `Normalize(...)`.
   - Training loop: ~15-20 epochs, track train loss, train acc, val loss, val acc per epoch.
   - Target accuracy: >= 80% (target >= 85%).
   - Model export: Save state_dict to `ml_pipeline/saved_models/waste_model.pth` AND copy to project root `waste_model.pth`.
   - Class indices export: Save `ml_pipeline/saved_models/class_to_idx.json` mapping indices to `["Organic Waste", "Paper Waste", "Plastic Waste"]`.
3. Implement `ml_pipeline/evaluate.py`:
   - Load `waste_model.pth` and evaluate on `val/` set.
   - Generate `confusion_matrix.png` (using seaborn heatmap with class labels) saved to `ml_pipeline/artifacts/confusion_matrix.png` and root `confusion_matrix.png`.
   - Generate `accuracy_curve.png` (train vs val loss and accuracy across epochs) saved to `ml_pipeline/artifacts/accuracy_curve.png` and root `accuracy_curve.png`.
   - Generate `classification_report.txt` (scikit-learn `classification_report` with precision, recall, f1-score, and support per class) saved to `ml_pipeline/artifacts/classification_report.txt` and root `classification_report.txt`.
4. Implement `ml_pipeline/predict.py`:
   - Clean, lightweight inference class `WasteClassifier(model_path="waste_model.pth")` that accepts an image path or PIL Image and returns a dictionary:
     `{"category": "Plastic Waste", "confidence": 0.9421, "confidence_percentage": "94.21%", "category_id": 2, "probabilities": {"Organic Waste": 0.03, "Plastic Waste": 0.94, "Paper Waste": 0.03}}`
     strictly matching `docs/API_SPECS.md` contract.
5. Author `ml_pipeline/README.md`:
   - Detailed guide on training, evaluating, hyperparameter settings, and running inference.
6. Execute and Verify:
   - Run `python ml_pipeline/train.py`
   - Run `python ml_pipeline/evaluate.py`
   - Run the E2E test runner: `python tests/e2e_runner.py`
   - Ensure 100% of tests pass!
7. Write your report to `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m3_m4_ml_1\handoff.md` and send a message to orchestrator (`2fb3c008-4b2b-4b9e-88d9-91a9473b651c`).


## 2026-11-01T12:32:29Z
[Message] timestamp=2026-11-01T12:32:29Z sender=2fb3c008-4b2b-4b9e-88d9-91a9473b651c priority=MESSAGE_PRIORITY_HIGH content=You are teamwork_worker_m3_m4_ml_1.
Working directory: D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m3_m4_ml_1
Read D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\ORIGINAL_REQUEST.md and the dispatch instructions at D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m3_m4_ml_1\DISPATCH.md.
Also read D:\Ngoding\interviewWeb\BillcodeTech\PROJECT.md, D:\Ngoding\interviewWeb\BillcodeTech\TEST_READY.md, and D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\explorer_env_1\analysis.md.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Implement ml_pipeline/train.py (PyTorch MobileNetV2 transfer learning with data augmentation), train model on ml_pipeline/dataset/ to achieve >=80% evaluation accuracy, export waste_model.pth, generate evaluation artifacts (confusion_matrix.png, accuracy_curve.png, classification_report.txt), export class_to_idx.json, implement predict.py, and verify with python tests/e2e_runner.py.
Write your completion handoff to D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m3_m4_ml_1\handoff.md.
When finished, send a message to orchestrator (conversation ID: 2fb3c008-4b2b-4b9e-88d9-91a9473b651c) with a summary.
