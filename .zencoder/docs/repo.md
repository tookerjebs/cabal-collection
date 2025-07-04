# Cabal Collection Automation Information

## Summary
A Python-based automation tool for the Cabal game that uses computer vision to detect and collect items with red dot indicators. The application provides a GUI for configuring detection areas and button coordinates, then automates the collection process with configurable delays for optimal performance.

## Structure
- **auto-collection/**: Main application code
  - **automation/**: Contains collection automation logic
  - **core/**: Core functionality (game connection, area selection, settings)
  - **data/**: Data files including red dot template image
  - **ui/**: User interface components
- **main.spec**: PyInstaller specification for building executable

## Language & Runtime
**Language**: Python
**Version**: Compatible with Python 3.6+
**Build System**: PyInstaller
**Package Manager**: pip

## Dependencies
**Main Dependencies**:
- pillow==10.2.0: Image processing
- pywinauto==0.6.8: Windows automation
- keyboard==0.13.5: Keyboard input handling
- mouse==0.7.1: Mouse input handling
- opencv-python==4.8.1.78: Computer vision for red dot detection
- numpy<2: Numerical processing

**Development Dependencies**:
- pyinstaller==6.4.0: For creating standalone executable

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

## Application Structure
**Entry Point**: auto-collection/main.py
**Main Components**:
- **MainWindow**: Main application window with tabbed interface
- **CollectionTab**: UI for configuring and controlling collection automation
- **CollectionAutomation**: Core automation logic for detecting and collecting items
- **GameConnector**: Handles interaction with the game window
- **SettingsManager**: Manages saving/loading of configuration

## Functionality
The application works by:
1. Connecting to the Cabal game window
2. Allowing users to define detection areas for collection tabs, dungeon list, and collection items
3. Setting coordinates for action buttons (Auto Refill, Register, Yes) and pagination
4. Using OpenCV template matching to detect red dots indicating collectible items
5. Automating the collection process with configurable delays

## Configuration
**Settings File**: settings.json (root directory)
**Configuration Parameters**:
- Detection areas for collection tabs, dungeon list, and collection items
- Button coordinates for actions and pagination
- Delay settings in milliseconds

## Testing
No formal testing framework is implemented. The application relies on manual testing and validation through the GUI.