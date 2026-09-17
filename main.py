#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AURA // AI Deep Focus & Telemetry Companion
Full-Stack Web Application (FastAPI + React + Vite)
"""

import sys
import os
import webbrowser
import threading
import time
from pathlib import Path

# Set UTF-8 for console output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def open_browser(url: str = "http://127.0.0.1:8000"):
    time.sleep(1.5)
    try:
        webbrowser.open(url)
    except Exception:
        pass


def run_web_app(host: str = "127.0.0.1", port: int = 8000):
    print("=" * 65)
    print("⚡ AURA // AI DEEP FOCUS & BIOMETRIC TELEMETRY PLATFORM")
    print("   Architecture: FastAPI + React 19 + SQLite")
    print(f"   Listening on: http://{host}:{port}")
    print("=" * 65)

    # Open browser in background after server is ready
    threading.Thread(target=open_browser, args=(f"http://{host}:{port}",), daemon=True).start()

    import uvicorn
    uvicorn.run("backend.server:app", host=host, port=port, reload=False)


def main():
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print("""
AURA AI Study Companion - Command Line Interface

Usage:
  python main.py          Start the web application and launch browser
  python main.py --dev    Print development server instructions (HMR mode)
  python main.py --host   Bind to 0.0.0.0 for LAN access

Options:
  --host    Bind to all interfaces (0.0.0.0) instead of localhost
  --port N  Override default port (default: 8000)
""")
        return

    if "--dev" in args:
        print("""
[DEVELOPMENT MODE - Hot Module Replacement]

Terminal 1 — FastAPI backend with auto-reload:
   python -m uvicorn backend.server:app --reload --port 8000

Terminal 2 — Vite dev server with HMR:
   cd frontend && npm run dev

Open http://localhost:5173 in your browser.
API is available at http://localhost:8000
""")
        return

    # Parse optional host / port overrides
    host = "0.0.0.0" if "--host" in args else "127.0.0.1"
    port = 8000
    if "--port" in args:
        idx = args.index("--port")
        try:
            port = int(args[idx + 1])
        except (IndexError, ValueError):
            pass

    run_web_app(host=host, port=port)


if __name__ == "__main__":
    main()
