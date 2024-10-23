import argparse

from drtv_dl.logger import logger
from drtv_dl.main import download
from drtv_dl.exceptions import DRTVDownloaderError

def parse_args():
    parser = argparse.ArgumentParser(description="Download videos from DR TV")
    parser.add_argument("url", help="URL of the video to download")
    parser.add_argument("--resolution", default="360p", help="Desired video resolution (e.g., 1080p, 720p)")
    parser.add_argument("--include-subs", action="store_true", help="Download with subtitles")
    parser.add_argument("--ntmpl", help="User-custom naming template i.e. \"{title} E{episode_number} {year} [{id}]\"")
    parser.add_argument("--proxy", default=None,help="Proxy to use for the download")
    parser.add_argument("--list-formats", action="store_true", help="List available formats")
    parser.add_argument("--suppress-output", action="store_true", help="Suppress output to the screen")
    parser.add_argument("--log-level", default="INFO", help="Set the logging level")
    args = parser.parse_args()

    logger.setLevel(args.log_level.upper())
    
    download(
        url=args.url, 
        resolution=args.resolution,
        include_subs=args.include_subs,
        ntmpl=args.ntmpl,
        proxy=args.proxy,
        list_formats=args.list_formats,
        suppress_output=args.suppress_output
    )


if __name__ == "__main__":
    parse_args()