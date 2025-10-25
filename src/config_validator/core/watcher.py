from __future__ import annotations

import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, TYPE_CHECKING

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

if TYPE_CHECKING:
    from .validation_service import ValidationService

log = logging.getLogger(__name__)

# Patterns to ignore during file watching
IGNORE_PATTERNS = [
    "**/.git/**",
    "**/__pycache__/**",
    "**/node_modules/**",
    "**/.pytest_cache/**",
    "**/.mypy_cache/**",
    "**/*.pyc",
]

# Patterns to watch (YAML config files only)
WATCH_PATTERNS = [
    "*.yml",
    "*.yaml",
]


class BatchedEventHandler(PatternMatchingEventHandler):
 

    def __init__(
        self,
        callback: Callable[[set[str], set[str]], None],
        debounce_ms: int = 250,
    ):
 
        super().__init__(
            patterns=WATCH_PATTERNS,
            ignore_patterns=IGNORE_PATTERNS,
        )
        self.callback = callback
        self.debounce_ms = debounce_ms

         
        self._lock = threading.Lock()
        self._changed_files: set[str] = set()
        self._deleted_files: set[str] = set()
        self._timer: threading.Timer | None = None
        
         
        self._file_hashes: dict[str, str] = {}

    def _has_file_content_changed(self, file_path: str) -> bool:
        """Check if file content has actually changed by comparing hashes."""
        try:
            import hashlib
            path = Path(file_path)
            if not path.exists():
                return False
                
             
            with path.open('rb') as f:
                current_hash = hashlib.md5(f.read()).hexdigest()
            
             
            old_hash = self._file_hashes.get(file_path)
            if old_hash != current_hash:
                self._file_hashes[file_path] = current_hash
                return True
            return False
        except Exception:
             
            return True

    def _schedule_batch_callback(self) -> None:
        with self._lock:
             
            if self._timer is not None:
                self._timer.cancel()

             
            self._timer = threading.Timer(
                self.debounce_ms / 1000.0,
                self._process_batch,
            )
            self._timer.daemon = True
            self._timer.start()

    def _process_batch(self) -> None:
 
        with self._lock:
            changed = self._changed_files.copy()
            deleted = self._deleted_files.copy()

            self._changed_files.clear()
            self._deleted_files.clear()
            self._timer = None

        if changed or deleted:
            log.info(
                "File changes detected: %d changed, %d deleted. Processing batch...",
                len(changed),
                len(deleted),
            )
            self.callback(changed, deleted)

    def on_created(self, event) -> None:
 
        if not event.is_directory:
             
            if self._has_file_content_changed(event.src_path):
                with self._lock:
                    self._changed_files.add(event.src_path)
                self._schedule_batch_callback()

    def on_modified(self, event) -> None:
        """Handle file modification events."""
        if not event.is_directory:
             
            if self._has_file_content_changed(event.src_path):
                with self._lock:
                    self._changed_files.add(event.src_path)
                self._schedule_batch_callback()

    def on_moved(self, event) -> None:
        """Handle file move/rename events."""
        if not event.is_directory:
            with self._lock:
                 
                self._deleted_files.add(event.src_path)
                 
                if self._has_file_content_changed(event.dest_path):
                    self._changed_files.add(event.dest_path)
            self._schedule_batch_callback()

    def on_deleted(self, event) -> None:
        """Handle file deletion events."""
        if not event.is_directory:
            with self._lock:
                 
                self._changed_files.discard(event.src_path)
                self._deleted_files.add(event.src_path)
            self._schedule_batch_callback()


def run_watch(
    root_path: Path,
    callback: Callable[[set[str], set[str]], None],
    debounce_ms: int = 250,
    workers: int = 8,
) -> None:
 
    root_path = Path(root_path).resolve()

    
    executor = ThreadPoolExecutor(max_workers=workers)

     
    def batch_callback(changed: set[str], deleted: set[str]) -> None:
 
        executor.submit(callback, changed, deleted)

    event_handler = BatchedEventHandler(
        callback=batch_callback,
        debounce_ms=debounce_ms,
    )

     
    observer = Observer()
    observer.schedule(event_handler, str(root_path), recursive=True)
    observer.start()

    log.info("Watching %s (recursive) ... Press Ctrl+C to stop", root_path)
    log.info("Listening for *.yaml and *.yml files")

    try:
         
        while True:
            observer.join(timeout=1)
            if not observer.is_alive():
                break
    except KeyboardInterrupt:
        log.info("Shutting down watcher...")
        observer.stop()
        observer.join()
        log.info("Watcher stopped cleanly")
        executor.shutdown(wait=True)
        log.info("Thread pool executor shut down")




def watch_with_validation_service(
    validation_service: 'ValidationService',
    debounce_ms: int = 250,
    workers: int = 8,
) -> None:
  
 
    def batch_callback(changed: set[str], deleted: set[str]) -> None:
        """Process batch of changed files with ValidationService."""
        if changed:
            log.info("Validating %d changed files", len(changed))
            validation_service.validate_specific_files(list(changed))
        elif deleted:
            log.info("Detected %d deleted files, running full validation", len(deleted))
            validation_service.run_validation()

    run_watch(
        validation_service.root_path,
        batch_callback,
        debounce_ms=debounce_ms,
        workers=workers,
    )



 