import logging

class DRTVDLCustomFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, 'module_class'):
            record.module_class = record.module
        return super().format(record)

def setup_logger():
    logger = logging.getLogger('drtv_dl')
    logger.setLevel(logging.INFO)
    formatter = DRTVDLCustomFormatter('[%(module_class)s] - %(message)s')
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()