# Stellar and Arrival Skill Automation

Automated OCR tool for stellar system and arrival skill rerolling.

## Features

- **Arrival Skill Automation** - Dual stat detection and rerolling
- **Stellar System Automation** - Single stat detection and rerolling
- **BitBlt Screen Capture** - Works with background windows
- **Tesseract OCR** - Fast and accurate text recognition
- **Direct Window Clicking** - No mouse movement required
- **Emergency Stop** - ESC key stops automation instantly

## Usage

1. **Run the tool** - Start `Stellar_and_Arrival_Automation.exe` always RUN as ADMIN
2. **Select tab** - Choose "Arrival Skill" or "Stellar System"
3. **Set coordinates** - Click buttons to set Apply/Change/Imprint positions
4. **Define area** - Drag to select OCR detection area
5. **Configure stats** - Select desired stats and minimum values
6. **Start automation** - Click Start button

## Requirements

- Game running in windowed mode
- Tesseract OCR (included)
- Windows 10/11
- use default font in game Tahoma
- Do not make the UI in game too small or else OCR becomes inaccurate, default setting is fine, or slightly smaller (10-20%)

## How to Build

**Step 1: Create virtual environment**
```bash
python -m venv venv
```

**Step 2: Activate virtual environment**
```bash
venv\Scripts\activate.bat
```

**Step 3: Install dependencies**
```bash
pip install -r requirements_minimal.txt
```

**Step 4: Build executable**
```bash
pyinstaller main.spec
```

**Step 5: Find your executable**
The built executable will be in the `dist` folder:
```
dist\Stellar_and_Arrival_Automation.exe
```

## Known Issues
certain stats with long names like "Arrival Skill Cool Time decreased." collides with the stat value in game.
Currently arrival skill cool time and arrival skill duration will trigger a success message with any stat value. you cant set any specific value for it. Possible fix: You reduce the UI size in game settings to minimum, however this will also reduce the OCR accuracy and requires the special case handling to be improved.


