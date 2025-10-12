# Study Focus App - Python 3.8-3.12 Compatible

A powerful Python-based study productivity application with real-time eye tracking using MediaPipe.

## 🐍 Python Version Support

**Supported Versions:** Python 3.8, 3.9, 3.10, 3.11, 3.12

**Note:** Python 3.13+ is not yet supported due to MediaPipe compatibility limitations.

## 🚀 Quick Start

### Option 1: One-Click Launch (Recommended)
```bash
# Windows
start_app.bat

# macOS/Linux  
./start_app.sh
```

### Option 2: Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

## ✨ Features

### 🎦 Real-Time Eye Tracking
- **MediaPipe integration** for accurate face and eye detection
- **Eye Aspect Ratio (EAR) analysis** to detect blinks and attention
- **Gaze direction tracking** (left, center, right)
- **Head pose estimation** for comprehensive focus analysis

### 📊 Advanced Focus Analysis  
- **Multi-factor focus scoring** combining eye state, gaze, and head pose
- **Distraction detection** with customizable sensitivity
- **Real-time alerts** when attention wavers
- **Detailed analytics** and session reports

### ⏱️ Session Management
- **Customizable study timers** (1-180 minutes)
- **Break reminders** with short and long break options
- **Pause/resume functionality** 
- **Session statistics** and progress tracking

### 📚 Study Materials
- **Quick links** to online resources
- **Built-in study techniques** (Pomodoro, Active Recall, etc.)
- **Daily motivation** quotes and tips
- **Resource management** system
- **🤖 AI Study Assistant** powered by Google Gemini
  - Ask questions with internet knowledge
  - Query your uploaded study materials
  - Smart context-aware responses
  - Chat history and conversation tracking

### 🤖 AI Study Assistant (NEW!)
- **Dual-Mode Intelligence:**
  - 🌐 **Internet Mode:** Get answers from the web
  - 📚 **Materials Mode:** Query only your uploaded study materials
- **Multi-Format Document Support:**
  - 📄 **PDF files** - Extract text from PDF documents
  - 📝 **Word documents** - .docx and .doc files
  - 📊 **PowerPoint presentations** - .pptx and .ppt files
  - 📈 **Excel spreadsheets** - .xlsx and .xls files
  - 📁 **Text & Code files** - .txt, .md, .py, .java, .cpp, .js, .html, .css, .json, etc.
- **Smart Responses:** Context-aware answers based on mode
- **Chat History:** Review past conversations
- **Material Management:** Upload, organize, and delete study materials
- **Pre-configured:** No API key setup needed for users - administrator sets up once!
- See [ADMIN_SETUP.md](ADMIN_SETUP.md) for initial configuration (admin only)

### 📈 Productivity Reports
- **Session completion rates** and efficiency metrics
- **Focus percentage** trends over time
- **Distraction pattern analysis**
- **CSV/JSON export** for external analysis

## 🔧 System Requirements

- **Python:** 3.8 - 3.12 (3.13+ not supported yet)
- **Camera:** Built-in or external webcam (720p recommended)
- **RAM:** 4GB minimum (8GB recommended)
- **OS:** Windows 10+, macOS 10.14+, or Linux

## 📦 Dependencies

All dependencies are automatically installed via `requirements.txt`:

- **opencv-python** - Camera access and image processing
- **mediapipe** - Face mesh and eye tracking  
- **numpy** - Numerical computations
- **pandas** - Data analysis and CSV handling
- **matplotlib** - Plotting and visualizations
- **pillow** - Image processing for GUI
- **pygame** - Audio alerts
- **plyer** - Cross-platform notifications
- **google-generativeai** - Gemini AI integration (for AI assistant)
- **PyPDF2** - PDF document parsing
- **python-docx** - Word document (.docx) parsing
- **python-pptx** - PowerPoint presentation parsing
- **openpyxl** - Excel spreadsheet parsing
- **tkinter** - GUI framework (included with Python)

## 🎯 How It Works

### Eye Tracking Algorithm
1. **Face Detection:** MediaPipe detects face landmarks in real-time
2. **Eye Analysis:** Calculates Eye Aspect Ratio (EAR) to determine if eyes are open
3. **Gaze Tracking:** Analyzes iris position relative to eye corners
4. **Head Pose:** Estimates pitch, yaw, and roll angles
5. **Focus Scoring:** Combines all metrics into a focus score (0.0-1.0)

### Focus Detection Formula
```
Focus Score = (Eye Openness × 0.4) + (Gaze Direction × 0.35) + (Head Pose × 0.25)

Where:
- Eye Openness: Based on EAR threshold (typically 0.25)
- Gaze Direction: Center gaze scores highest
- Head Pose: Upright position scores highest
```

## ⚙️ Configuration

### Focus Sensitivity Settings
- **High:** More strict distraction detection (fewer false negatives)
- **Medium:** Balanced detection (default)  
- **Low:** More lenient detection (fewer false positives)

### Camera Settings
- **Resolution:** 640x480 (default) up to 1920x1080
- **FPS:** 30 (recommended)
- **Camera Index:** 0 (default), try 1, 2 for external cameras

## 📖 Usage Tips

### Optimal Setup
- **Lighting:** Good, even lighting on your face (avoid backlighting)
- **Distance:** Position camera 2-3 feet from your face
- **Angle:** Camera at eye level for best head pose detection
- **Background:** Minimize distracting elements behind you

### Getting Started
1. Launch the app using one of the start methods above
2. Allow camera permissions when prompted
3. Position yourself in camera view and test focus detection
4. Set your study duration and start a session
5. Study normally - the app will alert you if you become distracted

## 🔍 Troubleshooting

### Common Issues

**Camera not working:**
- Check camera permissions in system settings
- Try different camera index (0, 1, 2) in settings
- Ensure camera isn't used by other applications

**Poor focus detection:**
- Improve lighting conditions
- Adjust camera position and angle
- Calibrate focus sensitivity in settings

**Python version error:**
- Verify Python version: `python --version`
- Use Python 3.8-3.12 only
- Consider using pyenv for version management

**Dependency installation fails:**
- Update pip: `pip install --upgrade pip`
- Try: `pip install --no-cache-dir -r requirements.txt`
- On Linux: `sudo apt-get install python3-opencv`


## 🙏 Acknowledgments

- **MediaPipe Team** - Advanced face detection and tracking
- **OpenCV Community** - Computer vision framework
- **Python Community** - Amazing ecosystem of libraries

---

**Ready to focus better?** 🎯

*Start your productive study session today!*
