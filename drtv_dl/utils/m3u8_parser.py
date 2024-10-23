import re
from collections import defaultdict
from urllib.parse import (
    urljoin, 
    unquote
)

class M3U8Parser:
    def __init__(self, base_uri, m3u8_content):
        self.base_uri = base_uri
        self.m3u8_content = m3u8_content.splitlines()
        self.streams = defaultdict(list)
        self.audio_codecs = {}

    def parse(self):
        current_stream = None
        for line in self.m3u8_content:
            line = line.strip()
            if line.startswith("#EXT-X-MEDIA:TYPE=AUDIO"):
                attrs = self._parse_attributes(line)
                attrs['uri'] = self._get_complete_uri(attrs.get('uri'))
                self.streams['audio'].append(attrs)
            elif line.startswith("#EXT-X-MEDIA:TYPE=SUBTITLES"):
                attrs = self._parse_attributes(line)
                attrs['uri'] = self._get_complete_uri(attrs.get('uri'), is_subtitle=True)
                self.streams['subtitles'].append(attrs)
            elif line.startswith("#EXT-X-STREAM-INF:"):
                attrs = self._parse_attributes(line)
                codecs = attrs.pop('codecs', '').split(',')
                attrs['video_codec'] = codecs[0] if len(codecs) > 0 else None
                attrs['audio_codec'] = codecs[1] if len(codecs) > 1 else None
                audio_group = attrs.get('audio')
                if audio_group and attrs['audio_codec']:
                    self.audio_codecs[audio_group] = attrs['audio_codec']
                current_stream = attrs
            elif current_stream:
                current_stream['uri'] = self._get_complete_uri(line)
                current_stream['codec'] = current_stream.pop('video_codec')
                self.streams['video'].append(current_stream)
                current_stream = None

        for audio_stream in self.streams['audio']:
            group_id = audio_stream.get('group-id')
            audio_stream['codec'] = self.audio_codecs.get(group_id)

        return dict(self.streams)

    def _parse_attributes(self, line):
        attrs = {}
        pattern = re.compile(r'([A-Z\-]+)=("([^"]*)"|([^",]*))(?:,|$)')
        for match in pattern.findall(line):
            key = match[0].lower()
            value = match[2] or match[3]
            attrs[key] = value
        return attrs

    def _get_complete_uri(self, uri, is_subtitle=False):
        if is_subtitle:
            uri = uri.replace("/playlist.m3u8", ".vtt")
        return urljoin(self.base_uri, uri)

    @staticmethod
    def extract_map_uri(m3u8_content, base_url):
        for line in m3u8_content.splitlines():
            if line.startswith('#EXT-X-MAP:'):
                uri_match = re.search(r'URI="([^"]+)"', line)
                if uri_match:
                    return urljoin(base_url, unquote(uri_match.group(1)))
        return None