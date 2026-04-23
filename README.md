<div align="center">

# 📝 VibePad v2.3.0
### *Premium Desktop Sticky Notes for Modern Workflows*

[![Version](https://img.shields.io/badge/version-2.3.0-blue.svg?style=for-the-badge)](https://github.com/bappykumar/VibePad)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg?style=for-the-badge)](https://github.com/bappykumar/VibePad)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)](https://github.com/bappykumar/VibePad)
[![Python](https://img.shields.io/badge/Python-3.x-yellow.svg?style=for-the-badge)](https://www.python.org/)

---

**VibePad** is a realistic, modern, and high-performance desktop sticky note widget. It brings tactile aesthetics to your digital workspace with professional power features like **Markdown, Checklists, and Intelligent Bengali Detection.**

</div>

---

## ✨ What's New in v2.3.0?

Version 2.3.0 is a major leap forward, focusing on **Personalization, Stability, and Zero-Dependency Portability.**

- 🚀 **Zero-Dependency Mode**: Run the app on any Windows PC without installing Python.
- 📌 **Smart Header Pin**: Toggle "Always on Top" instantly with the integrated header icon.
- 🔤 **Font Library**: Choose from 7 curated fonts (Handwriting, Modern, Bengali, etc.).
- 🇧🇩 **Auto-Bengali Engine**: Intelligent detection that switches to **Li Ador Noirrit** for perfect Bengali rendering.
- 🛠️ **Redesigned Control Panel**: A centralized hub to manage your notes and Windows integration.
- 🗸 **Interactive Checklist Mode**: Create and manage TODO lists with a unique tri-state toggle.
- 🎨 **Harmonious Palette**: Six premium themes designed for focus and aesthetics.

---

## 🚀 Quick Start (No Python Required)

VibePad is now **Standalone**. You don't need Python installed to use it!

1.  **Download** the latest release folder.
2.  **Double-click** `VibePad_Control_Panel.exe` to manage your notes.
3.  **Click** `Launch VibePad` to start creating!

*Tip: Use `setup_autostart.bat` to have your notes ready every time you log in.*

---

## 💎 Core Features

### 1. Realistic Handwriting Aesthetics
Uses the high-quality **Segoe Print** font by default to mimic real pen-on-paper feel, paired with modern micro-animations and borderless design.

### 2. Live Markdown Formatting
Select text to reveal the **Floating Toolbar**. Apply styles instantly:
- `# Headers` for hierarchy.
- `**Bold**` for importance.
- `*Italics*` for notes.
- *Syntax markers auto-hide when focus is lost for a clean look.*

### 3. Smart Window Management
- **Pin Header**: Keeps notes "Always on Top" for reference.
- **Auto-Save**: Every keystroke is saved locally in your AppData.
- **Dynamic Scaling**: Modern resize handle (◢) for flexible note sizes.

---

## ⌨️ Power User Shortcuts

| Shortcut | Action |
| :-- | :-- |
| **Ctrl + N** | Create a New Note |
| **Ctrl + P** | Toggle Pin (Always on Top) |
| **Ctrl + D** | Delete Current Note |
| **Double-Click Title** | Inline Rename Note |
| **Right-Click** | Full Options Menu |

---

## 📂 Project Structure

- `VibePad_Control_Panel.exe`: The main hub for users.
- `VibePad.exe`: The core note engine.
- `Start_VibePad.bat`: Quick-start launcher.
- `setup_autostart.bat`: Enables Windows startup integration.
- `VibePad_Cleaner.bat`: Safely stops processes and resets data.
- `build_exe.bat`: (For Developers) Rebuilds the executables from source.

---

## 🛠️ Developer Guide (Running from Source)

If you wish to modify the code or contribute:

1.  **Install Python 3.12+** and ensure it's added to your PATH.
2.  **Clone the Repo**:
    ```bash
    git clone https://github.com/bappykumar/VibePad.git
    cd VibePad
    ```
3.  **Run the Script**:
    ```bash
    python VibePad.py
    ```
4.  **Rebuild EXEs**:
    ```bash
    pip install pyinstaller
    build_exe.bat
    ```

---

## 🌍 Data Storage
Your data is stored securely in your local environment:
- **Windows**: `%APPDATA%\VibePad\notes.json`

---

## 🤝 Developed By
**Bappy Kumar**
*Visualizer | Vibe Coder*

Support: [🌐 Telegram Community](https://t.me/designbd2)

---

<div align="center">
  <p>© 2026 VibePad Project. Designed for the aesthetics of productivity.</p>
</div>
