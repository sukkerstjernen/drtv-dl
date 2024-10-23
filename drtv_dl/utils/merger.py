import ffmpeg
import os

from drtv_dl.utils.helpers import print_to_screen
from drtv_dl.logger import logger

class Merger:
    cwd = os.getcwd()
    output_params = {'c:v': 'copy', 'c:a': 'copy'}

    def __init__(self, video_file, audio_file, subtitle_file, output_file):
        self.video_file = os.path.join(self.cwd, video_file)
        self.audio_file = os.path.join(self.cwd, audio_file)
        self.subtitle_file = os.path.join(self.cwd, subtitle_file) if subtitle_file else None
        self.output_file = os.path.join(self.cwd, output_file)
    
    def _get_input_streams(self):
        streams = [
            ffmpeg.input(self.video_file),
            ffmpeg.input(self.audio_file)
        ]
        
        if self.subtitle_file:
            streams.append(ffmpeg.input(self.subtitle_file))
            self.output_params['c:s'] = 'mov_text'
        
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
        except ffmpeg.Error as e:
            logger.error(f"Error merging files: {str(e)}")
            return False
    
    @staticmethod
    def merge(video_file, audio_file, subtitle_file, output_file, note=None):
        print_to_screen(note)
        merger = Merger(video_file, audio_file, subtitle_file, output_file)
        return merger._merge_streams()
