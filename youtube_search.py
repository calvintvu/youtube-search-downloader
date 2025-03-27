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

def search_videos_by_title(keyword, max_results=5):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=API_KEY)

    search_response = (
        youtube.search()
        .list(q=keyword, part="id,snippet", maxResults=max_results, type="video")
        .execute()
    )

    video_urls = []
    for item in search_response.get("items", []):
        title = item["snippet"]["title"]
        if title == "private video":
                # Skip private videos
                continue
        video_id = item["id"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        if keyword.lower() in title.lower():
            video_urls.append(video_url)
    return video_urls


def download_videos_by_url(url, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "format": f"bestvideo[filesize<{MAX_FILE_SIZE}]+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        'cookiefile': COOKIEFILE,  
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Starting download: {url}")
            ydl.download([url])
            print(f"Finished download: {url}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")


def download_youtube_videos(keywords, output_dir, maxResults=10, maxWorkers=2):
    urls = search_videos_by_title(keywords, max_results=maxResults)
    with concurrent.futures.ThreadPoolExecutor(max_workers=maxWorkers) as executor:
        futures = [
            executor.submit(download_videos_by_url, url, output_dir) for url in urls
        ]
        concurrent.futures.wait(futures)


if __name__ == "__main__":
    download_youtube_videos()
