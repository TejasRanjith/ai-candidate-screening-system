import logging
from typing import List, Dict, Any, Optional
import chromadb
from app.core.config import settings

logger = logging.getLogger("screening.rag")

ROLE_FUNDAMENTALS = {
    "AI/ML Engineer": [
        "empirical risk minimization loss functions gradient descent optimization",
        "overfitting L1 L2 regularization bias-variance tradeoff cross validation",
        "deep neural networks backpropagation activation functions batch norm dropout",
        "precision recall ROC-AUC class imbalance focal loss SMOTE",
        "support vector machines linear logistic regression decision trees"
    ],
    "Data Scientist": [
        "hypothesis testing model evaluation ROC-AUC precision recall F1",
        "feature selection L1 regularization bias-variance tradeoff",
        "logistic regression decision trees ensemble random forest gradient boosting",
        "class imbalance cross validation data preprocessing metrics",
        "empirical risk optimization loss functions"
    ],
    "Backend Engineer": [
        "concurrency asynchronous IO event loop threading race conditions",
        "database indexing B-Trees LSM-Trees ACID transactions isolation levels",
        "distributed caching cache stampede cache-aside write-through invalidation",
        "CAP theorem linearizable consistency eventual consistency partitions",
        "API resiliency circuit breaker rate limiting idempotency keys"
    ]
}

class RAGEngine:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection("interview_knowledge_base")

    def retrieve_context(self, query: str, role: str = "AI/ML Engineer", k: int = 3) -> List[Dict[str, Any]]:
        """
        Query textbook vector database for grounded chunks.
        Includes fallback to role fundamentals if candidate query yields weak similarity or empty results.
        """
        if self.collection.count() == 0:
            logger.warning("Knowledge base collection is empty. Run ingest_book.py first.")
            return []

        # Determine metadata where filter if role is recognized
        normalized_role = "AI/ML Engineer"
        if "backend" in role.lower() or "systems" in role.lower():
            normalized_role = "Backend Engineer"
        elif "data" in role.lower() or "analytics" in role.lower():
            normalized_role = "AI/ML Engineer"  # Data Science uses ML foundations

        results = None
        try:
            # First attempt: Target query
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")

        chunks = self._format_results(results)

        # Fallback check: if results are empty or top distance indicates low relevance
        if not chunks or (len(chunks) > 0 and chunks[0].get("distance", 0.0) > 1.4):
            logger.info(f"Query '{query}' produced weak/sparse retrieval. Triggering role fundamental fallback for '{normalized_role}'.")
            fallback_query = " ".join(ROLE_FUNDAMENTALS.get(normalized_role, ROLE_FUNDAMENTALS["AI/ML Engineer"])[:2])
            try:
                fallback_results = self.collection.query(
                    query_texts=[fallback_query],
                    n_results=k
                )
                fallback_chunks = self._format_results(fallback_results)
                if fallback_chunks:
                    chunks = fallback_chunks
            except Exception as fb_err:
                logger.error(f"Fallback retrieval failed: {fb_err}")

        return chunks[:k]

    def _format_results(self, raw_results) -> List[Dict[str, Any]]:
        if not raw_results or not raw_results.get("documents"):
            return []

        docs = raw_results["documents"][0]
        metas = raw_results.get("metadatas", [[]])[0]
        ids = raw_results.get("ids", [[]])[0]
        distances = raw_results.get("distances", [[]])[0] if raw_results.get("distances") else [0.0] * len(docs)

        formatted = []
        for doc, meta, cid, dist in zip(docs, metas, ids, distances):
            formatted.append({
                "chunk_id": cid,
                "text": doc,
                "source": meta.get("source", "Textbook"),
                "book": meta.get("book", "Textbook Corpus"),
                "chapter": meta.get("chapter", "Foundational Concepts"),
                "role": meta.get("role", "General"),
                "distance": float(dist)
            })
        return formatted

rag_engine = RAGEngine()
