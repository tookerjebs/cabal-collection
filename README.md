# Cabal Collection Automation

Fast automated collection system for Cabal game using computer vision to detect and collect items with red dot indicators. Optimized for speed with configurable delays and efficient clicking.

## Quick Setup & Usage

### Prerequisites
- Cabal game running in windowed mode or full screen

### How to USE

**Option A: Use Pre-built Executable**
1. Download the latest release v1, download the red-dot.png file and place it next to the exe
2. run `Cabal_Collection_Automation.exe` RUN AS ADMIN
3. Define the areas and define the coordinates of the relevant buttons, video guide https://youtu.be/mPaBDvGdkTA
   **Set Detection Areas** (drag rectangles around):
   - Collection tabs area (Dungeon, World, Special, Boss tabs)
   - Dungeon list area (left panel with scrollable entries)
   - Collection items area (right panel with collectible items)
   **Set Button Coordinates** (click each button in-game):
   - Action buttons: Auto Refill, Register, Yes
   - Pagination: Page 2, Page 3, Page 4, Arrow Right
4. ADJUST DELAY** (milliseconds): test different delays until you find a balance between speed and reliability
5. GO to page 1, Dungeon Tab
5. Click Start

**Option B: Build from Source**
```bash
git clone <repository-url>
cd cabal-collection-automation
pip install -r requirements_minimal.txt
python auto-collection/main.py
```
## How to Build Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller main.spec

# Executable will be in dist/ folder
```

## Troubleshooting

- Verify all 3 detection areas are configured
- Ensure `red-dot.png` is in the same folder
- Check if red dots are actually visible in game
- Use default game UI size
- Make sure no in game messages are COVERING the red dots !! Change your UI size or switch from windowed to fullscreen to avoid having any in game message covering the red dots




## License
Educational and personal use only.
 