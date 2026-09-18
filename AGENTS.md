# AI-Study-Companion: Agents & Architecture Guide

Welcome to the **AI-Study-Companion** (AURA) codebase. This document outlines the project architecture, design system, component guidelines, database workflows, deployment configuration, and developer conventions for AI agents and human contributors.

---

## 1. Project Overview & Design Philosophy

**AURA** is a full-stack, computer-vision-assisted study workstation engineered for high-cognition deep work. It integrates real-time browser-based eye tracking, native YOLOv8 phone distraction guarding, an adaptive Pomodoro sprint engine, a Gemini-powered lecture tutor, and longitudinal productivity analytics.

### Design Standard: "Dark Engineering Precision"
* **Zero Generic Glassmorphism**: Avoid blurry gradient blobs, milky frosted glass, and low-contrast pastel tropes.
* **Palette**: Deep matte obsidian (`#08090D`, `#0D0F15`), razor-sharp 1px micro-borders (`#1B1F2A`, `#262D3D`), dot-matrix / crosshair canvas overlays, and monospace telemetry (`JetBrains Mono`, `Geist Mono`).
* **Accents**: Electric Laser Cyan (`#00F2FE`), Focus Emerald (`#10B981`), Warning Amber (`#F59E0B`), and Alert Crimson (`#EF4444`).
* **Motion Design**: Powered by **Framer Motion** with spring damping, glowing keyline border beams, and tactile hover states.

---

## 2. Technology Stack

### Frontend Stack
* **Framework**: React 19 + Vite 6
* **Hosting**: Vercel (Region: Mumbai `bom1`, configured in `frontend/vercel.json`)
* **Styling**: Tailwind CSS (Tailwind v3/v4 with custom engineering design tokens)
* **Animation**: Framer Motion
* **Icons**: Lucide React
* **Charts**: Chart.js & `react-chartjs-2`
* **Audio**: Native Web Audio API synthesized frequencies (no external audio assets)
* **Computer Vision**: In-browser `@mediapipe/face_mesh` via WebAssembly

### Backend Stack
* **API Framework**: FastAPI + Uvicorn
* **Hosting**: Render (Region: Singapore via Docker) or Railway
* **Database**: Managed PostgreSQL on Supabase (`ap-south-1` Mumbai) via connection pooling (`port 6543`) with automatic fallback to local SQLite
* **ORM**: SQLAlchemy 2.0 with `psycopg2-binary`
* **AI Engine**: Google Gemini API (`google-genai` SDK v2+, supporting Gemini Flash models)
* **Object Detection**: Ultralytics YOLOv8 nano (`yolov8n.pt`, COCO class 67 for smartphones)
* **Document Parsing**: `PyPDF2`, `python-docx`, `python-pptx`, `openpyxl`

---

## 3. Repository Layout

```
AI-Study-Companion/
├── AGENTS.md                         # Architecture, developer conventions, and AI agent guide
├── README.md                         # Public documentation and setup guide
├── requirements.txt                  # Python dependencies (FastAPI, PyTorch, YOLOv8, psycopg2)
├── Dockerfile                        # Multi-stage production container for Render/Railway
├── render.yaml                       # Render 1-click blueprint specification
├── main.py                           # Master launcher for local execution
│
├── backend/                          # FastAPI application
│   ├── server.py                     # API routing, CORS preflights, rate limiting middleware
│   ├── db.py                         # SQLAlchemy models (User, StudySession, Flashcard, etc.)
│   ├── auth.py                       # Bcrypt password hashing & JWT token verification
│   ├── config.py                     # Env loading & PostgreSQL sslmode normalization
│   └── routes/
│       ├── auth_routes.py            # Registration, login, Google OAuth, user stats
│       ├── session_routes.py         # Study sprint lifecycle & distraction logging
│       ├── materials_routes.py       # Multi-format document upload, flashcards, links
│       ├── ai_routes.py              # Gemini chat, session persistence, offline copilot
│       └── vision_routes.py          # Telemetry status & YOLOv8 phone detection
│
├── frontend/                         # React 19 + Vite client application
│   ├── index.html                    # Branded dark HUD entry point
│   ├── vercel.json                   # Vercel SPA client rewrites & Mumbai region (bom1)
│   ├── vite.config.js                # Vite build and proxy configuration
│   ├── public/                       # Static public assets (favicon.svg, robots.txt)
│   └── src/
│       ├── components/
│       │   ├── auth/                 # Google Identity Services & email login
│       │   ├── dashboard/            # Workstation tabs (HUD, Timer, AI Studio, Analytics)
│       │   ├── landing/              # Obsidian dark engineering landing page
│       │   └── ui/                   # Shared motion components (GlowBadge, TiltCard, BorderBeam)
│       └── lib/
│           ├── api.js                # Dynamic backend URL resolver (VITE_API_URL support)
│           ├── audio.js              # Synthesized Web Audio API sound generator
│           └── utils.js              # Class name merging helper (clsx + tailwind-merge)
│
└── src/                              # Domain logic modules
    ├── ai_assistant.py               # Gemini RAG document indexing & prompt engineering
    ├── focus_tracker.py              # YOLOv8 object detection & EAR calculations
    └── study_materials.py            # Multi-format file parsing & extraction
```

---

## 4. Environment Variables Specification

All sensitive configuration is decoupled into environment variables:

| Variable | Scope | Description |
|---|---|---|
| `DATABASE_URL` | Backend | PostgreSQL connection string (Supabase) or SQLite URI |
| `JWT_SECRET` | Backend | Cryptographic secret for signing session JWT tokens |
| `GEMINI_API_KEY` | Backend | Google Gemini API key (optional server-wide default) |
| `GOOGLE_CLIENT_ID` | Backend | Google OAuth 2.0 Web Client ID for backend token validation |
| `VITE_GOOGLE_CLIENT_ID` | Frontend | Google OAuth 2.0 Web Client ID for Google Identity Services |
| `VITE_API_URL` | Frontend | Base URL of deployed FastAPI backend on Render |
| `FRONTEND_URL` | Backend | Allowed CORS origin for production frontend on Vercel |
| `PORT` | Backend | HTTP listening port (defaults to 8000 or 10000 on Render) |
| `ENVIRONMENT` | Backend | `development` or `production` |

---

## 5. Key Engineering Conventions

### Frontend Conventions
1. **API Calls**: Always use the `apiUrl(path)` helper from `frontend/src/lib/api.js` rather than hardcoding relative or absolute URLs.
2. **Icons**: Exclusively use `lucide-react`. Prune unused icon imports.
3. **Sound**: Trigger audio using `sounds` from `frontend/src/lib/audio.js`. Never introduce heavy external `.mp3` or `.wav` assets into source control.
4. **Camera & Vision**: Keep camera stream processing client-side inside `CameraTracker.jsx` via MediaPipe FaceMesh to maintain zero-latency responsiveness and total user privacy.

### Backend Conventions
1. **Database Schema**: All models in `backend/db.py` must maintain primary key indices. When deploying to remote PostgreSQL (Supabase), ensure `sslmode=require` is preserved in `backend/config.py`.
2. **Headless Linux Compatibility**: Cloud Linux containers cannot load desktop X11 / OpenGL libraries. Always use `opencv-python-headless` alongside system `libgl1` in the Dockerfile.
3. **YOLO Model Caching**: Do not track `yolov8n.pt` in Git (ignored by `.gitignore`). The Dockerfile automatically downloads and bakes official weights into the container image during build.
