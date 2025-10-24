from __future__ import annotations


from abc import ABC, abstractmethod
from typing import List




class ValidationPlugin(ABC):
    """Interface for validation plugins.


    Implement `validate(data)` to return a list of error strings (empty if OK).
    """


    @abstractmethod
    def validate(self, data: dict) -> List[str]: # pragma: no cover - interface only
        raise NotImplementedError