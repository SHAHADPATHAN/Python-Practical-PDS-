"""
PDS Log Intelligence — FastAPI Backend (Serving SPA + API)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from backend.api import dataset, eda, ips, model, practicals, records, upload

# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="PDS Log Intelligence API",
    description=(
        "Backend API for the PDS Log Analytics & Security Intelligence Dashboard.\n"
        "Serves results from all 10 data-science practicals."
    ),
    version="1.0.0",
)

# ─── CORS ────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────────────────────────────────

app.include_router(dataset.router)
app.include_router(eda.router)
app.include_router(ips.router)
app.include_router(model.router)
app.include_router(practicals.router)
app.include_router(records.router)
app.include_router(upload.router)


# ─── Health ───────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {
        "status": "online",
        "service": "PDS Log Intelligence API",
        "version": "1.0.0",
    }


# ─── Serve React frontend (built static files) ────────────────────────────────

FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(FRONTEND_DIST / "assets")),
        name="assets",
    )

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        """Serve React SPA for all non-API routes."""
        return FileResponse(str(FRONTEND_DIST / "index.html"))
