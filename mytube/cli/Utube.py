import yt_dlp
import os

def download_playlist_videos():
    """
    Downloads videos from a YouTube playlist based on user input.
    Uses yt-dlp for robustness and performance.
    """
    url = input('Enter the Playlist URL: ')

    # yt-dlp options to extract info without downloading
    ydl_opts_info = {
        'extract_flat': True,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            playlist_info = ydl.extract_info(url, download=False)
            
            if 'entries' not in playlist_info:
                print("Error: The provided URL does not seem to be a playlist or is not accessible.")
                return

            print('\n\n--- Playlist Stats ---')
            print(f"Playlist : {playlist_info.get('title', 'Unknown')}")
            print(f"No. of Videos : {len(playlist_info['entries'])}")
            print(f"Owner : {playlist_info.get('uploader', 'Unknown')}\n")

            output_dir = "downloads"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            for i, entry in enumerate(playlist_info['entries']):
                if not entry: continue
                
                video_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                
                print(f"Video {i+1} : {entry.get('title', 'Unknown')}")
                y = input('Would you like to download? (y/n): ')
                
                if y.lower() == 'y':
                    print(f'Resolution Options:\n1: 360p\n2: 720p\n3: 1080p (best)\nEnter Choice (default 720p): ')
                    res_choice = input('Enter Choice: ')
                    
                    format_str = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
                    if res_choice == '1':
                        format_str = 'bestvideo[height<=360]+bestaudio/best[height<=360]'
                    elif res_choice == '3':
                        format_str = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'

                    ydl_opts_download = {
                        'format': format_str,
                        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
                        'quiet': False,
                        'no_warnings': True,
                    }

                    print(f"Downloading: {entry.get('title')}...")
                    with yt_dlp.YoutubeDL(ydl_opts_download) as ydl_down:
                        ydl_down.download([video_url])
                else:
                    print('Skipping...\n')
                    continue

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    download_playlist_videos()
