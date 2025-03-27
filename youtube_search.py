import os
import yt_dlp
import concurrent.futures
import argparse
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
API_KEY = os.getenv("API_KEY")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

class TypeHelpFormatter(argparse.HelpFormatter):
    def _format_action_invocation(self, action):
        # For positional arguments (no option strings), display the destination and type.
        if not action.option_strings:
            metavar = action.metavar or action.dest.upper()
            # Get the type name, defaulting to "str" if not specified.
            type_name = action.type.__name__ if action.type is not None else "str"
            return f"{metavar} ({type_name})"
        # For optional arguments, fallback to the default formatting.
        return super()._format_action_invocation(action)


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
        video_id = item["id"]["videoId"]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        if keyword.lower() in title.lower():
            video_urls.append(video_url)
    return video_urls


def download_videos_by_url(url, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
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

    parser = argparse.ArgumentParser(
        description="Arguments to download youtube videos.",
        formatter_class=TypeHelpFormatter
    )


    parser.add_argument(
        "title", type=str, help="Keywords that match title of the video to search for."
    )
    parser.add_argument(
        "output_dir", type=str, help="Directory to store downloaded videos in."
    )
    parser.add_argument(
        "max_results", type=int, help="Maximum number of videos to download."
    )
    parser.add_argument("max_workers", type=int, help="Max number of workers.")
    args = parser.parse_args()
    download_youtube_videos(
        args.title, args.output_dir, args.max_results, args.max_workers
    )
