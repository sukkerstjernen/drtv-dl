import ffmpeg
import os

from drtv_dl.exceptions import (
    ContainerNotSupportedError, 
    MergeError
)
from drtv_dl.utils.helpers import print_to_screen

class Merger:
    cwd = os.getcwd()
    output_params = {'c:v': 'copy', 'c:a': 'copy'}

    def __init__(self, video_file, audio_file, subtitle_file, output_file, cfmt):
        self.video_file = os.path.join(self.cwd, video_file)
        self.audio_file = os.path.join(self.cwd, audio_file)
        self.subtitle_file = os.path.join(self.cwd, subtitle_file) if subtitle_file else None
        self.output_file = os.path.join(self.cwd, output_file)
        self.cfmt = cfmt
    
    def _get_input_streams(self):
        streams = [
            ffmpeg.input(self.video_file),
            ffmpeg.input(self.audio_file)
        ]
        
        if self.subtitle_file:
            streams.append(ffmpeg.input(self.subtitle_file))
            if self.cfmt in ["mkv", "webm"]:
                self.output_params['c:s'] = 'srt'
            elif self.cfmt in ["mp4", "mov"]:
                self.output_params['c:s'] = 'mov_text'
            else:
                raise ContainerNotSupportedError(f"Container format '{self.cfmt}' not supported with subtitles")
        
        return streams

    def _merge_streams(self):
        streams  = self._get_input_streams()
        try:
            ffmpeg.output(
                *streams,
                self.output_file,
                **self.output_params
            ).run(quiet=True, overwrite_output=True)
            return True
        except Exception as e:
            raise MergeError(f"Error merging files: {str(e)}")
    
    def merge(self, note=None):
        print_to_screen(note)
        return self._merge_streams()
