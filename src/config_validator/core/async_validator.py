# async_validator.py
from __future__ import annotations
import asyncio, os, threading
from pathlib import Path
from typing import Any, Callable

class AsyncValidator:
    def __init__(
        self,
        session_factory: Callable[[], Any],
        validate_sync: Callable[[Any, str], Any],
        max_concurrency: int | None = None,
        per_task_timeout: float | None = 30.0,
    ):
        self._session_factory = session_factory
        self._validate_sync = validate_sync
        self._sem = asyncio.Semaphore(max_concurrency or min(32, (os.cpu_count() or 4) * 2))
        self._timeout = per_task_timeout
        self._thread_local = threading.local()   

     
    def _get_thread_session(self) -> Any:
        sess = getattr(self._thread_local, "session", None)
        if sess is None:
            sess = self._session_factory()
            self._thread_local.session = sess
        return sess

    def _validate_one_sync(self, path: Path) -> Any:
 
        sess = self._get_thread_session()
        return self._validate_sync(sess, str(path))

    async def _validate_one_async(self, path: Path) -> Any:
        async with self._sem:  # bounded concurrency
      
            return await asyncio.to_thread(self._validate_one_sync, path)

    async def validate_files(self, files: list[Path]) -> list[Any]:
 
        tasks = [asyncio.create_task(self._validate_one_async(p)) for p in files]

        results: list[Any] = [None] * len(files)
        for i, t in enumerate(tasks):
            try:
                results[i] = await asyncio.wait_for(t, timeout=self._timeout) if self._timeout else await t
            except asyncio.TimeoutError:
                results[i] = {"status": "fail", "path": str(files[i]), "error": "TIMEOUT"}
            except Exception as e:
                results[i] = {"status": "fail", "path": str(files[i]), "error": repr(e)}
        return results