class DRTVDLException(Exception):
    """Base class for all exceptions related to the DRTV downloader."""
    pass


class DownloadError(DRTVDLException):
    """Raised when an error occurs during the download process."""
    pass


class ExtractionError(DRTVDLException):
    """Raised when extracting necessary data (e.g., metadata) fails."""
    pass


class TokenRetrievalError(DRTVDLException):
    """Error in retrieving an anonymous token for API authentication."""
    pass


class ItemIDExtractionError(DRTVDLException):
    """Raised when the item ID can't be extracted from the URL."""
    pass


class SeasonIDExtractionError(DRTVDLException):
    """Raised when the season ID can't be extracted from the URL."""
    pass


class SeriesIDExtractionError(DRTVDLException):
    """Raised when the series ID can't be extracted from the URL."""
    pass


class InvalidURLError(DRTVDLException):
    """Raised when the URL format is invalid for DR TV content."""
    pass


class MergeError(DRTVDLException):
    """Error during the merging of video, audio, or subtitle streams."""
    pass


class StreamNotFoundError(DRTVDLException):
    """Raised when no suitable video, audio, or subtitle stream is found."""
    pass


class ProxyError(DRTVDLException):
    """Error related to the proxy configuration or usage."""
    pass

class ContainerNotSupportedError(DRTVDLException):
    """Raised when the container format is not supported."""
    pass

class FFmpegNotAccessibleError(DRTVDLException):
    """Raised when FFmpeg is not installed or not accessible."""
    pass
