# mytube

Professional Terminal Media Hub: Download, Loop, and Advanced Clipping. Designed for high-performance media management and rote learning (e.g., Quran Hifz).

## 🚀 Quick Start

Use `uv` for lightning-fast dependency management and execution.

```bash
# 1. Install everything
uv sync

# 2. Run the Pro TUI Dashboard
uv run mytube-tui

# 3. Or use the Interactive CLI Downloader
uv run mytube-cli download
```

---

## 🛠 System Requirements (CRITICAL)

The TUI and CLI rely on these system-level tools. Ensure they are installed and in your PATH:

### 1. VLC Media Player
Required for the **A-B Looper** (audio/video repetition).
- **Mac:** `brew install --cask vlc`
- **Linux:** `sudo apt install vlc`
- **Windows:** Download from [videolan.org](https://www.videolan.org/).

### 2. FFmpeg
Required for **Advanced Clipping** and high-quality audio extraction.
- **Mac:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`
- **Windows:** `choco install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/).

---

## 🚀 Overview

`mytube` provides a full suite of tools to download, loop, and clip media directly from your terminal.

1.  **TUI (Pro Mode):** A trendy Terminal User Interface built with `Textual` for downloading, looping, and clipping with visual feedback. Run with `uv run mytube-tui`.
2.  **CLI (Interactive):** A fast, question-based interface for batch downloading playlists, shorts, and videos. Run with `uv run mytube-cli download`.
3.  **Clipper (Advanced):** CLI mode for precision media cutting and multi-segment stitching. Run with `uv run mytube-cli clip`.

---

## 🛠 Detailed Usage

### Pro TUI Dashboard
```bash
uv run mytube-tui
```
*   **Download Tab:** 
    *   **Analyze Link:** Paste a URL (Shorts/Video/Playlist) to see details.
    *   **Individual Selection:** For playlists, check/uncheck exactly which items you want.
    *   **Advanced Settings:** Set custom base paths or subfolder names.
    *   **Live Progress:** Visual progress bars for batch downloads.
*   **A-B Looper Tab:** Load a local media file, set precise start/end points, and track repetitions automatically.
*   **Advanced Clipper Tab:** Multi-segment stitching mode. enter segments as `start,end; start,end`.

### Interactive Downloader
```bash
uv run mytube-cli download
```
*   Supports all YouTube link variations (Mobile, Desktop, Shorts).
*   Automatic playlist detection with batch selection.
*   Resolution control (360p, 720p, 1080p, best).
*   Dedicated MP3 audio extraction mode.

### Advanced Clipping & Stitching
```bash
uv run mytube-cli clip path/to/video.mp4
```
*   Extract multiple segments from a single source and stitch them into one high-quality file.
*   Input format: `00:10,00:20; 01:00,01:30`.

---

## 🎨 Design Philosophy
-   **Terminal First:** Focused on efficiency and high-signal terminal interfaces.
-   **Privacy First:** 100% local processing. No servers, no accounts.
-   **Industrial Grade:** Powered by `yt-dlp` and `FFmpeg` for rock-solid reliability.

---

## 📄 License
MIT
