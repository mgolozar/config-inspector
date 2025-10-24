from __future__ import annotations


import argparse
import json
import logging
from pathlib import Path
from typing import Any


from .core.discovery import Discovery
from .storage.local_strategy import LocalStrategy
from .core.validator import Validator   
from .core.report import aggregate_and_summarize
from .core.watcher import watch_polling
from .core.config import load_validation_config
from .utils.logging_setup import configure_logging  


logger = logging.getLogger(__name__)

def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s")

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Concurrent YAML config validator")
    p.add_argument("--path", type=Path, default=Path("."), help="Root directory to scan")
    p.add_argument("--report", type=Path, default=Path("report.json"), help="Output JSON path")
    p.add_argument("--config", type=Path, help="Validation configuration file")
    p.add_argument("--replicas-min", type=int, help="Minimum replicas (overrides config file)")
    p.add_argument("--replicas-max", type=int, help="Maximum replicas (overrides config file)")
    p.add_argument("--watch", action="store_true", help="Watch files and revalidate on change")
    p.add_argument("--verbose", action="store_true", help="Verbose logging")
    return p.parse_args(argv)

def run_once(root: Path, report_path: Path, config_path: Path = None, replicas_min: int = None, replicas_max: int = None) -> dict[str, Any]:
    # Load configuration
    config = load_validation_config(config_path)
    
    # Override with command line arguments if provided
    if replicas_min is not None:
        config.replicas_min = replicas_min
    if replicas_max is not None:
        config.replicas_max = replicas_max
    
    # from concurrent.futures import as_completed

    # executor = BoundedExecutor(max_workers=16, max_queue=512)
    # futs = [executor.submit(Validator.validate_file, p, config) for p in iter_yaml_files(root)]

    # results = []
    # for fut in as_completed(futs):
    #     results.append(fut.result())

    # executor.shutdown()
    # logger.info("Processed %d YAML files", len(results))

    discovery = Discovery(root, LocalStrategy({
        'base_path': str(root)
    }))

    files = discovery.discover_yaml_files(root)
    logger.info("Discovered %d YAML files", len(files))
    results = [Validator.validate_file(p, config) for p in files]
    report = aggregate_and_summarize(results)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    logger.info("Report written to %s", report_path)
    # Print short human summary to stdout
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
        watch_polling(args.path, lambda: run_once(args.path, args.report, args.config, args.replicas_min, args.replicas_max))
        return 0
    else:
        run_once(args.path, args.report, args.config, args.replicas_min, args.replicas_max)
        return 0



# from __future__ import annotations
# import argparse
# import json
# import logging
# from pathlib import Path
# from typing import List


# from .utils.logging_setup import configure_logging
# from .discovery import discover_configs
# from .validation.core import validate_all
# from .validation.rules import default_rules, load_plugins
# from .reporting.json_reporter import write_report
# from .watcher import watch_loop


# log = logging.getLogger(__name__)




# def build_parser() -> argparse.ArgumentParser:
#     p = argparse.ArgumentParser(prog="config-validator", description="Validate YAML configs")
#     p.add_argument("--root", required=True, help="Root directory to scan for YAML files")
#     p.add_argument("--watch", action="store_true", help="Watch mode: re-validate on changes")
#     p.add_argument("--report", required=False, default="out/report.json", help="Path to write JSON report")
#     p.add_argument("--workers", type=int, default=4, help="Number of validation worker threads")
#     p.add_argument("--log-level", default="INFO", choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"], help="Logging level")
#     return p




# def main(argv: List[str] | None = None) -> int:
#     parser = build_parser()
#     args = parser.parse_args(argv)


#     configure_logging(args.log_level)


#     root = Path(args.root)
#     if not root.exists():
#         raise SystemExit(f"Root does not exist: {root}")


#     # Load rules + plugins
#     rules = default_rules()
#     load_plugins(rules)


#     # First run
#     files = discover_configs(root)
#     results = validate_all(files, rules, workers=args.workers)
#     write_report(Path(args.report), results)
#     log.info("Initial validation complete: %s issues", sum(len(r["issues"]) for r in results.values()))


#     if args.watch:
#         watch_loop(root, rules, Path(args.report), workers=args.workers)


#     return 0
# # def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
# #     if issubclass(exc_type, KeyboardInterrupt):
# #         # کاربر Ctrl+C زد، لاگ ننداز
# #         sys.__excepthook__(exc_type, exc_value, exc_traceback)
# #         return

# #     log = logging.getLogger("UncaughtException")
# #     log.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

# # # نصب global handler
# # sys.excepthook = handle_uncaught_exception

# if __name__ == "__main__":
#     raise SystemExit(main())