"""
Records (log table) API routes.
"""

from typing import Optional
from fastapi import APIRouter, Query
from backend.services import records_service

router = APIRouter(prefix="/api/records", tags=["records"])


@router.get("")
def get_records(
    page:       int           = Query(1,   ge=1),
    page_size:  int           = Query(100, ge=1, le=500),
    label:      Optional[str] = Query(None),
    ip:         Optional[str] = Query(None),
    search:     Optional[str] = Query(None),
    sort_by:    str           = Query("timestamp"),
    sort_order: str           = Query("asc"),
):
    return records_service.get_records(
        page=page,
        page_size=page_size,
        label=label,
        ip=ip,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/columns")
def get_columns():
    return {"columns": records_service.get_record_columns()}
