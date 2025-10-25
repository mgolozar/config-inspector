from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, List

import yaml

from .base_validator import BaseValidator, ValidationResult
from .config import load_validation_config
from .discovery import Discovery
from .report import aggregate_and_summarize
from .sync_validator import SyncValidator
from .async_validator import AsyncValidator
from ..storage.strategy_loader import load_storage_strategy

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for orchestrating validation operations."""

    def __init__(
        self,
        root_path: Path,
        report_path: Path,
        config_path: Path | None = None,
        storage_config_path: Path | None = None,
        replicas_min: int | None = None,
        replicas_max: int | None = None,
        use_async: bool = True,
        max_concurrency: int | None = None,
    ) -> None:
        """Initialize validation service."""
        self.root_path = root_path
        self.report_path = report_path
        self.config_path = config_path
        self.storage_config_path = storage_config_path
        self.replicas_min = replicas_min
        self.replicas_max = replicas_max
        self.use_async = use_async
        self.max_concurrency = max_concurrency

        # Lazy-loaded components
        self._config = None
        self._storage_strategy = None
        self._discovery = None
        self._validator: BaseValidator | None = None

    def _load_config(self) -> None:
        """Load validation configuration."""
        if self._config is None:
            # Load validation config (core rules)
            self._config = load_validation_config(self.config_path)

            # Apply CLI overrides
            if self.replicas_min is not None:
                self._config.replicas_min = self.replicas_min
            if self.replicas_max is not None:
                self._config.replicas_max = self.replicas_max

    def _load_storage_strategy(self) -> None:
        """Load storage strategy."""
        if self._storage_strategy is None:
            if self.storage_config_path is None or not self.storage_config_path.exists():
                raise FileNotFoundError(f"Storage config file not found: {self.storage_config_path}")

            storage_config = self.load_yaml(self.storage_config_path)
            self._storage_strategy = load_storage_strategy(storage_config)

    def _setup_discovery(self) -> None:
        """Setup file discovery."""
        if self._discovery is None:
            self._load_storage_strategy()
            self._discovery = Discovery(self.root_path, self._storage_strategy)

    def _setup_validator(self) -> None:
        """Setup validator based on configuration."""
        if self._validator is None:
            self._load_config()
            self._load_storage_strategy()
            
            if self.use_async:
                self._validator = AsyncValidator(
                    config=self._config,
                    storage=self._storage_strategy,
                    max_concurrency=self.max_concurrency
                )
            else:
                self._validator = SyncValidator(
                    config=self._config,
                    storage=self._storage_strategy
                )

    @staticmethod
    def load_yaml(path: Path) -> dict[str, Any]:
        """Load YAML file."""
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def discover_files(self) -> List[Path]:
        """Discover YAML files to validate."""
        self._setup_discovery()
        files = self._discovery.discover_yaml_files(self.root_path)
        logger.info("Discovered %d YAML files", len(files))
        return files

    def validate_files(self, files: List[Path]) -> List[ValidationResult]:
        """Validate files using the configured validator."""
        self._setup_validator()
        file_paths = [str(f) for f in files]
        
        if self.use_async:
            return self._validator.validate_files_sync(file_paths)
        else:
            return self._validator.validate_files(file_paths)

    def generate_report(self, results: List[ValidationResult]) -> dict[str, Any]:
        """Generate validation report from results."""
        
        dict_results = []
        for result in results:
            dict_results.append({
                "path": result.path,
                "valid": result.valid,
                "errors": result.errors,
                "registry": result.registry,
                "data": result.data
            })
        
        return aggregate_and_summarize(dict_results)

    def save_report(self, report: dict[str, Any]) -> None:
        """Save validation report to file."""
         
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        dynamic_report_path = self.report_path.parent / f"Report{current_time}.json"
        
        try:
             
            dynamic_report_path.parent.mkdir(parents=True, exist_ok=True)
            
            
            dynamic_report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            logger.info("Report written to %s", dynamic_report_path)
            
        except PermissionError as e:
            logger.error("Permission denied when writing report to %s: %s", dynamic_report_path, e)
            self._save_report_fallback(report, current_time)
            
        except OSError as e:
            logger.error("OS error when writing report to %s: %s", dynamic_report_path, e)
            self._save_report_fallback(report, current_time)
            
        except Exception as e:
            logger.error("Unexpected error when writing report: %s", e)
            raise

    def _save_report_fallback(self, report: dict[str, Any], current_time: str) -> None:
        """Try to save report to fallback locations."""
         
        fallback_path = Path.cwd() / f"Report{current_time}.json"
        try:
            fallback_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
            logger.info("Report written to fallback location: %s", fallback_path)
        except PermissionError as fallback_error:
            logger.error("Permission denied for fallback location %s: %s", fallback_path, fallback_error)
            
             
            import tempfile
            temp_dir = Path(tempfile.gettempdir())
            temp_report_path = temp_dir / f"config-validator-report-{current_time}.json"
            try:
                temp_report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
                logger.info("Report written to temporary location: %s", temp_report_path)
            except Exception as temp_error:
                logger.error("Failed to write report to any location: %s", temp_error)
                raise RuntimeError(f"Unable to write report file. Tried: {fallback_path}, {temp_report_path}")

    def print_summary(self, report: dict[str, Any]) -> None:
        """Print validation summary."""
        print(
            f"Valid: {report['summary']['valid_count']} Invalid: {report['summary']['invalid_count']} "
            f"Issues: {report['summary']['total_issues']}\n"
            f"Registries: {report['summary']['registry_counts']}"
        )

    def run_validation(self) -> dict[str, Any]:
        """Run complete validation process."""
         
        files = self.discover_files()

         
        results = self.validate_files(files)

         
        report = self.generate_report(results)

         
        self.save_report(report)

         
        self.print_summary(report)

        return report

    def validate_specific_files(self, file_paths: List[str]) -> dict[str, Any]:
        """Validate specific files."""
         
        files = [Path(p) for p in file_paths]

         
        results = self.validate_files(files)

         
        report = self.generate_report(results)

        
        self.save_report(report)

         
        self.print_summary(report)

        return report