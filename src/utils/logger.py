"""
Minimal logger setup for the application.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

from src.utils.config import get_settings

settings = get_settings()

log_format = logging.Formatter(
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)

file_handler: Optional[RotatingFileHandler] = None
log_file_path = settings.LOG_FILE

if log_file_path and log_file_path.strip():
    try:
        log_dir = os.path.dirname(log_file_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file_path, maxBytes=100 * 1024 * 1024, backupCount=5
        )
        file_handler.setFormatter(log_format)
    except Exception as e:
        _temp_setup_logger = logging.getLogger(f"{__name__}.setup_warning")
        _temp_console_handler = logging.StreamHandler()
        _temp_console_handler.setFormatter(log_format)
        _temp_setup_logger.addHandler(_temp_console_handler)
        _temp_setup_logger.setLevel(logging.WARNING)
        _temp_setup_logger.warning(
            f"Failed to initialize file logger for path '{log_file_path}': {e}. "
            f"File logging will be disabled. Check log file path and permissions."
        )
        _temp_setup_logger.removeHandler(_temp_console_handler)
        file_handler = None
elif log_file_path is not None:
    _temp_setup_logger = logging.getLogger(f"{__name__}.setup_warning")
    _temp_console_handler = logging.StreamHandler()
    _temp_console_handler.setFormatter(log_format)
    _temp_setup_logger.addHandler(_temp_console_handler)
    _temp_setup_logger.setLevel(logging.WARNING)
    _temp_setup_logger.warning(
        "Log file path is configured as an empty string. File logging will be disabled."
    )
    _temp_setup_logger.removeHandler(_temp_console_handler)
    file_handler = None


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with configured handlers.

    Args:
        name: The name of the logger (usually __name__)

    Returns:
        A configured logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.addHandler(console_handler)
        if file_handler:
            logger.addHandler(file_handler)
        level_name = settings.LOG_LEVEL.upper()
        level = getattr(logging, level_name, logging.INFO)
        if not isinstance(level, int):
            _temp_setup_logger = logging.getLogger(f"{__name__}.setup_warning")
            _temp_console_handler = logging.StreamHandler()
            _temp_console_handler.setFormatter(log_format)
            _temp_setup_logger.addHandler(_temp_console_handler)
            _temp_setup_logger.setLevel(logging.WARNING)
            _temp_setup_logger.warning(
                f"Invalid log level '{level_name}' in settings. Defaulting to INFO."
            )
            _temp_setup_logger.removeHandler(_temp_console_handler)
            level = logging.INFO
        logger.setLevel(level)
    return logger
