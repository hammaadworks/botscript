# 🚀 Wgetube Production Readiness & Deployment Guide

Wgetube is ready for production. Follow these steps to start the apps locally or deploy them to the web.

---

## 🛠 System Requirements (CRITICAL)

The TUI and Web App rely on these system-level tools. If you see "Missing" in the TUI status bar, follow these steps:

### 1. VLC Media Player
Required for the **Looper Tutor** (audio/video repetition).
- **Mac:** `brew install --cask vlc`
- **Linux:** `sudo apt install vlc`
- **Windows:** Download from [videolan.org](https://www.videolan.org/).

### 2. FFmpeg
Required for **Clipping** and high-quality audio extraction.
- **Mac:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`
- **Windows:** `choco install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/).

---

## 💻 TUI App (Terminal Dashboard)

The TUI is a professional "Pro Mode" dashboard built with `Textual`.

### 1. Installation
Ensure you have Python 3.12+ and `uv` installed.
```bash
# Install dependencies
uv sync
```

### 2. Starting the TUI
Run the dashboard with:
```bash
uv run cli/main.py
```

### 3. TUI Features
- **Download Tab:** 
    - **Fetch Metadata:** Paste a URL and click fetch to see playlist details.
    - **Selection List:** For playlists, you can check/uncheck exactly which videos you want.
    - **Custom Config:** Expand the configuration to set a custom "Base Path" or "Folder Name" for your downloads.
    - **Batch Progress:** A live progress bar tracks the overall progress of all selected items.
- **Looper Tab:** Load an audio/video file, set A and B points, and start the repetition tracker.
- **Clipper Tab:** Enter a file path and timestamps to generate a clip locally.

---

## 🌐 Web App (GUI)

The Web App is a client-side Vite application. It is ready to be hosted for free on **Vercel**, **Netlify**, or **GitHub Pages**.

### 1. Local Development
```bash
cd web
pnpm install
pnpm dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

### 2. Production Build
To create a production-ready bundle:
```bash
cd web
pnpm build
```
This generates a `dist/` folder containing optimized HTML, CSS, and JS.

### 3. Deployment (Production)
Since it is a static Vite app, deployment is instant:
- **Vercel:** Just run `vercel` in the `web` directory.
- **Netlify:** Drag and drop the `dist/` folder.
- **Manual:** Serve the `dist/` folder using any static web server (e.g., `pnpm dlx serve dist`).

---

## 🛠 Production Quality Checks
- [x] **Privacy:** 100% Client-side. No user data is sent to a server.
- [x] **Persistence:** Uses IndexedDB for reliable local storage of loop counts.
- [x] **Performance:** FFmpeg WASM handles video processing on the user's hardware.
- [x] **Responsiveness:** The UI is adaptive and works on iPhones, Androids, and Macs.
- [x] **CORS Awareness:** The Web App is designed to process *local* files. Users download via the CLI and then drop files into the Web App for professional looping/clipping.

---

## 📄 Final Summary of Commands
| Feature | CLI Command | Web UI Tab |
| :--- | :--- | :--- |
| **Download** | `download [url]` | N/A (Local File Drop) |
| **Playlists** | `playlist [url]` | N/A |
| **A-B Looping** | `loop [path]` | "Looper" Tab |
| **Loop Stats** | Automatic (Rich TUI) | "History" Tab |
| **Clipping** | `clip [path]` | "Clipper" Tab |
