from __future__ import annotations
import logging
from logging.config import dictConfig


_LEVELS = {
"CRITICAL": logging.CRITICAL,
"ERROR": logging.ERROR,
"WARNING": logging.WARNING,
"INFO": logging.INFO,
"DEBUG": logging.DEBUG,
}


def configure_logging(level: str = "INFO") -> None:
    lvl = _LEVELS.get(level.upper(), logging.INFO)
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "std": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                }
            },
            "handlers": {
                "stderr": {
                    "class": "logging.StreamHandler",
                    "formatter": "std",
                    "level": lvl,
                }
            },
            "root": {"handlers": ["stderr"], "level": lvl},
            "disable_existing_loggers": False,
        }
    )