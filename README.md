# ⚡ AURA — AI Deep Focus & Biometric Telemetry Study Companion

<div align="center">

![AURA Banner](https://img.shields.io/badge/AURA-Deep%20Focus%20Workstation-06b6d4?style=for-the-badge&logo=target&logoColor=white)

**An intelligent, privacy-first study workstation combining real-time in-browser gaze telemetry, native YOLOv8 smartphone distraction detection, RAG-powered Gemini AI tutoring, and SuperMemo SM-2 spaced repetition flashcards.**

[![React 19](https://img.shields.io/badge/React-19.2-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8.3-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-Flash%202.0-8E75B2?style=flat-square&logo=google&logoColor=white)](https://aistudio.google.com/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF?style=flat-square&logo=opencv&logoColor=black)](https://github.com/ultralytics/ultralytics)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-FaceMesh%20WASM-FF6F00?style=flat-square&logo=google&logoColor=white)](https://developers.google.com/mediapipe)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=flat-square&logo=supabase&logoColor=white)](https://supabase.com/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)

[Live Demo](#-cloud-deployment-architecture) • [Key Features](#-key-features) • [Tech Stack & Tools](#%EF%B8%8F-tools--technologies-used) • [Quickstart](#-local-quickstart) • [Environment Reference](#%EF%B8%8F-environment-variables-reference) • [Privacy & Security](#-privacy--security-by-design)

</div>

---

## 🌟 Overview

**AURA** is a full-stack, production-grade productivity platform engineered for students, researchers, and engineers who need deep, uninterrupted cognitive focus.

Unlike generic Pomodoro timers or cloud-monitored proctoring tools, AURA operates with an **edge-first biometric philosophy**: all computer vision processing (facial landmark triangulation, eye aspect ratio, and gaze direction) runs **100% locally in your browser via WebAssembly** or through an ephemeral local computer vision daemon. Your camera stream is never uploaded, recorded, or transmitted to any third-party server.

---

## 🛠️ Tools & Technologies Used

### **Frontend Client**
| Technology | Role / Purpose |
| :--- | :--- |
| **React 19** | Modern UI engine with latest asynchronous rendering and concurrent state management |
| **Vite 8** | Lightning-fast ESM build tool, bundling, and instant Hot Module Replacement (HMR) |
| **TailwindCSS 3.4** | Utility-first styling with custom cyber/obsidian dark mode, glow effects, and glassmorphism |
| **Framer Motion 13** | Smooth spring animations, HUD telemetry transitions, and 3D card flips |
| **MediaPipe FaceMesh WASM** | 468-point 3D facial landmark mesh computed directly on the client's GPU via WebAssembly |
| **Chart.js & React-Chartjs-2** | Interactive biometric focus and session historical trend visualizations |
| **Lucide Icons** | Clean, minimalist vector iconography |
| **Canvas Confetti** | Dynamic visual rewards upon completing focus sprints and flashcard mastery milestones |
| **Web Audio API** | Real-time synthetic multi-tone sound generator for soft focus nudges and sprint bells |

### **Backend & Machine Learning**
| Technology | Role / Purpose |
| :--- | :--- |
| **FastAPI** | High-throughput, async Python REST API with automatic OpenAPI / Swagger documentation |
| **Uvicorn** | Production ASGI server implementation with worker clustering support |
| **Ultralytics YOLOv8** | Neural object detection model (`yolov8n.pt`) fine-tuned for real-time mobile device identification |
| **OpenCV** | Optical matrix transformations, pupil triangulation, and video stream decoding |
| **SQLAlchemy 2.0** | Robust ORM for multi-dialect schema management (PostgreSQL & SQLite) |
| **Google GenAI SDK** | Direct integration with Google Gemini 2.0 Flash for RAG, Socratic tutoring, and quiz generation |
| **Document Parsers** | Multi-format extraction pipeline using `PyPDF2`, `python-docx`, `python-pptx`, and `openpyxl` |
| **JWT & Bcrypt** | Cryptographic session tokens (HS256) and salt-hashed password authentication |
| **Google Auth Library** | Server-side Google GIS ID token cryptographic signature verification |

### **Database & Infrastructure**
| Service / Platform | Role / Purpose |
| :--- | :--- |
| **Vercel** | Global Edge CDN hosting for the React SPA with automated SPA routing rewrites |
| **Render / Railway / Docker** | Containerized backend execution with automatic SSL and persistent storage |
| **Supabase (PostgreSQL)** | Cloud SQL database with PgBouncer transaction-mode connection pooling |
| **SQLite3** | Zero-configuration local development database with instant zero-setup fallback |

---

## ✨ Key Features

### 👁️ 1. Edge-First Biometric Telemetry & Gaze Tracking
* **MediaPipe FaceMesh (WASM)** calculates Eye Aspect Ratio (EAR), blink frequency, and head yaw/pitch/roll.
* **Gaze Orientation Engine**: Accurately classifies whether you are *Focused on Screen*, *Looking Away (Left/Right)*, or *Drowsy/Sleeping*.
* **Zero Video Leakage**: Video frames remain strictly inside client GPU/VRAM memory.

### 📱 2. YOLOv8 Smartphone Distraction Guard
* Neural object detection tracks physical smartphones (`class 67`) appearing in the camera workspace.
* **Smart Heuristics**: Differentiates between looking down at physical handwritten notebooks vs. holding up a smartphone to scroll social media.

### 🤖 3. Multi-Modal RAG AI Copilot (Google Gemini 2.0)
* **Document-Aware Knowledge Base**: Upload lecture PDFs, Word documents (`.docx`), PowerPoint slide decks (`.pptx`), Excel sheets (`.xlsx`), or raw text.
* **Specialized Learning Modes**:
  * 🧠 **Socratic Tutor**: Guides you with thought-provoking questions rather than just handing you the answer.
  * 🔬 **Deep Dive**: Breaks down complex theorems into intuitive mental models and real-world analogies.
  * 📝 **Exam Prep & Quiz Gen**: Generates practice questions with detailed explanations directly from uploaded course syllabi.
  * ⚡ **Flashcard Forge**: Instantly turns lecture slides into spaced repetition flashcard decks.

### 🗂️ 4. Active Recall & Spaced Repetition Flashcards (SuperMemo SM-2)
* Powered by the battle-tested **SuperMemo SM-2 algorithm** that calculates optimal review intervals ($I_n$) and ease factors ($EF$).
* Interactive 3D flip cards with rating buttons (*Again*, *Hard*, *Good*, *Easy*).
* Filter flashcard decks by subject, tags, or source document.

### ⏱️ 5. Sprint Engine & Adaptive Audio Workstation
* Presets for **Standard Pomodoro (25/5 min)**, **Deep Work (50/10 min)**, or custom sprint intervals.
* Synthesized ambient chimes and distraction audio alerts via the browser's native **Web Audio API** (no bulky audio assets required).
* Live **Focus Index Score (%)** calculated from session telemetry and uninterrupted sprint streaks.

### 📊 6. Analytics & Cognitive Protocols
* Time-series focus graphs (1-Day, 7-Day, 14-Day, 30-Day metrics).
* Interactive cheat-sheets for proven learning protocols: **Feynman Technique**, **Leitner Box**, **Active Recall**, and **Ultradian Rhythms**.

---

## 📁 Project Architecture

```
AI-Study-Companion/
├── backend/                       # FastAPI Backend Application
│   ├── server.py                  # Main entry point, CORS, Rate Limiting & routing
│   ├── db.py                      # SQLAlchemy ORM Models (User, Session, Flashcard, Material)
│   ├── auth.py                    # JWT token creation, validation & Bcrypt hashing
│   ├── config.py                  # Config loader & Supabase connection URL normalizer
│   └── routes/
│       ├── auth_routes.py         # Login, Registration, Google OAuth, Profile stats
│       ├── session_routes.py      # Sprint sessions & distraction event telemetry
│       ├── materials_routes.py    # Multi-format doc parsing, flashcards, link indexer
│       ├── ai_routes.py           # Gemini RAG chat, document indexing & offline fallback
│       └── vision_routes.py       # Camera diagnostics & YOLOv8 phone detection daemon
├── frontend/                      # React 19 + Vite Frontend SPA
│   ├── index.html                 # Branded dark HUD entry
│   ├── vercel.json                # Vercel SPA client rewrite & Mumbai region routing
│   ├── public/                    # Static assets & vector biometric HUD icons
│   └── src/
│       ├── components/
│       │   ├── auth/              # Google GIS One-Tap & email auth modals
│       │   ├── dashboard/         # HUD, CameraTracker, Timer, AI Studio, Analytics
│       │   ├── landing/           # Obsidian dark cyber landing page
│       │   └── ui/                # GlowBadge, TiltCard, BorderBeam, GlassPanel
│       └── lib/
│           ├── api.js             # Dynamic backend URL resolver & Axios client
│           ├── audio.js           # Web Audio API synthesizers for soft alerts & chimes
│           └── utils.js           # Class name merger utilities
├── src/                           # Core Domain Logic Modules
│   ├── ai_assistant.py            # Gemini RAG pipeline & vector keyword chunker
│   ├── focus_tracker.py           # OpenCV pupil analysis & YOLOv8 detector
│   └── study_materials.py         # Document parsers (PDF, DOCX, PPTX, XLSX)
├── Dockerfile                     # Production multi-stage Docker container
├── render.yaml                    # Render 1-click blueprint specification
├── main.py                        # Unified local development launcher
└── requirements.txt               # Backend dependencies
```

---

## 🚀 Local Quickstart

### 1. Prerequisites
* **Python**: `3.10`, `3.11`, or `3.12`
* **Node.js**: `18.x` or higher (`npm 9+`)
* **Google Gemini API Key**: Free tier available at [Google AI Studio](https://aistudio.google.com/app/apikey)
* **Google OAuth Client ID** *(Optional)*: From [Google Cloud Console](https://console.cloud.google.com)

---

### 2. Clone & Setup Environment

```bash
git clone https://github.com/Adithiya-S/AI-Study-Companion.git
cd AI-Study-Companion
```

Create a `.env` file in the root directory:

```env
# ----------------------------------------------------
# BACKEND CONFIGURATION
# ----------------------------------------------------
# Database: Uses SQLite automatically if left blank or set to sqlite:///data/study_companion.db
DATABASE_URL=sqlite:///data/study_companion.db

# Security: Generate with `openssl rand -hex 32` or any random string
JWT_SECRET=your_super_secret_jwt_key_here_min_32_chars

# AI Engine: Free key from https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Google OAuth 2.0 (Optional - allows 'Sign in with Google')
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com

# ----------------------------------------------------
# FRONTEND CONFIGURATION
# ----------------------------------------------------
VITE_GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
# For local dev, frontend defaults to http://localhost:8000
# VITE_API_URL=http://localhost:8000
```

---

### 3. Install Dependencies

#### Backend
```bash
# Optional: Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python requirements
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
cd ..
```

---

### 4. Run Development Servers

**Option A — Dual Terminals (Recommended for active dev):**

```bash
# Terminal 1: Start FastAPI Backend
python -m uvicorn backend.server:app --reload --port 8000

# Terminal 2: Start Vite Frontend
cd frontend
npm run dev
```

**Option B — Unified Launcher:**
```bash
python main.py
```

* 🖥️ **Web App**: [http://localhost:5173](http://localhost:5173)
* 📖 **Interactive API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
* 📊 **Redoc API Schema**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## ☁️ Cloud Deployment Architecture

Deploy in 3 simple steps:

```
[ Supabase PostgreSQL ] ◄── (Transaction Pooling) ──► [ Render Backend (FastAPI) ] ◄── (CORS API) ──► [ Vercel Frontend (React 19) ]
```

### Step 1: Database (Supabase)
1. Create a free project at [supabase.com](https://supabase.com).
2. Go to **Project Settings** ➔ **Database** ➔ **Connection string** ➔ **URI**.
3. Select **Mode: Transaction (Port 6543)** and copy the URI.
   > *Note: If your database password contains special characters like `@`, `%`, or `#`, URL-encode them (e.g., `@` becomes `%40`).*

### Step 2: Backend (Render or Railway)
1. In [render.com](https://render.com), create a **New Web Service** and connect your repo.
2. Select **Runtime: Docker** (or Python with start command: `uvicorn backend.server:app --host 0.0.0.0 --port $PORT`).
3. Add Environment Variables:
   * `DATABASE_URL`: *(Your Supabase connection string)*
   * `JWT_SECRET`: *(Random 32+ character string)*
   * `GEMINI_API_KEY`: *(Your Google AI Studio API key)*
   * `GOOGLE_CLIENT_ID`: *(Optional: Google OAuth Client ID)*
4. Deploy and copy the live URL (e.g. `https://aura-backend.onrender.com`).

### Step 3: Frontend (Vercel)
1. In [vercel.com](https://vercel.com), import your repository.
2. Set **Root Directory** to `frontend`.
3. Framework Preset will auto-detect as `Vite`.
4. Add Environment Variables:
   * `VITE_API_URL`: `https://aura-backend.onrender.com` *(Your Render URL without trailing slash)*
   * `VITE_GOOGLE_CLIENT_ID`: *(Your Google OAuth Client ID)*
5. Click **Deploy**.

---

## ⚙️ Environment Variables Reference

| Variable | Scope | Description | Default / Example |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | Backend | PostgreSQL / SQLite connection string | `sqlite:///data/study_companion.db` |
| `JWT_SECRET` | Backend | Secret key used to sign and verify HS256 JWT tokens | `min_32_chars_random_string` |
| `GEMINI_API_KEY` | Backend | Google AI Studio Gemini API Key | `AIzaSy...` |
| `GOOGLE_CLIENT_ID` | Backend | Google OAuth 2.0 Web Client ID for token verification | `xxx.apps.googleusercontent.com` |
| `VITE_API_URL` | Frontend | Target backend API base URL for production | `https://your-backend.onrender.com` |
| `VITE_GOOGLE_CLIENT_ID` | Frontend | Google OAuth 2.0 Client ID for frontend GIS button | `xxx.apps.googleusercontent.com` |

---

## 🔒 Privacy & Security by Design

* 🛡️ **Zero Camera Ingestion**: The backend never receives raw video feeds. All face mesh landmarks and pupil geometry are processed in-browser.
* 🛡️ **Ephemeral Object Diagnostics**: When local YOLOv8 diagnostics run, frames are processed in-memory and immediately destroyed.
* 🛡️ **Rate-Limiting Protection**: Sliding-window rate limiters prevent brute force on authentication and abuse on AI endpoints.
* 🛡️ **Sanitized Markdown**: All AI responses pass through sanitized AST renderers to prevent XSS attacks.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

<div align="center">
  <sub>Built for thinkers, builders, and lifelong learners. Elevate your focus with AURA.</sub>
</div>
