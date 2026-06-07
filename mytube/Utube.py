import yt_dlp

def download_playlist_videos():
    """Downloads videos from a YouTube playlist based on user input.

    Prompts the user for a playlist URL, displays playlist information, 
    and then iterates through each video in the playlist, prompting the user 
    if they wish to download the video. If yes, the user is prompted to select
    a resolution, and the video is downloaded.
    """
    url = input('Enter the Playlist URL: ')

    # yt-dlp options to extract info without downloading
    ydl_opts_info = {
        'extract_flat': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            playlist_info = ydl.extract_info(url, download=False)
            
            if 'entries' not in playlist_info:
                print("Error: The provided URL does not seem to be a playlist or is not accessible.")
                return

            print('\n\nStats')
            print(f"\nPlaylist : {playlist_info.get('title', 'Unknown')}")
            print(f"No. of Videos : {len(playlist_info['entries'])}")
            print(f"Owner : {playlist_info.get('uploader', 'Unknown')}\n")

            for i, entry in enumerate(playlist_info['entries']):
                video_url = entry.get('url')
                if not video_url:
                    # In some cases, we might need to construct the URL
                    video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                
                print(f"Video {i+1} : {entry.get('title', 'Unknown')}")
                y = input('Would you like to download - Y? : ')
                
                if y.lower() == 'y':
                    print(f'Resolution Options:\n1: 360p\n2: 720p\n3: 1080p (best)\nEnter Resolution Option : ')
                    res_choice = input('Enter Choice: ')
                    
                    # Map choices to yt-dlp format strings
                    # Note: yt-dlp's 'bestvideo+bestaudio/best' handles merging if ffmpeg is available
                    format_str = 'best'
                    if res_choice == '1':
                        format_str = 'bestvideo[height<=360]+bestaudio/best[height<=360]'
                    elif res_choice == '2':
                        format_str = 'bestvideo[height<=720]+bestaudio/best[height<=720]'
                    elif res_choice == '3':
                        format_str = 'bestvideo[height<=1080]+bestaudio/best[height<=1080]'
                    else:
                        print('Downloading Default (Best Available)')
                        format_str = 'bestvideo+bestaudio/best'

                    ydl_opts_download = {
                        'format': format_str,
                        'outtmpl': '%(title)s.%(ext)s',
                        'quiet': False,
                    }

                    print(f"Downloading: {entry.get('title')}")
                    with yt_dlp.YoutubeDL(ydl_opts_download) as ydl_down:
                        ydl_down.download([video_url])
                else:
                    print('Skipping...\n')
                    continue

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    download_playlist_videos()
