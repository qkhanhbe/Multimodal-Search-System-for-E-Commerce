"""Data layer: a tiny in-memory vector index (stands in for a vector database)."""
import numpy as np


def cosine_similarity(a, b):

    numerator = np.dot(a, b)

    denominator = (
        np.linalg.norm(a) *
        np.linalg.norm(b)
    )

    if denominator == 0:
        return 0.0

    return float(numerator / denominator)


class VectorIndex:

    def __init__(self):
        self.vectors = {}

    def add(self, product_id, embedding):
        self.vectors[product_id] = np.asarray(embedding, dtype=float)

    def __len__(self):
        return len(self.vectors)

    def search(self, query_embedding, k=None):
        """Return [(product_id, cosine)] sorted by similarity, top-k if k is given."""
        scores = [(pid, cosine_similarity(query_embedding, emb))
                  for pid, emb in self.vectors.items()]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k] if k else scores
