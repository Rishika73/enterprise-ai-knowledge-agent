from typing import List, Dict
import os
import numpy as np

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class VectorStore:
    def __init__(self):
        self.documents: List[Dict] = []
        self.embeddings = None

    def _embed_texts(self, texts: List[str]) -> np.ndarray:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )

        vectors = [
            item.embedding
            for item in response.data
        ]

        embeddings = np.array(vectors, dtype=np.float32)

        norms = np.linalg.norm(
            embeddings,
            axis=1,
            keepdims=True
        )

        return embeddings / np.clip(norms, 1e-12, None)

    def add_documents(self, chunks: List[Dict]) -> None:
        if not chunks:
            return

        texts = [chunk["text"] for chunk in chunks]
        embeddings = self._embed_texts(texts)

        if self.embeddings is None:
            self.embeddings = embeddings
        else:
            self.embeddings = np.vstack(
                [self.embeddings, embeddings]
            )

        self.documents.extend(chunks)

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        if self.embeddings is None or not self.documents:
            return []

        query_embedding = self._embed_texts([query])[0]

        scores = np.dot(
            self.embeddings,
            query_embedding
        )

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []

        for index in top_indices:
            document = self.documents[index].copy()
            document["score"] = float(scores[index])
            results.append(document)

        return results
