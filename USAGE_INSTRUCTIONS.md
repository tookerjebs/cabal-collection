# Cabal Collection Automation - Usage Instructions

## Quick Start Guide

### 1. Setup Requirements
- Make sure Cabal game is running in **windowed mode** (not fullscreen)
- The `red-dot.png` file must be in the same folder as the executable
- Run the executable as Administrator for best compatibility

### 2. Initial Configuration

#### Step 1: Connect to Game Window
1. Launch `Cabal_Collection_Automation.exe`
2. Click "Connect to Game" button
3. Select your Cabal game window from the list

#### Step 2: Configure Detection Areas
You need to set up 3 detection areas by dragging rectangles:

1. **Collection Tabs Area**: 
   - Drag around the area containing the collection tabs (Dungeon, World, Special, Boss)
   - This should include all the tab buttons at the top

2. **Dungeon List Area**: 
   - Drag around the area where dungeon/world/special/boss entries are listed
   - This is typically the left panel with scrollable list

3. **Collection Items Area**: 
   - Drag around the area where collection items/materials are shown
   - This is typically the right panel showing collectible items

#### Step 3: Set Button Coordinates
Click on each button to capture their coordinates:

**Action Buttons:**
- **Auto Refill**: Click this button in the game to capture its position
- **Register**: Click this button in the game to capture its position  
- **Yes**: Click this button in the game to capture its position

**Pagination Buttons:**
- **Page 2**: Click this button in the game to capture its position
- **Page 3**: Click this button in the game to capture its position
- **Page 4**: Click this button in the game to capture its position
- **Arrow Right**: Click this button in the game to capture its position

### 3. Running the Automation

1. After all areas and buttons are configured, click **"Start Collection"**
2. The automation will:
   - Scan collection tabs for red dots
   - Click on tabs with red dots
   - Scan dungeon lists for red dots
   - Click on dungeons with red dots
   - Scan collection items for red dots
   - Click on items with red dots and execute the collection sequence

### 4. Troubleshooting

#### "Collection complete" immediately appears:
- **Check areas**: Make sure all 3 detection areas are properly configured
- **Check red-dot.png**: Ensure the file is in the same folder as the executable
- **Check game state**: Make sure there are actually red dots visible in the collection interface

#### Red dots not being detected:
- **Template matching**: The red-dot.png might not match the actual red dots in your game
- **Screen scaling**: Make sure Windows display scaling is set to 100%
- **Game UI size**: Use default or slightly smaller UI size in game settings

#### Debug Information:
- The tool will print debug information to help identify issues
- Check the console output for messages about template loading and detection results

### 5. Speed Control

- Use the speed multiplier slider to adjust automation speed
- Higher values = slower automation (more reliable)
- Lower values = faster automation (may miss detections)
- Recommended: Start with 1.0x and adjust as needed

### 6. Emergency Stop

- Press **ESC** key at any time to stop the automation
- Or click the **"Stop"** button in the interface

## Important Notes

- Always test the automation with a small area first
- Make sure you have the correct permissions and are following game rules
- The tool works by detecting visual red dot indicators - if the game UI changes, you may need to reconfigure
- Keep the red-dot.png file in the same directory as the executable