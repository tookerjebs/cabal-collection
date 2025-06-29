# Cabal Collection Automation

An automated collection system for the Cabal game that uses computer vision to detect and collect items with red dot indicators.

## Features

- **Red Dot Detection**: Uses OpenCV template matching to find red dots indicating collectible items
- **Automated Collection**: Systematically processes collection tabs, dungeons, and items
- **Smart Navigation**: Handles pagination and tab switching automatically
- **Speed Control**: Adjustable delay multipliers for different automation speeds
- **Area-based Detection**: Configurable detection areas for different UI sections

## Components

### Core Automation
- `unified_game_automation/automation/collection_automation.py` - Main automation logic
- `unified_game_automation/core/game_connector.py` - Game window interaction
- `unified_game_automation/data/collection_data.py` - Collection configuration data

### User Interface
- `unified_game_automation/ui/main_window.py` - Main application window
- `unified_game_automation/ui/collection_tab.py` - Collection automation controls

### Detection Assets
- `unified_game_automation/data/red-dot.png` - Template image for red dot detection

## How It Works

1. **Setup Phase**: Configure detection areas and button coordinates through the UI
2. **Detection Phase**: Scan collection tabs for red dots indicating available collections
3. **Navigation Phase**: Click on tabs with red dots and navigate through dungeon lists
4. **Collection Phase**: Process items in each dungeon/area with red dots
5. **Pagination**: Automatically handle multiple pages of content

## Requirements

See `requirements_minimal.txt` for Python dependencies:
- OpenCV for computer vision
- PyWinAuto for Windows automation
- Tkinter for GUI
- NumPy for image processing
- Pillow for image handling

## Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements_minimal.txt`
3. Run the application: `python unified_game_automation/ui/main_window.py`

## Usage

1. Launch the application
2. Connect to the Cabal game window
3. Configure detection areas using the calibration tools
4. Set button coordinates for automation actions
5. Start the collection automation

## Configuration

The automation requires setup of:
- Collection tabs area (where tab red dots appear)
- Dungeon list area (where dungeon red dots appear)  
- Collection items area (where item red dots appear)
- Action button coordinates (Auto Refill, Register, Yes)
- Pagination button coordinates (Page 2, 3, 4, Arrow Right)

## Safety Features

- Validation checks before starting automation
- Status updates during operation
- Emergency stop functionality
- Speed control to prevent detection issues

## License

This project is for educational and personal use only.
 