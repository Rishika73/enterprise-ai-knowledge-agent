from ingest import ingest_document
from vector_store import VectorStore


def build_retriever(file_path: str) -> VectorStore:
    chunks = ingest_document(file_path)

    vector_store = VectorStore()
    vector_store.add_documents(chunks)

    return vector_store


def retrieve(query: str, file_path: str, top_k: int = 3):
    vector_store = build_retriever(file_path)

    results = vector_store.search(
        query=query,
        top_k=top_k
    )

    return results


if __name__ == "__main__":
    file_path = "data/sample_document.txt"

    query = "How does retrieval augmented generation reduce hallucinations?"

    results = retrieve(
        query=query,
        file_path=file_path,
        top_k=3
    )

    print(f"\nQuery: {query}\n")

    for i, result in enumerate(results, start=1):
        print(f"Result {i}")
        print(f"Score: {result['score']:.4f}")
        print(result["text"])
        print("-" * 80)
