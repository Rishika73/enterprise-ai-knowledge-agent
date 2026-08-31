from typing import List, Dict
import math
import os

from dotenv import load_dotenv

load_dotenv()


class VectorStore:
    def __init__(self):
        self.documents: List[Dict] = []
        self.embeddings: List[List[float]] = []

    def _get_client(self):
        # Import only when an API request is actually needed.
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        return OpenAI(
            api_key=api_key,
            timeout=30.0
        )

    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        client = self._get_client()

        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )

        return [
            item.embedding
            for item in response.data
        ]

    @staticmethod
    def _cosine_similarity(
        vector_a: List[float],
        vector_b: List[float]
    ) -> float:

        dot_product = sum(
            a * b
            for a, b in zip(vector_a, vector_b)
        )

        norm_a = math.sqrt(
            sum(a * a for a in vector_a)
        )

        norm_b = math.sqrt(
            sum(b * b for b in vector_b)
        )

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def add_documents(self, chunks: List[Dict]) -> None:
        if not chunks:
            return

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = self._embed_texts(texts)

        self.embeddings.extend(embeddings)
        self.documents.extend(chunks)

    def search(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict]:

        if not self.embeddings or not self.documents:
            return []

        query_embedding = self._embed_texts(
            [query]
        )[0]

        scored_documents = []

        for document, embedding in zip(
            self.documents,
            self.embeddings
        ):
            score = self._cosine_similarity(
                query_embedding,
                embedding
            )

            result = document.copy()
            result["score"] = score

            scored_documents.append(result)

        scored_documents.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return scored_documents[:top_k]
