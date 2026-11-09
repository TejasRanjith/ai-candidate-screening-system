#!/usr/bin/env python3
"""
CLI Script for Ingesting Textbook Knowledge Base into ChromaDB.
Specification:
- Load PDF / Markdown / Text files
- Chunk (size 600-800, overlap 100)
- Generate embeddings
- Index into persistent ChromaDB
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from pypdf import PdfReader

# Ensure backend root is on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.core.config import settings

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
            # Paragraph itself exceeds chunk size, split by sentences or lines
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
                                # Keep overlap
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

    # Derive chapter/topic from header or filename
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

def ingest_corpus():
    corpus_dir = Path(settings.CORPUS_DIR)
    print(f"[*] Ingesting knowledge corpus from: {corpus_dir}")
    print(f"[*] Target ChromaDB directory: {settings.CHROMA_PERSIST_DIR}")

    chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    collection = chroma_client.get_or_create_collection(
        name="interview_knowledge_base",
        metadata={"description": "Grounded textbook knowledge base for role-based candidate screening"}
    )

    files = [f for f in corpus_dir.iterdir() if f.is_file() and f.suffix.lower() in [".md", ".txt", ".pdf"]]
    if not files:
        print("[!] No documents found in corpus directory.")
        return

    total_chunks = 0
    all_docs = []
    all_metadatas = []
    all_ids = []

    for file_path in sorted(files):
        print(f"-> Processing: {file_path.name}")
        content = extract_file_content(file_path)
        meta = infer_metadata(file_path.name, content)
        chunks = chunk_text(content, chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
        
        print(f"   Generated {len(chunks)} chunks (target size {settings.CHUNK_SIZE}, overlap {settings.CHUNK_OVERLAP})")
        
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
            total_chunks += 1

    # Upsert in batches of 50 to ChromaDB
    batch_size = 50
    for i in range(0, len(all_ids), batch_size):
        end = i + batch_size
        collection.upsert(
            ids=all_ids[i:end],
            documents=all_docs[i:end],
            metadatas=all_metadatas[i:end]
        )

    print(f"[+] Successfully ingested and indexed {total_chunks} chunks across {len(files)} documents!")
    print(f"[+] Collection total items: {collection.count()}")

if __name__ == "__main__":
    ingest_corpus()
