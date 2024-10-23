import os
import requests

from drtv_dl.logger import logger
from drtv_dl.utils.merger import Merger
from drtv_dl.utils import settings
from drtv_dl.utils.m3u8_parser import M3U8Parser
from drtv_dl.utils.progress_tracker import ProgressTracker
from drtv_dl.utils.helpers import (
    generate_filename,
    download_webpage,
    vtt_to_srt,
    get_optimal_format,
    get_optimal_stream,
    print_formats,
    print_to_screen,
    delete_files,
)
from drtv_dl.exceptions import (
    DownloadError, 
    MergeError
)

class DRTVDownloader:
    def download(self, info, list_formats, resolution, include_subs, ntmpl):
        base_filename = generate_filename(info, ntmpl)

        stream_url = get_optimal_format(info.get('formats', [])).get('url')
        m3u8_streams = self._download_m3u8_manifest(stream_url)
        parsed_m3u8_streams = M3U8Parser(stream_url, m3u8_streams).parse()

        if list_formats:
            print_formats(parsed_m3u8_streams)
            return
        
        if self._check_if_downloaded(base_filename):
            return

        optimal_stream = get_optimal_stream(parsed_m3u8_streams, resolution, include_subs)
        video_filename = self._download_stream(optimal_stream['video'], base_filename, stream_type='video')
        audio_filename = self._download_stream(optimal_stream['audio'], base_filename, stream_type='audio')
        subtitle_filename = self._download_subtitle(optimal_stream, base_filename, include_subs)

        self._merge_streams(info, video_filename, audio_filename, subtitle_filename, base_filename)
        self._cleanup(video_filename, audio_filename, subtitle_filename)

    def _download_stream(self, stream, base_filename, stream_type):
        m3u8 = download_webpage(url=stream['uri'])
        map_uri = M3U8Parser.extract_map_uri(m3u8, stream['uri'])
        if map_uri:
            filename = f"{base_filename}.{stream_type}"
            self._download_file(map_uri, filename, note=f"{stream_type.capitalize()} saved as {filename}")
            return filename
        else:
            logger.error(f"Could not find {stream_type} MAP URI")
            raise DownloadError(f"Could not find {stream_type} MAP URI")

    def _download_subtitle(self, optimal_stream, base_filename, include_subs):
        if include_subs and optimal_stream['subtitle']:
            subtitle_url = optimal_stream['subtitle']['uri']
            vtt_filename = f"{base_filename}.vtt"
            self._download_file(subtitle_url, vtt_filename, note=f"Subtitles saved as {vtt_filename}")
            
            srt_filename = f"{base_filename}.srt"
            vtt_to_srt(vtt_filename, srt_filename)
            os.remove(vtt_filename)
            return srt_filename
        
        return None
    
    @staticmethod
    def _download_m3u8_manifest(stream_url):
        print_to_screen(f"Downloading m3u8 manifest...")
        return download_webpage(
            url=stream_url
        )

    @staticmethod
    def _check_if_downloaded(base_filename):
        if os.path.exists(base_filename + ".mp4"):
            print_to_screen(f"{base_filename} is already downloaded")
            return True
        return False

    @staticmethod
    def _download_file(url, filename, note):
        response = requests.get(url, stream=True, proxies=settings.PROXY)
        response.raise_for_status()
        
        initial_size = int(response.headers.get('content-length', None))
        progress_tracker = ProgressTracker(initial_size, filename)
        
        print_to_screen(f"Destination: {filename}")
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                size = file.write(chunk)
                progress_tracker.update(size)
        
        progress_tracker.finish()

        print_to_screen(note)
    
    @staticmethod
    def _merge_streams(info, video_filename, audio_filename, subtitle_filename, base_filename):
        output_filename = f"{base_filename}.mp4"
        result = Merger.merge(
            video_filename,
            audio_filename,
            subtitle_filename,
            output_filename,
            note=f"{info['id']}: Merging streams into {output_filename}"
        )
        if not result:
            raise MergeError(f"Failed to merge streams for {info['id']}")
    
    @staticmethod
    def _cleanup(video_filename, audio_filename, subtitle_filename):
        delete_files(
            video_filename, 
            audio_filename, 
            subtitle_filename
        )


