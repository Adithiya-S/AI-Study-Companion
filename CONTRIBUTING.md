# Contributing to Study Focus App

Thank you for your interest in contributing to the Study Focus App! 🎯

## 🚀 Getting Started

### Prerequisites
- Python 3.8 - 3.12 (Python 3.13+ not yet supported)
- Git installed on your system
- A webcam for testing eye tracking features

### Setting Up the Development Environment

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/Adithiya-S/study-focus-app.git
   cd study-focus-app
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Test the Setup**
   ```bash
   python verify_setup.py
   ```

4. **Run the App**
   ```bash
   python main.py
   ```

## 🔄 Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Write clean, documented code
- Follow Python PEP 8 style guidelines
- Test your changes thoroughly

### 3. Commit Your Changes
```bash
git add .
git commit -m "Add: Brief description of your feature"
```

**Commit Message Format:**
- `Add:` for new features
- `Fix:` for bug fixes
- `Update:` for improvements
- `Docs:` for documentation changes

### 4. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title and description
- Screenshots/videos if applicable
- List of changes made

## 🎯 Areas for Contribution

### High Priority
- **Enhanced Focus Algorithms**: Improve eye tracking accuracy
- **New Study Techniques**: Add more productivity methods
- **UI/UX Improvements**: Better user interface design
- **Performance Optimization**: Faster processing, lower CPU usage

### Medium Priority
- **Cross-platform Compatibility**: Better macOS/Linux support
- **Additional Languages**: Internationalization support
- **Data Visualization**: Better charts and analytics
- **Sound/Notification Options**: More alert types

### Low Priority
- **Themes**: Dark/light mode options
- **Plugin System**: Extensible architecture
- **Mobile App**: Companion mobile application
- **Cloud Sync**: Online session storage

## 🧪 Testing Guidelines

### Before Submitting
1. **Functionality Test**: Ensure your feature works as expected
2. **Eye Tracking Test**: Verify camera detection still works
3. **Cross-compatibility**: Test on different Python versions if possible
4. **Error Handling**: Test edge cases and error scenarios

### Testing Your Changes
```bash
# Run the verification script
python verify_setup.py

# Test the main application
python main.py

# Test specific modules (if applicable)
python -m src.focus_tracker
```

## 📋 Code Guidelines

### Python Style
- Follow PEP 8 conventions
- Use meaningful variable and function names
- Add docstrings for functions and classes
- Keep functions small and focused

### File Structure
```
src/
├── __init__.py          # Package initialization
├── focus_tracker.py     # Eye tracking logic
├── gui_manager.py       # User interface
├── session_manager.py   # Study session handling
├── study_materials.py   # Resource management
└── utils.py            # Utility functions
```

### Documentation
- Update README.md for new features
- Add inline comments for complex logic
- Update requirements.txt for new dependencies

## 🐛 Bug Reports

When reporting bugs, please include:
- Operating system and version
- Python version
- Full error message/traceback
- Steps to reproduce
- Expected vs actual behavior

## 💡 Feature Requests

For new feature ideas:
- Describe the feature clearly
- Explain the use case/benefit
- Consider implementation complexity
- Discuss with maintainers first for major features

## 🤝 Code Review Process

1. **Automated Checks**: Code will be reviewed for style and basic functionality
2. **Peer Review**: Other contributors will review your changes
3. **Testing**: Changes will be tested on different systems
4. **Integration**: Approved changes will be merged into main branch

## 📞 Getting Help

- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Direct Contact**: Reach out to maintainers for major contributions

## 📝 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Happy Coding!** 🚀

*Let's make studying more productive together!*
