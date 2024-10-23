# CREDIT TO https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/extractor/drtv.py

import uuid
import json
import requests
from urllib.parse import urljoin

from drtv_dl.utils import settings
from drtv_dl.logger import logger
from drtv_dl.exceptions import (
    TokenRetrievalError, 
    ItemIDExtractionError, 
    SeasonIDExtractionError, 
    SeriesIDExtractionError
)
from drtv_dl.utils.helpers import (
    download_webpage, 
    extract_ids_from_url, 
    print_to_screen, 
    search_content
)

class InfoExtractor:
    BASE_URL = "https://www.dr.dk/drtv"
    ITEM_DATA_PARAMS = {
        'device': 'web_browser',
        'ff': 'idp,ldp,rpt',
        'lang': 'da',
        'expand': 'all',
        'sub': 'Anonymous',
    }
    ITEM_API_URL = 'https://production-cdn.dr-massive.com/api/items/{}'
    STREAM_API_URL = 'https://production.dr-massive.com/api/account/items/{}/videos'
    ANONYMOUS_SSO_URL = 'https://isl.dr-massive.com/api/authorization/anonymous-sso'
    ANONYMOUS_SSO_PARAMS = {
        'device': 'phone_android',
        'lang': 'da',
        'supportFallbackToken': 'true',
    }

    def __init__(self):
        print_to_screen("Obtaining anonymous token")
        anon_token_response = requests.post(
            url=self.ANONYMOUS_SSO_URL,
            params=self.ANONYMOUS_SSO_PARAMS,
            headers={'Content-Type': 'application/json'},
            json={
                'deviceId': str(uuid.uuid4()),
                'scopes': ['Catalog'],
                'optout': True,
            },
            proxies=settings.PROXY
        )
        anon_token_response.raise_for_status()
        anon_token_json = anon_token_response.json()
        self._TOKEN = next((entry['value'] for entry in anon_token_json if entry['type'] == 'UserAccount'), None)
        if not self._TOKEN:
            raise TokenRetrievalError("Couldn't retrieve anonymous token")

    def extract(self, url):
        _, item_id = extract_ids_from_url(url)
        print_to_screen(f"Extracting information from: {item_id}")
        if not item_id:
            raise ItemIDExtractionError("Could not extract item ID from URL")

        print_to_screen(f"{item_id}: Downloading item JSON metadata")
        item = json.loads(download_webpage(
            self.ITEM_API_URL.format(item_id),
            params=self.ITEM_DATA_PARAMS,
            headers={'Authorization': f'Bearer {self._TOKEN}'}
        ))

        video_id = item.get('customId', '').split(':')[-1] or item_id

        print_to_screen(f"{video_id}: Fetching stream data...")
        stream_data = json.loads(download_webpage(
            self.STREAM_API_URL.format(item_id),
            params={
                'delivery': 'stream',
                'device': 'web_browser',
                'ff': 'idp,ldp,rpt',
                'lang': 'da',
                'resolution': 'HD-1080',
                'sub': 'Anonymous',
            },
            headers={'Authorization': f'Bearer {self._TOKEN}'}
        ))

        logger.debug(f"{video_id}: Parsing available formats")
        formats = []
        for stream in stream_data:
            stream_url = stream.get('url', None)
            if not stream_url:
                continue

            format_id = stream.get('format', 'na')
            access_service = stream.get('accessService')
            preference = None
            if access_service in ('SpokenSubtitles', 'SignLanguage', 'VisuallyInterpreted'):
                preference = -1
                format_id += f'-{access_service}'
            elif access_service == 'StandardVideo' or access_service is None:
                preference = 1

            formats.append({
                'format_id': format_id,
                'url': stream_url,
                'preference': preference,
            })

        return {
            "id": video_id,
            "title": item.get('season', {}).get('title', None) or item.get('title'),
            "description": item.get('description', None),
            "duration": item.get('duration', None),
            "year": search_content(r'fra (\d{4})', item.get('description', '')) or item.get('releaseYear', None),
            "season_number": item.get('season', {}).get('seasonNumber', None),
            "episode_number": item.get('episodeNumber', None),
            "episode_name": item.get('episodeName', '').replace(f"{item.get('season', {}).get('title', '')}:", '').strip() or None,
            "formats": formats,
        }


class SeasonInfoExtractor:
    BASE_URL = "https://www.dr.dk/drtv"
    SEASON_API_URL = 'https://production-cdn.dr-massive.com/api/page'
    SEASON_API_PARAMS = {
        'device': 'web_browser',
        'item_detail_expand': 'all',
        'lang': 'da',
        'max_list_prefetch': '3',
    }

    def __init__(self, ie):
        self.info_extractor = ie

    def extract(self, url):
        display_id, season_id = extract_ids_from_url(url)
        print_to_screen(f"Extracting season information from: {display_id}_{season_id}")
        if not season_id:
            logger.error("Could not extract season ID from URL")
            raise SeasonIDExtractionError("Could not extract season ID from URL")

        print_to_screen(f"{season_id}: Downloading season JSON metadata")
        season_data = json.loads(download_webpage(
            url=self.SEASON_API_URL,
            params={
                **self.SEASON_API_PARAMS,
                'path': f'/saeson/{display_id}_{season_id}'
            },
        ))

        episodes = season_data.get('entries', [])[0].get('item', {}).get('episodes', {}).get('items', [])
        episode_urls = []
        for episode in episodes:
            episode_path = episode.get('path')
            episode_url = urljoin(self.BASE_URL, episode_path)
            episode_urls.append(episode_url)

        season_number = season_data.get('entries', [])[0].get('item', {}).get('seasonNumber')

        print_to_screen(f"Found {len(episode_urls)} episodes in season {season_number}")
        return {
            'season_number': season_number,
            'episode_urls': episode_urls
        }
 
class SeriesInfoExtractor:
    BASE_URL = "https://www.dr.dk/drtv"
    SERIES_API_URL = 'https://production-cdn.dr-massive.com/api/page'
    SERIES_API_PARAMS = {
        'device': 'web_browser',
        'item_detail_expand': 'all',
        'lang': 'da',
        'max_list_prefetch': '3',
    }

    def __init__(self, sie):
        self.season_extractor = sie

    def extract(self, url):
        display_id, series_id = extract_ids_from_url(url)
        print_to_screen(f"Extracting series information from: {display_id}_{series_id}")
        if not series_id:
            logger.error("Could not extract series ID from URL")
            raise SeriesIDExtractionError("Could not extract series ID from URL")

        print_to_screen(f"{series_id}: Downloading series JSON metadata")
        series_data = json.loads(download_webpage(
            url=self.SERIES_API_URL,
            params={
                **self.SERIES_API_PARAMS,
                'path': f'/serie/{display_id}_{series_id}'
            },
        ))

        seasons = series_data.get('entries', [])[0].get('item', {}).get('show', {}).get('seasons', {}).get('items', [])
        season_info = []
        for season in seasons:
            season_path = season.get('path')
            season_url = urljoin(self.BASE_URL, season_path)
            print_to_screen(f"Processing season: {season_url}")
            season = self.season_extractor.extract(season_url)
            season_info.append(season)

        print_to_screen(f"Total seasons found: {len(season_info)}")
        return season_info