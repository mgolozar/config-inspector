from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from .config import load_validation_config
from .discovery import Discovery
from .report import aggregate_and_summarize
from .validator import ValidationSession
from ..storage.strategy_loader import load_storage_strategy
import asyncio
from .async_validator import AsyncValidator  # مسیر صحیح ایمپورت خودت
import os

logger = logging.getLogger(__name__)


class ValidationService:

    def __init__(
        self,
        root_path: Path,
        report_path: Path,
        config_path: Path | None = None,
        storage_config_path: Path | None = None,
        replicas_min: int | None = None,
        replicas_max: int | None = None,
    ):

        self.root_path = root_path
        self.report_path = report_path
        self.config_path = config_path
        self.storage_config_path = storage_config_path
        self.replicas_min = replicas_min
        self.replicas_max = replicas_max

        # Initialize components
        self._config = None
        self._storage_strategy = None
        self._discovery = None
        self._validation_session = None
    def _new_validation_session(self) -> ValidationSession:
    
        self._load_config()
        self._load_storage_strategy()
        return ValidationSession(self._config, self._storage_strategy)

     
    def _session_factory(self):
      
        return self._new_validation_session()

    def _validate_sync(self, session: ValidationSession, path_str: str):
        return session.validate_file(path_str)

    async def validate_files_async(self, files: list[Path]) -> list[Any]:
        # می‌تونی این عدد را از config یا CLI بگیری
        max_workers = min(32, (os.cpu_count() or 4) * 2)

        validator = AsyncValidator(
            session_factory=self._session_factory,
            validate_sync=self._validate_sync,
            max_concurrency=max_workers,
            per_task_timeout=30.0,   
        )
        return await validator.validate_files(files)

    def _load_config(self) -> None:
        
        if self._config is None:
            # Load validation config (core rules)
            self._config = load_validation_config(self.config_path)

            # Apply CLI overrides
            if self.replicas_min is not None:
                self._config.replicas_min = self.replicas_min
            if self.replicas_max is not None:
                self._config.replicas_max = self.replicas_max

    def _load_storage_strategy(self) -> None:
        
        if self._storage_strategy is None:
            if self.storage_config_path is None or not self.storage_config_path.exists():
                raise FileNotFoundError(f"Storage config file not found: {self.storage_config_path}")

            storage_config = self.load_yaml(self.storage_config_path)
            self._storage_strategy = load_storage_strategy(storage_config)

    def _setup_discovery(self) -> None:
        
        if self._discovery is None:
            self._load_storage_strategy()
            self._discovery = Discovery(self.root_path, self._storage_strategy)

    def _setup_validation_session(self) -> None:
    
        if self._validation_session is None:
            self._load_config()
            self._load_storage_strategy()
            self._validation_session = ValidationSession(self._config, self._storage_strategy)

    @staticmethod
    def load_yaml(path: Path) -> dict[str, Any]:

        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def discover_files(self) -> list[Path]:

        self._setup_discovery()
        files = self._discovery.discover_yaml_files(self.root_path)
        logger.info("Discovered %d YAML files", len(files))
        return files

    def validate_files(self, files: list[Path]) -> list[Any]:
        results = asyncio.run(self.validate_files_async(files))
        return results

        

    def generate_report(self, results: list[Any]) -> dict[str, Any]:

        report = aggregate_and_summarize(results)
        return report

    def save_report(self, report: dict[str, Any]) -> None:

        # Generate dynamic filename with current datetime
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        dynamic_report_path = self.report_path.parent / f"Report{current_time}.json"
        
        try:
            # Ensure parent directory exists
            dynamic_report_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the report file
            dynamic_report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            logger.info("Report written to %s", dynamic_report_path)
            
        except PermissionError as e:
            logger.error("Permission denied when writing report to %s: %s", dynamic_report_path, e)
            
            # Try to write to a fallback location (current working directory)
            fallback_path = Path.cwd() / f"Report{current_time}.json"
            try:
                fallback_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
                logger.info("Report written to fallback location: %s", fallback_path)
            except PermissionError as fallback_error:
                logger.error("Permission denied for fallback location %s: %s", fallback_path, fallback_error)
                
                # Try to write to temp directory
                import tempfile
                temp_dir = Path(tempfile.gettempdir())
                temp_report_path = temp_dir / f"config-validator-report-{current_time}.json"
                try:
                    temp_report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
                    logger.info("Report written to temporary location: %s", temp_report_path)
                except Exception as temp_error:
                    logger.error("Failed to write report to any location: %s", temp_error)
                    raise RuntimeError(f"Unable to write report file. Tried: {dynamic_report_path}, {fallback_path}, {temp_report_path}")
                    
        except OSError as e:
            logger.error("OS error when writing report to %s: %s", dynamic_report_path, e)
            
            # Try fallback to current directory
            fallback_path = Path.cwd() / f"Report{current_time}.json"
            try:
                fallback_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
                logger.info("Report written to fallback location: %s", fallback_path)
            except Exception as fallback_error:
                logger.error("Failed to write report to fallback location: %s", fallback_error)
                raise RuntimeError(f"Unable to write report file: {e}")
                
        except Exception as e:
            logger.error("Unexpected error when writing report: %s", e)
            raise

    def print_summary(self, report: dict[str, Any]) -> None:

        print(
            f"Valid: {report['summary']['valid_count']} Invalid: {report['summary']['invalid_count']} "
            f"Issues: {report['summary']['total_issues']}\n"
            f"Registries: {report['summary']['registry_counts']}"
        )

    def run_validation(self) -> dict[str, Any]:

        # Discover files
        files = self.discover_files()

        # Validate files
        results = self.validate_files(files)

        # Generate report
        report = self.generate_report(results)

        # Save report
        self.save_report(report)

        # Print summary
        self.print_summary(report)

        return report

    def validate_specific_files(self, file_paths: list[str]) -> dict[str, Any]:

        # Convert string paths to Path objects
        files = [Path(p) for p in file_paths]

        # Validate files
        results = self.validate_files(files)

        # Generate report
        report = self.generate_report(results)

        # Save report
        self.save_report(report)

        # Print summary
        self.print_summary(report)

        return report
