"""
Utility module for configuring and creating application loggers.
"""

import logging
import os
import sys
from datetime import datetime


def get_logger(name: str) -> logging.Logger:
    """
    Create and configure an application logger.

    The logger writes log messages to both:
    1. A UTF-8 encoded log file
    2. The console using UTF-8 encoding

    If the logger has already been configured, the existing logger
    is returned to prevent duplicate handlers.

    Parameters
    ----------
    name : str
        Name of the logger, typically __name__.

    Returns
    -------
    logging.Logger
        Configured logger instance.
    """

    # Create logs directory if it does not exist
    os.makedirs("logs", exist_ok=True)

    # Create a unique log file for each application run
    log_file = os.path.join(
        "logs", f"app_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.log"
    )

    # Create logger
    logger = logging.getLogger(name)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Do not propagate messages to the root logger
    # This prevents duplicate log messages in some applications.
    logger.propagate = False

    # Log message format
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )

    # ---------------------------------------------------------
    # File Handler - UTF-8
    # ---------------------------------------------------------

    file_handler = logging.FileHandler(log_file, encoding="utf-8")

    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # ---------------------------------------------------------
    # Console Handler - UTF-8
    # ---------------------------------------------------------

    console_handler = logging.StreamHandler(sys.stdout)

    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Force console output to UTF-8 on Windows
    if hasattr(console_handler.stream, "reconfigure"):
        try:
            console_handler.stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    # ---------------------------------------------------------
    # Add handlers
    # ---------------------------------------------------------

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
