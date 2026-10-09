"""
Upload API route.
"""

import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from backend.pipeline.upload_pipeline import analyze_upload
from backend.utils import paths, cache

router = APIRouter(prefix="/api/upload", tags=["upload"])

# Max upload size: 500 MB
MAX_SIZE_BYTES = 500 * 1024 * 1024


@router.post("")
async def upload_log(
    file: UploadFile = File(...),
    parser_hint: str  = Form(None),
):
    # Validate extension
    allowed_extensions = {".log", ".txt", ".csv", ".json", ".jsonl"}
    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{suffix}'. "
                   f"Allowed: {', '.join(allowed_extensions)}",
        )

    # Save to uploads dir
    safe_name = f"{uuid.uuid4()}{suffix}"
    dest = paths.UPLOAD_DIR / safe_name

    try:
        with dest.open("wb") as out:
            chunk_size = 1024 * 1024  # 1 MB
            total_written = 0
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                total_written += len(chunk)
                if total_written > MAX_SIZE_BYTES:
                    dest.unlink(missing_ok=True)
                    raise HTTPException(
                        status_code=413,
                        detail="File too large (max 500 MB)",
                    )
                out.write(chunk)
    except HTTPException:
        raise
    except Exception as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}")

    # Analyse
    try:
        result = analyze_upload(
            file_path=dest,
            parser_hint=parser_hint or None,
        )
    except Exception as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")
    finally:
        # Clean up uploaded file
        dest.unlink(missing_ok=True)

    # Cache upload result for subsequent requests
    cache.set("last_upload_result", result)

    return result


@router.get("/last")
def get_last_upload():
    result = cache.get("last_upload_result")
    if result is None:
        raise HTTPException(status_code=404, detail="No recent upload found")
    return result
