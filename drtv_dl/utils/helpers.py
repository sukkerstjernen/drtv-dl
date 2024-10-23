import re
import os
import html
import inspect
import logging
import requests

from drtv_dl.logger import logger
from drtv_dl.utils import settings
from drtv_dl.exceptions import (
    DownloadError,
    StreamNotFoundError,
)


def is_valid_drtv_url(url):
    pattern = r'^https://www\.dr\.dk/drtv/(se|episode|saeson|serie|program)/[a-zA-Z0-9\-_]+_\d+$'
    return bool(re.match(pattern, url))

def print_to_screen(message, level='info'):
    if settings.SUPPRESS_OUTPUT:
        return
    if not message:
        return
    frame = inspect.currentframe().f_back
    module = inspect.getmodule(frame)
    module_name = module.__name__.split('.')[-1] if module else 'unknown_module'
    locals_ = frame.f_locals
    class_name = None
    if 'self' in locals_:
        class_name = locals_['self'].__class__.__name__
    elif 'cls' in locals_:
        class_name = locals_['cls'].__name__
    if class_name:
        identifier = f'{module_name}:{class_name.lower()}'
    else:
        identifier = module_name
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.log(log_level, message, extra={'module_class': identifier})

def search_content(pattern, text, group_num=1):
    if isinstance(pattern, str):
        pattern = re.compile(pattern, re.DOTALL)
    match = pattern.search(text)
    if not match:
        return None
    try:
        return html.unescape(match.group(group_num))
    except IndexError:
        raise ValueError(f"Group {group_num} does not exist in the match.")

def download_webpage(url, headers=None, data=None, params=None, json=None):
    logger.debug(f"Requesting URL: {url}")
    response = requests.get(
        url=url,
        headers=headers,
        data=data,
        params=params,
        json=json,
        proxies=settings.PROXY
    )
    if response.status_code == 403:
        raise DownloadError("Access denied – likely due to geoblocking. Ensure your IP is recognized as being in Denmark by using a proxy or a VPN.")
    response.raise_for_status()
    logger.debug(f"Received response from {url}")
    return response.text

def extract_ids_from_url(url):
    path_parts = url.strip('/').split('/')
    last_part = path_parts[-1]
    if '_' in last_part:
        display_id, item_id = last_part.rsplit('_', 1)
    else:
        raise ValueError("Invalid URL format")
    logger.debug(f"Extracted display_id: {display_id}, item_id: {item_id}")
    return display_id, item_id

def sanitize_filename(filename):
    sanitized = re.sub(r'[<>:"/\\|?*]', ' - ', filename)
    logger.debug(f"Sanitized filename: {sanitized}")
    return sanitized.replace("  ", " ")

def vtt_to_srt(vtt_file, srt_file):
    with open(vtt_file, 'r', encoding='utf-8') as vtt, open(srt_file, 'w', encoding='utf-8') as srt:
        content = re.sub(r'WEBVTT\n\n', '', vtt.read())
        content = re.sub(r'(\d{2}:\d{2}:\d{2})\.(\d{3})', r'\1,\2', content)
        lines = content.split('\n\n')
        for i, line in enumerate(lines, start=1):
            srt.write(f"{i}\n{line}\n\n")

def get_optimal_stream(parsed_m3u8_streams, desired_resolution, include_subs):
        optimal_stream = {
            'video': None,
            'audio': None,
            'subtitle': None
        }

        if include_subs:
            subtitles = parsed_m3u8_streams.get('subtitles', None)
            if subtitles:
                optimal_stream['subtitle'] = subtitles[-1]
            else:
                raise StreamNotFoundError("No subtitles stream found")

        for stream in parsed_m3u8_streams['video']:
            if stream['resolution'].split('x')[1] == desired_resolution.replace('p', ''):
                optimal_stream['video'] = stream
                break

        if optimal_stream['video'] is None:
            raise StreamNotFoundError(f"No video stream found with resolution: '{desired_resolution}'")
        
        audio_group = optimal_stream['video']['audio']
        for audio_stream in parsed_m3u8_streams['audio']:
            if audio_stream['group-id'] == audio_group:
                optimal_stream['audio'] = audio_stream
                break

        if optimal_stream['audio'] is None:
            raise StreamNotFoundError(f"No audio stream found for group: '{audio_group}'")

        return optimal_stream

def get_optimal_format(formats):
    if not formats:
        logger.error("No available formats to choose from")
        raise DownloadError("No formats for media were available")
    preferred_formats = [f for f in formats if f.get('preference') == 1]
    if not preferred_formats:
        logger.error("No suitable formats found")
        raise DownloadError("No suitable formats found.")
    logger.debug(f"Optimal format selected: '{preferred_formats[0]['format_id']}'")
    return preferred_formats[0]

def print_formats(formats):
    def format_row(columns, widths):
        return " │ ".join([col.ljust(width) for col, width in zip(columns, widths)])

    data_rows = [["ID", "EXT", "FPS", "RESOLUTION", "TBR", "VBR", "VCODEC", "ACODEC", "PROTOCOL"]]

    for category, ext in [('audio', 'mp4'), ('subtitles', 'vtt'), ('video', 'mp4')]:
        for item in formats.get(category, []):
            if category == 'audio':
                row = [f"audio_{item['group-id']}-{item['name']}-{item['language']}", ext, "n/a", "audio only", 
                       "n/a", "n/a", "audio only", f"[{item['language']}] {item['name']}", "m3u8"]
            elif category == 'subtitles':
                row = [f"subs_{item['name']}-{item['language']}", ext, "n/a", "subtitles", 
                       "n/a", "n/a", "sub only", f"[{item['language']}] {item['name']}", "m3u8"]
            else:  # video
                row = [f"video_{item['bandwidth']}", ext, item['frame-rate'], item['resolution'], 
                       f"{int(item['bandwidth']) // 1000}k", f"{int(item['average-bandwidth']) // 1000}k", 
                       item['codecs'].split(",")[0], "video only", "m3u8"]
            data_rows.append(row)

    column_widths = [max(len(str(item)) for item in col) for col in zip(*data_rows)]
    
    print("\n" + "─" * (sum(column_widths) + 3 * (len(column_widths) - 1)))
    for i, row in enumerate(data_rows):
        print(format_row(row, column_widths))
        if i == 0:
            print("─" * (sum(column_widths) + 3 * (len(column_widths) - 1)))
    print("─" * (sum(column_widths) + 3 * (len(column_widths) - 1)) + "\n")


def generate_filename(info, ntmpl):
    if ntmpl:
        filename = ntmpl
        for key in re.findall(r'\{(\w+)\}', filename):
            if key.lower() in info and info[key.lower()] is not None:
                value = str(info[key.lower()])
                if key.lower() in ['season_number', 'episode_number']:
                    value = value.zfill(2)
                filename = filename.replace(f'{{{key}}}', value)
            else:
                raise KeyError(f"Key '{key}' is either not found in info dictionary or is None")
    else:
        title = info.get('title', '')
        _id = info.get('id', '')
        season_number = info.get('season_number')
        episode_number = info.get('episode_number')
        episode_name = info.get('episode_name', '')
        year = info.get('year')

        if season_number and episode_number:
            filename = f"{title} S{int(season_number):02d}E{int(episode_number):02d} - {episode_name} [{_id}]"
        else:
            filename = f"{title} ({year}) [{_id}]" if year else f"{title} [{_id}]"

    return sanitize_filename(filename)

def delete_files(*file_paths):
    for file_path in file_paths:
        if not file_path:
            continue
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError as e:
            logger.error(f"Error deleting {file_path}: {e}")
