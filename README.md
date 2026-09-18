# AURA // AI Deep Focus & Biometric Telemetry Study Companion

A high-precision study productivity workstation combining real-time in-browser eye tracking, native YOLOv8 smartphone distraction detection, an adaptive Pomodoro engine, multi-modal Google Gemini AI tutoring, active recall flashcards, and live biometric analytics.

---

## 🏗️ Architecture & Cloud Infrastructure

AURA is engineered for hybrid cloud and local-first execution:

* **Frontend**: React 19 + Vite SPA with TailwindCSS, Framer Motion, and MediaPipe FaceMesh WASM. Hosted globally on **Vercel** with regional edge routing in **Mumbai (`bom1`)**.
* **Backend**: FastAPI + Uvicorn with native YOLOv8 nano phone detection and document RAG pipelines. Hosted on **Render** (Singapore) or **Railway** via Docker.
* **Database**: Managed PostgreSQL on **Supabase** (South Asia / Mumbai `ap-south-1`) via connection pooling (port 6543) with automatic fallback to local SQLite.
* **AI Engine**: Google Gemini API (`google-genai` SDK v2+, supporting Gemini Flash models).

```
AI-Study-Companion/
├── backend/                       # FastAPI backend
│   ├── server.py                  # API endpoints, CORS, sliding-window rate limiting
│   ├── db.py                      # SQLAlchemy models (User, StudySession, Flashcard, etc.)
│   ├── auth.py                    # Bcrypt hashing & JWT token creation
│   ├── config.py                  # Environment config & database URL normalization
│   └── routes/
│       ├── auth_routes.py         # Registration, login, Google OAuth, user stats
│       ├── session_routes.py      # Session lifecycle & distraction logging
│       ├── materials_routes.py    # Multi-format document upload, flashcards, links
│       ├── ai_routes.py           # Gemini chat, session history, offline copilot
│       └── vision_routes.py       # Telemetry status & YOLOv8 phone detection
├── frontend/                      # React 19 + Vite client application
│   ├── index.html                 # Branded dark HUD entry
│   ├── vercel.json                # Vercel SPA client rewrite & Mumbai region (bom1)
│   ├── public/
│   │   └── favicon.svg            # Vector cyan biometric crosshair icon
│   └── src/
│       ├── components/
│       │   ├── auth/              # Google GIS & email auth
│       │   ├── dashboard/         # Biometric HUD, Timer, AI Studio, Analytics
│       │   ├── landing/           # Obsidian dark engineering landing page
│       │   └── ui/                # GlowBadge, TiltCard, BorderBeam
│       └── lib/
│           ├── api.js             # Dynamic backend URL resolver
│           ├── audio.js           # Web Audio API alert synthesizers
│           └── utils.js           # Class name utility helpers
├── src/                           # Domain logic modules
│   ├── ai_assistant.py            # Gemini RAG & document indexing
│   ├── focus_tracker.py           # YOLOv8 object detection & OpenCV heuristics
│   └── study_materials.py         # Document parsers (PDF, DOCX, PPTX, XLSX)
├── Dockerfile                     # Multi-stage production container for Render/Railway
├── render.yaml                    # Render 1-click blueprint specification
├── main.py                        # Unified local launcher
└── requirements.txt               # Backend dependencies (FastAPI, PyTorch, YOLOv8)
```

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites
* **Python 3.10 – 3.12**
* **Node.js 18+**
* **Google Gemini API Key** (Free tier at [Google AI Studio](https://aistudio.google.com/app/apikey))
* **Google OAuth 2.0 Client ID** (Optional, from [Google Cloud Console](https://console.cloud.google.com))

### 2. Configure Environment (`.env`)
Create a `.env` file in the project root:
```env
# Database (defaults to local SQLite if blank)
DATABASE_URL=sqlite:///data/study_companion.db

# JWT & Authentication
JWT_SECRET=your_32_character_random_secret_here

# Google Gemini AI Key
GEMINI_API_KEY=your_gemini_api_key_here

# Google OAuth 2.0 (Optional)
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
VITE_GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
```

### 3. Install Dependencies
```bash
# Backend dependencies
pip install -r requirements.txt

# Frontend dependencies
cd frontend && npm install && cd ..
```

### 4. Run Development Servers
**Terminal 1 — Backend (FastAPI + hot-reload):**
```bash
python -m uvicorn backend.server:app --reload --port 8000
```

**Terminal 2 — Frontend (Vite HMR):**
```bash
cd frontend && npm run dev
```

* Frontend: `http://localhost:5173`
* Backend API & Docs: `http://localhost:8000/docs`

---

## ☁️ Cloud Deployment Guide

Deploy in order: **1. Supabase (DB)** ➔ **2. Render / Railway (Backend)** ➔ **3. Vercel (Frontend)**.

### Step 1: Supabase (PostgreSQL Database)
1. Create a project at [supabase.com](https://supabase.com) in region **South Asia (Mumbai) - `ap-south-1`**.
2. Go to **Project Settings** ➔ **Database** ➔ **Connection String** ➔ **URI** (Mode: Transaction, Port: 6543).
3. Copy the URI (remember to percent-encode any special characters in the password, e.g. `@` as `%40`).

### Step 2: Render (Backend Web Service)
1. In [render.com](https://render.com), click **New +** ➔ **Web Service** and link your GitHub repository.
2. Select **Runtime: Docker** (or Python).
3. Configure Environment Variables:
   * `DATABASE_URL` = *(Your Supabase connection string)*
   * `JWT_SECRET` = *(Random 32+ character string)*
   * `GEMINI_API_KEY` = *(Your Google AI Studio API key)*
   * `GOOGLE_CLIENT_ID` = *(Your Google Client ID)*
4. Deploy and copy your live service URL (e.g. `https://aura-study-backend.onrender.com`).

### Step 3: Vercel (Frontend SPA)
1. In [vercel.com](https://vercel.com), import your repository.
2. Set **Root Directory** to `frontend`.
3. Framework Preset: `Vite` (auto-detected).
4. Add Environment Variables:
   * `VITE_API_URL` = *(Your Render backend URL, e.g. `https://aura-study-backend.onrender.com`)*
   * `VITE_GOOGLE_CLIENT_ID` = *(Your Google Client ID)*
5. Click **Deploy**.

---

## ✨ Features

### 👁️ Biometric Eye Tracking & Telemetry HUD
* In-browser MediaPipe FaceMesh (WASM) monitors Eye Aspect Ratio (EAR) and head yaw/pitch.
* Real-time gaze orientation classification (Focused, Looking Left, Looking Right, Eyes Closed/Drowsy).
* Zero latency client-side execution with zero video transmission to servers for complete privacy.

### 📱 Native YOLOv8 Phone Distraction Guard
* Background neural network detects physical cell phones (`class 67`) in the camera frame.
* Distinguishes between reading physical notebooks/textbooks vs. looking at smartphone screens.

### ⏱️ Sprint Workstation & Adaptive Audio
* Structured Pomodoro (25/5 min) and Deep Work (50/10 min) sprint intervals.
* Synthesized Web Audio API chimes for distraction warnings and sprint completions.

### 📚 Study Materials & Spaced Repetition Flashcards
* Multi-format document parser supporting PDF, Word DOCX, PowerPoint PPTX, Excel XLSX, and text files.
* Interactive 3D flip flashcards powered by the SuperMemo SM-2 spaced repetition algorithm.
* AI auto-generation of flashcards directly from lecture slides.

### 📊 Deep Analytics & Cognitive Protocols
* Historical trend visualizations (1D, 7D, 14D, 30D) using Chart.js.
* Cognitive protocols guide (Feynman Technique, Leitner Box Spaced Repetition, Active Recall).

---

## 🔒 Security & Privacy

* **Zero Camera Stream Storage**: Camera frames are processed strictly in-browser via WebAssembly and ephemeral memory.
* **Rate Limiting & Anti-Spam**: In-memory sliding window rate limiting on sensitive telemetry and authentication endpoints.
* **JWT Cryptography**: User sessions are signed with cryptographically secure HS256 JWT tokens.

---

## 📄 License

MIT License. Designed for high-cognition deep work.
