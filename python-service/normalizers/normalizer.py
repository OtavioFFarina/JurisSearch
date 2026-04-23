"""Semantic Normalizer for Legal Terms.

Takes raw movements, preserves them, and attaches a normalized
string based on explicit dictionary mapping.
"""

import logging
import unicodedata
from .base import BaseNormalizer
from .legal_terms import LEGAL_MAPPING

logger = logging.getLogger(__name__)


class SemanticNormalizer(BaseNormalizer):
    """Normalizes legal definitions based on static mapping list."""

    def _canonical_key(self, text: str) -> str:
        """Create deterministic key without changing original stored text."""
        normalized = unicodedata.normalize("NFKD", text)
        no_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
        return " ".join(no_accents.lower().strip().split())

    def normalize_movements(self, movimentos: list[dict]) -> list[dict]:
        """Normalize movements while strictly preserving original data."""
        if not movimentos:
            return []

        normalizados = []
        for mov in movimentos:
            # Strictly ensure we don't modify the dict reference directly
            mov_dict = mov.copy()
            
            original_text = mov_dict.get("movimento_original", "")
            
            if not original_text:
                mov_dict["movimento_normalizado"] = ""
                normalizados.append(mov_dict)
                continue

            canonical = self._canonical_key(original_text)
            mapped = LEGAL_MAPPING.get(canonical)

            # Controlled normalization: complement only when explicit mapping exists.
            mov_dict["movimento_normalizado"] = mapped if mapped else canonical

            normalizados.append(mov_dict)

        return normalizados
