from __future__ import annotations

import asyncio
import logging
import os
import threading
from typing import Any, Callable, List

from .base_validator import BaseValidator, ValidationResult

logger = logging.getLogger(__name__)


class AsyncValidator(BaseValidator):
    """Asynchronous validator that uses a sync validator with thread pool execution."""

    def __init__(
        self,
        config: Any,   
        storage: Any,  
        max_concurrency: int | None = None,
        per_task_timeout: float | None = 30.0,
    ) -> None:
        """Initialize async validator with config and storage strategy."""
        super().__init__(config, storage)
        self._sem = asyncio.Semaphore(max_concurrency or min(32, (os.cpu_count() or 4) * 2))
        self._timeout = per_task_timeout
        self._thread_local = threading.local()
        self._sync_validator: BaseValidator | None = None

    def _get_sync_validator(self) -> BaseValidator:
        """Get or create a thread-local sync validator."""
        validator = getattr(self._thread_local, "validator", None)
        if validator is None:
            
            from .sync_validator import SyncValidator
            validator = SyncValidator(self.config, self.storage)
            self._thread_local.validator = validator
        return validator

    async def _validate_one_async(self, file_path: str) -> ValidationResult:
        """Validate a single file asynchronously using thread pool."""
        async with self._sem:  
            return await asyncio.to_thread(self._validate_one_sync, file_path)

    def _validate_one_sync(self, file_path: str) -> ValidationResult:
        """Validate a single file synchronously (runs in thread pool)."""
        validator = self._get_sync_validator()
        return validator.validate_file(file_path)

    async def validate_file(self, file_path: str) -> ValidationResult:
        """Validate a single file asynchronously."""
        try:
            return await asyncio.wait_for(
                self._validate_one_async(file_path), 
                timeout=self._timeout
            ) if self._timeout else await self._validate_one_async(file_path)
        except asyncio.TimeoutError:
            logger.error(f"Timeout validating {file_path}")
            return ValidationResult(
                path=file_path,
                valid=False,
                errors=["TIMEOUT"],
                registry=None,
                data=None
            )
        except Exception as e:
            logger.error(f"Error validating {file_path}: {e}")
            return ValidationResult(
                path=file_path,
                valid=False,
                errors=[repr(e)],
                registry=None,
                data=None
            )

    async def validate_files(self, file_paths: List[str]) -> List[ValidationResult]:
        """Validate multiple files asynchronously."""
        tasks = [asyncio.create_task(self.validate_file(path)) for path in file_paths]
        return await asyncio.gather(*tasks, return_exceptions=True)

    def validate_files_sync(self, file_paths: List[str]) -> List[ValidationResult]:
        """Synchronous wrapper for validate_files."""
        return asyncio.run(self.validate_files(file_paths))