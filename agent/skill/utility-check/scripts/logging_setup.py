"""Structured logging."""

import logging
import sys


def configure(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("utility_check")
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger
