"""
IP intelligence API routes.
"""

from typing import Optional
from fastapi import APIRouter, Query
from backend.services import ip_service

router = APIRouter(prefix="/api/ips", tags=["ips"])


@router.get("")
def list_ips(
    page:       int            = Query(1,    ge=1),
    page_size:  int            = Query(50,   ge=1, le=500),
    label:      Optional[str]  = Query(None),
    sort_by:    str            = Query("request_count"),
    sort_order: str            = Query("desc"),
    search:     Optional[str]  = Query(None),
):
    return ip_service.get_ip_list(
        page=page,
        page_size=page_size,
        label=label,
        sort_by=sort_by,
        sort_order=sort_order,
        search=search,
    )


@router.get("/top")
def top_ips(n: int = Query(10, ge=1, le=100)):
    return ip_service.get_top_ips(n)


@router.get("/{ip}")
def ip_detail(ip: str):
    detail = ip_service.get_ip_detail(ip)
    if detail is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"IP {ip} not found")
    return detail
