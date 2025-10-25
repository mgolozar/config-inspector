from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

import yaml

from .core.discovery import Discovery
 
from .core.report import aggregate_and_summarize
from .core.watcher import watch_polling
from .core.config import load_validation_config
from .utils.logging_setup import configure_logging
from .storage.strategy_loader import load_storage_strategy
from .core.validator import ValidationSession

logger = logging.getLogger(__name__)


def _setup_logging(verbose: bool) -> None:
    level = "DEBUG" if verbose else "INFO"
    
    # Create logs directory explicitly
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = str(log_dir / "config-validator.log")
    configure_logging(level, log_file=log_file)
    logger.info(f"Logging level set to: {level}")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


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


def run_once(
    root: Path,
    report_path: Path,
    config_path: Path = None,
    storage_config_path: Path = None,
    replicas_min: int = None,
    replicas_max: int = None
) -> dict[str, Any]:
    # Load validation config (core rules)
    config = load_validation_config(config_path)

    # Apply CLI overrides
    if replicas_min is not None:
        config.replicas_min = replicas_min
    if replicas_max is not None:
        config.replicas_max = replicas_max

    # Load storage strategy
    if storage_config_path is None or not storage_config_path.exists():
        raise FileNotFoundError(f"Storage config file not found: {storage_config_path}")

    storage_config = load_yaml(storage_config_path)
    storage_strategy = load_storage_strategy(storage_config)

    # Run discovery
    discovery = Discovery(root, storage_strategy)
    files = discovery.discover_yaml_files(root)
    logger.info("Discovered %d YAML files", len(files))
    
    # Run validation
    # results = [Validator.validate_file(p, config) for p in files]

    session = ValidationSession(config, storage_strategy)
    results = [session.validate_file(str(p)) for p in files]
    
    report = aggregate_and_summarize(results)

    # Save report
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    logger.info("Report written to %s", report_path)

    # Human-readable summary
    print(
        f"Valid: {report['summary']['valid_count']} Invalid: {report['summary']['invalid_count']} "
        f"Issues: {report['summary']['total_issues']}\n"
        f"Registries: {report['summary']['registry_counts']}"
    )

    return report


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    _setup_logging(args.verbose)

    if args.watch:
        run_once(
            args.path,
            args.report,
            args.config,
            args.storage_config,
            args.replicas_min,
            args.replicas_max,
        )
        watch_polling(
            args.path,
           lambda: print("Watching files...")
 )
        return 0
    else:
        run_once(
            args.path,
            args.report,
            args.config,
            args.storage_config,
            args.replicas_min,
            args.replicas_max,
        )
        return 0