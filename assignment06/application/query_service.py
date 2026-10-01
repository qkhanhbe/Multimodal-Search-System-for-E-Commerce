"""Application layer: converts every input modality into one common query object.

    text  q_t -> z_t      voice q_v -> z_v      image q_i -> z_i

The query object is a plain dict. Text and voice queries carry normalised search terms and
filters (price, category); image queries carry an embedding; a multimodal query carries both.
"""
import re

STOPWORDS = {
    "a", "an", "the", "find", "show", "me", "my", "i", "want", "to", "buy", "search", "for",
    "please", "some", "any", "products", "product", "similar", "this", "is", "where", "of",
    "with", "and", "dollars", "dollar", "usd", "price", "in",
}
PRICE_RE = re.compile(r"\b(?:under|below|less than|cheaper than|max)\s*\$?\s*(\d+(?:\.\d+)?)")
ORDER_ID_RE = re.compile(r"\b(o\d{3}|\d{8})\b", re.IGNORECASE)


class QueryService:

    def text_query(self, text):
        return self._parse(text, "text")

    def voice_query(self, text):
        return self._parse(text, "voice")

    def image_query(self, embedding):
        return {
            "type": "image",
            "embedding": embedding,
        }

    def multimodal_query(self, text, embedding, text_weight=0.5):
        query = self._parse(text, "multimodal")
        query["embedding"] = embedding
        query["weights"] = {"text": text_weight, "image": 1.0 - text_weight}
        return query

    def _parse(self, text, mode):
        raw = text.strip()
        lowered = raw.lower()

        if re.search(r"\border\b", lowered):
            match = ORDER_ID_RE.search(lowered)
            return {
                "type": "order",
                "source": mode,
                "query": raw,
                "order_id": match.group(1).upper() if match else None,
                "latest": bool(re.search(r"\b(latest|last|recent)\b", lowered)),
            }

        filters = {}
        price = PRICE_RE.search(lowered)
        if price:
            filters["max_price"] = float(price.group(1))
            lowered = PRICE_RE.sub(" ", lowered)

        words = re.findall(r"[a-z0-9\-]+", lowered)
        terms = [w for w in words if w not in STOPWORDS]

        return {
            "type": mode,
            "query": raw,
            "terms": terms,
            "filters": filters,
        }
