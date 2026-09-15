from app.hybrid_retriever import hybrid_search
from app.reranker import rerank_results


QUESTIONS = [
    "How does retrieval augmented generation reduce hallucinations?",
    "What is hybrid retrieval?",
    "Why are vector databases useful in RAG?"
]


def compare(question: str):
    initial_results = hybrid_search(
        query=question,
        file_path="data/sample_document.txt",
        top_k=5
    )

    reranked_results = rerank_results(
        query=question,
        results=initial_results,
        top_k=3
    )

    print(f"\nQuestion: {question}")

    print("\nBefore reranking:")
    for result in initial_results[:3]:
        print(
            f"chunk={result['chunk_id']} "
            f"hybrid={result['hybrid_score']:.4f}"
        )

    print("\nAfter reranking:")
    for result in reranked_results:
        print(
            f"chunk={result['chunk_id']} "
            f"rerank={result['rerank_score']:.4f}"
        )

    print("-" * 80)


if __name__ == "__main__":
    for question in QUESTIONS:
        compare(question)
