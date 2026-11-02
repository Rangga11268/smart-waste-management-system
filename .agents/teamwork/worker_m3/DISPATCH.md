## 2026-11-02T09:38:13Z

You are worker_m3, a teamwork_worker subagent.
Your working directory: D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m3\
Project root: D:\Ngoding\interviewWeb\BillcodeTech

MANDATORY FIRST STEP:
Read:
1. D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\ORIGINAL_REQUEST.md (Day 2 requirement R4)
2. D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\orchestrator_2\PROJECT.md
3. D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\spec_miner_day2\handoff.md
4. D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\explorer_backend\handoff.md
5. D:\Ngoding\interviewWeb\BillcodeTech\tests\test_day2_predict.py
6. D:\Ngoding\interviewWeb\BillcodeTech\ml_pipeline\predict.py
7. docs/API_SPECS.md (Section 2: Prediction Endpoint)

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your Milestone Scope (M3: PyTorch ML Inference Integration & Static Media):
You will integrate the trained PyTorch MobileNetV2 model (`waste_model.pth` via `ml_pipeline/predict.py`) into the `POST /api/v1/predict` endpoint and configure static media uploads:

1. `backend/app/schemas/predict.py`:
   - Schema matching docs/API_SPECS.md Section 2:
     - `PredictResponseData`:
       - `category`: str (e.g. "Plastic Waste", "Organic Waste", "Paper Waste")
       - `confidence`: float (e.g. 0.9421)
       - `confidence_percentage`: str (e.g. "94.21%")
       - `category_id`: int (1 for Organic, 2 for Plastic, 3 for Paper)
       - `probabilities`: Dict[str, float] (normalized float probabilities across all 3 categories)
     - `PredictResponse`:
       - `status`: str = "success"
       - `data`: PredictResponseData

2. `backend/app/api/v1/predict.py`:
   - `POST /api/v1/predict` (support route at `""` and `"/"` under prefix `/api/v1/predict`):
     - Parameter: `file: UploadFile = File(...)`
     - Extension validation: Check `file.filename` extension. Allowed: `['.bmp', '.jpeg', '.jpg', '.png', '.webp']`. If not allowed, raise `HTTPException(status_code=400, detail="Unsupported image extension. Allowed: ['.bmp', '.jpeg', '.jpg', '.png', '.webp']")`.
     - Read bytes: `content = await file.read()`. If `len(content) == 0`: raise `HTTPException(status_code=400, detail="Corrupted or invalid image file")`.
     - Integrity check: Attempt opening image with `PIL.Image.open(io.BytesIO(content))`. Call `image.verify()`. If UnidentifiedImageError or exception, raise `HTTPException(status_code=400, detail="Corrupted or invalid image file")`.
     - Re-open image and convert to RGB (supports grayscale, RGBA, CMYK seamlessly).
     - Run inference using `WastePredictor`:
       - Import from `ml_pipeline.predict import get_default_predictor` (or singleton).
       - Call predictor: `result = predictor.predict_image(image)`.
       - Format response strictly matching `PredictResponse`.

3. Update `backend/app/main.py`:
   - Ensure upload folder `backend/uploads/reports` is created.
   - Mount static file serving:
     `app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")`
   - Include router:
     `app.include_router(predict_router, prefix=f"{settings.API_V1_STR}/predict", tags=["Prediction"])`

Verification:
- Execute `pytest tests/test_day2_predict.py -v`. All 14 tests in the test suite MUST pass!
- Execute `pytest tests/test_day2_auth.py tests/test_day2_db_fallback.py` to ensure zero regressions.

Write your report to `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m3\handoff.md`.
Follow Handoff Protocol. Send a message to your caller when done.
