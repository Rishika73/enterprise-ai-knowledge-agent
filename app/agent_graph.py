import os
from typing import TypedDict, List, Dict, Any

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from app.hybrid_retriever import hybrid_search
from app.reranker import rerank_results
from app.security import sanitize_retrieved_text

load_dotenv()


class AgentState(TypedDict, total=False):
    query: str
    file_path: str
    top_k: int
    retrieved_results: List[Dict[str, Any]]
    reranked_results: List[Dict[str, Any]]
    context: str
    answer: str


def get_openai_client():
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured.")

    return OpenAI(
        api_key=api_key,
        timeout=30.0
    )


def build_context(results: List[Dict[str, Any]]) -> str:
    context_parts = []

    for i, result in enumerate(results, start=1):
        safe_text = sanitize_retrieved_text(
            result["text"]
        )

        context_parts.append(
            f"[Source {i}]\n{safe_text}"
        )

    return "\n\n".join(context_parts)


def retrieve_node(state: AgentState) -> Dict[str, Any]:
    print("LangGraph: retrieving documents...")

    query = state["query"]
    file_path = state["file_path"]
    top_k = state.get("top_k", 3)

    initial_results = hybrid_search(
        query=query,
        file_path=file_path,
        top_k=max(top_k * 3, top_k)
    )

    return {
        "retrieved_results": initial_results
    }


def rerank_node(state: AgentState) -> Dict[str, Any]:
    print("LangGraph: reranking results...")

    query = state["query"]
    top_k = state.get("top_k", 3)
    retrieved_results = state.get("retrieved_results", [])

    reranked = rerank_results(
        query=query,
        results=retrieved_results,
        top_k=top_k
    )

    return {
        "reranked_results": reranked
    }


def answer_node(state: AgentState) -> Dict[str, Any]:
    print("LangGraph: generating answer...")

    results = state.get("reranked_results", [])

    if not results:
        return {
            "context": "",
            "answer": "No relevant information was found."
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
{state["query"]}
"""

    client = get_openai_client()

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return {
        "context": context,
        "answer": response.output_text
    }


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("rerank", rerank_node)
    graph.add_node("answer", answer_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "rerank")
    graph.add_edge("rerank", "answer")
    graph.add_edge("answer", END)

    return graph.compile()


agent_graph = build_graph()


def run_agent(query: str, file_path: str, top_k: int = 3):
    return agent_graph.invoke(
        {
            "query": query,
            "file_path": file_path,
            "top_k": top_k
        }
    )


if __name__ == "__main__":
    question = "How does hybrid retrieval improve RAG?"

    result = run_agent(
        query=question,
        file_path="data/sample_document.txt",
        top_k=3
    )

    print("\nFINAL ANSWER\n")
    print(result["answer"])

    print("\nRERANKED SOURCES\n")
    for source in result["reranked_results"]:
        print(
            f"Chunk {source['chunk_id']} "
            f"(score={source['score']:.4f})"
        )
