"""Application layer: retrieval of candidate products / orders (no ranking here).

R(q) = TopK_{x in X} s(q, x)
"""


def _stem(word):
    return word[:-1] if len(word) > 3 and word.endswith("s") else word


class SearchService:

    def __init__(self, repository, vector_index=None, order_repository=None, image_top_k=5):
        self.repository = repository
        self.vector_index = vector_index
        self.order_repository = order_repository
        self.image_top_k = image_top_k

    def search_text(self, query, filters=None):
        """Keyword matching: score = number of query words found in the product text."""

        words = query.lower().split() if isinstance(query, str) else query
        words = {_stem(w) for w in words}
        filters = filters or {}

        results = []

        for product in self.repository.all_products():

            if product["price"] > filters.get("max_price", float("inf")):
                continue

            text = (
                product["name"] + " " +
                product["category"] + " " +
                product["color"] + " " +
                product["brand"]
            ).lower()
            tokens = {_stem(t) for t in text.replace("-", " ").split()}

            score = 0

            for word in words:

                if word in tokens:
                    score += 1

            if score > 0:

                results.append(
                    (product, score)
                )

        results.sort(
            key=lambda x: x[1],
            reverse=True
        )

        return results

    def search_image(self, query_embedding, k=None):
        """Vector similarity: [(product, cosine)] for the top-k most similar images."""
        hits = self.vector_index.search(query_embedding, k or self.image_top_k)
        return [(self.repository.find_by_id(pid), score) for pid, score in hits]

    def retrieve(self, query):
        """Candidate set C(q) for a common query object: {id: {product, text, image}}."""
        candidates = {}

        def add(product, signal, value):
            entry = candidates.setdefault(product["id"],
                                          {"product": product, "text": 0, "image": 0.0})
            entry[signal] = value

        if query.get("terms"):
            for product, score in self.search_text(query["terms"], query.get("filters")):
                add(product, "text", score)

        if query.get("embedding") is not None:
            for product, score in self.search_image(query["embedding"]):
                if product["price"] <= query.get("filters", {}).get("max_price", float("inf")):
                    add(product, "image", score)

        return list(candidates.values())

    def search_orders(self, query, customer_id=None):
        if query.get("order_id"):
            order = self.order_repository.find_order(query["order_id"])
            return [order] if order else []
        if query.get("latest") and customer_id:
            order = self.order_repository.latest_order(customer_id)
            return [order] if order else []
        return []
