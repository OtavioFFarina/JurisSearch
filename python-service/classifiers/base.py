"""Base classifier interface — Strategy Pattern.

All classifiers must implement this interface.
To swap classification logic, create a new class extending BaseClassifier.
"""

from abc import ABC, abstractmethod


class BaseClassifier(ABC):
    """Abstract base for decision classifiers."""

    @abstractmethod
    def classify(self, movimentos: list[dict]) -> dict[str, str]:
        """Classify a legal case based on a list of normalized movements.

        Args:
            movimentos: List of movement dicts, expected to contain "movimento_normalizado".

        Returns:
            Dict containing: "resultado", "confidence", "justificativa".
            Must NEVER raise an exception — return "neutro" as fallback.
        """
        pass
