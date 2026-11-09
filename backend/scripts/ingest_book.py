#!/usr/bin/env python3
"""
CLI Script for Ingesting Textbook Knowledge Base into ChromaDB.
Specification:
- Load PDF / Markdown / Text files
- Chunk (size 600-800, overlap 100)
- Generate embeddings
- Index into persistent ChromaDB
"""

import sys
from pathlib import Path

# Ensure backend root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.services.rag_engine import (
    rag_engine,
    chunk_text,
    extract_file_content,
    infer_metadata
)
from app.core.config import settings

def ingest_corpus():
    corpus_dir = Path(settings.CORPUS_DIR)
    print(f"[*] Ingesting knowledge corpus from: {corpus_dir}")
    print(f"[*] Target ChromaDB directory: {settings.CHROMA_PERSIST_DIR}")
    rag_engine.auto_ingest_corpus()
    print(f"[+] Collection total items: {rag_engine.collection.count()}")

if __name__ == "__main__":
    ingest_corpus()
