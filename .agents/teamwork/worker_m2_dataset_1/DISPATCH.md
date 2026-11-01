# Dispatch: Worker M2 (Dataset Collection & Curation)

## Objective
Download and curate a real, genuine dataset of at least 150 images across three categories: Organic Waste, Plastic Waste, and Paper Waste (minimum 50 images per category, recommended 70/class = 210 total) from public sources. Organize the dataset with an 80% training and 20% validation/testing split (`train/` and `val/`), and document data source citations in `CITATIONS.md`.

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Working Directory
`D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m2_dataset_1`

## Inputs
- `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\ORIGINAL_REQUEST.md`
- `D:\Ngoding\interviewWeb\BillcodeTech\PROJECT.md`
- `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\explorer_env_1\analysis.md` (Contains HuggingFace Mostafa Abla 12-class dataset details and direct download script template)

## File Ownership
- Exclusively owns:
  - `D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\dataset/**`
  - `D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\download_dataset.py`
  - `D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\dataset\CITATIONS.md`
- DO NOT touch or write to `backend/`, `web/`, `mobile/`, `tests/`, or root files.

## Instructions
1. Review `explorer_env_1`'s dataset findings. The Mostafa Abla 12-Class Garbage Classification dataset on HuggingFace contains:
   - `paper`: 1,050 images
   - `plastic`: 865 images
   - `biological` (Organic waste): 985 images
2. Implement a robust download and curation script `ml_pipeline/download_dataset.py` that:
   - Downloads or streams the zip file from the verified URL (`https://huggingface.co/datasets/UdaraChamidu/Garbage-Classification-with-12-classes/resolve/main/garbage_classification.zip` or open mirror).
   - Extracts genuine images: minimum 50 per class (recommended 70 per class: 56 train, 14 val).
   - Validates that each image is a genuine, non-corrupted RGB image using Pillow.
   - Saves into directory hierarchy:
     - `ml_pipeline/dataset/train/organic/` (>=40 images)
     - `ml_pipeline/dataset/train/plastic/` (>=40 images)
     - `ml_pipeline/dataset/train/paper/` (>=40 images)
     - `ml_pipeline/dataset/val/organic/` (>=10 images)
     - `ml_pipeline/dataset/val/plastic/` (>=10 images)
     - `ml_pipeline/dataset/val/paper/` (>=10 images)
3. Execute `python ml_pipeline/download_dataset.py` to curate the dataset on disk.
4. Author `ml_pipeline/dataset/CITATIONS.md` documenting:
   - Dataset name, authors, publication/source URL.
   - Licensing (e.g. CC-BY / Open Source).
   - Category mapping rationale (`biological` -> `organic`).
   - Image distribution table (counts per category and split).
5. Verify that all image files are non-empty and valid.
6. Write your report to `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m2_dataset_1\handoff.md` and send a message to orchestrator (`2fb3c008-4b2b-4b9e-88d9-91a9473b651c`).

## 2026-11-01T12:22:20Z
From: 2fb3c008-4b2b-4b9e-88d9-91a9473b651c
Priority: MESSAGE_PRIORITY_HIGH
Content:
You are teamwork_worker_m2_dataset_1.
Working directory: D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m2_dataset_1
Read D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\ORIGINAL_REQUEST.md and the dispatch instructions at D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m2_dataset_1\DISPATCH.md.
Also read D:\Ngoding\interviewWeb\BillcodeTech\PROJECT.md and D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\explorer_env_1\analysis.md.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Download and curate >=150 real waste images across organic, plastic, and paper (>=50/class) with 80/20 train/val split into ml_pipeline/dataset/ and write CITATIONS.md.
Write your completion handoff to D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m2_dataset_1\handoff.md.
When finished, send a message to orchestrator (conversation ID: 2fb3c008-4b2b-4b9e-88d9-91a9473b651c) with a summary.
