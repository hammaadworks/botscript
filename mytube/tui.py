from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, Label, ProgressBar, TabbedContent, TabPane, Log, SelectionList, Collapsible
from textual.widgets.selection_list import Selection
from textual.containers import Container, Horizontal, Vertical
from textual import on, work
import yt_dlp
import os
import vlc
import time
import subprocess
from typing import List

class mytubeApp(App):
    """
    mytube: Professional Terminal Media Hub
    Consolidated Video Hub for Downloading, Looping, and Advanced Clipping.
    """
    CSS = """
    Screen {
        background: #0f172a;
    }
    #main-container {
        padding: 1;
    }
    .section-title {
        text-style: bold;
        color: #38bdf8;
        margin-bottom: 1;
    }
    #download-log, #clip-log {
        height: 10;
        background: #000;
        border: solid #334155;
        margin-top: 1;
        color: #e2e8f0;
    }
    Button {
        margin-top: 1;
        width: 100%;
    }
    #loop-stats {
        height: auto;
        border: double #38bdf8;
        padding: 1;
        text-align: center;
        background: #1e293b;
    }
    .stat-label {
        color: #94a3b8;
    }
    .stat-value {
        text-style: bold;
        color: #fbbf24;
    }
    #playlist-selection {
        height: 12;
        border: solid #334155;
        display: none;
        margin-bottom: 1;
    }
    #playlist-selection.show {
        display: block;
    }
    .config-input {
        margin-top: 1;
    }
    .system-status {
        margin-bottom: 1;
        padding: 0 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.player = None
        self.vlc_instance = None
        self.loop_count = 0
        self.is_looping = False
        self.fetched_entries = []
        self.is_playlist = False
        
        try:
            self.vlc_instance = vlc.Instance()
            self.player = self.vlc_instance.media_player_new()
        except Exception:
            self.vlc_instance = None
            self.player = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main-container"):
            with Horizontal(classes="system-status"):
                yield Label("VLC: " + ("[green]OK[/green]" if self.player else "[red]Missing[/red]"))
                yield Label("  FFmpeg: " + ("[green]OK[/green]" if self.check_ffmpeg() else "[red]Missing[/red]"))

            with TabbedContent():
                with TabPane("Download", id="tab-download"):
                    yield Label("mytube Pro Downloader", classes="section-title")
                    yield Input(placeholder="Paste YouTube URL (Shorts/Video/Playlist)...", id="dl-url")
                    yield Button("Analyze Link", variant="default", id="btn-fetch")
                    
                    with Vertical(id="playlist-selection"):
                        yield Label("Individual Selection (Playlist/Series):", classes="stat-label")
                        yield SelectionList(id="entry-list")
                    
                    with Collapsible(title="Advanced Settings", id="dl-config"):
                        yield Input(placeholder="Save to (default: downloads/)", id="dl-base-path", classes="config-input")
                        yield Input(placeholder="Custom Folder Name", id="dl-folder-name", classes="config-input")
                    
                    with Horizontal():
                        yield Button("Video", variant="primary", id="btn-dl-video")
                        yield Button("Audio (MP3)", variant="success", id="btn-dl-audio")
                    
                    yield ProgressBar(id="dl-progress", show_percentage=True)
                    yield Log(id="download-log")

                with TabPane("A-B Looper", id="tab-loop"):
                    yield Label("Memorization Mode (Local Media)", classes="section-title")
                    yield Input(placeholder="Absolute Path to Media...", id="loop-path")
                    with Horizontal():
                        yield Input(placeholder="Start (s)", id="loop-start", value="0")
                        yield Input(placeholder="End (s)", id="loop-end")
                    yield Button("Start Looping", variant="primary", id="btn-start-loop")
                    yield Button("Stop", variant="error", id="btn-stop-loop")
                    with Vertical(id="loop-stats"):
                        yield Label("REPETITIONS", classes="stat-label")
                        yield Label("0", id="stat-count", classes="stat-value")

                with TabPane("Advanced Clipper", id="tab-clip"):
                    yield Label("Segment Stitching Mode", classes="section-title")
                    yield Input(placeholder="Source File Path...", id="clip-path")
                    yield Input(placeholder="Segments (0:10,0:20; 1:00,1:30)", id="clip-segments")
                    yield Button("Clip & Stitch", variant="warning", id="btn-clip")
                    yield Log(id="clip-log")

        yield Footer()

    def check_ffmpeg(self):
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except: return False

    @on(Button.Pressed, "#btn-fetch")
    @work(exclusive=True, thread=True)
    def action_fetch_metadata(self):
        url = self.query_one("#dl-url").value.strip()
        if not url: return
        
        log = self.query_one("#download-log")
        self.call_from_thread(log.write_line, f"[blue]Analyzing:[/blue] {url}")
        
        ydl_opts = {'extract_flat': 'in_playlist', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    self.is_playlist = True
                    self.fetched_entries = [e for e in info['entries'] if e]
                    options = [Selection(e.get('title') or e.get('id'), i, True) for i, e in enumerate(self.fetched_entries)]
                    
                    def update_ui():
                        self.query_one("#entry-list", SelectionList).clear()
                        self.query_one("#entry-list", SelectionList).add_options(options)
                        self.query_one("#playlist-selection").add_class("show")
                        self.query_one("#dl-folder-name").value = info.get('title', 'Playlist')
                        log.write_line(f"[green]Playlist Identified:[/green] {info.get('title')}")
                    self.call_from_thread(update_ui)
                else:
                    self.is_playlist = False
                    self.fetched_entries = [info]
                    def update_ui_single():
                        self.query_one("#playlist-selection").remove_class("show")
                        log.write_line(f"[green]Media Identified:[/green] {info.get('title')}")
                    self.call_from_thread(update_ui_single)
            except Exception as e:
                self.call_from_thread(log.write_line, f"[red]Error:[/red] {str(e)}")

    @on(Button.Pressed, "#btn-dl-video")
    def action_dl_video(self): self.start_download(False)

    @on(Button.Pressed, "#btn-dl-audio")
    def action_dl_audio(self): self.start_download(True)

    @work(exclusive=True, thread=True)
    def start_download(self, audio_only: bool):
        log = self.query_one("#download-log")
        progress = self.query_one("#dl-progress")
        base = self.query_one("#dl-base-path").value.strip() or "downloads"
        folder = self.query_one("#dl-folder-name").value.strip()
        out_dir = os.path.join(base, folder) if folder else base
        os.makedirs(out_dir, exist_ok=True)

        if self.is_playlist:
            def get_sel(): return list(self.query_one("#entry-list").selected)
            selected = self.call_from_thread(get_sel)
        else: selected = [0]

        total = len(selected)
        for i, idx in enumerate(selected):
            entry = self.fetched_entries[idx]
            url = entry.get('webpage_url') or entry.get('url') or self.query_one("#dl-url").value
            
            def hook(d):
                if d['status'] == 'downloading':
                    p = d.get('downloaded_bytes', 0) / (d.get('total_bytes') or 1)
                    self.call_from_thread(progress.update, progress=((i + p) / total) * 100)
            
            opts = {
                'format': 'bestaudio/best' if audio_only else 'bestvideo+bestaudio/best',
                'outtmpl': f'{out_dir}/%(title)s.%(ext)s',
                'progress_hooks': [hook], 'quiet': True
            }
            if audio_only: opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                try: ydl.download([url])
                except Exception as e: self.call_from_thread(log.write_line, f"[red]Failed:[/red] {str(e)}")
        
        self.call_from_thread(progress.update, progress=100)
        self.call_from_thread(log.write_line, "[bold green]Success: Batch Download Finished![/bold green]")

    # --- A-B Looper Logic ---
    @on(Button.Pressed, "#btn-start-loop")
    def action_loop(self):
        path = self.query_one("#loop-path").value.strip()
        if not os.path.exists(path) or not self.player: return
        start = float(self.query_one("#loop-start").value or 0)
        end = float(self.query_one("#loop-end").value or 0) or None
        
        media = self.vlc_instance.media_new(path)
        self.player.set_media(media)
        self.player.play()
        self.is_looping = True
        self.loop_count = 0
        self.monitor_loop(start, end)

    @work(exclusive=True, thread=True)
    def monitor_loop(self, start, end):
        time.sleep(1)
        dur = (self.player.get_length() / 1000.0) if end is None else end
        while self.is_looping:
            try:
                curr = self.player.get_time() / 1000.0
                if curr >= dur:
                    self.player.set_time(int(start * 1000))
                    self.loop_count += 1
                    self.call_from_thread(self.query_one("#stat-count").update, str(self.loop_count))
            except: break
            time.sleep(0.1)

    @on(Button.Pressed, "#btn-stop-loop")
    def action_stop(self):
        self.is_looping = False
        if self.player: self.player.stop()

    @on(Button.Pressed, "#btn-clip")
    @work(exclusive=True, thread=True)
    def action_advanced_clip(self):
        path = self.query_one("#clip-path").value.strip()
        raw = self.query_one("#clip-segments").value.strip()
        log = self.query_one("#clip-log")
        if not os.path.exists(path) or not raw: return

        try:
            segments = [s.strip().split(',') for s in raw.split(';')]
            name, ext = os.path.splitext(path)
            output = f"{name}_stitched{ext}"
            
            clips = []
            for i, (s, e) in enumerate(segments):
                tmp = f"temp_{i}{ext}"
                subprocess.run(["ffmpeg", "-i", path, "-ss", s.strip(), "-to", e.strip(), "-c", "copy", tmp, "-y"], check=True, capture_output=True)
                clips.append(tmp)

            with open("list.txt", "w") as f:
                for c in clips: f.write(f"file '{c}'\n")
            
            subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", "list.txt", "-c", "copy", output, "-y"], check=True, capture_output=True)
            for c in clips: os.remove(c)
            os.remove("list.txt")
            self.call_from_thread(log.write_line, f"[green]Stitched clip created:[/green] {output}")
        except Exception as e:
            self.call_from_thread(log.write_line, f"[red]Clip Error:[/red] {str(e)}")

if __name__ == "__main__":
    mytubeApp().run()
