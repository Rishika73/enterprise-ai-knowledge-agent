from app.reranker import rerank_results


def test_reranker_orders_best_result_first():
    query = "hybrid retrieval semantic keyword"

    results = [
        {
            "chunk_id": 1,
            "text": "Docker packages applications into containers.",
            "hybrid_score": 0.40
        },
        {
            "chunk_id": 2,
            "text": (
                "Hybrid retrieval combines semantic search "
                "with keyword search."
            ),
            "hybrid_score": 0.60
        }
    ]

    reranked = rerank_results(
        query=query,
        results=results,
        top_k=2
    )

    assert reranked[0]["chunk_id"] == 2
    assert "rerank_score" in reranked[0]
