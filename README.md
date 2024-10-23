# drtv-dl

drtv-dl is a tool for downloading videos from [DRTV](https://dr.dk/drtv), including encrypted content.

## Installation

To install drtv-dl, run:

```
pip install git+https://github.com/sukkerstjernen/drtv-dl.git
```

Make sure you have [FFmpeg](https://ffmpeg.org) and [Git](https://git-scm.com) installed on your system.

## Usage

### CLI

Basic usage:

```
drtv-dl [URL] [OPTIONS]
```

Example with ntmpl (also works when using it as a Python module):

```
drtv-dl https://www.dr.dk/drtv/serie/den-tid-paa-ugen_473629 \
           --ntmpl "{title} S{season_number}E{episode_number} - {episode_name} [{id}]"
```

This will download the following files:
- "Den tid på ugen S01E01 - Trusselsbreve og chips i hjernen [00252412010].mp4"
- "Den tid på ugen S01E02 - Oktoberfest og den stjålne Picasso [00252412020].mp4"
- "Den tid på ugen S01E03 - Taliban og Svend Svingarm [00252412030].mp4"

### Python Module

```python
import drtv_dl    

drtv_dl.download(
    url="REPLACE_URL", 
    resolution="1080p", 
    include_subs=True
)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Disclaimer

This tool is for educational purposes only. Please respect the copyright and terms of service of [DRTV](https://dr.dk/drtv). The developers of this tool are not responsible for any misuse or legal consequences.