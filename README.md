# Enhanced Stellar OCR Tool

> **This is a fork of aquazz's stellarlinkg auto imprint** with direct window clicking, visual area selection

## ⚡ Key Enhancements
- **Direct window clicking** - No mouse movement, works in background
- **Visual area selection** - Drag interface with real-time preview
- **Emergency kill switch** - Press ESC anytime to stop

## 🚀 Quick Start

### Download
- **Ready-to-use exe**: Download from [Releases](../../releases)
- **Build from source**: See build instructions below

### Setup
1. **Set Imprint Button** - Click "Set Imprint Button" and click the Imprint button in game
2. **Define OCR Area** - Click "Define area" and drag to select the text area
3. **Configure Options** - Select stat type and minimum value (optional)
4. **Start** - Click "Start" and automation begins

### Emergency Stop
- **Press ESC key anytime** to instantly stop automation

## 📋 Available Options
- PVE Penetration
- PVE Critical DMG
- All Attack UP
- Penetration
- Critical DMG.
- Ignore Accuracy ( just for testing)

## 🔧 Build Instructions
```bash
# Install dependencies
pip install -r requirements_minimal.txt

# Build executable
pyinstaller main.spec
```

## ⚠️ Important Notes
- **Use at your own risk**
- **Font**: Use Tahoma font in game (Esc → Options → Preferences → Font)
- **Logs**: Stored in `C:\Users\[USERNAME]\stellarlink_logs\`
- **Monitor**: Use on primary screen for accurate coordinates


## 🎮 How It Works
1. Takes screenshot of defined area
2. OCR processes the image to extract text
3. Checks if desired stats are found
4. Sends direct clicks to game window
5. Repeats until target found or manually stopped
