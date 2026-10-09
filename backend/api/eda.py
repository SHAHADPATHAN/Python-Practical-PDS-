"""
EDA API routes.
"""

from fastapi import APIRouter
from backend.services import eda_service

router = APIRouter(prefix="/api/eda", tags=["eda"])


@router.get("/summary")
def eda_summary():
    return eda_service.get_eda_summary()


@router.get("/hourly")
def hourly_activity():
    return eda_service.get_hourly_activity()


@router.get("/requests-by-hour")
def requests_by_hour():
    return eda_service.get_requests_by_hour()


@router.get("/top-ips")
def top_ips():
    return eda_service.get_top_ips_eda()


@router.get("/top-scanner-ips")
def top_scanner_ips():
    return eda_service.get_top_scanner_ips()


@router.get("/heatmap")
def heatmap():
    return eda_service.get_hourly_heatmap_matrix()
