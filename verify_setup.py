#!/usr/bin/env python3
"""
Study Focus App - Final Setup Verification
Tests all components and dependencies for Python 3.8-3.12
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 8):
        print("❌ ERROR: Python 3.8+ required")
        return False
    elif version > (3, 12):
        print("⚠️  WARNING: Python 3.13+ not officially supported")
        print("   MediaPipe may not work correctly")
        return True  # Allow but warn
    else:
        print("✅ Python version compatible")
        return True

def check_files():
    """Check all required files exist."""
    required_files = [
        "main.py",
        "requirements.txt", 
        "README.md",
        "src/__init__.py",
        "src/focus_tracker.py",
        "src/gui_manager.py",
        "src/session_manager.py",
        "src/study_materials.py",
        "src/utils.py"
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
            
    if missing:
        print("❌ Missing files:")
        for file in missing:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files present")
        return True

def check_dependencies():
    """Check core dependencies."""
    required_deps = [
        ('cv2', 'opencv-python'),
        ('mediapipe', 'mediapipe'),
        ('numpy', 'numpy'),
        ('pandas', 'pandas'),
        ('PIL', 'pillow'),
        ('matplotlib', 'matplotlib'),
        ('tkinter', 'tkinter (built-in)')
    ]
    
    optional_deps = [
        ('pygame', 'pygame'),
        ('plyer', 'plyer')
    ]
    
    missing_required = []
    missing_optional = []
    
    print("\n🔍 Checking required dependencies:")
    for import_name, package_name in required_deps:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name}")
            missing_required.append(package_name)
            
    print("\n🔍 Checking optional dependencies:")
    for import_name, package_name in optional_deps:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"⚠️  {package_name} (optional)")
            missing_optional.append(package_name)
    
    if missing_required:
        print(f"\n❌ Missing required packages: {', '.join(missing_required)}")
        print("Install with: pip install -r requirements.txt")
        return False
    elif missing_optional:
        print(f"\n⚠️  Missing optional packages: {', '.join(missing_optional)}")
        print("App will work but some features may be limited")
        
    return True

def test_imports():
    """Test importing our app modules."""
    sys.path.insert(0, 'src')
    
    modules_to_test = [
        'focus_tracker',
        'session_manager', 
        'study_materials',
        'utils',
        'gui_manager'
    ]
    
    print("\n🧪 Testing app module imports:")
    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            return False
            
    return True

def test_camera():
    """Test camera availability."""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Camera available")
            cap.release()
            return True
        else:
            print("⚠️  Camera not available (may be in use)")
            return True  # Not critical for testing
    except Exception as e:
        print(f"⚠️  Camera test failed: {e}")
        return True  # Not critical

def main():
    """Run complete setup verification."""
    print("🧪 STUDY FOCUS APP - SETUP VERIFICATION")
    print("Python 3.8-3.12 Compatible Version")
    print("=" * 50)
    
    tests = [
        ("Python Version", check_python_version),
        ("File Structure", check_files),
        ("Dependencies", check_dependencies), 
        ("Module Imports", test_imports),
        ("Camera Hardware", test_camera)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        results.append(test_func())
    
    print("\n" + "=" * 50)
    print("📊 VERIFICATION RESULTS:")
    
    critical_tests = results[:4]  # All except camera
    if all(critical_tests):
        print("🎉 SETUP VERIFICATION PASSED!")
        print("\n✅ Ready to run Study Focus App")
        print("\n🚀 Next steps:")
        print("1. Run: python main.py")
        print("2. Or use: ./start_app.sh (Unix) / start_app.bat (Windows)")
        print("\n📖 See README.md for detailed usage instructions")
    else:
        print("❌ SETUP VERIFICATION FAILED!")
        print("\n🔧 Please fix the issues above before running the app")
        print("\n💡 Common solutions:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Check Python version: python --version")
        print("- Verify all files are extracted correctly")

if __name__ == "__main__":
    main()
