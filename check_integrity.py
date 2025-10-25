#!/usr/bin/env python3
"""
AI Study Companion - Integrity Check Script
Verifies that all files, dependencies, and configurations are correct
"""

import os
import sys
from pathlib import Path
import json

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def check_files():
    """Check if all critical files exist."""
    print_header("FILE STRUCTURE CHECK")
    
    required_files = {
        "Main Files": [
            "main.py",
            "requirements.txt",
            "README.md",
            ".gitignore",
            ".env"
        ],
        "Java Files": [
            "StudyCompanionLauncher.java",
            "run_launcher.bat"
        ],
        "Source Files": [
            "src/__init__.py",
            "src/ai_assistant.py",
            "src/animations.py",
            "src/focus_tracker.py",
            "src/gui_manager_modern.py",
            "src/session_manager.py",
            "src/study_materials.py",
            "src/utils.py"
        ]
    }
    
    all_good = True
    for category, files in required_files.items():
        print(f"\n{category}:")
        for file in files:
            exists = Path(file).exists()
            status = "✅" if exists else "❌"
            print(f"  {status} {file}")
            if not exists:
                all_good = False
    
    return all_good

def check_directories():
    """Check if all required directories exist."""
    print_header("DIRECTORY STRUCTURE CHECK")
    
    required_dirs = [
        "src",
        "data",
        "data/materials",
        "data/materials/uploaded_files",
        "data/preferences",
        "data/sessions",
        "assets",
        "assets/sounds"
    ]
    
    all_good = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        exists = path.exists() and path.is_dir()
        status = "✅" if exists else "❌"
        print(f"  {status} {dir_path}/")
        if not exists:
            all_good = False
            print(f"      Creating directory: {dir_path}")
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"      ✅ Created successfully")
            except Exception as e:
                print(f"      ❌ Failed to create: {e}")
    
    return all_good

def check_python_version():
    """Check Python version compatibility."""
    print_header("PYTHON VERSION CHECK")
    
    version = sys.version_info
    print(f"  Detected: Python {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 8):
        print("  ❌ ERROR: Python 3.8 or higher is required")
        return False
    elif version.major == 3 and version.minor == 11:
        print("  ✅ PERFECT: Python 3.11 - Optimal version!")
        return True
    elif version >= (3, 13):
        print("  ⚠️  WARNING: Python 3.13+ detected")
        print("      MediaPipe has compatibility issues with Python 3.13+")
        print("      STRONGLY RECOMMENDED: Use Python 3.11 for full compatibility")
        return True
    elif version.major == 3 and 8 <= version.minor <= 12:
        print("  ✅ COMPATIBLE: Python version is supported")
        print("      Note: Python 3.11 is recommended for optimal performance")
        return True
    
    return False
    """Check if dependencies are installed."""
    print_header("DEPENDENCY CHECK")
    
    dependencies = [
        ('cv2', 'opencv-python'),
        ('mediapipe', 'mediapipe'),
        ('numpy', 'numpy'),
        ('pandas', 'pandas'),
        ('PIL', 'pillow'),
        ('matplotlib', 'matplotlib'),
        ('pygame', 'pygame'),
        ('plyer', 'plyer'),
        ('google.generativeai', 'google-generativeai'),
        ('dotenv', 'python-dotenv'),
        ('PyPDF2', 'PyPDF2'),
        ('docx', 'python-docx'),
        ('pptx', 'python-pptx'),
        ('openpyxl', 'openpyxl'),
    ]
    
    missing = []
    installed = []
    
    for import_name, package_name in dependencies:
        try:
            __import__(import_name)
            print(f"  ✅ {package_name}")
            installed.append(package_name)
        except ImportError:
            print(f"  ❌ {package_name} (not installed)")
            missing.append(package_name)
    
    # Check tkinter
    try:
        import tkinter
        print(f"  ✅ tkinter (built-in)")
        installed.append("tkinter")
    except ImportError:
        print(f"  ❌ tkinter (required, built-in)")
        missing.append("tkinter")
    
    if missing:
        print(f"\n  Missing packages: {len(missing)}")
        print(f"  Installed packages: {len(installed)}")
        print(f"\n  To install missing packages:")
        print(f"    pip install -r requirements.txt")
        return False
    else:
        print(f"\n  ✅ All {len(installed)} dependencies installed!")
        return True

def check_env_file():
    """Check .env file configuration."""
    print_header("ENVIRONMENT CONFIGURATION CHECK")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("  ❌ .env file not found")
        print("      AI features will not work without API key")
        return False
    
    print("  ✅ .env file exists")
    
    try:
        with open(env_path, 'r') as f:
            content = f.read()
            if 'GEMINI_API_KEY' in content:
                # Check if it has a value (not empty)
                has_value = any(line.startswith('GEMINI_API_KEY=') and 
                              len(line.split('=', 1)[1].strip()) > 0 
                              for line in content.split('\n'))
                if has_value:
                    print("  ✅ GEMINI_API_KEY is configured")
                    return True
                else:
                    print("  ⚠️  GEMINI_API_KEY found but empty")
                    return False
            else:
                print("  ❌ GEMINI_API_KEY not found in .env")
                return False
    except Exception as e:
        print(f"  ❌ Error reading .env: {e}")
        return False

def check_java_setup():
    """Check Java setup."""
    print_header("JAVA LAUNCHER CHECK")
    
    java_file = Path("StudyCompanionLauncher.java")
    class_file = Path("StudyCompanionLauncher.class")
    batch_file = Path("run_launcher.bat")
    
    checks = [
        (java_file.exists(), f"StudyCompanionLauncher.java"),
        (class_file.exists(), f"StudyCompanionLauncher.class (compiled)"),
        (batch_file.exists(), f"run_launcher.bat")
    ]
    
    all_good = True
    for exists, name in checks:
        status = "✅" if exists else "❌"
        print(f"  {status} {name}")
        if not exists:
            all_good = False
    
    if all_good:
        print("\n  ✅ Java launcher is ready to use")
    else:
        print("\n  ⚠️  Java launcher may need compilation")
        print("      Run: javac StudyCompanionLauncher.java")
    
    return all_good

def check_data_integrity():
    """Check data directory integrity."""
    print_header("DATA INTEGRITY CHECK")
    
    # Check if data directories have proper structure
    checks = []
    
    # Check materials directory
    materials_dir = Path("data/materials")
    if materials_dir.exists():
        uploaded_files = list((materials_dir / "uploaded_files").glob("*.*"))
        print(f"  ✅ Materials directory exists")
        print(f"      Uploaded files: {len(uploaded_files)}")
        checks.append(True)
    else:
        print(f"  ❌ Materials directory missing")
        checks.append(False)
    
    # Check sessions directory
    sessions_dir = Path("data/sessions")
    if sessions_dir.exists():
        session_files = list(sessions_dir.glob("*.json"))
        print(f"  ✅ Sessions directory exists")
        print(f"      Session files: {len(session_files)}")
        checks.append(True)
    else:
        print(f"  ❌ Sessions directory missing")
        checks.append(False)
    
    # Check preferences directory
    prefs_dir = Path("data/preferences")
    if prefs_dir.exists():
        print(f"  ✅ Preferences directory exists")
        config_file = prefs_dir / "config.json"
        if config_file.exists():
            print(f"      Config file exists")
        checks.append(True)
    else:
        print(f"  ❌ Preferences directory missing")
        checks.append(False)
    
    return all(checks)

def generate_summary(results):
    """Generate integrity check summary."""
    print_header("INTEGRITY CHECK SUMMARY")
    
    total_checks = len(results)
    passed_checks = sum(1 for v in results.values() if v)
    failed_checks = total_checks - passed_checks
    
    print(f"\n  Total Checks: {total_checks}")
    print(f"  ✅ Passed: {passed_checks}")
    print(f"  ❌ Failed: {failed_checks}")
    
    percentage = (passed_checks / total_checks) * 100
    print(f"\n  Integrity Score: {percentage:.1f}%")
    
    if percentage == 100:
        print("\n  🎉 EXCELLENT! All checks passed!")
        print("  The application is ready to run.")
    elif percentage >= 80:
        print("\n  ✅ GOOD! Most checks passed.")
        print("  The application should work, but some features may be limited.")
    elif percentage >= 60:
        print("\n  ⚠️  WARNING! Several checks failed.")
        print("  The application may not work properly.")
    else:
        print("\n  ❌ CRITICAL! Many checks failed.")
        print("  The application needs attention before running.")
    
    print("\n" + "=" * 70)
    
    # Provide recommendations
    if not results.get('dependencies', False):
        print("\n  📦 RECOMMENDATION: Install dependencies")
        print("     Run: pip install -r requirements.txt")
        print("     Or use: py -3.11 -m pip install -r requirements.txt")
    
    if not results.get('env_file', False):
        print("\n  🔑 RECOMMENDATION: Configure API key")
        print("     Add your GEMINI_API_KEY to the .env file")
    
    version = sys.version_info
    if version.major == 3 and version.minor != 11:
        print("\n  🐍 RECOMMENDATION: Use Python 3.11")
        print("     Download from: https://www.python.org/downloads/release/python-3110/")
        print("     Python 3.11 provides the best compatibility with all features")
        if version >= (3, 13):
            print("     Python 3.13+ causes MediaPipe compatibility issues!")

def main():
    """Run all integrity checks."""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║         AI STUDY COMPANION - INTEGRITY CHECK                     ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    
    results = {
        'files': check_files(),
        'directories': check_directories(),
        'python_version': check_python_version(),
        'dependencies': check_dependencies(),
        'env_file': check_env_file(),
        'java_setup': check_java_setup(),
        'data_integrity': check_data_integrity()
    }
    
    generate_summary(results)
    
    print("\n")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
