import typer
import sys
import os
import yt_dlp
import questionary
import ffmpeg
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(help="ytd_cli: Professional Media Hub (Download, Loop, Clip & Stitch).")
console = Console()

def get_yt_dlp_info(url: str):
    """Robust link analysis for all YT variations."""
    ydl_opts = {
        'extract_flat': 'in_playlist',
        'quiet': True,
        'no_warnings': True,
        # Force generic extractor for non-standard links if needed
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

@app.command()
def tui():
    """Launch the Professional TUI Dashboard."""
    try:
        from ytd_tui import mytubeApp
        mytubeApp().run()
    except Exception as e:
        console.print(f"[red]Error: Could not start TUI: {e}[/red]")

@app.command()
def download(url: str = typer.Argument(None, help="YouTube Link (Shorts, Video, or Playlist)")):
    """Download Shorts, Videos, or Playlists with individual item selection."""
    if not url:
        url = questionary.text("Enter YouTube URL:").ask()
        if not url: return

    with console.status("[bold blue]Analyzing link...[/bold blue]"):
        try:
            info = get_yt_dlp_info(url)
        except Exception as e:
            console.print(f"[red]Failed to analyze URL: {e}[/red]")
            return

    to_download = []
    output_subfolder = ""

    if 'entries' in info:
        # Playlist logic
        entries = [e for e in info['entries'] if e]
        console.print(f"[green]Playlist Found:[/green] {info.get('title')} ({len(entries)} items)")
        
        choices = [questionary.Choice(title=f"{i+1}. {e.get('title')}", value=i) for i, e in enumerate(entries)]
        selected_indices = questionary.checkbox(
            "Select items to download (Space to toggle, Enter to confirm):",
            choices=choices
        ).ask()
        
        if not selected_indices: return
        to_download = [entries[i] for i in selected_indices]
        output_subfolder = info.get('title', 'Playlist').replace('/', '_')
    else:
        # Individual video/short logic
        console.print(f"[green]Media Found:[/green] {info.get('title')}")
        to_download = [info]

    audio_only = questionary.confirm("Download Audio (MP3) only?").ask()
    res = "720" if not audio_only else None
    if not audio_only:
        res = questionary.select("Max Resolution:", choices=["360", "720", "1080", "best"], default="720").ask()

    base_dir = "downloads"
    output_dir = os.path.join(base_dir, output_subfolder) if output_subfolder else base_dir
    os.makedirs(output_dir, exist_ok=True)

    for entry in to_download:
        item_url = entry.get('webpage_url') or entry.get('url') or url
        if not item_url and 'id' in entry:
            item_url = f"https://www.youtube.com/watch?v={entry['id']}"
            
        title = entry.get('title', 'Unknown')
        console.print(f"\n[bold blue]↓[/bold blue] Downloading: [bold]{title}[/bold]")
        
        ydl_opts = {
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            'format': 'bestaudio/best' if audio_only else f'bestvideo[height<={res}]+bestaudio/best[height<={res}]' if res != "best" else "best",
        }
        if audio_only:
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([item_url])
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

@app.command()
def clip(path: str = typer.Argument(..., help="Path to local media")):
    """Advanced Clipping: Extract and stitch multiple segments."""
    if not os.path.exists(path):
        console.print(f"[red]File not found: {path}[/red]")
        return

    console.print(Panel("[bold]Multi-Segment Clipping Mode[/bold]\nEnter segments like: 00:10,00:20; 01:00,01:30"))
    raw_segments = questionary.text("Enter segments (start,end; start,end):").ask()
    if not raw_segments: return

    # Parse segments
    segments = []
    try:
        for s in raw_segments.split(';'):
            start, end = s.strip().split(',')
            segments.append((start.strip(), end.strip()))
    except:
        console.print("[red]Invalid segment format.[/red]")
        return

    name, ext = os.path.splitext(path)
    output = f"{name}_stitched{ext}"
    
    with console.status("[bold green]Clipping and Stitching...[/bold green]"):
        try:
            clips = []
            for i, (start, end) in enumerate(segments):
                temp_clip = f"temp_clip_{i}{ext}"
                ffmpeg.input(path, ss=start, to=end).output(temp_clip, c='copy').run(overwrite_output=True, quiet=True)
                clips.append(temp_clip)

            # Stitching using concat demuxer
            with open("concat_list.txt", "w") as f:
                for c in clips:
                    f.write(f"file '{c}'\n")
            
            ffmpeg.input("concat_list.txt", format='concat', safe=0).output(output, c='copy').run(overwrite_output=True, quiet=True)
            
            # Cleanup
            for c in clips: os.remove(c)
            os.remove("concat_list.txt")
            
            console.print(f"\n[bold green]Success![/bold green] Stitched clip saved: [cyan]{output}[/cyan]")
        except Exception as e:
            console.print(f"[red]Failed to stitch clips: {e}[/red]")

def tui_app():
    tui()

def cli_app():
    app()

if __name__ == "__main__":
    app()