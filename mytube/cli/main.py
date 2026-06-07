import typer
import sys
import os

# Add the current directory to sys.path to allow absolute imports within the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = typer.Typer(help="Wgetube: Professional YouTube Downloader, Looper, and Clipper.")

@app.command()
def tui():
    """Launch the Pro TUI Dashboard (Textual based)."""
    try:
        from cli.tui import WgetubeApp
        app_instance = WgetubeApp()
        app_instance.run()
    except Exception as e:
        print(f"Error: Could not start the TUI.")
        print(f"Details: {e}")
        print("\nEnsure you have VLC installed on your system.")

@app.command()
def interactive():
    """Launch the Interactive Playlist Downloader (CLI based)."""
    from cli.Utube import download_playlist_videos
    download_playlist_videos()

if __name__ == "__main__":
    app()
