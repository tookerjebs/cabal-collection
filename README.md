# Cabal Collection Automation

Automated collection system for Cabal game using computer vision to detect and collect items with red dot indicators.

## Quick Setup & Usage

### Prerequisites
- Cabal game running in **windowed mode** (not fullscreen)
- Run as Administrator 

### Step 1: Installation

**Option A: Use Pre-built Executable**
1. Download the latest release
2. Extract and run `Cabal_Collection_Automation.exe`

**Option B: Build from Source**
```bash
git clone <repository-url>
cd cabal-collection-automation
pip install -r requirements_minimal.txt
python auto-collection/main.py
```

### Step 2: Configuration
1. **Connect to Game**: Click "Connect to Game" and select your Cabal window
2. **Set Detection Areas** (drag rectangles around):
   - Collection tabs area (Dungeon, World, Special, Boss tabs)
   - Dungeon list area (left panel with scrollable entries)
   - Collection items area (right panel with collectible items)
3. **Set Button Coordinates** (click each button in-game):
   - Action buttons: Auto Refill, Register, Yes
   - Pagination: Page 2, Page 3, Page 4, Arrow Right

### Step 3: Run Automation
1. Click **"Start Collection"**
2. Press **ESC** or click **"Stop"** to halt anytime
3. Adjust speed multiplier if needed (1.0x recommended)

## How to Build Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller main.spec

# Executable will be in dist/ folder
```

## Troubleshooting

**"Collection complete" immediately?**
- Verify all 3 detection areas are configured
- Ensure `red-dot.png` is in the same folder
- Check if red dots are actually visible in game

**Red dots not detected?**
- Confirm Windows scaling is 100%
- Use default game UI size
- Verify game is in windowed mode

## Requirements
- Python 3.8+
- OpenCV, PyWinAuto, Tkinter, NumPy, Pillow (see `requirements_minimal.txt`)

## License
Educational and personal use only.
 