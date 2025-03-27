import youtube_search
import youtube_playlist
import browser_cookie3
import os
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

def extract_cookies():
    if os.path.exists(cookies_path):
        print(f"{cookies_path} exists!")
        return
    else:
        print(f"{cookies_path} does not exist, generating file.")
        try:
            cj = browser_cookie3.brave()
            m_cj = MozillaCookieJar(cookies_path)
            for cookie in cj:
                m_cj.set_cookie(cookie)
            m_cj.save(ignore_discard=True, ignore_expires=True)
            print(f"Cookies saved to {cookies_path}")
        except Exception as e:
            print(f"Error generating cookies: {e}")

def validate_downloads(output_dir):
    pass


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
    parser.add_argument(
        "-p",
        action="store_true",
        help="Search in playlists instead of regular search."
    )
    args = parser.parse_args()

    extract_cookies()
    if (args.p):
        youtube_playlist.download_youtube_videos_from_playlist(str(args.title), str(args.output_dir), int(args.max_results), int(args.max_workers))
    else:
        youtube_search.download_youtube_videos(str(args.title), str(args.output_dir), int(args.max_results), int(args.max_workers))