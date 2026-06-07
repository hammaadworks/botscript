from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, Static, Label, ProgressBar, TabbedContent, TabPane, Log, SelectionList, Collapsible
from textual.widgets.selection_list import Selection
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual import on, work
import yt_dlp
import os
import vlc
import time
import ffmpeg
import subprocess
from typing import Optional, List

class WgetubeApp(App):
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
    .info-panel {
        background: #1e293b;
        border: solid #334155;
        padding: 1;
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
        
        # Initialize VLC early to check for library availability
        try:
            self.vlc_instance = vlc.Instance()
            self.player = self.vlc_instance.media_player_new()
        except Exception:
            self.vlc_instance = None
            self.player = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main-container"):
            # System Status Bar
            with Horizontal(classes="system-status"):
                yield Label("VLC: " + ("[green]OK[/green]" if self.player else "[red]Missing[/red]"))
                yield Label("  FFmpeg: " + ("[green]OK[/green]" if self.check_ffmpeg() else "[red]Missing[/red]"))

            with TabbedContent():
                with TabPane("Download", id="tab-download"):
                    yield Label("Professional Media Downloader", classes="section-title")
                    yield Input(placeholder="Paste URL (YouTube, Twitter, IG, etc.)", id="dl-url")
                    yield Button("Fetch Details", variant="default", id="btn-fetch")
                    
                    with Vertical(id="playlist-selection"):
                        yield Label("Select items to download:", classes="stat-label")
                        yield SelectionList(id="entry-list")
                    
                    with Collapsible(title="Download Settings", id="dl-config"):
                        yield Input(placeholder="Save to (e.g., downloads/)", id="dl-base-path", classes="config-input")
                        yield Input(placeholder="Custom Folder Name", id="dl-folder-name", classes="config-input")
                    
                    with Horizontal():
                        yield Button("Video", variant="primary", id="btn-dl-video")
                        yield Button("Audio", variant="success", id="btn-dl-audio")
                    
                    yield ProgressBar(id="dl-progress", show_percentage=True)
                    yield Log(id="download-log")

                with TabPane("Looper Tutor", id="tab-loop"):
                    yield Label("A-B Memorization Mode", classes="section-title")
                    yield Input(placeholder="Path to audio/video file", id="loop-path")
                    with Horizontal():
                        yield Input(placeholder="Start (s)", id="loop-start", value="0")
                        yield Input(placeholder="End (s)", id="loop-end")
                    yield Button("Start Looping", variant="primary", id="btn-start-loop")
                    yield Button("Stop", variant="error", id="btn-stop-loop")
                    with Vertical(id="loop-stats"):
                        yield Label("REPETITIONS", classes="stat-label")
                        yield Label("0", id="stat-count", classes="stat-value")

                with TabPane("Clipper", id="tab-clip"):
                    yield Label("Professional Clipping", classes="section-title")
                    yield Input(placeholder="Path to source file", id="clip-path")
                    with Horizontal():
                        yield Input(placeholder="Start (00:01:20)", id="clip-start")
                        yield Input(placeholder="End (00:01:45)", id="clip-end")
                    yield Button("Generate Clip", variant="warning", id="btn-clip")
                    yield Log(id="clip-log")

        yield Footer()

    def check_ffmpeg(self):
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return True
        except:
            return False

    @on(Button.Pressed, "#btn-fetch")
    @work(exclusive=True, thread=True)
    def action_fetch_metadata(self):
        url_input = self.query_one("#dl-url").value.strip()
        if not url_input: 
            self.notify("URL is required", severity="warning")
            return
        
        log = self.query_one("#download-log")
        self.call_from_thread(log.write_line, f"[blue]Fetching:[/blue] {url_input}")
        
        ydl_opts = {
            'extract_flat': True, 
            'quiet': True,
            'no_warnings': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url_input, download=False)
                if not info:
                    self.call_from_thread(log.write_line, "[red]Could not fetch info.[/red]")
                    return

                self.fetched_entries = []
                
                if 'entries' in info:
                    self.is_playlist = True
                    entries = [e for e in info['entries'] if e]
                    self.fetched_entries = entries
                    
                    options = [Selection(e.get('title') or e.get('id') or f"Item {i+1}", i, True) for i, e in enumerate(entries)]
                    
                    def update_ui():
                        sel_list = self.query_one("#entry-list", SelectionList)
                        sel_list.clear()
                        sel_list.add_options(options)
                        self.query_one("#playlist-selection").add_class("show")
                        self.query_one("#dl-folder-name").value = info.get('title', 'Playlist')
                        log.write_line(f"[green]Found Playlist:[/green] {info.get('title')} ({len(entries)} items)")
                    
                    self.call_from_thread(update_ui)
                else:
                    self.is_playlist = False
                    self.fetched_entries = [info]
                    
                    def update_ui_single():
                        self.query_one("#playlist-selection").remove_class("show")
                        log.write_line(f"[green]Found Video:[/green] {info.get('title')}")
                    
                    self.call_from_thread(update_ui_single)
                    
            except Exception as e:
                self.call_from_thread(log.write_line, f"[red]Error: {str(e)}[/red]")

    @on(Button.Pressed, "#btn-dl-video")
    def action_download_video(self):
        self.start_download(False)

    @on(Button.Pressed, "#btn-dl-audio")
    def action_download_audio(self):
        self.start_download(True)

    @work(exclusive=True, thread=True)
    def start_download(self, audio_only: bool):
        url_input = self.query_one("#dl-url").value.strip()
        if not url_input: return

        log = self.query_one("#download-log")
        progress = self.query_one("#dl-progress")
        base_path = self.query_one("#dl-base-path").value.strip() or "downloads"
        folder_name = self.query_one("#dl-folder-name").value.strip()
        
        output_dir = base_path
        if folder_name:
            output_dir = os.path.join(base_path, folder_name)
        
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                self.call_from_thread(log.write_line, f"[red]Directory Error: {str(e)}[/red]")
                return

        selected_indices = []
        if self.is_playlist:
            # We must call query_one in the main thread's context via a helper or safely
            # But in work(thread=True), we can query widgets directly if they are thread-safe or we use call_from_thread
            # Actually, query_one is usually okay to read from in worker threads in modern Textual, but let's be safe.
            def get_selection():
                return list(self.query_one("#entry-list").selected)
            selected_indices = self.call_from_thread(get_selection)
            
            if not selected_indices:
                self.call_from_thread(log.write_line, "[yellow]No items selected.[/yellow]")
                return
        else:
            selected_indices = [0]

        total_items = len(selected_indices)
        self.call_from_thread(log.write_line, f"[blue]Downloading {total_items} item(s)...[/blue]")

        for idx, entry_idx in enumerate(selected_indices):
            if idx >= len(self.fetched_entries): continue # Safety
            
            entry = self.fetched_entries[entry_idx]
            item_url = entry.get('url') or entry.get('webpage_url') or url_input
            
            def hook(d):
                if d['status'] == 'downloading':
                    total = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
                    p = d.get('downloaded_bytes', 0) / total
                    overall_p = ((idx + p) / total_items) * 100
                    self.call_from_thread(progress.update, progress=overall_p)
                elif d['status'] == 'finished':
                    self.call_from_thread(log.write_line, f"[green]Finished:[/green] {os.path.basename(d['filename'])}")

            ydl_opts = {
                'format': 'bestaudio/best' if audio_only else 'bestvideo+bestaudio/best',
                'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
                'progress_hooks': [hook],
                'quiet': True,
                'noplaylist': True,
                'no_warnings': True,
            }
            if audio_only:
                ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([item_url])
                except Exception as e:
                    self.call_from_thread(log.write_line, f"[red]Failed item {idx+1}: {str(e)}[/red]")
        
        self.call_from_thread(progress.update, progress=100)
        self.call_from_thread(log.write_line, "[bold green]Download queue finished![/bold green]")

    @on(Button.Pressed, "#btn-start-loop")
    def action_start_loop(self):
        if not self.player:
            self.notify("VLC Media Player not found on your system.", severity="error")
            return
            
        file_path = self.query_one("#loop-path").value.strip()
        start_val = self.query_one("#loop-start").value
        start = float(start_val if start_val else 0)
        end_val = self.query_one("#loop-end").value
        end = float(end_val) if end_val else None

        if not os.path.exists(file_path):
            self.notify("File does not exist!", severity="error")
            return

        try:
            media = self.vlc_instance.media_new(file_path)
            self.player.set_media(media)
            self.player.play()
            
            self.is_looping = True
            self.loop_count = 0
            self.query_one("#stat-count").update("0")
            
            self.run_loop_monitor(start, end)
        except Exception as e:
            self.notify(f"Playback Error: {e}", severity="error")

    @work(exclusive=True, thread=True)
    def run_loop_monitor(self, start, end):
        time.sleep(1) # Wait for buffer
        duration = (self.player.get_length() / 1000.0) if end is None else end
        while self.is_looping:
            try:
                current = self.player.get_time() / 1000.0
                if current >= duration:
                    self.player.set_time(int(start * 1000))
                    self.loop_count += 1
                    self.call_from_thread(self.query_one("#stat-count").update, str(self.loop_count))
            except:
                break
            time.sleep(0.1)

    @on(Button.Pressed, "#btn-stop-loop")
    def action_stop_loop(self):
        if self.player:
            self.is_looping = False
            self.player.stop()

    @on(Button.Pressed, "#btn-clip")
    @work(exclusive=True, thread=True)
    def action_clip(self):
        path = self.query_one("#clip-path").value.strip()
        start = self.query_one("#clip-start").value.strip()
        end = self.query_one("#clip-end").value.strip()
        log = self.query_one("#clip-log")

        if not os.path.exists(path):
            self.call_from_thread(log.write_line, "[red]Source file not found.[/red]")
            return

        if not start or not end:
            self.call_from_thread(log.write_line, "[yellow]Please provide start and end timestamps.[/yellow]")
            return

        name, ext = os.path.splitext(path)
        output = f"{name}_clip{ext}"
        self.call_from_thread(log.write_line, f"Processing: {path}...")
        
        try:
            (ffmpeg.input(path, ss=start, to=end).output(output, c='copy').run(overwrite_output=True, quiet=True))
            self.call_from_thread(log.write_line, f"[green]Clip created:[/green] {output}")
        except Exception as e:
            self.call_from_thread(log.write_line, f"[red]Clipping Error: {str(e)}[/red]")

if __name__ == "__main__":
    app = WgetubeApp()
    app.run()
