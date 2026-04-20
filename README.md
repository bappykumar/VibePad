<div align="center">

# 📝 VibePad v2.2.0
### *Premium Desktop Sticky Notes for Modern Workflows*

[![Version](https://img.shields.io/badge/version-2.2.0-blue.svg?style=for-the-badge)](https://github.com/bappykumar/VibePad)
[![Platform](https://img.shields.io/badge/platform-Windows%20|%20macOS%20|%20Linux-lightgrey.svg?style=for-the-badge)](https://github.com/bappykumar/VibePad)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)](https://github.com/bappykumar/VibePad)

---

**VibePad** is a realistic, modern, and high-performance desktop sticky note widget. Designed to feel like physical notes on your digital screen, it combines tactile aesthetics with professional power features like Markdown, Checklists, and Auto-sync.

</div>

## 🚀 Quick Launch
Just double-click **`VibePad_Control_Panel.exe`** to start your workspace. No Python installation required!

## ✨ What's New in v2.2.0?

Version 2.2.0 is a major refactor focused on **Stability**, **Aesthetics**, and **Productivity**.

- 🚀 **Single-Process Engine**: Optimized performance and no more file-locking issues.
- 🗸 **Checklist Mode**: Create interactive TODO lists with a click.
- ✍️ **Markdown Support**: Headers, Bold, and Italics with a clean "Syntax-Hide" interface.
- 🎨 **Harmonious Palette**: Six curated themes designed for readability and focus.
- 🛠️ **Utility Suite**: Integrated Control Panel and One-click Data Cleaner.

---

## 💎 Core Features

### 1. Realistic Design
Uses the high-quality **Segoe Print** font to mimic real handwriting, paired with a subtle border and shadow-like header design.

### 2. Markdown & Styling
Just select text to reveal the **Floating Toolbar**. Apply formatting instantly:
- `# Headers` for structure.
- `**Bold**` for emphasis.
- `*Italics*` for footnotes.
- *Tip: Syntax markers hide automatically when you focus elsewhere!*

### 3. Interactive Checklists
Right-click or click the `(+)` icon to create a **New Checklist**.
- `☐` Empty -> `☑` Completed -> `☒` Critical -> `☐` Reset.

### 4. Smart Window Management
- **Pin Header**: Keeps notes "Always on Top" for quick reference.
- **Auto-Save**: Every keystroke is saved instantly; never lose a thought.
- **Dynamic Resizing**: Grab the modern triangle handle (◢) to scale your note.
- **Multi-Note Support**: Run as many pads as you need simultaneously.

---

## ⌨️ Productivity Shortcuts

| Shortcut | Action |
| :-- | :-- |
| **Ctrl + N** | Create a New Note |
| **Ctrl + P** | Toggle "Always on Top" (Pin) |
| **Ctrl + D** | Delete Current Note (with confirmation) |
| **Double-Click Title** | Rename the Note Title |
| **Right-Click** | Open Context Menu (Themes, About, Utilities) |

---

## 🛠️ Included Utilities

The package includes a suite of tools for a seamless experience:

- **`VibePad_Control_Panel.exe`**: Manage your experience from a central hub.
- **`Start_VibePad.bat`**: The quickest way to launch the app.
- **`setup_autostart.bat`**: Adds VibePad to your Windows Startup folder.
- **`VibePad_Cleaner.bat`**: Safely stops the app and resets todos/notes if you want a fresh start.

---

## 📂 Installation

### For Windows Users (Recommended)
1. Download the `VibePad_v2.2.0` folder.
2. Double-click **`VibePad_Control_Panel.exe`**.
3. (Optional) Run `setup_autostart.bat` to have your notes ready every time you log in.

### ⚠️ Troubleshooting: "Windows cannot find 'pythonw'"
If you see an error saying "Windows cannot find 'pythonw'", it means Python is missing or not configured correctly.

**Step-by-Step Fix:**
1. **Download Python:** Visit [python.org/downloads](https://www.python.org/downloads/) and download the latest version.
2. **Run Installer:** Open the `.exe` file you just downloaded.
3. **CRITICAL:** Check the box **"Add Python.exe to PATH"** at the bottom before clicking Install.
4. **Install:** Click **"Install Now"**.
5. **Try Again:** Once finished, run `Start_VibePad.bat` or `VibePad_Control_Panel.exe` again.

### Running from Source (Developers)
If you prefer running the Python source code:
1. Ensure you have Python 3.x installed (with PATH enabled).
2. Run `python VibePad.py` or use `Start_VibePad.bat`.
```bash
# Clone the repository
git clone https://github.com/bappykumar/VibePad.git

# Run the app
python VibePad.py
```

---

## 🌍 Data Storage
Your notes are stored locally and securely in standard application directories:
- **Windows**: `%APPDATA%\VibePad\notes.json`
- **macOS**: `~/Library/Application Support/VibePad/notes.json`
- **Linux**: `~/.config/VibePad/notes.json`

---

## 🤝 Developed By
**Bappy Kumar**
*Visualizer | Vibe Coder*

Join our community for updates: [🌐 Telegram Support](https://t.me/designbd2)

---

<div align="center">
  <p>© 2026 VibePad App. Designed for the aesthetics of productivity.</p>
</div>
