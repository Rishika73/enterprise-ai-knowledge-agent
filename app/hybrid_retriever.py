import re
from typing import List, Dict

from app.ingest import ingest_document
from app.vector_store import VectorStore


def tokenize(text: str) -> set[str]:
    return set(
        re.findall(r"\b[a-zA-Z]+\b", text.lower())
    )


def keyword_score(query: str, document: str) -> float:
    query_terms = tokenize(query)
    document_terms = tokenize(document)

    if not query_terms:
        return 0.0

    matched_terms = query_terms.intersection(document_terms)

    return len(matched_terms) / len(query_terms)


def hybrid_search(
    query: str,
    file_path: str,
    top_k: int = 3,
    semantic_weight: float = 0.7,
    keyword_weight: float = 0.3
) -> List[Dict]:

    chunks = ingest_document(file_path)

    vector_store = VectorStore()
    vector_store.add_documents(chunks)

    semantic_results = vector_store.search(
        query=query,
        top_k=len(chunks)
    )

    combined_results = []

    for result in semantic_results:
        semantic_score = result["score"]

        lexical_score = keyword_score(
            query,
            result["text"]
        )

        hybrid_score = (
            semantic_weight * semantic_score
            + keyword_weight * lexical_score
        )

        combined = result.copy()
        combined["semantic_score"] = semantic_score
        combined["keyword_score"] = lexical_score
        combined["hybrid_score"] = hybrid_score

        combined_results.append(combined)

    combined_results.sort(
        key=lambda item: item["hybrid_score"],
        reverse=True
    )

    return combined_results[:top_k]


if __name__ == "__main__":
    query = "How does hybrid retrieval improve RAG?"

    results = hybrid_search(
        query=query,
        file_path="data/sample_document.txt",
        top_k=3
    )

    print(f"\nQuery: {query}\n")

    for index, result in enumerate(results, start=1):
        print(f"Result {index}")
        print(f"Semantic score: {result['semantic_score']:.4f}")
        print(f"Keyword score: {result['keyword_score']:.4f}")
        print(f"Hybrid score: {result['hybrid_score']:.4f}")
        print(result["text"])
        print("-" * 80)
