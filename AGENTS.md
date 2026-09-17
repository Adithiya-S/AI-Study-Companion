# AI-Study-Companion: Agents & Architecture Guide

Welcome to the **AI-Study-Companion** codebase. This document outlines the project architecture, design system, component guidelines, database workflows, and developer conventions for AI agents and human contributors.

---

## 1. Project Overview & Vision

**AI-Study-Companion** is a full-stack, computer-vision-assisted study platform designed for high-focus deep work. It combines real-time eye tracking and distraction detection with an adaptive Pomodoro engine, a Gemini-powered multi-modal study assistant, interactive flashcards, and deep productivity analytics.

### Core Philosophy: "Dark Engineering Precision"
* **Zero Glassmorphism**: Avoid frosted glass, blurry gradient blobs, and pastel "vibecoded" tropes.
* **Aesthetic**: Linear, Raycast, and Vercel inspired. Deep matte obsidian (`#08090D`, `#0D0F15`), razor-sharp 1px micro-borders (`#1B1F2A`, `#262D3D`), dot-matrix / crosshair canvas grids, and high-legibility monospace telemetry (`JetBrains Mono`, `Geist Mono`).
* **Accent Palette**: Laser Electric Cyan (`#00F2FE`), Focus Emerald (`#10B981`), Warning Amber (`#F59E0B`), and Alert Crimson (`#EF4444`).
* **Motion Design**: Powered by **Vengeance UI** & **Framer Motion** (cursor-following spotlights, 3D physics tilt cards, animated glowing border beams, and tactile magnetic click states).

---

## 2. User Journey & Navigation Flow

The frontend follows a 3-tier user journey:
```
[ 1. Hero Landing Page ]
        │ (Click "Enter Workspace" / "Initialize Session")
        ▼
[ 2. Futuristic Auth / Login Page ] (With 1-Click Instant Demo Mode)
        │ (Authenticated Session)
        ▼
[ 3. Personal Study Dashboard ]
   ├── Session Controller (Pomodoro / Deep Work / Custom Timer)
   ├── Biometric HUD (Live Webcam, Face Mesh, EAR, Gaze Vector)
   ├── Gemini AI Study Studio (Chat, Prompt Chips, Document QA)
   ├── Materials & Flashcards (PDF/DOCX/Notes Upload, Flip Cards)
   ├── Interactive Analytics (Chart.js Trends, Focus Heatmaps)
   └── Settings & Preferences
```

---

## 3. Technology Stack & Directory Structure

### Frontend Stack
* **Framework**: React 19 + Vite
* **Styling**: Tailwind CSS (Tailwind v3/v4 with custom engineering design tokens)
* **Animation**: Framer Motion
* **UI Components**: Vengeance UI motion primitives + custom micro-border cards
* **Icons**: Lucide React
* **Charts**: Chart.js & `react-chartjs-2`
* **Audio**: Web Audio API synthesized chimes & notification alerts

### Backend & Database Stack
* **Backend**: FastAPI (Python 3.11–3.14 compatible) + Uvicorn
* **Database**: PostgreSQL with SQLAlchemy ORM (fallback to SQLite for zero-config offline runs)
* **AI Engine**: Google Gemini API (`google-genai` SDK v2+, model: `gemini-3.5-flash`)
* **Computer Vision**: In-browser MediaPipe / WebRTC with fallback to backend OpenCV
* **Database Snapshotting & Testing**: `@driftcli/drift` for row-level diffing, test seeding, and rapid fixture restoration

### Repository Layout
```
AI-Study-Companion/
├── AGENTS.md                         # This specification and instructions file
├── README.md                         # Public documentation and setup guide
├── requirements.txt                  # Python dependencies (FastAPI, SQLAlchemy, etc.)
├── main.py                           # Master launcher (boots backend + serves/proxies frontend)
├── drift.config.json                 # Drift CLI database snapshot configuration
├── docker-compose.yml                # Optional 1-command PostgreSQL 16 container
│
├── frontend/                         # React + Vite application
│   ├── index.html                    # HTML entry with Google Fonts (Inter + JetBrains Mono)
│   ├── package.json
│   ├── tailwind.config.js            # Dark engineering palette & animations
│   ├── vite.config.js                # Dev server and API proxy config
│   └── src/
│       ├── main.jsx
│       ├── App.jsx                   # View Router (Landing / Auth / Dashboard)
│       ├── index.css                 # Base styles & custom utility classes
│       ├── lib/
│       │   └── utils.js              # cn() helper (clsx + tailwind-merge)
│       └── components/
│           ├── ui/                   # Vengeance UI motion components
│           │   ├── Spotlight.jsx     # Radial mouse-following spotlight glow
│           │   ├── TiltCard.jsx      # 3D interactive physics tilt card
│           │   ├── BorderBeam.jsx    # Glowing keyline border animation
│           │   ├── MagneticButton.jsx# Spring-damped CTA button
│           │   └── BackgroundGrid.jsx# High-precision dot-matrix / crosshair grid
│           ├── landing/              # Landing page sections
│           │   ├── Navbar.jsx
│           │   ├── Hero.jsx          # Hero with live telemetry preview
│           │   ├── FeaturesBento.jsx # 3D tilt feature showcase
│           │   └── Footer.jsx
│           ├── auth/                 # Authentication
│           │   └── LoginPage.jsx     # Micro-border card with 1-click Demo access
│           └── dashboard/            # Study workspace components
│               ├── DashboardHeader.jsx
│               ├── SessionTimer.jsx  # Glowing circular radial timer + audio chime
│               ├── CameraTracker.jsx # Live camera HUD with face mesh & EAR gauge
│               ├── StatCards.jsx     # Animated metric cards
│               ├── AIChatTab.jsx     # Gemini study chat with prompt chips
│               ├── MaterialsTab.jsx  # Drag & drop upload & flashcard flip engine
│               ├── AnalyticsTab.jsx  # Chart.js weekly focus & duration trends
│               └── SettingsTab.jsx   # Camera, sensitivity, sound toggles
│
├── backend/                          # FastAPI Python backend
│   ├── server.py                     # FastAPI application entry point
│   ├── config.py                     # Environment variables & DB settings
│   ├── db.py                         # SQLAlchemy database models & sessionmaker
│   ├── auth.py                       # JWT generation, password hashing & verification
│   ├── seed_data.py                  # Initial seed script for demo user & session history
│   └── routes/
│       ├── auth_routes.py            # /api/auth/register, /api/auth/login, /api/auth/demo
│       ├── session_routes.py         # /api/sessions/start, /api/sessions/log, /api/sessions/history
│       ├── ai_routes.py              # /api/ai/chat, /api/ai/summarize, /api/ai/quiz
│       └── materials_routes.py       # /api/materials/upload, /api/materials/links
│
└── src/                              # Original computer vision & utility modules (maintained for desktop/CLI)
    ├── focus_tracker.py
    ├── session_manager.py
    ├── study_materials.py
    ├── ai_assistant.py
    └── utils.py
```

---

## 4. Design Guidelines for Agents

When creating or modifying components, adhere to these rules:

1. **No Glassmorphism**: Never use `backdrop-blur-md bg-white/10` or frosted pastel bubbles. Use solid matte containers:
   - Card Background: `bg-[#0D1117]` or `bg-[#111620]`
   - Page Background: `bg-[#08090D]`
   - Border: `border border-[#1E2433]` or `border-zinc-800`
2. **Typography**:
   - Primary Headings & UI: `font-sans` (Inter, Outfit)
   - Telemetry, Timers, Code, Readouts: `font-mono` (`JetBrains Mono`, `Geist Mono`, `ui-monospace`)
3. **Interactive States**:
   - Always provide crisp hover, active, and focus states.
   - Use subtle keyline lighting or neon hairline glows (`shadow-[0_0_15px_rgba(0,242,254,0.15)]`) instead of heavy dropshadows.
4. **Resilience & Fallbacks**:
   - Camera access should gracefully display an animated simulated telemetry loop if no webcam is present or permission is denied.
   - Gemini AI chat should provide simulated high-quality study responses if no `GEMINI_API_KEY` is configured in the environment.
   - The database should automatically fall back to local SQLite if a PostgreSQL connection string is not provided or reachable.

---

## 5. Drift (@driftcli/drift) Workflows

`drift` is integrated to snapshot, diff, and restore the database for testing and demonstration:

* **Initialize workspace**:
  ```bash
  drift init --db postgres://drift:drift@localhost:5432/study_companion
  ```
* **Save baseline seed**:
  ```bash
  drift save baseline-demo
  ```
* **Inspect mutations during study session**:
  ```bash
  drift status
  ```
* **Roll back to clean state**:
  ```bash
  drift restore baseline-demo --yes
  ```
* **Bug Hunting**: Report any Windows backslash path issues (`.drift\snapshots\`), JSONB serialization issues, or foreign key ordering issues to the `driftjs` GitHub repository.

---

## 6. How to Run

### Development Mode:
1. **Backend**:
   ```bash
   python -m uvicorn backend.server:app --reload --port 8000
   ```
2. **Frontend**:
   ```bash
   cd frontend && npm run dev
   ```
3. **All-in-One**:
   ```bash
   python main.py
   ```
