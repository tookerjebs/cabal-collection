# Cabal Collection Automation

Fast automated collection system for Cabal game using computer vision to detect and collect items with red dot indicators. Features enhanced clicking reliability, optimized performance, and configurable speed settings.

## Quick Setup & Usage

### Prerequisites
- Cabal game running in windowed mode or full screen

### How to USE

**Option A: Use Pre-built Executable**
1. Download the latest release and place `red-dot.png` next to the exe
2. Run `Cabal_Collection_Automation.exe` **AS ADMINISTRATOR**
3. Configure detection areas and button coordinates ([Video Guide](https://youtu.be/mPaBDvGdkTA))
   
   **Set Detection Areas** (drag rectangles around):
   - Collection tabs area (Dungeon, World, Special, Boss tabs)
   - Dungeon list area (left panel with scrollable entries)  
   - Collection items area (right panel with collectible items)
   
   **Set Button Coordinates** (click each button in-game):
   - Action buttons: Auto Refill, Register, Yes
   - Pagination: Page 2, Page 3, Page 4, Arrow Right
4. **Adjust Speed Settings**: Fine-tune delay (milliseconds) for optimal speed vs reliability
5. Navigate to Page 1, Dungeon Tab in-game
6. Click Start

**Option B: Build from Source**
```bash
git clone <repository-url>
cd cabal-collection-automation
pip install -r requirements_minimal.txt
python auto-collection/main.py
```
## How to Build Executable

```bash
# Install dependencies
pip install -r requirements_minimal.txt
pip install pyinstaller

# Build executable using provided spec file
pyinstaller main.spec

# Executable will be in dist/ folder
# Copy red-dot.png to the same directory as the executable
```

## Recent Improvements

- **Enhanced Tab Clicking**: Improved reliability for tab switching with mouse movement
- **Optimized Performance**: Streamlined automation logic for faster execution  
- **Windows API Integration**: Exclusive use of Windows API for more reliable clicking
- **Better Error Handling**: Improved stability and graceful error recovery

## Troubleshooting

- Verify all 3 detection areas are configured
- Ensure `red-dot.png` is in the same folder as executable
- Check if red dots are actually visible in game
- Use default game UI size
- **Important**: Ensure no in-game messages are covering the red dots! Adjust UI size or switch between windowed/fullscreen modes if needed




## License
Educational and personal use only.
 