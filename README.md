# SnipSay

**Voice-to-clipboard on macOS.** Press a hotkey to start recording, press again to stop — your speech is transcribed locally with OpenAI Whisper and automatically copied to your clipboard.

- 🎯 **Fast** — Records and transcribes in seconds
- 🔒 **Private** — 100% offline, no data leaves your machine
- 💰 **Free** — No API keys, no subscriptions
- 🍎 **Native** — Uses system sounds and clipboard

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/snipsay.git
cd snipsay
./setup.sh
./start.sh
```

Press **Ctrl+Shift+Space** to start recording, press again to stop and transcribe.

## Requirements

- macOS (Intel or Apple Silicon)
- [Homebrew](https://brew.sh)
- [Hammerspoon](https://www.hammerspoon.org/) — `brew install --cask hammerspoon`
- Microphone access

## Installation

### One-Command Setup

```bash
./setup.sh
```

This installs all dependencies, creates a virtual environment, configures Hammerspoon, and downloads the Whisper model.

### Prerequisites (if not already installed)

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Hammerspoon
brew install --cask hammerspoon
```

## Usage

| Action | Result |
|--------|--------|
| **Ctrl+Shift+Space** | Start recording |
| **Ctrl+Shift+Space** | Stop & transcribe |
| **Cmd+V** | Paste transcribed text |

## Configuration

Edit `~/snipsay/config.lua` to customize your hotkey:

```lua
return {
    -- Hotkey modifiers and key
    hotkey_modifiers = {"ctrl", "shift"},
    hotkey_key = "space",
}
```

### Hotkey Examples

```lua
-- Cmd+Shift+V
hotkey_modifiers = {"cmd", "shift"},
hotkey_key = "V",

-- Just F12
hotkey_modifiers = {},
hotkey_key = "F12",

-- Ctrl+Option+Space
hotkey_modifiers = {"ctrl", "alt"},
hotkey_key = "space",
```

### Modifiers

| Key | Name |
|-----|------|
| `cmd` | ⌘ Command |
| `ctrl` | ⌃ Control |
| `shift` | ⇧ Shift |
| `alt` | ⌥ Option |
| `fn` | Function |
| `{}` | No modifier |

After changing config, click **Reload Config** in the menubar.

## Choosing a Whisper Model

```bash
./start.sh --model small   # Better accuracy, slower
./start.sh --model base    # Default - balanced (recommended)
```

| Model      | Size  | Speed   | Accuracy |
|------------|-------|---------|----------|
| `tiny`     | 39 MB | Fastest | Basic    |
| `base`     | 74 MB | Fast    | Good ✅   |
| `small`    | 244 MB| Medium  | Better   |
| `medium`   | 769 MB| Slow    | Best     |
| `large-v3` | 1550MB| Slowest | Excellent|

## Features

### Sound Effects

- **Pop** — Recording started
- **Bottle** — Recording stopped
- **Glass** — Transcription complete
- **Basso** — Error

### Menubar Indicator

- **🎙** — Idle
- **🔴** — Recording

### Recording Length

Supports up to **30+ minutes** of continuous recording.

## Auto-Start on Login (Optional)

```bash
ln -sf ~/snipsay/com.snipsay.backend.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.snipsay.backend.plist
```

## Troubleshooting

### "Backend not running" alert

```bash
./start.sh
```

### Hotkey not working

1. Click Hammerspoon icon → **Reload Config**
2. Grant Accessibility: System Settings → Privacy & Security → Accessibility → Enable Hammerspoon
3. Grant Microphone: System Settings → Privacy & Security → Microphone → Enable for Terminal and Hammerspoon

## Performance

Tested on **MacBook Pro 16,1 (2019, Intel i7, 16GB RAM)**:

| Model | Transcription Time | Memory |
|-------|-------------------|--------|
| `base` | ~4 seconds | ~400 MB |
| `small` | ~10 seconds | ~1.1 GB |

## Project Structure

```
snipsay/
├── config.lua              # User configuration (hotkey)
├── init.lua               # Hammerspoon config
├── setup.sh              # One-command installer
├── start.sh              # Start the backend
├── stop.sh               # Stop the backend
├── whisper_hotkey.py     # Python backend
└── README.md
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

- [Hammerspoon](https://www.hammerspoon.org/) — Global hotkey utility (MIT)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — Fast Whisper implementation (MIT)
- [PyAudio](https://people.csail.mit.edu/hub/#projects) — Audio recording (MIT)
