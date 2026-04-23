"""DATAJUD response parser.

Transforms raw Elasticsearch response into the standard
application format: {titulo, processo, tribunal, resumo, resultado}.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class DatajudParser:
    """Parses DATAJUD API responses into standardized case records."""

    def parse(self, raw_response: dict[str, Any]) -> list[dict[str, str]]:
        """Transform DATAJUD Elasticsearch response into standard format.

        Args:
            raw_response: Raw JSON from DATAJUD API.

        Returns:
            List of dicts with keys: titulo, processo, tribunal, resumo.
            The 'resultado' field is NOT set here — that's the classifier's job.
        """
        hits = raw_response.get("hits", {}).get("hits", [])

        if not hits:
            logger.info("No hits to parse")
            return []

        results = []
        for hit in hits:
            try:
                source = hit.get("_source", {})
                parsed = self._parse_single(source)
                if parsed:
                    results.append(parsed)
            except Exception as exc:
                logger.warning("Failed to parse hit: %s", str(exc)[:200])
                continue

        logger.info("Parsed %d/%d hits successfully", len(results), len(hits))
        return results

    def _parse_single(self, source: dict[str, Any]) -> dict[str, str] | None:
        """Parse a single Elasticsearch hit source into standard format."""
        processo = source.get("numeroProcesso", "")
        if not processo:
            return None

        titulo = self._build_titulo(source)
        classe_nome = self._extract_classe(source)
        tribunal = self._extract_tribunal(source)
        resumo = self._build_resumo(source)

        return {
            "titulo": titulo,
            "processo": self._format_processo(processo),
            "tribunal": tribunal,
            "classe": classe_nome,
            "resumo": resumo,
            "movimentos_crus": self._extract_movimentos_crus(source),
        }

    def _extract_classe(self, source: dict[str, Any]) -> str:
        """Extract class name preserving source value."""
        classe = source.get("classe", {})
        if isinstance(classe, dict):
            return classe.get("nome", "")
        return ""

    def _build_titulo(self, source: dict[str, Any]) -> str:
        """Build title from class name and subject."""
        classe = source.get("classe", {})
        classe_nome = classe.get("nome", "") if isinstance(classe, dict) else ""

        assuntos = source.get("assuntos", [])
        assunto_nome = ""
        if assuntos and isinstance(assuntos, list):
            first = assuntos[0]
            assunto_nome = first.get("nome", "") if isinstance(first, dict) else ""

        parts = [p for p in [classe_nome, assunto_nome] if p]
        return " — ".join(parts) if parts else "Processo sem título"

    def _extract_tribunal(self, source: dict[str, Any]) -> str:
        """Extract tribunal identifier from source data."""
        tribunal = source.get("tribunal", "")
        if tribunal:
            return tribunal.upper()

        # Fallback: infer from orgaoJulgador
        orgao = source.get("orgaoJulgador", {})
        if isinstance(orgao, dict):
            nome = orgao.get("nome", "")
            if "TJSP" in nome.upper() or "SÃO PAULO" in nome.upper():
                return "TJSP"

        return "TJSP"  # Default since we're querying TJSP endpoint

    RESUMO_PREVIEW_SIZE = 5

    def _build_resumo(self, source: dict[str, Any]) -> str:
        """Build UI-only preview string from the first N movements.

        WARNING — This is a display preview, NOT the authoritative record.
        The full, faithful movement history lives in `movimentos_crus`
        (see _extract_movimentos_crus). Do NOT consume this field for any
        legal, audit or validation logic — it is intentionally truncated
        for listing density.
        """
        movimentos = source.get("movimentos", [])
        if not movimentos or not isinstance(movimentos, list):
            return "Sem movimentações disponíveis."

        preview = movimentos[:self.RESUMO_PREVIEW_SIZE]
        total = len(movimentos)

        parts = []
        for mov in preview:
            if isinstance(mov, dict):
                nome = mov.get("nome", "")
                if nome:
                    parts.append(nome)

        if not parts:
            return "Sem movimentações disponíveis."

        base = ". ".join(parts) + "."
        if total > len(parts):
            base += f" (+{total - len(parts)} movimentações)"
        return base

    def _extract_movimentos_crus(self, source: dict[str, Any]) -> list[dict]:
        """Extract ALL raw movements preserving original strings and order.

        IMPORTANT — Legal fidelity rules:
        - No truncation: every movement = 1 record.
        - No deduplication: repeated events are preserved.
        - Chronological order from source is kept intact.
        """
        movimentos = source.get("movimentos", [])
        if not movimentos or not isinstance(movimentos, list):
            return []

        crus = []
        for mov in movimentos:
            if isinstance(mov, dict):
                nome = mov.get("nome", "")
                data = mov.get("dataHora", "")

                if nome:
                    complementos = mov.get("complementosTabelados", [])
                    descricao = ""
                    if complementos and isinstance(complementos, list):
                        partes = [c.get("descricao", "") or c.get("nome", "")
                                  for c in complementos if isinstance(c, dict)]
                        descricao = "; ".join(p for p in partes if p)

                    crus.append({
                        "movimento_original": nome,
                        "data": data,
                        "descricao": descricao,
                    })
        return crus

    def _format_processo(self, numero: str) -> str:
        """Format process number to standard NNNNNNN-NN.NNNN.N.NN.NNNN pattern."""
        digits = "".join(c for c in numero if c.isdigit())

        if len(digits) == 20:
            return (
                f"{digits[:7]}-{digits[7:9]}.{digits[9:13]}"
                f".{digits[13]}.{digits[14:16]}.{digits[16:]}"
            )

        return numero  # Return as-is if format is unexpected
