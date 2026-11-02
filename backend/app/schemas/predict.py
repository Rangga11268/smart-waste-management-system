"""Pydantic schemas for machine learning prediction endpoint."""

from typing import Dict
from pydantic import BaseModel, Field


class PredictResponseData(BaseModel):
    """Prediction result data payload."""

    category: str = Field(..., description="Predicted waste category name")
    confidence: float = Field(..., description="Model confidence score between 0.0 and 1.0")
    confidence_percentage: str = Field(..., description="Formatted confidence percentage string")
    category_id: int = Field(..., description="Relational category identifier (1: Organic, 2: Plastic, 3: Paper)")
    probabilities: Dict[str, float] = Field(..., description="Probability distribution across all categories")


class PredictResponse(BaseModel):
    """Enveloped response for POST /api/v1/predict."""

    status: str = Field("success", description="Status indicator")
    data: PredictResponseData
