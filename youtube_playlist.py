import os
import yt_dlp
import concurrent.futures
import argparse
from dotenv import load_dotenv
from googleapiclient.discovery import build


load_dotenv()
API_KEY = os.getenv("API_KEY")
MAX_FILE_SIZE = os.getenv("MAX_FILE_SIZE")
COOKIEFILE = os.getenv("COOKIE_FILE")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

exclude_keywords = [
    "album",
    "score",
    "soundtrack",
    "ost",
    "radio",
    "lore",
    "music"
]

def search_playlists(keyword, max_results=5):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    search_response = youtube.search().list(
        q=keyword,
        part="id,snippet",
        maxResults=max_results,
        type="playlist"
    ).execute()

    playlists = []
    for item in search_response.get("items", []):
        playlist_id = item["id"]["playlistId"]
        playlist_title = item["snippet"]["title"]
        playlists.append((playlist_id, playlist_title))
    return playlists

def get_videos_from_playlist(playlist_id, max_results=50):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)
    video_ids = []
    next_page_token = None

    while True:
        response = youtube.playlistItems().list(
            playlistId=playlist_id,
            part="snippet",
            maxResults=max_results,
            pageToken=next_page_token
        ).execute()

        for item in response.get("items", []):
            # Check if the video is private (its title will typically be "Private video")
            title = item["snippet"].get("title", "").lower()
            if title == "private video":
                # Skip private videos
                continue
            video_id = item["snippet"]["resourceId"]["videoId"]
            video_ids.append(video_id)

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return video_ids

def process_playlist(playlist_id, playlist_title, base_output_dir, maxResults=5):
    print(f"Starting download for playlist: {playlist_title}")
    playlist_output_dir = os.path.join(base_output_dir, playlist_title)
    os.makedirs(playlist_output_dir, exist_ok=True)
    
    video_ids = get_videos_from_playlist(playlist_id, max_results=maxResults)
    print(f"Found {len(video_ids)} videos in playlist '{playlist_title}'.")
    
    download_videos(video_ids, playlist_output_dir)
    print(f"Finished downloading playlist: {playlist_title}")

def download_videos(video_ids, output_dir):
    video_urls = [f"https://www.youtube.com/watch?v={vid}" for vid in video_ids]
    
    ydl_opts = {
        "format": f"bestvideo[filesize<{MAX_FILE_SIZE}]+bestaudio/best",
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'cookiefile': COOKIEFILE,  
    }   
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(video_urls)

def download_youtube_videos_from_playlist(keyword, output_dir, maxResults=10, maxWorkers=2):
    os.makedirs(output_dir, exist_ok=True)

    playlists = search_playlists(keyword)
    if not playlists:
        print("No playlists found for the given keyword.")
        return

    filtered_playlists = [
        (pid, title) for pid, title in playlists
        if not any(ex_kw.lower() in title.lower() for ex_kw in exclude_keywords)
    ]

    if not filtered_playlists:
        print("No playlists remain after filtering with the excluded keywords.")
        return

    print("Playlists after filtering:")
    for pid, title in filtered_playlists:
        print(f" - {title} (ID: {pid})")

    with concurrent.futures.ThreadPoolExecutor(max_workers=maxWorkers) as executor:
        futures = []
        for playlist_id, playlist_title in filtered_playlists:
            future = executor.submit(process_playlist, playlist_id, playlist_title, output_dir, maxResults)
            futures.append(future)
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"Playlist processing generated an exception: {exc}")
    


if __name__ == "__main__":
    download_youtube_videos_from_playlist()