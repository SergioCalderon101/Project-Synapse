"""Logging configuration and setup."""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    app_logger: Optional[logging.Logger] = None
) -> None:
    """Configure application logging.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        app_logger: Flask app logger (optional)
    """
    # Create logs directory if needed
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Formatter
    log_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s'
    )
    
    # Configure root or app logger
    logger = app_logger if app_logger else logging.getLogger()
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Console handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)
    
    # File handler (if path provided)
    if log_file:
        try:
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setFormatter(log_formatter)
            logger.addHandler(file_handler)
        except (OSError, PermissionError) as e:
            print(
                f"WARNING: No se pudo configurar logging a archivo '{log_file}': {e}",
                file=sys.stderr
            )
    
    # Prevent propagation if using app logger
    if app_logger:
        app_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
