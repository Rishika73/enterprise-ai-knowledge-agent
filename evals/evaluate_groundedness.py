import re
from typing import Dict

from app.rag import generate_answer


TEST_QUESTIONS = [
    "How does retrieval augmented generation help reduce hallucinations?",
    "What is hybrid retrieval?",
    "Why are vector databases used in RAG systems?",
]


def has_source_citation(answer: str) -> bool:
    return bool(re.search(r"\[Source \d+\]", answer))


def source_support_score(result: Dict) -> float:
    """
    Simple retrieval-support metric based on whether the system
    returned source chunks and whether the answer cites them.
    """

    answer = result["answer"]
    sources = result["sources"]

    if not sources:
        return 0.0

    citation_score = 1.0 if has_source_citation(answer) else 0.0

    relevant_sources = [
        source
        for source in sources
        if source.get("score", 0) > 0
    ]

    retrieval_score = (
        len(relevant_sources) / len(sources)
        if sources
        else 0.0
    )

    return (citation_score + retrieval_score) / 2


def evaluate():
    total = 0.0

    for index, question in enumerate(TEST_QUESTIONS, start=1):

        result = generate_answer(
            query=question,
            file_path="data/sample_document.txt",
            top_k=3
        )

        score = source_support_score(result)
        total += score

        print(f"\nTest {index}")
        print(f"Question: {question}")
        print(f"Answer: {result['answer']}")
        print(f"Sources returned: {len(result['sources'])}")
        print(
            f"Contains citation: "
            f"{has_source_citation(result['answer'])}"
        )
        print(f"Groundedness proxy score: {score:.2f}")
        print("-" * 80)

    average = total / len(TEST_QUESTIONS)

    print("\nGroundedness Evaluation Summary")
    print(f"Average groundedness proxy score: {average:.2f}")


if __name__ == "__main__":
    evaluate()
