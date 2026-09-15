from typing import List, Dict
import re


def _tokenize(text: str) -> set[str]:
    return set(
        re.findall(r"\b[a-zA-Z]+\b", text.lower())
    )


def rerank_results(
    query: str,
    results: List[Dict],
    top_k: int = 3
) -> List[Dict]:

    if not results:
        return []

    query_terms = _tokenize(query)

    reranked = []

    for result in results:
        document_terms = _tokenize(result["text"])

        overlap = query_terms.intersection(document_terms)

        lexical_overlap_score = (
            len(overlap) / len(query_terms)
            if query_terms
            else 0.0
        )

        hybrid_score = result.get(
            "hybrid_score",
            result.get("score", 0.0)
        )

        rerank_score = (
            0.8 * hybrid_score
            + 0.2 * lexical_overlap_score
        )

        updated = result.copy()
        updated["rerank_score"] = rerank_score

        reranked.append(updated)

    reranked.sort(
        key=lambda item: item["rerank_score"],
        reverse=True
    )

    return reranked[:top_k]
