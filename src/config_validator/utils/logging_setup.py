from __future__ import annotations
import logging
from logging.config import dictConfig
from pathlib import Path


_LEVELS = {
"CRITICAL": logging.CRITICAL,
"ERROR": logging.ERROR,
"WARNING": logging.WARNING,
"INFO": logging.INFO,
"DEBUG": logging.DEBUG,
}


def configure_logging(level: str = "INFO", log_file: str = None) -> None:
 
    lvl = _LEVELS.get(level.upper(), logging.INFO)
    
    # Create log file directory if needed
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    handlers_config = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "std",
            "level": lvl,
        }
    }
    
     
    if log_file:
        handlers_config["file"] = {
            "class": "logging.FileHandler",
            "formatter": "detailed",
            "level": logging.DEBUG,  # Always log DEBUG and above to file
            "filename": log_file,
            "encoding": "utf-8",
        }
    
    handlers_list = list(handlers_config.keys())
    
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "std": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "detailed": {
                    "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(funcName)s() | %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                }
            },
            "handlers": handlers_config,
            "root": {"handlers": handlers_list, "level": lvl},
            "disable_existing_loggers": False,
        }
    )
    
    logger = logging.getLogger(__name__)
    if log_file:
        logger.info(f"Logging configured. File logs: {log_file}")