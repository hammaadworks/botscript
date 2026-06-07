import typer
import sys
import os
import yt_dlp
import questionary
from rich.console import Console

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = typer.Typer(help="Wgetube: Professional Media Hub (Download, Loop, Clip).")
console = Console()

@app.command()
def tui():
    """Launch the Professional TUI Dashboard (Full Feature Suite)."""
    try:
        from cli.tui import WgetubeApp
        WgetubeApp().run()
    except Exception as e:
        console.print(f"[red]Error: Could not start TUI: {e}[/red]")
        console.print("[yellow]Ensure you have VLC installed on your system.[/yellow]")

@app.command()
def download(url: str = typer.Argument(None, help="YouTube Link (Shorts, Video, or Playlist)")):
    """Fast Interactive CLI Downloader (yt-dlp powered)."""
    if not url:
        url = questionary.text("Enter YouTube URL (Shorts/Video/Playlist):").ask()
        if not url: return

    ydl_opts_info = {'extract_flat': 'in_playlist', 'quiet': True}
    
    with console.status("[bold blue]Analyzing link...[/bold blue]"):
        try:
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as e:
            console.print(f"[red]Failed to analyze URL: {e}[/red]")
            return

    if 'entries' in info:
        # It's a playlist
        entries = [e for e in info['entries'] if e]
        console.print(f"[green]Playlist Found:[/green] {info.get('title')} ({len(entries)} items)")
        
        choices = [f"{i+1}. {e.get('title')}" for i, e in enumerate(entries)]
        selected = questionary.checkbox(
            "Select items to download:",
            choices=choices,
            default=choices
        ).ask()
        
        if not selected: return
        
        indices = [int(s.split('.')[0]) - 1 for s in selected]
        to_download = [entries[i] for i in indices]
    else:
        # Individual video/short
        console.print(f"[green]Media Found:[/green] {info.get('title')}")
        to_download = [info]

    audio_only = questionary.confirm("Download Audio (MP3) only?").ask()
    
    res = "720"
    if not audio_only:
        res = questionary.select(
            "Select Max Resolution:",
            choices=["360", "720", "1080", "best"],
            default="720"
        ).ask()

    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)

    for entry in to_download:
        item_url = entry.get('webpage_url') or entry.get('url') or url
        title = entry.get('title', 'Unknown')
        
        console.print(f"\n[bold]Downloading:[/bold] {title}")
        
        ydl_opts = {
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            'format': 'bestaudio/best' if audio_only else f'bestvideo[height<={res}]+bestaudio/best[height<={res}]' if res != "best" else "best",
            'quiet': False,
        }
        
        if audio_only:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([item_url])
        except Exception as e:
            console.print(f"[red]Error downloading {title}: {e}[/red]")

    console.print("\n[bold green]Success: All downloads finished! Alhamdulillah.[/bold green]")

@app.command()
def clip(
    path: str = typer.Argument(..., help="Path to source file"),
    start: str = typer.Option(..., "--start", "-s", help="Start time (e.g. 00:01:00 or 60)"),
    end: str = typer.Option(..., "--end", "-e", help="End time (e.g. 00:01:30 or 90)")
):
    """Fast CLI Clipping using FFmpeg."""
    if not os.path.exists(path):
        console.print(f"[red]File not found: {path}[/red]")
        return
    
    output = f"{os.path.splitext(path)[0]}_clip{os.path.splitext(path)[1]}"
    import subprocess
    try:
        subprocess.run(["ffmpeg", "-i", path, "-ss", start, "-to", end, "-c", "copy", output, "-y"], check=True)
        console.print(f"[green]Clip created successfully:[/green] {output}")
    except Exception as e:
        console.print(f"[red]Clipping failed: {e}[/red]")

def tui_app():
    """Entry point for mytube-tui script."""
    tui()

def cli_app():
    """Entry point for mytube-cli script."""
    app()

if __name__ == "__main__":
    app()
