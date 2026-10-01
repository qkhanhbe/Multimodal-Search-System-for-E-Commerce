"""Presentation layer: collects the customer's input and shows results.

The UI talks only to application services; it never opens products.json or the order list.
"""
import os


class VoiceInput:
    """Simulated microphone: the 'recording' is the sentence the customer said."""

    def record(self, spoken_sentence):
        return spoken_sentence


class ImageUpload:

    def upload(self, path):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"image not found: {path}")
        return os.path.abspath(path)


class SearchResultView:

    def show_products(self, title, steps, results):
        print(f"\n--- {title} ---")
        for step in steps:
            print(f"  {step}")
        if not results:
            print("  (no products found)")
            return
        print(f"  {'#':>2}  {'Product':<22} {'Price':>6} {'Stock':>5}  "
              f"{'keyword':>7} {'cosine':>6}  {'S(x|q)':>6}")
        for i, r in enumerate(results, 1):
            p = r["product"]
            print(f"  {i:>2}  {p['name']:<22} {p['price']:>6} {p['stock']:>5}  "
                  f"{r['text']:>7} {r['image']:>6.3f}  {r['score']:>6.3f}")

    def show_orders(self, title, steps, orders):
        print(f"\n--- {title} ---")
        for step in steps:
            print(f"  {step}")
        if not orders:
            print("  (no order found)")
        for o in orders:
            print(f"  Order: {o['order_id']}\n  Status: {o['status']}\n  Total: {o['total']}"
                  f"\n  Date: {o['date']}  Customer: {o['customer_id']}")


class SearchUI:

    def __init__(self, query_service, speech_service, image_service, search_service,
                 ranking_service, customer_id="C001", view=None):
        self.query_service = query_service
        self.speech_service = speech_service
        self.image_service = image_service
        self.search_service = search_service
        self.ranking_service = ranking_service
        self.customer_id = customer_id
        self.voice_input = VoiceInput()
        self.image_upload = ImageUpload()
        self.view = view or SearchResultView()

    # ---- one entry point per modality; all of them end in _run(common query) ----

    def search_text(self, text):
        query = self.query_service.text_query(text)
        return self._run(query, [f"input (text): {text!r}"])

    def search_voice(self, spoken_sentence):
        audio = self.voice_input.record(spoken_sentence)
        text = self.speech_service.transcribe(audio)
        query = self.query_service.voice_query(text)
        return self._run(query, [f"input (voice): <audio of {spoken_sentence!r}>",
                                 f"SpeechService.transcribe -> {text!r} (simulated STT)"])

    def search_image(self, path):
        path = self.image_upload.upload(path)
        embedding = self.image_service.encode(path)
        query = self.query_service.image_query(embedding)
        return self._run(query, [f"input (image): {os.path.basename(path)}",
                                 f"ImageService.encode -> {len(embedding)}-d embedding"])

    def search_multimodal(self, text, path, text_weight=0.5):
        embedding = self.image_service.encode(self.image_upload.upload(path))
        query = self.query_service.multimodal_query(text, embedding, text_weight)
        return self._run(query, [f"input (text + image): {text!r} + {os.path.basename(path)}",
                                 f"lambda_t = {text_weight}, lambda_i = {1 - text_weight}"])

    def _run(self, query, steps):
        if query["type"] == "order":
            orders = self.search_service.search_orders(query, self.customer_id)
            steps.append(f"QueryService -> order query (order_id={query['order_id']}, "
                         f"latest={query['latest']})")
            self.view.show_orders("Order search", steps, orders)
            return orders

        if query.get("terms") is not None:
            steps.append(f"QueryService -> terms={query['terms']} filters={query['filters']}")
        candidates = self.search_service.retrieve(query)
        steps.append(f"SearchService.retrieve -> {len(candidates)} candidates")
        results = self.ranking_service.rank(candidates, query)
        steps.append("RankingService.rank -> top results (alpha, beta, gamma) = "
                     + str(tuple(round(w, 2) for w in self.ranking_service.weights(query))))
        self.view.show_products(f"{query['type'].capitalize()} search", steps, results)
        return results
