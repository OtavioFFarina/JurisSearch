"""TJSP Collector — Fetches data from DATAJUD API (CNJ).

Uses the public DATAJUD Elasticsearch API to query
TJSP (Tribunal de Justiça de São Paulo) case metadata.
"""

import logging
import os
from typing import Any

import httpx

from .base import BaseCollector

logger = logging.getLogger(__name__)


class TJSPCollector(BaseCollector):
    """Collects case data from TJSP via DATAJUD public API."""

    TRIBUNAL_ALIAS = "api_publica_tjsp"

    def __init__(self):
        self.base_url = os.getenv(
            "DATAJUD_BASE_URL",
            "https://api-publica.datajud.cnj.jus.br",
        )
        self.api_key = os.getenv("DATAJUD_API_KEY", "")
        self.timeout = int(os.getenv("REQUEST_TIMEOUT", "5"))

        if not self.api_key:
            logger.warning("DATAJUD_API_KEY not set — requests will fail")

    def _build_query(self, query: str, max_results: int) -> dict[str, Any]:
        """Build Elasticsearch query body for DATAJUD API."""
        return {
            "size": max_results,
            "query": {
                "bool": {
                    "should": [
                        {"match": {"assuntos.nome": {"query": query, "boost": 2}}},
                        {"match": {"classe.nome": query}},
                        {"match": {"movimentos.nome": query}},
                    ],
                    "minimum_should_match": 1,
                }
            },
            "sort": [{"dataAjuizamento": {"order": "desc"}}],
        }

    async def collect(self, query: str, max_results: int = 10) -> dict[str, Any]:
        """Fetch case data from DATAJUD for the given query.

        Returns raw Elasticsearch response on success,
        or a safe empty structure with error info on failure.
        """
        url = f"{self.base_url}/{self.TRIBUNAL_ALIAS}/_search"
        headers = {
            "Authorization": f"APIKey {self.api_key}",
            "Content-Type": "application/json",
        }
        body = self._build_query(query, max_results)

        logger.info("Collecting from TJSP/DATAJUD — query='%s', max=%d", query, max_results)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=body)
                response.raise_for_status()

                data = response.json()
                hits_count = len(data.get("hits", {}).get("hits", []))
                logger.info("DATAJUD returned %d results", hits_count)
                return data

        except httpx.TimeoutException:
            logger.error("DATAJUD request timed out after %ds", self.timeout)
            return {"hits": {"hits": []}, "error": "request_timeout"}

        except httpx.HTTPStatusError as exc:
            logger.error("DATAJUD HTTP error: %d — %s", exc.response.status_code, exc.response.text[:200])
            return {"hits": {"hits": []}, "error": f"http_error_{exc.response.status_code}"}

        except httpx.RequestError as exc:
            logger.error("DATAJUD connection error: %s", str(exc)[:200])
            return {"hits": {"hits": []}, "error": "connection_error"}

        except Exception as exc:
            logger.error("Unexpected error in TJSP collector: %s", str(exc)[:200])
            return {"hits": {"hits": []}, "error": "unexpected_error"}
