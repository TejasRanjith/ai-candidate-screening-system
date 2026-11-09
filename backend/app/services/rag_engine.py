import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from pypdf import PdfReader
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

def chunk_text(text: str, chunk_size: int = 700, chunk_overlap: int = 100) -> List[str]:
    """
    Split text recursively on natural boundaries (paragraphs, lines, sentences)
    maintaining chunk_size between 600-800 chars and chunk_overlap ~100 chars.
    """
    if not text or not text.strip():
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(para) > chunk_size:
            lines = [l.strip() for l in para.split("\n") if l.strip()]
            for line in lines:
                if len(line) > chunk_size:
                    sentences = [s.strip() + "." for s in line.split(". ") if s.strip()]
                    for s in sentences:
                        if len(current_chunk) + len(s) + 1 <= chunk_size:
                            current_chunk = (current_chunk + " " + s).strip()
                        else:
                            if current_chunk:
                                chunks.append(current_chunk)
                                current_chunk = current_chunk[-chunk_overlap:] + " " + s
                            else:
                                chunks.append(s[:chunk_size])
                                current_chunk = s[chunk_size - chunk_overlap:]
                else:
                    if len(current_chunk) + len(line) + 1 <= chunk_size:
                        current_chunk = (current_chunk + "\n" + line).strip()
                    else:
                        if current_chunk:
                            chunks.append(current_chunk)
                            current_chunk = current_chunk[-chunk_overlap:] + "\n" + line
                        else:
                            current_chunk = line
        else:
            if len(current_chunk) + len(para) + 2 <= chunk_size:
                current_chunk = (current_chunk + "\n\n" + para).strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = current_chunk[-chunk_overlap:] + "\n\n" + para
                else:
                    current_chunk = para

    if current_chunk and current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks

def extract_file_content(file_path: Path) -> str:
    """Extract text from markdown, text, or PDF files."""
    if file_path.suffix.lower() == ".pdf":
        reader = PdfReader(str(file_path))
        pages_text = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                pages_text.append(t)
        return "\n\n".join(pages_text)
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

def infer_metadata(file_name: str, text: str) -> Dict[str, str]:
    """Extract book, chapter, and target role metadata."""
    fn_lower = file_name.lower()
    if "burkov" in fn_lower or "ml" in fn_lower:
        book = "The Hundred-Page Machine Learning Book (Andriy Burkov)"
        role = "AI/ML Engineer"
    elif "backend" in fn_lower or "sys" in fn_lower:
        book = "Backend Systems & Distributed Architecture Handbook"
        role = "Backend Engineer"
    else:
        book = "Technical Screening Knowledge Base"
        role = "General"

    chapter = file_name
    for line in text.splitlines()[:5]:
        if line.startswith("# ") or line.startswith("## "):
            chapter = line.replace("#", "").strip()
            break

    return {
        "source": file_name,
        "book": book,
        "chapter": chapter,
        "role": role
    }

class RAGEngine:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        self.collection = self.client.get_or_create_collection("interview_knowledge_base")
        if self.collection.count() == 0:
            self.auto_ingest_corpus()

    def auto_ingest_corpus(self):
        """Automatically index the textbook corpus if the vector database is empty."""
        try:
            corpus_path = Path(settings.CORPUS_DIR)
            if not corpus_path.exists():
                logger.warning(f"Corpus path {corpus_path} not found.")
                return

            files = [f for f in corpus_path.iterdir() if f.is_file() and f.suffix.lower() in [".md", ".txt", ".pdf"]]
            if not files:
                logger.warning(f"No documents found in {corpus_path}.")
                return

            logger.info(f"Auto-ingesting {len(files)} corpus documents into ChromaDB...")
            all_docs = []
            all_metadatas = []
            all_ids = []

            for file_path in sorted(files):
                content = extract_file_content(file_path)
                meta = infer_metadata(file_path.name, content)
                chunks = chunk_text(content, chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)

                for idx, chunk in enumerate(chunks):
                    chunk_id = f"{file_path.stem}_chunk_{idx:03d}"
                    all_ids.append(chunk_id)
                    all_docs.append(chunk)
                    all_metadatas.append({
                        "source": meta["source"],
                        "book": meta["book"],
                        "chapter": meta["chapter"],
                        "role": meta["role"],
                        "chunk_index": idx
                    })

            batch_size = 50
            for i in range(0, len(all_ids), batch_size):
                end = i + batch_size
                self.collection.upsert(
                    ids=all_ids[i:end],
                    documents=all_docs[i:end],
                    metadatas=all_metadatas[i:end]
                )
            logger.info(f"Successfully auto-ingested {len(all_ids)} chunks into ChromaDB.")
        except Exception as e:
            logger.error(f"Failed to auto-ingest corpus: {e}", exc_info=True)

    def retrieve_context(self, query: str, role: str = "AI/ML Engineer", k: int = 3) -> List[Dict[str, Any]]:
        """
        Query textbook vector database for grounded chunks.
        Includes fallback to role fundamentals if candidate query yields weak similarity or empty results.
        """
        if self.collection.count() == 0:
            self.auto_ingest_corpus()

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
