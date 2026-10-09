"""
Practicals and reports API routes.
"""

from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import FileResponse

from backend.services import report_service
from backend.utils import paths

router = APIRouter(prefix="/api", tags=["practicals"])


@router.get("/practicals")
def list_practicals():
    return report_service.get_all_practicals()


@router.get("/practicals/{pid}")
def get_practical(pid: int = Path(..., ge=1, le=10)):
    p = report_service.get_practical(pid)
    if not p:
        raise HTTPException(status_code=404, detail=f"Practical {pid} not found")
    return p


@router.get("/reports")
def list_reports():
    return report_service.get_all_reports()


@router.get("/reports/{key}")
def get_report(key: str):
    r = report_service.get_report(key)
    if not r:
        raise HTTPException(status_code=404, detail=f"Report '{key}' not found")
    return r


@router.get("/figures/{name}")
def get_figure(name: str):
    if name not in paths.FIGURES:
        raise HTTPException(status_code=404, detail=f"Figure '{name}' not found")
    fig_path = paths.FIGURES[name]
    if not fig_path.exists():
        raise HTTPException(status_code=404, detail=f"Figure file not found")
    return FileResponse(fig_path, media_type="image/png")
