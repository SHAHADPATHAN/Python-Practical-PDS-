"""
Dataset and summary API routes.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.services import dataset_service

router = APIRouter(prefix="/api/dataset", tags=["dataset"])


@router.get("/summary")
def dataset_summary():
    return dataset_service.get_dataset_summary()


@router.get("/labels")
def label_distribution():
    return dataset_service.get_label_distribution()


@router.get("/scanners")
def scanner_breakdown():
    return dataset_service.get_scanner_breakdown()
