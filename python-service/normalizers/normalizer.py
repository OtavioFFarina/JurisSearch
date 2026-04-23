"""Semantic Normalizer for Legal Terms.

Takes raw movements, preserves them, and attaches a normalized
string based on substring matching.
"""

import logging
from .base import BaseNormalizer
from .legal_terms import LEGAL_MAPPING

logger = logging.getLogger(__name__)


class SemanticNormalizer(BaseNormalizer):
    """Normalizes legal definitions based on static mapping list."""

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

            lowered_text = original_text.lower()
            encontrou = False

            # Search highest to lowest priority
            for search_term, normalized_term in LEGAL_MAPPING:
                if search_term in lowered_text:
                    mov_dict["movimento_normalizado"] = normalized_term
                    encontrou = True
                    break  # Stop at first (most specific) match

            # Fallback: if no match, use original text in lowercase
            if not encontrou:
                mov_dict["movimento_normalizado"] = lowered_text.strip()

            normalizados.append(mov_dict)

        return normalizados
