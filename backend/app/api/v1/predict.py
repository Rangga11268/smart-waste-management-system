"""Machine Learning inference router for waste classification."""

import io
from pathlib import Path
import sys
from typing import Set

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from PIL import Image, UnidentifiedImageError

# Ensure project root is in sys.path for ml_pipeline imports
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ml_pipeline.predict import get_default_predictor

try:
    from app.schemas.predict import PredictResponse, PredictResponseData
except ImportError:
    from backend.app.schemas.predict import PredictResponse, PredictResponseData

router = APIRouter()

ALLOWED_EXTENSIONS: Set[str] = {".bmp", ".jpeg", ".jpg", ".png", ".webp"}


@router.post("", response_model=PredictResponse, summary="Predict waste category from image")
@router.post("/", response_model=PredictResponse, include_in_schema=False)
async def predict_waste(
    file: UploadFile = File(..., description="Multipart image file to classify"),
) -> PredictResponse:
    """Classify an uploaded waste evidence photo using PyTorch MobileNetV2.

    Validates file extension, byte integrity, and image headers.
    Converts all valid color spaces (L, RGBA, CMYK) to RGB before inference.
    """
    # 1. Extension validation
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported image extension. Allowed: ['.bmp', '.jpeg', '.jpg', '.png', '.webp']",
        )

    # 2. Read bytes & check empty payload
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Corrupted or invalid image file",
        )

    # 3. Integrity verification & mode normalization
    try:
        # Verify file structure
        img_verify = Image.open(io.BytesIO(content))
        img_verify.verify()

        # Reopen for actual image processing (verify destroys buffer pointers)
        image = Image.open(io.BytesIO(content))
        if image.mode != "RGB":
            image = image.convert("RGB")
    except (UnidentifiedImageError, OSError, Exception):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Corrupted or invalid image file",
        )

    # 4. Model inference via WastePredictor
    predictor = get_default_predictor()
    try:
        result = await run_in_threadpool(predictor.predict_image, image)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference execution failed: {str(exc)}",
        )

    return PredictResponse(
        status="success",
        data=PredictResponseData(**result),
    )
