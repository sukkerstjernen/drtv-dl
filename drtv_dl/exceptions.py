class DRTVDownloaderError(Exception):
    """Base class for all exceptions related to the DRTV downloader."""
    pass


class DownloadError(DRTVDownloaderError):
    """Raised when an error occurs during the download process."""
    pass


class ExtractionError(DRTVDownloaderError):
    """Raised when extracting necessary data (e.g., metadata) fails."""
    pass


class TokenRetrievalError(DRTVDownloaderError):
    """Error in retrieving an anonymous token for API authentication."""
    pass


class ItemIDExtractionError(DRTVDownloaderError):
    """Raised when the item ID can't be extracted from the URL."""
    pass


class SeasonIDExtractionError(DRTVDownloaderError):
    """Raised when the season ID can't be extracted from the URL."""
    pass


class SeriesIDExtractionError(DRTVDownloaderError):
    """Raised when the series ID can't be extracted from the URL."""
    pass


class InvalidURLError(DRTVDownloaderError):
    """Raised when the URL format is invalid for DR TV content."""
    pass


class MergeError(DRTVDownloaderError):
    """Error during the merging of video, audio, or subtitle streams."""
    pass


class StreamNotFoundError(DRTVDownloaderError):
    """Raised when no suitable video, audio, or subtitle stream is found."""
    pass


class ProxyError(DRTVDownloaderError):
    """Error related to the proxy configuration or usage."""
    pass