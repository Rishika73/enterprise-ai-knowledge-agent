from typing import List, Dict

from app.rag import generate_answer


TEST_CASES: List[Dict] = [
    {
        "question": "How does retrieval augmented generation help reduce hallucinations?",
        "expected_keywords": [
            "retrieved",
            "context",
            "hallucinations"
        ],
    },
    {
        "question": "What is hybrid retrieval?",
        "expected_keywords": [
            "semantic",
            "vector",
            "keyword"
        ],
    },
    {
        "question": "Why are vector databases used in RAG systems?",
        "expected_keywords": [
            "embeddings",
            "semantic",
            "similar"
        ],
    },
]


def keyword_score(answer: str, expected_keywords: List[str]) -> float:
    answer_lower = answer.lower()

    matched = sum(
        1 for keyword in expected_keywords
        if keyword.lower() in answer_lower
    )

    return matched / len(expected_keywords)


def evaluate():
    total_score = 0.0

    for index, case in enumerate(TEST_CASES, start=1):

        result = generate_answer(
            query=case["question"],
            file_path="data/sample_document.txt",
            top_k=3
        )

        answer = result["answer"]

        score = keyword_score(
            answer,
            case["expected_keywords"]
        )

        total_score += score

        print(f"\nTest {index}")
        print(f"Question: {case['question']}")
        print(f"Answer: {answer}")
        print(f"Keyword score: {score:.2f}")
        print("-" * 80)

    average_score = total_score / len(TEST_CASES)

    print("\nEvaluation Summary")
    print(f"Average keyword score: {average_score:.2f}")


if __name__ == "__main__":
    evaluate()
