# <img src="note.png" width="36" height="36" alt="Notes Icon" align="center" /> Notes - Modern & Transparent Note App (v1.0.0)

A sleek, fast, and minimalist frameless desktop note-taking application for Windows, built with **Python** and **PySide6**. Features a translucent *Glassmorphism* dark UI, real-time auto-saving to local Markdown (`.md`) files, multi-tab note management, dynamic project organization, and built-in bilingual support (**English / Portuguese**).

---

## ✨ Features

- 💎 **Translucent Glassmorphic UI**: Frameless dark interface with a real-time window opacity slider (100% solid opacity support).
- 🌐 **Bilingual Support (EN / PT)**: Single-click language switcher in the header to instantly toggle between English and Portuguese.
- ⚡ **Instant Note Creation (`+`)**: One-click instant note creation beside tabs without intrusive prompt dialogs.
- 🔄 **Real-Time Auto-Save**: Saves every keystroke immediately to local disk Markdown files. Never lose your ideas.
- 📁 **Markdown Project Management**: Manage notes inside structured project folders with persistent `.notes.json` metadata.
- 🎯 **Lucide Vector Icons**: Clean monochrome vectors for crisp display on High-DPI monitors.
- 🎨 **Custom Glass Dialogs**: Frameless dark modal dialogs for project/note creation, renaming, and confirmation.
- ⌨️ **Productivity Shortcuts**:
  - `Ctrl + N`: Create a new note instantly.
  - `Ctrl + S`: Save all notes and projects.
  - `Ctrl + W`: Close the current active note/tab.

---

## 🚀 Getting Started

The codebase uses **dynamic relative pathing** for `sys.executable`, enabling the app to run from any directory without hardcoded file paths.

### Prerequisites
- **Python 3.10+** installed on your machine.

### 1. Clone the Repository
```bash
git clone https://github.com/humberto-jezus/Notes.git
cd Notes
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

---

## 📦 Building Standalone Executable (.exe)

To package the application into a single portable `.exe` binary without console window:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Run PyInstaller build:
```bash
pyinstaller --onefile --windowed --icon="icon.ico" --name="Notes" --hidden-import=PySide6.QtSvg --clean app.py
```

The compiled binary `Notes.exe` will be located in the `dist/` folder.

---

## 📁 Repository Structure

```text
├── app.py              # Main application source code
├── make_icon.py        # Utility script to convert PNG to transparent ICO
├── note.png            # Application logo icon
├── icon.ico            # Windows executable icon file
├── requirements.txt    # Dependencies (PySide6, Pillow, numpy)
├── .gitignore          # Git ignore rules
└── README.md           # Project documentation
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
