# Handoff Report: Monorepo Layout & ML Pipeline Architecture (Day 1)
**Author:** `explorer_repo_1` (Teamwork Explorer)  
**Recipient:** Orchestrator (`2fb3c008-4b2b-4b9e-88d9-91a9473b651c`)  
**Working Directory:** `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\explorer_repo_1`  
**Date:** 2026-11-01  

---

## 1. Observation

1. **Parent and Repository Filesystem (`list_dir D:\Ngoding\interviewWeb` & `run_command "git status"`):**
   - Git repository root is located at `D:\Ngoding\interviewWeb`.
   - `git status` output verbatim:
     ```text
     On branch main
     Your branch is up to date with 'origin/main'.

     Changes not staged for commit:
       deleted:    README.md
       deleted:    css/style.css
       deleted:    index.html
       deleted:    js/script.js

     Untracked files:
       BillcodeTech/
       SusiAir/
       Xolvon/
     ```
   - Running `Test-Path D:\Ngoding\interviewWeb\BillcodeTech\.git` returned `False`. `BillcodeTech` is an untracked directory in `interviewWeb` and does not yet possess its own `.git` directory or `.gitignore`.
2. **Existing Files in `BillcodeTech` (`list_dir D:\Ngoding\interviewWeb\BillcodeTech`):**
   - Directories: `.agents/` and `docs/`.
   - Files: `Gmail - Undangan Technical Coding Test – Fullstack Developer _ Bilcode Technology.pdf` (166,163 bytes) and `Undangan Technical Coding Test – Fullstack Developer _ Bilcode Technology.eml` (39,527 bytes).
   - No source directories (`backend/`, `ml_pipeline/`, `web/`, `mobile/`) exist yet.
   - `docs/` contains 10 specification files: `ADR.md` (3,602 B), `API_SPECS.md` (6,407 B), `ARCHITECTURE.md` (3,587 B), `ERD.md` (5,499 B), `FLOWS.md` (7,643 B), `PRD.md` (5,266 B), `RUNBOOK.md` (2,849 B), `SPEC.md` (10,083 B), `STYLING_GUIDE.md` (6,639 B), and `TASKS.md` (3,396 B).
3. **Host Toolchains (`python --version`, `pip --version`, `node --version`, `npm --version`, `flutter --version`, `git --version`):**
   - Python: `3.12.6` (pip `24.2`)
   - Node: `v24.12.0` (npm `11.5.1`)
   - Flutter: `3.41.1` (channel stable, Dart `3.11.0`)
   - Git: `2.49.0.windows.1`
4. **PyTorch Environment Failure & Pip Cache (`python -c "import torch"` & `pip install --dry-run torch torchvision --index-url https://download.pytorch.org/whl/cpu`):**
   - Executing `python -c "import torch"` produced verbatim:
     ```text
     Traceback (most recent call last):
       File "<string>", line 1, in <module>
       File "C:\Users\MyBook Hype AMD\AppData\Local\Programs\Python\Python312\Lib\site-packages\torch\__init__.py", line 427, in <module>
         from torch._C import *
     ImportError: DLL load failed while importing _C: The specified module could not be found.
     ```
   - Running `pip show torch` confirmed `WARNING: Package(s) not found: torch`.
   - Running `pip install --dry-run torch torchvision --index-url https://download.pytorch.org/whl/cpu` reported:
     ```text
     Using cached https://download-r2.pytorch.org/whl/cpu/torch-2.15.0%2Bcpu-cp312-cp312-win_amd64.whl (126.6 MB)
     Using cached https://download-r2.pytorch.org/whl/cpu/torchvision-0.29.2%2Bcpu-py3-none-win_amd64.whl (1.4 MB)
     Would install torch-2.15.0+cpu torchvision-0.29.2+cpu
     ```
     The CPU wheels are already cached on disk.
5. **Day 1 Requirements from `docs/TASKS.md` & `ORIGINAL_REQUEST.md`:**
   - **Task 1.1:** Setup monorepo structure (`backend/`, `ml_pipeline/`, `web/`, `mobile/`, `docs/`).
   - **Task 1.2:** Curate dataset with $\ge 150$ images across 3 categories (`organic`, `plastic`, `paper`, $\ge 50$ each) split 80% train / 20% val, with `CITATIONS.md`.
   - **Task 1.3:** Implement MobileNetV2 transfer learning (`train.py`) with data augmentation.
   - **Task 1.4:** Generate metric visualizations: `confusion_matrix.png`, `accuracy_curve.png`, and `classification_report.txt` (Target accuracy $\ge 80\%$, target $\ge 85\%$).
   - **Task 1.5:** Export model weights to `waste_model.pth`.

---

## 2. Logic Chain

1. **From Observation 1 & 2:**
   - `interviewWeb` is a parent folder housing several technical assessments (`BillcodeTech/`, `SusiAir/`, `Xolvon/`).
   - `BillcodeTech` is intended to be delivered as an independent public GitHub monorepo (`docs/PRD.md` item 1, `docs/TASKS.md` task 5.5).
   - Therefore, `BillcodeTech` requires its own comprehensive root `.gitignore` and `README.md`.
2. **From Observation 2 & 5:**
   - `docs/` is already fully drafted and comprehensive. It must be treated as immutable read-only input.
   - Day 1 specifically requires establishing directories for all 5 modules (`backend`, `ml_pipeline`, `web`, `mobile`, `docs`), while full implementation is focused on `ml_pipeline/`.
   - Therefore, `backend/`, `web/`, and `mobile/` must be scaffolded with minimal, valid, working stubs (e.g. `main.py`, `package.json`, `pubspec.yaml`, `README.md`) so that `Test-Path` checks pass without cluttering Day 2-4 implementation scopes.
3. **From Observation 4:**
   - The host's global python site-packages has a corrupted/broken torch stub missing `_C.pyd` DLLs.
   - Installing PyTorch CPU wheel (`torch-2.15.0+cpu`, `torchvision-0.29.2+cpu`) from the cached wheel using `--index-url https://download.pytorch.org/whl/cpu` or inside a virtual environment (`python -m venv venv`) resolves the missing DLL error immediately without downloading 2+ GB of CUDA packages.
4. **From Observation 5:**
   - For `ml_pipeline/`, `R2` requires $\ge 150$ images across `organic`, `plastic`, `paper` (min 50 per class) with an 80/20 train/val split.
   - Organizing into `dataset/train/{organic,plastic,paper}` ($\ge 40$ each) and `dataset/val/{organic,plastic,paper}` ($\ge 10$ each) directly supports PyTorch's `ImageFolder` loader.
   - MobileNetV2 with pre-trained weights (`MobileNet_V2_Weights.DEFAULT`) and classifier fine-tuning to 3 output classes easily achieves $\ge 85\%$ accuracy in 10-15 epochs with data augmentation.
   - Evaluation outputs (`waste_model.pth`, `confusion_matrix.png`, `accuracy_curve.png`, `classification_report.txt`) should be saved in `ml_pipeline/artifacts/` and `ml_pipeline/saved_models/`, with convenience copies in `ml_pipeline/` root to satisfy both `docs/SPEC.md` and `ORIGINAL_REQUEST.md`.
5. **Concurrency & File Boundaries:**
   - Dividing Day 1 into 3 distinct roles (Repo Scaffolder, Dataset Curator, ML Pipeline Engineer) creates zero file overlaps:
     - Scaffolder: `BillcodeTech/.gitignore`, `BillcodeTech/README.md`, `backend/**`, `web/**`, `mobile/**`.
     - Dataset Curator: `ml_pipeline/dataset/**`, `ml_pipeline/dataset/CITATIONS.md`.
     - ML Pipeline Engineer: `ml_pipeline/requirements.txt`, `ml_pipeline/train.py`, `ml_pipeline/evaluate.py`, `ml_pipeline/predict.py`, `ml_pipeline/saved_models/**`, `ml_pipeline/artifacts/**`, `ml_pipeline/README.md`.

---

## 3. Caveats

1. **Global PyTorch vs Virtualenv:** If downstream agents execute `python train.py` using the global python without installing the cached CPU wheel or activating a venv, `ImportError: DLL load failed` will occur. Downstream agents must install the cached wheel or run inside a virtualenv.
2. **Git Root Choice:** Whether `BillcodeTech` is initialized with its own `git init` or committed to parent `interviewWeb` depends on the user's preferred submission method. The monorepo layout designed here supports both.
3. **No Implementation in This Turn:** As an Explorer agent, no application source files or stub directories were written outside `.agents/teamwork/explorer_repo_1`. All designs, file specifications, and code samples are provided in `analysis.md`.

---

## 4. Conclusion

1. The exact Day 1 directory structure has been specified and documented in `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\explorer_repo_1\analysis.md`.
2. Three specialized worker roles are defined with disjoint file boundaries:
   - **Role 1 (Repo Scaffolder):** Root files (`.gitignore`, `README.md`), `backend/` stub, `web/` stub, `mobile/` stub.
   - **Role 2 (Dataset Curator):** `ml_pipeline/dataset/` ($\ge 150$ images in 80/20 train/val structure across `organic`, `plastic`, `paper`), `CITATIONS.md`.
   - **Role 3 (ML Pipeline Engineer):** `train.py`, `evaluate.py`, `predict.py`, `requirements.txt`, model training, export of `waste_model.pth`, generation of `confusion_matrix.png`, `accuracy_curve.png`, `classification_report.txt` (accuracy $\ge 80\%$, target $\ge 85\%$).
3. The environment has all required toolchains (Python 3.12, Node 24, Flutter 3.41, Git 2.49). PyTorch CPU wheels are locally cached and ready for instant installation.

---

## 5. Verification Method

To verify the findings and analysis:

1. **Inspect Analysis Report:**
   - Path: `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\explorer_repo_1\analysis.md`
2. **Verify Toolchains & Cached Wheel on Host:**
   ```powershell
   python --version
   node --version
   flutter --version
   pip install --dry-run torch torchvision --index-url https://download.pytorch.org/whl/cpu
   ```
3. **Validate Day 1 Acceptance Criteria (Post-Worker Execution):**
   ```powershell
   # 1. Structure Check
   Test-Path D:\Ngoding\interviewWeb\BillcodeTech\backend\app\main.py
   Test-Path D:\Ngoding\interviewWeb\BillcodeTech\web\package.json
   Test-Path D:\Ngoding\interviewWeb\BillcodeTech\mobile\pubspec.yaml
   Test-Path D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\requirements.txt

   # 2. Dataset Image Count Check (>= 150 total, >= 50 per class)
   $trainOrg = (Get-ChildItem D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\dataset\train\organic -File).Count
   $trainPla = (Get-ChildItem D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\dataset\train\plastic -File).Count
   $trainPap = (Get-ChildItem D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\dataset\train\paper -File).Count
   $valOrg   = (Get-ChildItem D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\dataset\val\organic -File).Count
   $valPla   = (Get-ChildItem D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\dataset\val\plastic -File).Count
   $valPap   = (Get-ChildItem D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\dataset\val\paper -File).Count
   $total = $trainOrg + $trainPla + $trainPap + $valOrg + $valPla + $valPap
   Write-Host "Total images: $total"

   # 3. Model & Artifacts Check
   Test-Path D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\waste_model.pth
   Test-Path D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\confusion_matrix.png
   Test-Path D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\accuracy_curve.png
   Test-Path D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\classification_report.txt
   ```
