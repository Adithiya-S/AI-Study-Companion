# AURA — AI Deep Focus & Biometric Telemetry Companion

A full-stack AI-powered study productivity platform with real-time browser-based eye tracking, biometric focus scoring, adaptive Pomodoro timers, Gemini AI tutoring, flashcards, and live session analytics.

## 🏗️ Architecture

```
AI-Study-Companion/
├── backend/              # FastAPI + SQLAlchemy (SQLite)
│   ├── server.py         # App entry, CORS, rate limiting
│   ├── db.py             # SQLAlchemy models
│   ├── auth.py           # JWT + bcrypt
│   ├── config.py         # Env config
│   └── routes/
│       ├── auth_routes.py       # Register, login, Google OAuth, stats
│       ├── session_routes.py    # Start/end sessions, analytics
│       ├── materials_routes.py  # File upload, flashcards, RAG
│       ├── ai_routes.py         # Gemini AI chat
│       └── vision_routes.py     # Eye tracking vision helpers
├── frontend/             # React 19 + Vite + TailwindCSS
│   └── src/
│       ├── components/
│       │   ├── dashboard/       # Full workspace UI
│       │   ├── landing/         # Public landing page
│       │   ├── auth/            # Login / register
│       │   └── ui/              # Shared design components
│       └── lib/                 # Audio, utilities
├── data/                 # SQLite DB + uploaded study files
├── main.py               # Convenience launcher
└── requirements.txt      # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- **Python 3.11** (recommended) — 3.8–3.12 supported
- **Node.js 18+**
- **Google Gemini API key** — free at [aistudio.google.com](https://aistudio.google.com/app/apikey)
- **Google OAuth Client ID** — free at [console.cloud.google.com](https://console.cloud.google.com)

### 1. Clone & Configure Environment

```bash
git clone <repo-url>
cd AI-Study-Companion

# Copy and fill in your keys
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=sqlite:///data/study_companion.db
JWT_SECRET=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
GEMINI_API_KEY=your_gemini_api_key_here
ENVIRONMENT=development
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 4. Run (Development — Two Terminals)

**Terminal 1 — Backend (FastAPI + hot-reload):**
```bash
python -m uvicorn backend.server:app --reload --port 8000
```

**Terminal 2 — Frontend (Vite HMR):**
```bash
cd frontend && npm run dev
```

Open **http://localhost:5173** in your browser.

### Run as Single Process (Production / Quick Launch)

Build the frontend first, then serve everything from FastAPI:
```bash
cd frontend && npm run build && cd ..
python main.py
```

Opens **http://127.0.0.1:8000** automatically in your browser.

---

## ✨ Features

### 👁️ Real-Time Biometric Eye Tracking
- MediaPipe Face Mesh in-browser (WASM) — no Python camera dependency
- Eye Aspect Ratio (EAR) blink and closure detection
- Gaze direction and iris tracking
- Live focus score (0–100%) computed per frame

### ⏱️ Adaptive Study Timer
- **Pomodoro** (25 min), **Deep Work** (50 min), **Break** (5 min) modes
- Session start/end synced to backend DB automatically
- Live distraction logging during active sessions
- Confetti + audio on completion

### 📊 Session Analytics
- Per-user live dashboard: total hours, sessions, avg focus score, streak
- Period filter: 1D / 7D / 14D / 30D
- Bar chart: study time distribution by day or time-of-day
- Line chart: focus score trend across sessions
- Full session history table with CSV export

### 🤖 Gemini AI Study Tutor
- **Internet mode**: general knowledge questions via Gemini 2.0 Flash
- **Materials mode**: RAG over your uploaded documents (PDF, DOCX, PPTX, XLSX, TXT)
- Persistent chat history per tab session
- Markdown rendering with syntax highlighting

### 📚 Materials & Flashcards
- Upload study documents → indexed for AI tutor context
- Create, shuffle, flip, and master flashcards
- AI auto-generate flashcards from your uploaded materials
- Quick-link bookmarks for study resources

### 🔐 Authentication
- Email + password register/login (bcrypt + JWT)
- Google OAuth one-click sign-in (Google Identity Services)
- All data is user-scoped and isolated

---

## ⚙️ Configuration

### Environment Variables (`.env`)

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///data/study_companion.db` |
| `JWT_SECRET` | Secret for signing JWT tokens | *(required)* |
| `GEMINI_API_KEY` | Google Gemini AI key | *(required)* |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | *(set in frontend config)* |
| `ENVIRONMENT` | `development` or `production` | `development` |

### Focus Sensitivity
Configurable per-user from the **Configuration** tab in the workspace:
- **High** — strict distraction detection (best for distraction-prone environments)
- **Medium** — balanced (default)
- **Low** — lenient (useful for reading or note-taking)

---

## 📦 Tech Stack

### Backend
| Package | Purpose |
|---|---|
| `fastapi` | REST API framework |
| `uvicorn` | ASGI server |
| `sqlalchemy` | ORM + SQLite |
| `google-genai` | Gemini 2.0 Flash AI |
| `google-auth` | Google OAuth token verification |
| `python-multipart` | File upload handling |
| `PyPDF2` / `python-docx` / `python-pptx` / `openpyxl` | Document parsing for RAG |
| `opencv-python` / `mediapipe` / `numpy` | Vision helpers (backend-side) |

### Frontend
| Package | Purpose |
|---|---|
| `react 19` | UI framework |
| `vite` | Build tool + HMR dev server |
| `tailwindcss` | Utility CSS |
| `framer-motion` | Animations |
| `chart.js` + `react-chartjs-2` | Analytics charts |
| `@mediapipe/face_mesh` | In-browser eye tracking (WASM) |
| `react-markdown` + `remark-gfm` | AI response rendering |
| `lucide-react` | Icon set |
| `canvas-confetti` | Session completion celebration |

---

## 🔍 Troubleshooting

**Camera not working in browser:**
- Grant camera permission when prompted
- Ensure no other app is using the webcam
- Use HTTPS or `localhost` — browser blocks camera on plain HTTP remote URLs

**Backend won't start:**
- Verify `.env` exists and `GEMINI_API_KEY` is set
- Check Python version: `python --version` (3.11 recommended)
- Run `pip install -r requirements.txt` to ensure all deps are installed

**Frontend won't connect to API:**
- Confirm backend is running on port `8000`
- CORS is pre-configured for `localhost:5173` and `localhost:3000`

**Analytics shows zeros after sessions:**
- Sessions only record when started with the timer **Start Sprint** button
- Data updates live — switch to the Session Recap tab to see results

---

## 🙏 Acknowledgments

- **Google MediaPipe** — In-browser face mesh & iris tracking
- **Google Gemini** — Multimodal AI tutoring
- **FastAPI** — High-performance Python web framework
- **Framer Motion** — Production-quality React animations
