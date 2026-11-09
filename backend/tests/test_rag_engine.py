import pytest
from app.services.rag_engine import rag_engine

def test_rag_collection_indexed():
    count = rag_engine.collection.count()
    assert count > 0, "ChromaDB collection should have indexed chunks."

def test_rag_ml_retrieval():
    chunks = rag_engine.retrieve_context("empirical risk minimization and loss functions", role="AI/ML Engineer", k=3)
    assert len(chunks) == 3
    assert any("loss" in c["text"].lower() or "risk" in c["text"].lower() for c in chunks)
    assert "source" in chunks[0]
    assert "chapter" in chunks[0]

def test_rag_backend_retrieval():
    chunks = rag_engine.retrieve_context("database transactions ACID B-Tree indexing", role="Backend Engineer", k=3)
    assert len(chunks) == 3
    assert any("b-" in c["text"].lower() or "acid" in c["text"].lower() or "index" in c["text"].lower() for c in chunks)

def test_rag_fallback_on_obscure_query():
    # Obscure meaningless tokens should trigger fallback to role fundamentals
    chunks = rag_engine.retrieve_context("xyzabc987 obscure nonsensical query", role="AI/ML Engineer", k=2)
    assert len(chunks) >= 1
    assert chunks[0]["role"] in ["AI/ML Engineer", "General"]
