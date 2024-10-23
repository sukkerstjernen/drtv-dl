
from collections import defaultdict
from urllib.parse import urljoin, unquote
import re

class M3U8Parser:
    def __init__(self, base_uri, m3u8_content):
        self.base_uri = base_uri
        self.m3u8_content = m3u8_content.splitlines()
        self.streams = defaultdict(list)
    
    def parse(self):
        stream_info = {}
        for line in self.m3u8_content:
            line = line.strip()
            if line.startswith("#EXT-X-MEDIA:TYPE=AUDIO"):
                audio_info = self._parse_attributes(line)
                self.streams['audio'].append({
                    **audio_info,
                    'uri': self._get_complete_uri(audio_info.get('uri'))
                })
            elif line.startswith("#EXT-X-MEDIA:TYPE=SUBTITLES"):
                subtitle_info = self._parse_attributes(line)
                self.streams['subtitles'].append({
                    **subtitle_info,
                    'uri': self._get_complete_uri(subtitle_info.get('uri'), is_subtitle=True)
                })
            elif line.startswith("#EXT-X-STREAM-INF:"):
                stream_info = self._parse_stream(line)
            elif stream_info:
                self.streams['video'].append({
                    **stream_info,
                    'uri': self._get_complete_uri(line)
                })
                stream_info = {} # reset for the next one
        return dict(self.streams)
    
    def _parse_attributes(self, line):
        attrs = {}
        matches = re.findall(r'([A-Z\-]+)=("[^"]*"|\d+x\d+|\d+|\w+)', line)
        for key, value in matches:
            attrs[key.lower()] = value.strip('"')
        return attrs
    
    def _parse_stream(self, line):
        return self._parse_attributes(line)
    
    def _get_complete_uri(self, uri, is_subtitle=False):
        if is_subtitle:
            uri = uri.replace("/playlist.m3u8", ".vtt")
        return urljoin(self.base_uri, uri)

    @staticmethod
    def extract_map_uri(m3u8_content, base_url):
            for line in m3u8_content.splitlines():
                if line.startswith('#EXT-X-MAP:'):
                    uri_part = line.split('URI=')[1].split(',')[0].strip('"')
                    uri = uri_part.split('"')[0]
                    return urljoin(base_url, unquote(uri))
            return None