from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, Static, Label, ProgressBar, TabbedContent, TabPane, Log, SelectionList, Collapsible
from textual.widgets.selection_list import Selection
from textual.containers import Container, Horizontal, Vertical
from textual import on, work
import yt_dlp
import os
import vlc
import time
import subprocess
from typing import List

class WgetubeApp(App):
    """
    Wgetube: Professional Terminal Media Hub
    Supports robust downloading of Shorts, Videos, and Playlists.
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
                    yield Label("Pro Downloader (Shorts/Videos/Playlists)", classes="section-title")
                    yield Input(placeholder="Paste YouTube Link...", id="dl-url")
                    yield Button("Fetch Media Details", variant="default", id="btn-fetch")
                    
                    with Vertical(id="playlist-selection"):
                        yield Label("Select items to download:", classes="stat-label")
                        yield SelectionList(id="entry-list")
                    
                    with Collapsible(title="Download Settings", id="dl-config"):
                        yield Input(placeholder="Save to (default: downloads/)", id="dl-base-path", classes="config-input")
                        yield Input(placeholder="Custom Subfolder Name", id="dl-folder-name", classes="config-input")
                    
                    with Horizontal():
                        yield Button("Download Video", variant="primary", id="btn-dl-video")
                        yield Button("Download Audio (MP3)", variant="success", id="btn-dl-audio")
                    
                    yield ProgressBar(id="dl-progress", show_percentage=True)
                    yield Log(id="download-log")

                with TabPane("Looper Tutor", id="tab-loop"):
                    yield Label("A-B Memorization Mode", classes="section-title")
                    yield Input(placeholder="Path to media file", id="loop-path")
                    with Horizontal():
                        yield Input(placeholder="Start (s)", id="loop-start", value="0")
                        yield Input(placeholder="End (s)", id="loop-end")
                    yield Button("Start Looping", variant="primary", id="btn-start-loop")
                    yield Button("Stop", variant="error", id="btn-stop-loop")
                    with Vertical(id="loop-stats"):
                        yield Label("REPETITIONS", classes="stat-label")
                        yield Label("0", id="stat-count", classes="stat-value")

                with TabPane("Clipper", id="tab-clip"):
                    yield Label("Quick Clip Generator", classes="section-title")
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
        self.call_from_thread(log.write_line, f"[blue]Analyzing Link:[/blue] {url_input}")
        
        ydl_opts = {
            'extract_flat': 'in_playlist', 
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url_input, download=False)
                if not info:
                    self.call_from_thread(log.write_line, "[red]Failed to retrieve info.[/red]")
                    return

                self.fetched_entries = []
                
                # Check if it's a playlist or multiple entries
                if 'entries' in info:
                    self.is_playlist = True
                    entries = [e for e in info['entries'] if e]
                    self.fetched_entries = entries
                    
                    options = [Selection(e.get('title') or e.get('id') or f"Item {i+1}", i, True) for i, e in enumerate(entries)]
                    
                    def update_ui_playlist():
                        sel_list = self.query_one("#entry-list", SelectionList)
                        sel_list.clear()
                        sel_list.add_options(options)
                        self.query_one("#playlist-selection").add_class("show")
                        self.query_one("#dl-folder-name").value = info.get('title', 'Playlist')
                        log.write_line(f"[green]Found Playlist:[/green] {info.get('title')} ({len(entries)} items)")
                    
                    self.call_from_thread(update_ui_playlist)
                else:
                    # Individual Video or Short
                    self.is_playlist = False
                    self.fetched_entries = [info]
                    
                    def update_ui_single():
                        self.query_one("#playlist-selection").remove_class("show")
                        media_type = "Short" if info.get('duration', 0) < 65 and 'shorts' in url_input else "Video"
                        log.write_line(f"[green]Found {media_type}:[/green] {info.get('title')}")
                        self.query_one("#dl-folder-name").value = "" # Clear folder for single
                    
                    self.call_from_thread(update_ui_single)
                    
            except Exception as e:
                self.call_from_thread(log.write_line, f"[red]Error:[/red] {str(e)}")

    @on(Button.Pressed, "#btn-dl-video")
    def action_download_video(self):
        self.start_download(audio_only=False)

    @on(Button.Pressed, "#btn-dl-audio")
    def action_download_audio(self):
        self.start_download(audio_only=True)

    @work(exclusive=True, thread=True)
    def start_download(self, audio_only: bool):
        url_input = self.query_one("#dl-url").value.strip()
        if not url_input or not self.fetched_entries: 
            self.notify("Please fetch details first", severity="warning")
            return

        log = self.query_one("#download-log")
        progress = self.query_one("#dl-progress")
        base_path = self.query_one("#dl-base-path").value.strip() or "downloads"
        folder_name = self.query_one("#dl-folder-name").value.strip()
        
        output_dir = os.path.join(base_path, folder_name) if folder_name else base_path
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Determine which items to download
        if self.is_playlist:
            def get_selection():
                return list(self.query_one("#entry-list").selected)
            selected_indices = self.call_from_thread(get_selection)
        else:
            selected_indices = [0]

        if not selected_indices:
            self.call_from_thread(log.write_line, "[yellow]No items selected.[/yellow]")
            return

        total_items = len(selected_indices)
        self.call_from_thread(log.write_line, f"[blue]Downloading {total_items} item(s)...[/blue]")

        for idx, entry_idx in enumerate(selected_indices):
            entry = self.fetched_entries[entry_idx]
            # Use original URL for single items, specific URL for playlist entries
            item_url = entry.get('webpage_url') or entry.get('url')
            if not item_url and not self.is_playlist:
                item_url = url_input
            elif not item_url and 'id' in entry:
                item_url = f"https://www.youtube.com/watch?v={entry['id']}"

            def hook(d):
                if d['status'] == 'downloading':
                    total = d.get('total_bytes') or d.get('total_bytes_estimate') or 1
                    p = d.get('downloaded_bytes', 0) / total
                    overall_p = ((idx + p) / total_items) * 100
                    self.call_from_thread(progress.update, progress=overall_p)
                elif d['status'] == 'finished':
                    self.call_from_thread(log.write_line, f"[green]Done:[/green] {os.path.basename(d['filename'])}")

            ydl_opts = {
                'format': 'bestaudio/best' if audio_only else 'bestvideo+bestaudio/best',
                'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
                'progress_hooks': [hook],
                'quiet': True,
                'no_warnings': True,
            }
            
            if audio_only:
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([item_url])
                except Exception as e:
                    self.call_from_thread(log.write_line, f"[red]Error downloading item {idx+1}:[/red] {str(e)}")
        
        self.call_from_thread(progress.update, progress=100)
        self.call_from_thread(log.write_line, "[bold green]Download Complete![/bold green]")

    # --- Looper & Clipper Logic ---
    @on(Button.Pressed, "#btn-start-loop")
    def action_start_loop(self):
        if not self.player:
            self.notify("VLC Media Player not found.", severity="error")
            return
        path = self.query_one("#loop-path").value.strip()
        if not os.path.exists(path):
            self.notify("File not found!", severity="error")
            return
        start = float(self.query_one("#loop-start").value or 0)
        end = float(self.query_one("#loop-end").value or 0) or None

        media = self.vlc_instance.media_new(path)
        self.player.set_media(media)
        self.player.play()
        self.is_looping = True
        self.loop_count = 0
        self.run_loop_monitor(start, end)

    @work(exclusive=True, thread=True)
    def run_loop_monitor(self, start, end):
        time.sleep(1)
        duration = (self.player.get_length() / 1000.0) if end is None else end
        while self.is_looping:
            try:
                current = self.player.get_time() / 1000.0
                if current >= duration:
                    self.player.set_time(int(start * 1000))
                    self.loop_count += 1
                    self.call_from_thread(self.query_one("#stat-count").update, str(self.loop_count))
            except: break
            time.sleep(0.1)

    @on(Button.Pressed, "#btn-stop-loop")
    def action_stop_loop(self):
        self.is_looping = False
        if self.player: self.player.stop()

    @on(Button.Pressed, "#btn-clip")
    @work(exclusive=True, thread=True)
    def action_clip(self):
        path = self.query_one("#clip-path").value.strip()
        start = self.query_one("#clip-start").value.strip()
        end = self.query_one("#clip-end").value.strip()
        log = self.query_one("#clip-log")
        if not os.path.exists(path) or not start or not end:
            self.call_from_thread(log.write_line, "[red]Invalid input or file path.[/red]")
            return
        output = f"{os.path.splitext(path)[0]}_clip{os.path.splitext(path)[1]}"
        try:
            subprocess.run(["ffmpeg", "-i", path, "-ss", start, "-to", end, "-c", "copy", output, "-y"], check=True)
            self.call_from_thread(log.write_line, f"[green]Clip created:[/green] {output}")
        except Exception as e:
            self.call_from_thread(log.write_line, f"[red]Clip Error:[/red] {str(e)}")

if __name__ == "__main__":
    WgetubeApp().run()
