import logging
import os
from logging.handlers import TimedRotatingFileHandler
import json_log_formatter

def setup_logging(log_dir="logs", log_file="app.json"):
    """
    Configure logging with JSON format, rotation, and console output.
    """
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, log_file)

    formatter = json_log_formatter.JSONFormatter()

    file_handler = TimedRotatingFileHandler(log_file_path, when="midnight", interval=1)
    file_handler.suffix = "%Y%m%d"
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, stream_handler],
    )
    return logging.getLogger(__name__)
