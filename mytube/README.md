# Wgetube

Professional Media Downloader, Looper, and Clipper for Pro Memorization.

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

## 🚀 Overview
Wgetube is a terminal-first tool designed for high-performance media downloading and rote learning (e.g., Quran Hifz). It provides a full suite of tools to download, loop, and clip media directly from your terminal.

1.  **TUI (Pro Mode):** A trendy Terminal User Interface built with `Textual` for downloading, looping, and clipping with visual feedback. Run with `uv run mytube-tui`.
2.  **CLI (Interactive):** A fast, question-based interface for batch downloading playlists, shorts, and videos. Run with `uv run mytube-cli download`.
3.  **Clipper (CLI):** Instant FFmpeg-powered clipping for precision media cutting. Run with `uv run mytube-cli clip`.

---

## 🛠 Usage

### Pro TUI Dashboard
```bash
uv run mytube-tui
```
*The TUI provides a dashboard for all features (Download, Loop, Clip).*

### Interactive Downloader
```bash
uv run mytube-cli download
```
*Supports Shorts, Videos, and Playlists with batch selection and resolution control.*

### Fast Clipping
```bash
uv run mytube-cli clip path/to/video.mp4 --start 00:01:00 --end 00:01:30
```

---

## 🎨 Design Philosophy
-   **Terminal First:** Focused on efficiency and high-signal terminal interfaces.
-   **Privacy First:** No servers, no accounts. Your data stays on your machine.
-   **Robustness:** Powered by `yt-dlp` and `FFmpeg` for industrial-grade reliability.

---

## 📄 License
MIT
