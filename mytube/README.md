# Wgetube

Professional Media Downloader, Looper, and Clipper for Pro Memorization.

## 🚀 Quick Start
We use a `Makefile` to simplify the workflow.

```bash
# 1. Install everything
make install

# 2. Run the Pro TUI Dashboard
make run-tui

# 3. Run the Web GUI
make run-web
```

---

## 🚀 Overview
Wgetube is a dual-interface tool designed for high-performance media downloading and rote learning (e.g., Quran Hifz). 
...
1.  **TUI (Pro Mode):** A trendy Terminal User Interface built with `Textual` for downloading, looping, and clipping directly in your terminal.
2.  **Web (GUI):** A beautiful, minimal client-side app for visual A-B looping, historical loop tracking, and local video clipping using FFmpeg WASM.

---

## 📚 Documentation
Detailed guides are available in the [@docs](./@docs) folder:
- [Production & Startup Guide](./@docs/PRODUCTION.md)

---

## 🛠 TUI Usage (`/cli`)
Built with Python, Typer, and Textual.

### Setup
```bash
# Install dependencies using uv
uv sync
```

### Starting the TUI
```bash
uv run cli/main.py tui
```
*The TUI provides a dashboard for all features (Download, Loop, Clip).*

### Starting the Interactive Downloader
```bash
uv run cli/main.py interactive
```
*A faster, CLI-based interactive playlist downloader.*

---

## 🌐 Web App (`/web`)
A minimal Vite + React application focused on user privacy and local processing.
...
### Features
-   **Looper Tutor:** Set precise A-B points and track loop counts.
-   **Local Clipping:** Trim and export clips entirely in your browser using `ffmpeg.wasm`.
-   **Zero Login:** All progress and history are saved locally in your browser's IndexedDB.

### Setup
```bash
cd web
pnpm install
pnpm dev
```

---

## 🎨 Design Philosophy
-   **Minimalist:** Focused on the task of memorization without distractions.
-   **Privacy First:** No servers, no accounts. Your data stays on your machine.
-   **Trendy TUI:** Professional, high-signal terminal interface for "Pro" users.

---

## 📄 License
MIT
