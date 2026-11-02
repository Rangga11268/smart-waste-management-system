# Milestone 3 Handoff: PyTorch ML Inference Integration & Static Media Serving

**Subagent**: `worker_m3`  
**Milestone**: M3 (PyTorch ML Inference Integration & Static Media)  
**Date**: 2026-11-02  
**Working Directory**: `D:\Ngoding\interviewWeb\BillcodeTech\.agents\teamwork\worker_m3\`  

---

## 1. Observation

1. **Pre-existing Codebase & Environment**:
   - `ml_pipeline/predict.py` provided `WastePredictor` which loads `waste_model.pth` and `class_to_idx.json`.
   - `tests/test_day2_predict.py` specified 14 tests across Tier 1 (JPEG, PNG, WebP inference, probability normalization, public and authenticated access) and Tier 2 (unsupported `.txt`, `.pdf` extensions, corrupt image bytes, empty 0-byte file, missing `file` multipart field, extreme 1x1 dimensions, large 1000x1000 dimensions, grayscale mode).
   - In `backend/app/main.py`, router stubs for predict were commented out, and `/uploads` static file mount was not yet established.
   - Database and auth regression suites were present at `tests/test_day2_auth.py` and `tests/test_day2_db_fallback.py`.

2. **Executed Changes**:
   - `backend/app/schemas/predict.py`: Created with Pydantic models `PredictResponseData` (fields: `category`, `confidence`, `confidence_percentage`, `category_id`, `probabilities`) and `PredictResponse` (`status="success"`, `data: PredictResponseData`).
   - `backend/app/schemas/__init__.py`: Re-exported `PredictResponse` and `PredictResponseData`.
   - `backend/app/api/v1/predict.py`: Implemented `POST /api/v1/predict` (handling both `""` and `"/"` paths):
     - Validates extension against `ALLOWED_EXTENSIONS = {'.bmp', '.jpeg', '.jpg', '.png', '.webp'}` (returns HTTP 400 if unsupported).
     - Validates content length > 0 (returns HTTP 400 if 0 bytes).
     - Validates image integrity via `PIL.Image.open(io.BytesIO(content)).verify()` (returns HTTP 400 on `UnidentifiedImageError` or corrupt stream).
     - Reopens image buffer and converts non-RGB images (`L`, `RGBA`, `CMYK`) to RGB.
     - Executes inference asynchronously via `run_in_threadpool(predictor.predict_image, image)`.
     - Returns enveloped `PredictResponse`.
   - `ml_pipeline/predict.py`: Added `predict_image = predict` method alias to `WastePredictor` class.
   - `backend/app/main.py`:
     - Imported `StaticFiles` from `fastapi.staticfiles`.
     - Ensured `backend/uploads/reports` directory is created.
     - Mounted static files serving at `/uploads` (`directory="backend/uploads"`).
     - Mounted `predict_router` with prefix `f"{settings.API_V1_STR}/predict"` and tags `["Prediction"]`.

3. **Verbatim Test Results**:
   - Command: `pytest tests/test_day2_predict.py -v`
     ```text
     tests/test_day2_predict.py::TestTier1PredictFeatureCoverage::test_predict_valid_jpeg_happy_path PASSED [  7%]
     tests/test_day2_predict.py::TestTier1PredictFeatureCoverage::test_predict_valid_png_image PASSED [ 14%]
     tests/test_day2_predict.py::TestTier1PredictFeatureCoverage::test_predict_valid_webp_image PASSED [ 21%]
     tests/test_day2_predict.py::TestTier1PredictFeatureCoverage::test_predict_probabilities_normalization_and_keys PASSED [ 28%]
     tests/test_day2_predict.py::TestTier1PredictFeatureCoverage::test_predict_public_accessibility_without_token PASSED [ 35%]
     tests/test_day2_predict.py::TestTier1PredictFeatureCoverage::test_predict_authenticated_accessibility_with_token PASSED [ 42%]
     tests/test_day2_predict.py::TestTier2PredictBoundaryAndCornerCases::test_predict_unsupported_extension_txt_rejected PASSED [ 50%]
     tests/test_day2_predict.py::TestTier2PredictBoundaryAndCornerCases::test_predict_unsupported_extension_pdf_rejected PASSED [ 57%]
     tests/test_day2_predict.py::TestTier2PredictBoundaryAndCornerCases::test_predict_corrupt_image_bytes_rejected PASSED [ 64%]
     tests/test_day2_predict.py::TestTier2PredictBoundaryAndCornerCases::test_predict_empty_file_zero_bytes_rejected PASSED [ 71%]
     tests/test_day2_predict.py::TestTier2PredictBoundaryAndCornerCases::test_predict_missing_file_form_field PASSED [ 78%]
     tests/test_day2_predict.py::TestTier2PredictBoundaryAndCornerCases::test_predict_extreme_small_dimension_1x1 PASSED [ 85%]
     tests/test_day2_predict.py::TestTier2PredictBoundaryAndCornerCases::test_predict_large_dimension_image PASSED [ 92%]
     tests/test_day2_predict.py::TestTier2PredictBoundaryAndCornerCases::test_predict_grayscale_mode_image PASSED [100%]
     ============================= 14 passed in 2.92s ==============================
     ```
   - Regression Command: `pytest tests/test_day2_auth.py tests/test_day2_db_fallback.py -v`
     ```text
     ============================= 30 passed in 21.88s =============================
     ```
   - Combined Command: `pytest tests/test_day2_predict.py tests/test_day2_auth.py tests/test_day2_db_fallback.py -v`
     ```text
     ============================= 44 passed in 26.52s =============================
     ```
   - Static Media Serving Test:
     Verified via `TestClient(app).get("/uploads/reports/test_static.txt")` returning status code `200` and body `"hello static"`.

---

## 2. Logic Chain

1. **Schema Compliance**:
   - `docs/API_SPECS.md` Section 2 requires an enveloped response `{"status": "success", "data": { ... }}` containing category, confidence (float), confidence_percentage (string), category_id (int), and probabilities (dictionary of float values summing to 1.0).
   - `backend/app/schemas/predict.py` implements this structure with strict Pydantic v2 validation.

2. **Validation and Error Handling**:
   - The test suite checks that uploading `.txt` or `.pdf` raises HTTP 400. The route inspects `Path(file.filename).suffix.lower()` against allowed image extensions and raises HTTP 400 with detail `"Unsupported image extension. Allowed: ['.bmp', '.jpeg', '.jpg', '.png', '.webp']"`.
   - The test suite checks that 0-byte uploads return HTTP 400 or 422. The route checks `len(content) == 0` and raises HTTP 400 with detail `"Corrupted or invalid image file"`.
   - For corrupt binary payloads, Pillow's `Image.open().verify()` detects invalid headers or truncated data and raises an exception caught by the handler, returning HTTP 400 with detail `"Corrupted or invalid image file"`.

3. **Color Mode Normalization**:
   - Grayscale (1-channel 'L') or RGBA/CMYK images cause shape mismatch errors in PyTorch's ImageNet normalization transforms if not converted.
   - The route checks `if image.mode != "RGB": image = image.convert("RGB")` before tensor transform, ensuring seamless handling of all color modes.

4. **Async Non-blocking Concurrency**:
   - PyTorch CPU inference on MobileNetV2 requires tensor normalization and matrix multiplications.
   - Executing `predictor.predict_image` inside `fastapi.concurrency.run_in_threadpool` prevents blocking the main asyncio event loop, preserving high API responsiveness.

5. **Static File Serving**:
   - Evidence photos submitted in waste reports must be served statically.
   - Mounting `app.mount("/uploads", StaticFiles(directory="backend/uploads"), name="uploads")` ensures any file placed in `backend/uploads/reports/` is immediately accessible over HTTP at `/uploads/reports/{filename}`.

---

## 3. Caveats

- **No Caveats**: The implementation strictly implements genuine PyTorch MobileNetV2 inference without dummy or mock responses. All 14 tests in `test_day2_predict.py` pass cleanly, and all 30 existing auth and fallback tests continue to pass with 0 regressions.

---

## 4. Conclusion

Milestone M3 is complete. The PyTorch MobileNetV2 waste classification model is fully integrated into the FastAPI backend at `POST /api/v1/predict` (supporting both `/api/v1/predict` and `/api/v1/predict/`), static media serving is mounted at `/uploads`, and all input validation and error boundaries adhere to `docs/API_SPECS.md`.

---

## 5. Verification Method

To independently verify this milestone:

1. **Verify Predict Endpoint Test Suite**:
   ```powershell
   cd D:\Ngoding\interviewWeb\BillcodeTech
   pytest tests/test_day2_predict.py -v
   ```
   *Expected outcome*: 14 passed in < 4s.

2. **Verify Regressions (Auth and Database Fallback)**:
   ```powershell
   cd D:\Ngoding\interviewWeb\BillcodeTech
   pytest tests/test_day2_auth.py tests/test_day2_db_fallback.py -v
   ```
   *Expected outcome*: 30 passed in ~22s.

3. **Verify Static File Serving**:
   ```powershell
   cd D:\Ngoding\interviewWeb\BillcodeTech
   python -c "import sys; sys.path.insert(0, 'backend'); from fastapi.testclient import TestClient; from app.main import app; from pathlib import Path; p = Path('backend/uploads/reports/test_verify.txt'); p.write_text('swms'); client = TestClient(app); r = client.get('/uploads/reports/test_verify.txt'); assert r.status_code == 200 and r.text == 'swms'; p.unlink(); print('Static files verified!')"
   ```
   *Expected outcome*: `"Static files verified!"` printed.
