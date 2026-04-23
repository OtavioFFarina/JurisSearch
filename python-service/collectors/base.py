"""Base collector interface — Strategy Pattern.

All tribunal collectors must implement this interface.
To add a new tribunal, create a new class extending BaseCollector.
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseCollector(ABC):
    """Abstract base for data collectors.

    Each implementation handles communication with a specific
    tribunal data source (API, scraping, etc).
    """

    @abstractmethod
    async def collect(self, query: str, max_results: int = 10) -> dict[str, Any]:
        """Fetch raw data from the tribunal source.

        Args:
            query: Search term entered by the user.
            max_results: Maximum number of results to return.

        Returns:
            Raw response data from the source (dict).
            On failure, returns {"hits": {"hits": []}, "error": "description"}.
        """
        pass
