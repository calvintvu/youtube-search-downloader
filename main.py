import youtube_search
import youtube_playlist
import browser_cookie3
import os
import cv2
import argparse
from http.cookiejar import MozillaCookieJar

COOKIEFILE = os.getenv("COOKIE_FILE")
cookies_path = COOKIEFILE

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

def validate_video(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return False
    ret, frame = cap.read()
    cap.release()
    return ret

def cleanup_invalid_videos(directory):
    video_extensions = {'.mp4', '.mkv', '.avi', '.flv', '.mov'}
    
    for root, _, files in os.walk(directory):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in video_extensions:
                video_path = os.path.join(root, file)
                print(f"Validating video: {video_path}")
                if not validate_video(video_path):
                    print(f"Invalid video detected. Deleting {video_path}")
                    try:
                        os.remove(video_path)
                    except Exception as e:
                        print(f"Error deleting {video_path}: {e}")
                else:
                    print(f"Video is valid: {video_path}")

def cleanup_cookies():
    if os.path.exists(cookies_path):
        os.remove(cookies_path)
        print(f"File '{cookies_path}' deleted successfully.")
    else:
        print(f"File '{cookies_path}' does not exist.")

def extract_cookies(browser="brave"):
    if os.path.exists(cookies_path):
        print(f"{cookies_path} exists!")
        return
    else:
        print(f"{cookies_path} does not exist, generating cookies.")
        try:
            if browser.lower() == "chrome":
                cj = browser_cookie3.chrome()
            elif browser.lower() == "firefox":
                cj = browser_cookie3.firefox()
            elif browser.lower() == "edge":
                cj = browser_cookie3.edge()
            elif browser.lower() == "brave":
                cj = browser_cookie3.brave()
            elif browser.lower() == "safari":
                cj = browser_cookie3.safari()
            else:
                print(f"Error generating cookies: {e}")
                return
            m_cj = MozillaCookieJar(cookies_path)
            for cookie in cj:
                m_cj.set_cookie(cookie)
            m_cj.save(ignore_discard=True, ignore_expires=True)
            print(f"Cookies saved to {cookies_path}")
        except Exception as e:
            print(f"Error generating cookies: {e}")

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
        "-browser", type=str, choices=["chrome", "firefox", "edge", "brave", "safari"], help="Browser cookies to use."
    )
    parser.add_argument(
        "max_results", type=int, help="Maximum number of videos to download."
    )
    parser.add_argument("max_workers", type=int, help="Max number of workers.")
    parser.add_argument(
        "-p",
        action="store_true",
        help="Search in playlists instead of regular search."
    )
    args = parser.parse_args()

    if args.browser != None:
        extract_cookies(args.browser)
    else:
        extract_cookies()
    if (args.p):
        youtube_playlist.download_youtube_videos_from_playlist(str(args.title), str(args.output_dir), int(args.max_results), int(args.max_workers))
    else:
        youtube_search.download_youtube_videos(str(args.title), str(args.output_dir), int(args.max_results), int(args.max_workers))
    
    cleanup_invalid_videos(args.output_dir)
    cleanup_cookies()