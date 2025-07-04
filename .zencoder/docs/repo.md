# Cabal Collection Automation Information

## Summary
A Python-based automation tool for the Cabal game that uses computer vision to detect and collect items with red dot indicators. The application provides a GUI for configuring detection areas and button coordinates, with optimizable speed settings for efficient collection.

## Structure
- **auto-collection/**: Main application code
  - **automation/**: Contains automation logic for collection process
  - **core/**: Core functionality (game connection, area selection, settings)
  - **data/**: Game-specific data and constants
  - **ui/**: User interface components
  - **main.py**: Application entry point
- **requirements_minimal.txt**: Python dependencies
- **main.spec**: PyInstaller configuration for executable building
- **settings.json**: Saved user settings

## Language & Runtime
**Language**: Python
**Version**: Compatible with Python 3.x
**Build System**: PyInstaller for executable creation
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- pillow==10.2.0: Image processing
- pywinauto==0.6.8: Windows automation
- keyboard==0.13.5: Keyboard input handling
- mouse==0.7.1: Mouse input handling
- opencv-python==4.8.1.78: Computer vision
- numpy<2: Numerical processing

**Development Dependencies**:
- pyinstaller==6.4.0: For creating standalone executables

## Build & Installation
```bash
# Install dependencies
pip install -r requirements_minimal.txt

# Run the application
python auto-collection/main.py

# Build executable
pip install pyinstaller
pyinstaller main.spec
```

## Application Architecture
**Main Components**:
- **GameConnector**: Connects to the game window using pywinauto
- **CollectionAutomation**: Core automation logic using OpenCV for detection
- **SettingsManager**: Handles saving/loading of user settings
- **MainWindow**: Main application window with tkinter
- **CollectionTab**: UI for collection configuration and control

**Key Features**:
- Computer vision-based red dot detection
- Configurable detection areas via drag-and-drop
- Button coordinate calibration
- Adjustable delay settings
- Emergency stop with ESC key
- Settings persistence

## Usage Flow
1. User defines detection areas (collection tabs, dungeon list, collection items)
2. User calibrates button coordinates (Auto Refill, Register, Yes, pagination)
3. User adjusts delay settings for optimal performance
4. Application automatically detects red dots and performs collection actions
5. Settings are saved for future sessions

## Distribution
The application can be distributed as:
- Source code requiring Python and dependencies
- Standalone executable created with PyInstaller (Windows)

The executable requires the red-dot.png file to be placed in the same directory for detection functionality.