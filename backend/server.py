import os
import sys
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# Ensure project root is in sys.path for reliable module imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from .db import init_db
from .routes.auth_routes import router as auth_router
from .routes.session_routes import router as session_router
from .routes.ai_routes import router as ai_router
from .routes.materials_routes import router as materials_router
from .routes.vision_routes import router as vision_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AURA // AI Study Companion API",
    description="Backend API for real-time eye-tracking, study sessions, and Gemini AI tutoring.",
    version="2.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# SPAM PROTECTION & RATE LIMITING MIDDLEWARE
# In-memory sliding window rate-limiter per client IP
# ---------------------------------------------------------------------------
RATE_LIMIT_BUCKET = defaultdict(list)
MAX_REQUESTS_PER_MINUTE = 60
SENSITIVE_MAX_PER_MINUTE = 20  # For /api/ai/ and /api/auth/register


@app.middleware("http")
async def spam_protection_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "127.0.0.1"
    path = request.url.path
    now = time.time()

    # Apply stricter rate limits to AI and registration endpoints to stop spam & quota draining
    is_sensitive = path.startswith("/api/ai") or path.startswith("/api/auth/register")
    limit = SENSITIVE_MAX_PER_MINUTE if is_sensitive else MAX_REQUESTS_PER_MINUTE

    # Purge timestamps older than 60 seconds
    key = f"{client_ip}:{path.split('/')[2] if len(path.split('/')) > 2 else 'root'}"
    timestamps = [t for t in RATE_LIMIT_BUCKET[key] if now - t < 60.0]
    if timestamps:
        RATE_LIMIT_BUCKET[key] = timestamps
    elif key in RATE_LIMIT_BUCKET:
        del RATE_LIMIT_BUCKET[key]

    if len(timestamps) >= limit:
        return JSONResponse(
            status_code=429,
            content={
                "error": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. High-frequency telemetry/AI spam protection active. Please wait 60s.",
                "retry_after": 60,
            },
            headers={"Retry-After": "60"},
        )

    RATE_LIMIT_BUCKET[key].append(now)

    # Security & HTTPS Headers
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Enforce HSTS if running over HTTPS
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

    return response


# ---------------------------------------------------------------------------
# CORS CONFIGURATION
# ---------------------------------------------------------------------------
frontend_env = os.getenv("FRONTEND_URL", "")
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
if frontend_env:
    for url in frontend_env.split(","):
        clean_url = url.strip().rstrip("/")
        if clean_url and clean_url not in ALLOWED_ORIGINS:
            ALLOWED_ORIGINS.append(clean_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(auth_router)
app.include_router(session_router)
app.include_router(ai_router)
app.include_router(materials_router)
app.include_router(vision_router)





@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AURA_STUDY_BACKEND",
        "engine": "FASTAPI_SQLITE_POSTGRES",
        "spam_protection": "ACTIVE",
    }


# Serve built React frontend if dist directory exists
frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon_icon():
        fav_svg = frontend_dist / "favicon.svg"
        if fav_svg.is_file():
            return FileResponse(str(fav_svg), media_type="image/svg+xml")
        return Response(status_code=204)

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        # Don't intercept API routes
        if full_path.startswith("api"):
            return JSONResponse(status_code=404, content={"error": "API route not found"})
        target = frontend_dist / full_path
        if target.is_file():
            return FileResponse(str(target))
        return FileResponse(str(frontend_dist / "index.html"))
