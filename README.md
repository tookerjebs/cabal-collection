# Cabal Collection Automation

Fast automated collection system for Cabal game using computer vision to detect and collect items with red dot indicators. Optimized for speed with configurable delays and efficient clicking.

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
1. **Set Delay**: Adjust delay in milliseconds (0 = fastest, 1000 = 1 second between actions)
2. Click **"Start Collection"**
3. Press **ESC** anytime for emergency stop
4. The tool will automatically process all collections with red dots

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

## Performance Tips
- **For maximum speed**: Set delay to 0ms
- **For stability**: Use 100-500ms delay
- **For slow systems**: Use 1000ms+ delay
- The tool automatically reduces retries when delay is set to 0 for optimal performance

## Features
- **Ultra-fast clicking** using Windows API (no built-in delays)
- **Configurable speed** from 0ms (instant) to any delay you prefer
- **Smart detection** with cached templates for better performance
- **Emergency stop** with ESC key
- **Automatic pagination** through multiple collection pages
- **Optimized UI** with compact design

## Requirements
- Python 3.8+
- OpenCV, PyWinAuto, Tkinter, NumPy, Pillow, Keyboard, Mouse (see `requirements_minimal.txt`)

## License
Educational and personal use only.
 