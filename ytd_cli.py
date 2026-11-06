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
NODE_PATH = "/opt/homebrew/bin/node" if os.path.exists("/opt/homebrew/bin/node") else "node"

def normalize_url(url: str) -> str:
    if not url: return url
    url = url.strip()
    if url.startswith("playlist?") or url.startswith("/playlist?"):
        url = f"https://www.youtube.com/{url.lstrip('/')}"
    elif url.startswith("watch?") or url.startswith("/watch?"):
        url = f"https://www.youtube.com/{url.lstrip('/')}"
    elif url.startswith("youtube.com") or url.startswith("youtu.be") or url.startswith("www.youtube.com"):
        url = f"https://{url}"
    return url

def get_yt_dlp_info(url: str, country: str = "DE", proxy: str = None, cookies_browser: str = None, cookie_file: str = None):
    """Robust link analysis for all YT variations with geo-bypass and optional proxy."""
    url = normalize_url(url)
    ydl_opts = {
        'extract_flat': 'in_playlist',
        'quiet': True,
        'no_warnings': True,
        'geo_bypass': True,
        'geo_bypass_country': country,
        'js_runtimes': {'node': {'path': NODE_PATH}},
        'extractor_args': {'youtube': ['player_client=ios,web']},
        'remote_components': ['ejs:github'],
    }
    if proxy:
        proxy = "".join(proxy.split())
        ydl_opts['proxy'] = proxy
    if cookies_browser:
        ydl_opts['cookiesfrombrowser'] = (cookies_browser,)
    if cookie_file:
        ydl_opts['cookiefile'] = cookie_file
    elif os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = "cookies.txt"

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
def download(
    url: str = typer.Argument(None, help="YouTube Link (Shorts, Video, or Playlist)"),
    country: str = typer.Option("DE", "--country", "-c", help="2-letter ISO country code for geo-bypass (default: DE)"),
    proxy: str = typer.Option(None, "--proxy", "-p", help="Optional HTTP/SOCKS5 proxy (e.g. socks5://127.0.0.1:1080)"),
    cookies_browser: str = typer.Option(None, "--cookies-from-browser", help="Browser to extract cookies from (e.g. chrome, brave, firefox, safari)"),
    cookies: str = typer.Option(None, "--cookies", help="Path to exported cookies.txt file"),
):
    """Download Shorts, Videos, or Playlists with individual item selection and geo-bypass."""
    if proxy:
        proxy = "".join(proxy.split())
    if not url:
        url = questionary.text("Enter YouTube URL:").ask()
        if not url: return
    url = normalize_url(url)

    with console.status(f"[bold blue]Analyzing link (Geo-Bypass: {country})...[/bold blue]"):
        try:
            info = get_yt_dlp_info(url, country=country, proxy=proxy, cookies_browser=cookies_browser, cookie_file=cookies)
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

    audio_only = questionary.confirm("Download Audio (MP3) only?", default=False).ask()
    res = "720" if not audio_only else None
    if not audio_only:
        # Dynamically discover real available resolutions to prevent false promises
        available_heights = []
        if 'formats' in info and info['formats']:
            available_heights = sorted({
                f['height'] for f in info['formats']
                if f.get('height') and f.get('vcodec') and f.get('vcodec') != 'none'
            }, reverse=True)
        elif to_download:
            # Sample first item from playlist if formats not yet extracted
            with console.status("[bold blue]Checking available video formats...[/bold blue]"):
                try:
                    sample_url = to_download[0].get('webpage_url') or to_download[0].get('url')
                    if not sample_url and 'id' in to_download[0]:
                        sample_url = f"https://www.youtube.com/watch?v={to_download[0]['id']}"
                    if sample_url:
                        sample_info = get_yt_dlp_info(sample_url, country=country, proxy=proxy, cookies_browser=cookies_browser, cookie_file=cookies)
                        available_heights = sorted({
                            f['height'] for f in sample_info.get('formats', [])
                            if f.get('height') and f.get('vcodec') and f.get('vcodec') != 'none'
                        }, reverse=True)
                except Exception:
                    available_heights = []

        res_labels = {
            4320: "4320p (8K UHD)",
            2160: "2160p (4K UHD)",
            1440: "1440p (2K QHD)",
            1080: "1080p (Full HD)",
            720: "720p (HD)",
            480: "480p (SD - Space Efficient)",
            360: "360p (Standard)",
            240: "240p (Low)",
            144: "144p (Minimum)",
        }

        # Ensure standard resolution targets (1080, 720, 480, 360) are always available choices
        combined_heights = sorted(set(available_heights) | {1080, 720, 480, 360}, reverse=True)
        choices = [questionary.Choice("Best Available (Highest Quality)", value="best")]
        for h in combined_heights:
            tag = " [green](Verified)[/green]" if h in available_heights else ""
            label = f"{res_labels.get(h, f'{h}p')}{tag}"
            choices.append(questionary.Choice(label, value=str(h)))
        
        default_val = "480" if "480" in [c.value for c in choices] else "best"
        res = questionary.select(
            "Select Target Resolution:",
            choices=choices,
            default=default_val
        ).ask()

    base_dir = "downloads"
    output_dir = os.path.join(base_dir, output_subfolder) if output_subfolder else base_dir
    os.makedirs(output_dir, exist_ok=True)

    for entry in to_download:
        item_url = entry.get('webpage_url') or entry.get('url') or url
        if not item_url and 'id' in entry:
            item_url = f"https://www.youtube.com/watch?v={entry['id']}"
            
        title = entry.get('title', 'Unknown')
        console.print(f"\n[bold blue]↓[/bold blue] Downloading: [bold]{title}[/bold]")
        
        if audio_only:
            fmt = 'bestaudio/best'
        elif res == "best":
            fmt = 'bestvideo+bestaudio/best'
        else:
            # First match exact height, then closest <= target to avoid bloated downloads, then best available
            fmt = f'bestvideo[height={res}]+bestaudio/bestvideo[height<={res}]+bestaudio/bestvideo+bestaudio/best'
            
        ydl_opts = {
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            'format': fmt,
            # Prioritize AV1 and VP9 for high space efficiency and pristine clarity, fallback to H.264
            'format_sort': ['res', 'codec:av01:vp9:h264', 'size', 'br'],
            'merge_output_format': 'mp4',
            'geo_bypass': True,
            'geo_bypass_country': country,
            'concurrent_fragment_downloads': 8,
            'js_runtimes': {'node': {'path': NODE_PATH}},
            'extractor_args': {'youtube': ['player_client=ios,web']},
            'remote_components': ['ejs:github'],
        }
        if proxy:
            ydl_opts['proxy'] = proxy
        if cookies_browser:
            ydl_opts['cookiesfrombrowser'] = (cookies_browser,)
        if cookies:
            ydl_opts['cookiefile'] = cookies
        elif os.path.exists("cookies.txt"):
            ydl_opts['cookiefile'] = "cookies.txt"
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