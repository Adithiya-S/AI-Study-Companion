#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Study Focus App - Advanced Eye Tracking Study Assistant
Compatible with Python 3.8 - 3.12

Main entry point for the application.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Fix encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def check_python_version():
    """
    Check Python version compatibility.
    """
    version = sys.version_info

    print(f"🐍 Detected Python {version.major}.{version.minor}.{version.micro}")

    if version < (3, 8):
        print("❌ ERROR: Python 3.8 or higher is required")
        print("Please upgrade to Python 3.11 for best compatibility")
        return False
    elif version.major == 3 and version.minor == 11:
        print("✅ PERFECT: Python 3.11 detected - Optimal version!")
        return True
    elif version >= (3, 13):
        print("⚠️  WARNING: Python 3.13+ is not officially supported")
        print("MediaPipe has compatibility issues with Python 3.13+")
        print("STRONGLY RECOMMENDED: Use Python 3.11 for full functionality")
        print("The app will attempt to run, but camera features will likely NOT work")
        return True  # Allow running for testing UI
    elif version.major == 3 and 8 <= version.minor <= 12:
        print("✅ COMPATIBLE: Python version supported")
        print("💡 Note: Python 3.11 is recommended for optimal performance")
        return True

    return False

def check_dependencies():
    """
    Check if all required dependencies are installed.
    """
    required_packages = [
        ('cv2', 'opencv-python'),
        ('mediapipe', 'mediapipe'),
        ('numpy', 'numpy'),
        ('pandas', 'pandas'), 
        ('PIL', 'pillow'),
        ('matplotlib', 'matplotlib'),
        ('pygame', 'pygame'),
        ('plyer', 'plyer')
    ]

    missing_packages = []

    print("\n🔍 Checking dependencies...\n")

    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} (missing)")
            missing_packages.append(package_name)

    # Check tkinter separately (built-in)
    try:
        import tkinter
        print("✅ tkinter (GUI support)")
    except ImportError:
        print("❌ tkinter (GUI will not work)")
        missing_packages.append("tkinter")

    if missing_packages:
        print(f"\n❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install with:")
        print("   pip install -r requirements.txt")
        return False

    print("\n✅ All dependencies available!")
    return True

def check_camera():
    """
    Check if camera is available.
    """
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera detected and accessible")
            cap.release()
            return True
        else:
            print("⚠️  Camera not detected or in use by another application")
            print("Eye tracking may not work properly")
            return False
    except Exception as e:
        print(f"⚠️  Camera check failed: {e}")
        return False

def main():
    """
    Main application entry point.
    """
    print("🎯 STUDY FOCUS APP - ADVANCED EYE TRACKING ASSISTANT")
    print("=" * 60)

    # Check Python version compatibility
    if not check_python_version():
        print("\n❌ Incompatible Python version. Exiting.")
        input("Press Enter to exit...")
        sys.exit(1)

    # Check dependencies
    if not check_dependencies():
        print("\n❌ Missing required dependencies. Please install them first.")
        input("Press Enter to exit...")
        sys.exit(1)

    # Check camera (optional but recommended)
    camera_ok = check_camera()

    if not camera_ok:
        print("\n⚠️  Camera issues detected.")
        response = input("Continue without camera? (y/n): ").lower()
        if response != 'y':
            sys.exit(0)

    try:
        print("\n🚀 Loading Study Focus App...")

        # Import and run Modern GUI
        from gui_manager_modern import ModernStudyFocusGUI

        app = ModernStudyFocusGUI()
        app.run()

    except ImportError as e:
        print(f"❌ Error importing application modules: {e}")
        print("Make sure all source files are present in the src/ directory.")

        print("\n💡 Troubleshooting tips:")
        print("1. Ensure all files are properly extracted")
        print("2. Check that src/ directory contains all Python modules")
        print("3. Verify Python version is 3.8-3.12")
        print("4. Reinstall dependencies with: pip install -r requirements.txt")

        input("Press Enter to exit...")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Application interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 Please report this error with the traceback above.")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
