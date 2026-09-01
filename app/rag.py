import os
from typing import List, Dict

from dotenv import load_dotenv

from app.hybrid_retriever import hybrid_search

load_dotenv()


def get_openai_client():
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured.")

    return OpenAI(
        api_key=api_key,
        timeout=30.0
    )


def build_context(results: List[Dict]) -> str:
    context_parts = []

    for i, result in enumerate(results, start=1):
        context_parts.append(
            f"[Source {i}]\n{result['text']}"
        )

    return "\n\n".join(context_parts)


def generate_answer(
    query: str,
    file_path: str,
    top_k: int = 3
) -> Dict:

    print("Starting retrieval...")

    results = hybrid_search(
        query=query,
        file_path=file_path,
        top_k=top_k
    )

    print(f"Retrieved {len(results)} source chunks.")

    if not results:
        return {
            "answer": "No relevant information was found.",
            "sources": []
        }

    context = build_context(results)

    prompt = f"""
You are an enterprise knowledge assistant.

Answer the user's question using ONLY the provided context.

Rules:
- Do not invent information.
- If the answer is not supported by the context, say that the information is not available.
- Cite supporting sources using [Source 1], [Source 2], etc.
- Keep the answer clear and concise.

Context:
{context}

Question:
{query}
"""

    print("Calling language model...")

    client = get_openai_client()

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    print("Language model response received.")

    return {
        "answer": response.output_text,
        "sources": results
    }


if __name__ == "__main__":

    question = (
        "How does retrieval augmented generation "
        "help reduce hallucinations?"
    )

    result = generate_answer(
        query=question,
        file_path="data/sample_document.txt"
    )

    print("\nANSWER\n")
    print(result["answer"])

    print("\nSOURCES\n")

    for source in result["sources"]:
        print(
            f"Chunk {source['chunk_id']} "
            f"(score={source['score']:.4f})"
        )
