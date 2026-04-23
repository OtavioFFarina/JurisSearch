"""Base normalizer interface.

All normalizers must implement this interface.
"""

from abc import ABC, abstractmethod


class BaseNormalizer(ABC):
    """Abstract base for data normalizers."""

    @abstractmethod
    def normalize_movements(self, movimentos: list[dict]) -> list[dict]:
        """Normalize a list of movement dictionaries.

        Ensures each dictionary gets a "movimento_normalizado" key
        while preserving the "movimento_original" string.
        """
        pass
