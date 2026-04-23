"""LegalTech Jurisprudence Search — FastAPI Service.

Orchestrates the search pipeline:
  Query → Collector → Parser → Classifier → Response

Runs on port 8001 by default.
"""

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from collectors import TJSPCollector
from collectors.esaj import ESAJSnapshotCollector
from parsers import DatajudParser
from classifiers import KeywordClassifier
from normalizers import SemanticNormalizer
from validators import DatajudEsajComparator

# Load environment variables before anything else
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LegalTech — Serviço de Jurisprudência",
    description="API para busca e classificação de jurisprudência criminal",
    version="1.0.0",
)

# CORS — allow frontend to call this service
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service instances (Strategy Pattern — swap implementations here)
collector = TJSPCollector()
parser = DatajudParser()
normalizer = SemanticNormalizer()
classifier = KeywordClassifier()
esaj_collector = ESAJSnapshotCollector()
comparator = DatajudEsajComparator()

# Configuration
MAX_RESULTS = int(os.getenv("MAX_RESULTS", "10"))
ENABLE_CROSS_VALIDATION = os.getenv("ENABLE_CROSS_VALIDATION", "true").lower() == "true"


@app.get("/search")
async def search(q: str = Query(..., min_length=2, description="Termo de busca")):
    """Search for jurisprudence and return classified results.

    Always returns a valid JSON response, even on failure.
    """
    logger.info("=== Search request: q='%s' ===", q)

    try:
        # Step 1: Collect raw data
        raw_data = await collector.collect(query=q, max_results=MAX_RESULTS)

        # Check for collector-level errors
        if "error" in raw_data:
            logger.warning("Collector returned error: %s", raw_data["error"])
            return {
                "results": [],
                "error": raw_data["error"],
                "query": q,
            }

        # Step 2: Parse into standard format
        parsed = parser.parse(raw_data)

        # Step 3 & 4: Normalize movements and Classify
        results = []
        for item in parsed:
            movimentos_crus = item.pop("movimentos_crus", [])
            
            # Normalization Layer
            normalizados = normalizer.normalize_movements(movimentos_crus)
            item["movimentos"] = normalizados
            
            # Inject trace data
            item["fonte"] = "DATAJUD"
            
            # Classification Layer
            classificacao = classifier.classify(normalizados)
            item["resultado"] = classificacao["resultado"]
            item["confidence"] = classificacao["confidence"]
            item["justificativa"] = classificacao["justificativa"]

            # Validation Layer (DataJud vs e-SAJ snapshot) - no data mutation.
            if ENABLE_CROSS_VALIDATION:
                esaj_item = esaj_collector.find_by_processo(item.get("processo", ""))
                item["validacao"] = comparator.validate(item, esaj_item).to_dict()
            
            # Detailed logging per item
            logger.info("Processo %s -> %s (Confiança: %s)", 
                        item.get("processo"), classificacao["resultado"], classificacao["confidence"])
            
            results.append(item)

        logger.info("Search complete — %d results for '%s'", len(results), q)

        return {
            "results": results,
            "query": q,
            "total": len(results),
            "validacao_ativa": ENABLE_CROSS_VALIDATION,
        }

    except Exception as exc:
        logger.error("Unexpected error in search pipeline: %s", str(exc))
        return {
            "results": [],
            "error": "internal_error",
            "query": q,
        }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "python-jurisprudencia"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8001"))
    logger.info("Starting FastAPI on port %d", port)
    uvicorn.run(app, host="0.0.0.0", port=port)
