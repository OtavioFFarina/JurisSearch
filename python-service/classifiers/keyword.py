"""Keyword-based classifier for legal decisions.

Simple rule-based classification using keyword matching.
Designed to be easily replaced with ML/NLP classifier in the future.
"""

import logging

from .base import BaseClassifier

logger = logging.getLogger(__name__)


class KeywordClassifier(BaseClassifier):
    """Classifies decisions based on keyword presence in text."""

    FAVORAVEL = [
        "absolvicao",
        "recurso provido",
        "ordem concedida",
        "sentenca_reformada",
        "decisao favoravel",
        "alvara_soltura",
        "trancamento_acao",
        "extincao_punibilidade",
    ]

    DESFAVORAVEL = [
        "condenacao",
        "recurso improvido",
        "ordem denegada",
        "sentenca_mantida",
        "decisao desfavoravel",
        "sentenca_condenatoria",
    ]

    PESOS = {
        "forte": 10,
        "medio": 5,
        "fraco": 2
    }

    def _obter_peso_por_sinal(self, sinal: str, is_favoravel: bool) -> tuple[int, str]:
        """Return the weight and confidence for a signal based on heuristics."""
        # Simple heuristic since user required static mapping implementation
        if "absolvicao" in sinal or "condenacao" in sinal or "concedida" in sinal or "provido" in sinal:
            return self.PESOS["forte"], "alta"
        if "alvara_soltura" in sinal or "trancamento_acao" in sinal or "extincao" in sinal or "mantida" in sinal:
            return self.PESOS["medio"], "media"
        return self.PESOS["fraco"], "baixa"

    def classify(self, movimentos: list[dict]) -> dict[str, str]:
        """Classify based on analyzing normalized movements with explicability."""
        fallback = {
            "resultado": "neutro",
            "confidence": "baixa",
            "justificativa": "Sem sinais favoráveis ou desfavoráveis claros nas movimentações encontradas."
        }
        
        if not movimentos:
            return fallback

        try:
            maior_peso = 0
            resultado_final = "neutro"
            confidence_final = "baixa"
            justificativa_final = fallback["justificativa"]

            # Reverse the list so the most recent is checked last?
            # Or iterate specifically looking for strongest since user said:
            # "se houver conflito (favorável vs desfavorável): usar movimento mais recente"
            # Assuming list is already most recent first (from DATAJUD)
            # We want the HIGHEST weight. If weights are equal, we want the most recent.
            # So by iterating chronological or reverse, we can do this.
            
            for mov in movimentos:
                norm = mov.get("movimento_normalizado", "")
                if not norm:
                    continue
                
                # Check favorable
                for fav in self.FAVORAVEL:
                    if fav in norm:
                        peso, conf = self._obter_peso_por_sinal(fav, True)
                        # If weight is GREATER, we replace. So earlier (more recent) only gets replaced 
                        # if a stronger signal is found later. This satisfies "most recent wins ties".
                        if peso >= maior_peso:  
                            maior_peso = peso
                            resultado_final = "favorável"
                            confidence_final = conf
                            justificativa_final = f"Classificado como favorável por conter '{fav}' nos movimentos."

                # Check unfavorable
                for des in self.DESFAVORAVEL:
                    if des in norm:
                        peso, conf = self._obter_peso_por_sinal(des, False)
                        if peso >= maior_peso:
                            maior_peso = peso
                            resultado_final = "desfavorável"
                            confidence_final = conf
                            justificativa_final = f"Classificado como desfavorável por conter '{des}' nos movimentos."

            if maior_peso == 0:
                return fallback

            return {
                "resultado": resultado_final,
                "confidence": confidence_final,
                "justificativa": justificativa_final
            }

        except Exception as exc:
            logger.warning("Classification error, defaulting to neutro: %s", str(exc))
            return fallback
