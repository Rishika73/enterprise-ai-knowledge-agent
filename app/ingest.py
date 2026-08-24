from pathlib import Path
from typing import List, Dict
import re


def load_text_file(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() != ".txt":
        raise ValueError("Currently only .txt files are supported.")

    return path.read_text(encoding="utf-8")


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> List[Dict]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    words = text.split()
    chunks = []

    start = 0
    chunk_id = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]

        chunks.append(
            {
                "chunk_id": chunk_id,
                "text": " ".join(chunk_words),
                "start_word": start,
                "end_word": end,
            }
        )

        chunk_id += 1

        if end == len(words):
            break

        start = end - overlap

    return chunks


def ingest_document(file_path: str) -> List[Dict]:
    raw_text = load_text_file(file_path)
    cleaned_text = clean_text(raw_text)
    return chunk_text(cleaned_text)


if __name__ == "__main__":
    sample_file = "data/sample_document.txt"

    chunks = ingest_document(sample_file)

    print(f"Created {len(chunks)} chunks")

    for chunk in chunks[:3]:
        print("\n---")
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(chunk["text"][:300])
