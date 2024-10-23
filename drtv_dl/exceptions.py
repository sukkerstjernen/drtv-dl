class DRTVDownloaderError(Exception):
    pass

class DownloadError(DRTVDownloaderError):
    pass

class ExtractionError(DRTVDownloaderError):
    pass

class TokenRetrievalError(DRTVDownloaderError):
    pass

class ItemIDExtractionError(DRTVDownloaderError):
    pass

class SeasonIDExtractionError(DRTVDownloaderError):
    pass

class SeriesIDExtractionError(DRTVDownloaderError):
    pass

class InvalidURLError(DRTVDownloaderError):
    pass

class MergeError(DRTVDownloaderError):
    pass

class StreamNotFoundError(DRTVDownloaderError):
    pass

class ProxyError(DRTVDownloaderError):
    pass