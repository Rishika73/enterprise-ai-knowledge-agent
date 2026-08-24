from typing import List, Dict
import numpy as np

from sentence_transformers import SentenceTransformer


class VectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.documents: List[Dict] = []
        self.embeddings = None

    def add_documents(self, chunks: List[Dict]) -> None:
        if not chunks:
            return

        texts = [chunk["text"] for chunk in chunks]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

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

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )[0]

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
