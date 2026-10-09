"""
ML model API routes.
"""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services import ml_service

router = APIRouter(prefix="/api/model", tags=["model"])


class PredictRequest(BaseModel):
    features: Dict[str, Any]


@router.get("/info")
def model_info():
    return ml_service.get_model_info()


@router.post("/predict")
def predict(request: PredictRequest):
    result = ml_service.predict(request.features)
    if "error" in result and not result.get("available", True):
        raise HTTPException(status_code=422, detail=result["error"])
    return result
