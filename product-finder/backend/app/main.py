from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .database import SessionLocal, init_db
from .routers import auth, core, influencer
from .services.influencer_service import ensure_demo_user

STATIC_DIR = Path(__file__).resolve().parent / "static"
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Multi-marketplace product search, analytics dashboard, and influencer automation.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(core.router)
app.include_router(influencer.router)
app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    db = SessionLocal()
    try:
        ensure_demo_user(db)
    finally:
        db.close()


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/influencer")
def influencer_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "influencer.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "2.0.0"}
