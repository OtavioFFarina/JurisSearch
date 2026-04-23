"""Cross-source validator for DataJud vs e-SAJ.

Compares required fields and movement consistency while preserving legal
fidelity. It does not alter ingested data; only emits validation metrics.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass


@dataclass
class ValidationResult:
    processo: str
    classe_match: bool
    tribunal_match: bool
    movimentos_match: float
    confiabilidade: str
    fonte_verdade_disponivel: bool
    cobertura_mapping: float

    def to_dict(self) -> dict:
        return {
            "processo": self.processo,
            "classe_match": self.classe_match,
            "tribunal_match": self.tribunal_match,
            "movimentos_match": round(self.movimentos_match, 2),
            "confiabilidade": self.confiabilidade,
            "fonte_verdade_disponivel": self.fonte_verdade_disponivel,
            "cobertura_mapping": round(self.cobertura_mapping, 2),
        }


class DatajudEsajComparator:
    """Compares a DataJud process payload with an e-SAJ snapshot payload."""

    POSITION_TOLERANCE = 1

    def validate(self, datajud: dict, esaj: dict | None) -> ValidationResult:
        processo = datajud.get("processo", "")
        dj_movs = datajud.get("movimentos", []) or []

        if not esaj:
            return ValidationResult(
                processo=processo,
                classe_match=False,
                tribunal_match=False,
                movimentos_match=0.0,
                confiabilidade="indisponivel",
                fonte_verdade_disponivel=False,
                cobertura_mapping=self._mapping_coverage(dj_movs),
            )

        classe_match = self._canon(datajud.get("classe", "")) == self._canon(esaj.get("classe", ""))
        tribunal_match = self._canon(datajud.get("tribunal", "")) == self._canon(esaj.get("tribunal", ""))

        esaj_movs = esaj.get("movimentacoes", []) or []
        movimentos_match = self._movement_similarity(dj_movs, esaj_movs)

        confiabilidade = self._confidence_label(classe_match, tribunal_match, movimentos_match)

        return ValidationResult(
            processo=processo,
            classe_match=classe_match,
            tribunal_match=tribunal_match,
            movimentos_match=movimentos_match,
            confiabilidade=confiabilidade,
            fonte_verdade_disponivel=True,
            cobertura_mapping=self._mapping_coverage(dj_movs),
        )

    def _movement_similarity(self, datajud_movs: list[dict], esaj_movs: list[dict]) -> float:
        """Score similarity without altering data.

        Strategy:
        - Match on normalized tag OR on original text (whichever aligns).
        - Position tolerance of ±POSITION_TOLERANCE to absorb minor misalignments.
        - Quantity score rewards same length; order score rewards positional matches.
        """
        if not datajud_movs and not esaj_movs:
            return 1.0

        if not datajud_movs or not esaj_movs:
            return 0.0

        max_len = max(len(datajud_movs), len(esaj_movs))
        min_len = min(len(datajud_movs), len(esaj_movs))

        order_hits = 0
        for idx in range(min_len):
            if self._matches_in_window(datajud_movs, esaj_movs, idx):
                order_hits += 1

        order_score = order_hits / max_len
        quantity_score = min_len / max_len

        return (order_score * 0.7) + (quantity_score * 0.3)

    def _matches_in_window(self, a: list[dict], b: list[dict], idx: int) -> bool:
        """Check if a[idx] matches any b[idx ± tolerance]."""
        a_tag, a_orig = self._movement_keys(a[idx])
        if not a_tag and not a_orig:
            return False

        lo = max(0, idx - self.POSITION_TOLERANCE)
        hi = min(len(b), idx + self.POSITION_TOLERANCE + 1)
        for j in range(lo, hi):
            b_tag, b_orig = self._movement_keys(b[j])
            if a_tag and a_tag == b_tag:
                return True
            if a_orig and a_orig == b_orig:
                return True
        return False

    def _movement_keys(self, mov: dict) -> tuple[str, str]:
        """Return (normalized_tag, canonical_original) for a movement dict."""
        tag = self._canon(mov.get("movimento_normalizado", ""))
        orig = self._canon(mov.get("movimento_original", ""))
        return tag, orig

    def _mapping_coverage(self, movs: list[dict]) -> float:
        """Fraction of movements whose normalized tag differs from the canonical
        original — i.e., that hit an explicit LEGAL_MAPPING entry.
        """
        if not movs:
            return 0.0
        mapped = 0
        for mov in movs:
            tag = self._canon(mov.get("movimento_normalizado", ""))
            orig_canon = self._canon(mov.get("movimento_original", ""))
            if tag and tag != orig_canon:
                mapped += 1
        return mapped / len(movs)

    def _confidence_label(self, classe_match: bool, tribunal_match: bool, movimentos_match: float) -> str:
        base = 0.0
        if classe_match:
            base += 0.2
        if tribunal_match:
            base += 0.2
        base += movimentos_match * 0.6

        if base >= 0.8:
            return "alta"
        if base >= 0.5:
            return "media"
        return "baixa"

    def _canon(self, value: str) -> str:
        """Accent-strip + lowercase + collapse whitespace. Read-only."""
        text = unicodedata.normalize("NFKD", str(value))
        no_accents = "".join(ch for ch in text if not unicodedata.combining(ch))
        return " ".join(no_accents.strip().lower().split())
