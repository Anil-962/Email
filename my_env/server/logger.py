import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    """
    Standardizes logging across the application to ensure clean, actionable, 
    and production-ready telemetry.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers if logger is imported multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        
        # Production formatting includes timestamps, origin service, and severity
        formatter = logging.Formatter(
            '%(asctime)s | [%(levelname)s] | %(name)s : %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
