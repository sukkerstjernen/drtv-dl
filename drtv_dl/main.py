from drtv_dl.downloader import DRTVDownloader
from drtv_dl.exceptions import InvalidURLError
from drtv_dl.utils.settings import set_suppress_output, set_proxy
from drtv_dl.extractor import (
    InfoExtractor, 
    SeasonInfoExtractor, 
    SeriesInfoExtractor 
)
from drtv_dl.utils.helpers import (
    print_to_screen, 
    is_valid_drtv_url,
)

def download(url, resolution="360p", include_subs=False, ntmpl=None, proxy=None, list_formats=False, suppress_output=False):
    if not is_valid_drtv_url(url):
        raise InvalidURLError("URL was not found to be valid")
    
    if suppress_output:
        set_suppress_output(suppress_output)
    if proxy:
        set_proxy(proxy)

    print_to_screen(f"Processing URL: {url}")
    ie = InfoExtractor()
    sie = SeasonInfoExtractor(ie)

    if '/drtv/serie/' in url:
        print_to_screen("Identified as a series URL")
        extractor = SeriesInfoExtractor(sie)
    elif '/drtv/saeson/' in url:
        print_to_screen("Identified as a season URL")
        extractor = sie
    else:
        print_to_screen("Identified as a single item URL")
        extractor = ie

    info = extractor.extract(url)
    downloader = DRTVDownloader()

    if isinstance(info, dict) and 'episode_urls' in info:
        print_to_screen(f"Starting download of season {info.get('season_number', '')}")
        for idx, episode_url in enumerate(info['episode_urls'], start=1):
            print_to_screen(f"Processing episode {idx} of {len(info['episode_urls'])}")
            episode_info = ie.extract(episode_url)
            downloader.download(episode_info, list_formats, resolution=resolution, include_subs=include_subs, ntmpl=ntmpl)
    elif isinstance(info, list):
        total_seasons = len(info)
        for season_idx, season in enumerate(info, start=1):
            print_to_screen(f"Processing season {season_idx} of {total_seasons}")
            for idx, episode_url in enumerate(season['episode_urls'], start=1):
                print_to_screen(f"Processing episode {idx} of {len(season['episode_urls'])} in season {season_idx} of {total_seasons}")
                episode_info = ie.extract(episode_url)
                downloader.download(episode_info, list_formats, resolution=resolution, include_subs=include_subs, ntmpl=ntmpl)
    else:
        print_to_screen("Processing a single item")
        downloader.download(info, list_formats, resolution=resolution, include_subs=include_subs, ntmpl=ntmpl)
