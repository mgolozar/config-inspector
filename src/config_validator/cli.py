from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .core.validation_service import ValidationService
from .core.watcher import watch_with_validation_service
from .utils.logging_setup import configure_logging

logger = logging.getLogger(__name__)


def _setup_logging(verbose: bool) -> None:
    level = "DEBUG" if verbose else "INFO"
    
    # Create logs directory explicitly
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = str(log_dir / "config-validator.log")
    configure_logging(level, log_file=log_file)
    logger.info(f"Logging level set to: {level}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Concurrent YAML config validator")

    p.add_argument("--path", type=Path, default=Path("."), help="Root directory to scan")
    p.add_argument("--report", type=Path, default=Path("report.json"), help="Output JSON report path")
    p.add_argument("--config", type=Path, help="Validation configuration file")
    p.add_argument("--storage-config", type=Path, required=False, default=Path("config/storage-config.yaml"),
                   help="Path to storage strategy configuration file")
    p.add_argument("--replicas-min", type=int, help="Minimum replicas (overrides config file)")
    p.add_argument("--replicas-max", type=int, help="Maximum replicas (overrides config file)")
    p.add_argument("--watch", action="store_true", help="Watch files and revalidate on change")
    p.add_argument("--verbose", action="store_true", help="Verbose logging")

    return p.parse_args(argv)




def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    _setup_logging(args.verbose)

    # Create validation service
    validation_service = ValidationService(
        root_path=args.path,
        report_path=args.report,
        config_path=args.config,
        storage_config_path=args.storage_config,
        replicas_min=args.replicas_min,
        replicas_max=args.replicas_max,
    )

    if args.watch:
        # Run initial validation
        try:
            validation_service.run_validation()
        except Exception as e:
            logger.error("Validation failed: %s", e)
            return 1
        
        # Start watching for changes with efficient incremental validation
        watch_with_validation_service(validation_service)
        return 0
    else:
        # Run single validation
        try:
            validation_service.run_validation()
            return 0
        except Exception as e:
            logger.error("Validation failed: %s", e)
            return 1