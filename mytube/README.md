# Wgetube

Professional Media Downloader, Looper, and Clipper for Pro Memorization.

## 🚀 Quick Start
We use a `Makefile` to simplify the workflow and `uv` for lightning-fast dependency management.

```bash
# 1. Install everything
make install

# 2. Run the Pro TUI Dashboard
make run-tui

# 3. Or use the Interactive CLI Downloader
make run-download
```

---

## 🚀 Overview
Wgetube is a terminal-first tool designed for high-performance media downloading and rote learning (e.g., Quran Hifz). It provides a full suite of tools to download, loop, and clip media directly from your terminal.

1.  **TUI (Pro Mode):** A trendy Terminal User Interface built with `Textual` for downloading, looping, and clipping with visual feedback.
2.  **CLI (Interactive):** A fast, question-based interface for batch downloading playlists, shorts, and videos.
3.  **Clipper (CLI):** Instant FFmpeg-powered clipping for precision media cutting.

---

## 🛠 Usage (`/cli`)

### Starting the TUI
```bash
uv run cli/main.py tui
```
*The TUI provides a dashboard for all features (Download, Loop, Clip).*

### Starting the Interactive Downloader
```bash
uv run cli/main.py download
```
*Supports Shorts, Videos, and Playlists with batch selection and resolution control.*

### Fast Clipping
```bash
uv run cli/main.py clip path/to/video.mp4 --start 00:01:00 --end 00:01:30
```

---

## 🎨 Design Philosophy
-   **Terminal First:** Focused on efficiency and high-signal terminal interfaces.
-   **Privacy First:** No servers, no accounts. Your data stays on your machine.
-   **Robustness:** Powered by `yt-dlp` and `FFmpeg` for industrial-grade reliability.

---

## 📄 License
MIT
