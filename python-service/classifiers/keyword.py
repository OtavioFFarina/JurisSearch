"""Keyword-based classifier for legal decisions.

Uses exact normalized tags from legal_terms.py (no substring guessing).
Designed to be easily replaced with ML/NLP classifier in the future.
"""

import logging

from .base import BaseClassifier

logger = logging.getLogger(__name__)


class KeywordClassifier(BaseClassifier):
    """Classifies decisions based on exact normalized movement tags."""

    # Tags must match values in legal_terms.LEGAL_MAPPING exactly.
    SINAIS: dict[str, dict] = {
        # ── Favoráveis ───────────────────────────────────
        "sentenca_absolutoria":  {"tipo": "favorável", "peso": 10, "conf": "alta"},
        "recurso_provido":      {"tipo": "favorável", "peso": 10, "conf": "alta"},
        "alvara_soltura":       {"tipo": "favorável", "peso": 8,  "conf": "alta"},
        "extincao_punibilidade":{"tipo": "favorável", "peso": 8,  "conf": "media"},
        "extincao_processo":    {"tipo": "favorável", "peso": 6,  "conf": "media"},
        "arquivamento":         {"tipo": "favorável", "peso": 5,  "conf": "media"},
        "arquivamento_definitivo":{"tipo": "favorável","peso": 7, "conf": "media"},
        "baixa_definitiva":     {"tipo": "favorável", "peso": 5,  "conf": "media"},
        "recurso_parcialmente_provido": {"tipo": "favorável", "peso": 6, "conf": "media"},

        # ── Desfavoráveis ────────────────────────────────
        "sentenca_condenatoria":{"tipo": "desfavorável","peso": 10,"conf": "alta"},
        "recurso_improvido":    {"tipo": "desfavorável","peso": 10,"conf": "alta"},
        "mandado_prisao":       {"tipo": "desfavorável","peso": 8, "conf": "alta"},
        "cumprimento_prisao":   {"tipo": "desfavorável","peso": 8, "conf": "alta"},
        "transito_em_julgado":  {"tipo": "desfavorável","peso": 7, "conf": "media"},
    }

    def classify(self, movimentos: list[dict]) -> dict[str, str]:
        """Classify based on exact match of normalized movement tags.

        Iterates from most recent to oldest (DataJud order).
        On tie (same weight), most recent wins.
        """
        fallback = {
            "resultado": "neutro",
            "confidence": "baixa",
            "justificativa": "Sem sinais favoráveis ou desfavoráveis claros nas movimentações encontradas.",
        }

        if not movimentos:
            return fallback

        try:
            melhor_peso = 0
            resultado = "neutro"
            confidence = "baixa"
            justificativa = fallback["justificativa"]

            for mov in movimentos:
                norm = mov.get("movimento_normalizado", "")
                if not norm:
                    continue

                sinal = self.SINAIS.get(norm)
                if not sinal:
                    continue

                # >= garante que, em empate de peso, o mais recente (primeiro na lista) vence.
                if sinal["peso"] >= melhor_peso:
                    melhor_peso = sinal["peso"]
                    resultado = sinal["tipo"]
                    confidence = sinal["conf"]
                    justificativa = (
                        f"Classificado como {sinal['tipo']} com base na movimentação "
                        f"'{mov.get('movimento_original', norm)}'."
                    )

            if melhor_peso == 0:
                return fallback

            return {
                "resultado": resultado,
                "confidence": confidence,
                "justificativa": justificativa,
            }

        except Exception as exc:
            logger.warning("Classification error, defaulting to neutro: %s", str(exc))
            return fallback
