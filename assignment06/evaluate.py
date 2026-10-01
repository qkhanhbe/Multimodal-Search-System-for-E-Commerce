"""Small test set: Success Rate = successful queries / total queries (top-1 must be expected).

    python evaluate.py
"""
import contextlib
import io
import os

from main import QUERY_IMAGES, build_app

TESTS = [  # (mode, input, expected top-1 product name / order id)
    ("text", "black shoes", "Nike Running Shoes"),
    ("text", "white polo shirt", "White Polo Shirt"),
    ("text", "find Nike shoes under 100 dollars", "Nike Court Sneakers"),
    ("text", "red bag", "Red Canvas Backpack"),
    ("text", "cheap watch under 60", "Silver Analog Watch"),
    ("text", "leather handbag", "Black Leather Bag"),
    ("voice", "find running shoes", "Adidas Running Shoes"),
    ("voice", "show me a blue cap", "Blue Denim Cap"),
    ("voice", "i want a smart watch", "Black Smart Watch"),
    ("image", "query_black_shoe.png", "Nike Running Shoes"),
    ("image", "query_red_shoe.png", "Red Running Shoes"),
    ("image", "query_white_shoe.png", "Adidas Running Shoes"),
    ("image", "query_black_bag.png", "Black Leather Bag"),
    ("image", "query_blue_cap.png", "Blue Denim Cap"),
    ("image", "query_silver_watch.png", "Silver Analog Watch"),
    ("image", "query_black_tshirt.png", "Black Cotton T-Shirt"),
    ("multimodal", ("running shoes", "query_red_shoe.png"), "Red Running Shoes"),
    ("multimodal", ("nike", "query_white_shoe.png"), "Nike Court Sneakers"),
    ("text", "find my order O001", "O001"),
    ("voice", "where is my latest order", "20261001"),
]


def run(ui, mode, value):
    with contextlib.redirect_stdout(io.StringIO()):
        if mode == "text":
            out = ui.search_text(value)
        elif mode == "voice":
            out = ui.search_voice(value)
        elif mode == "image":
            out = ui.search_image(os.path.join(QUERY_IMAGES, value))
        else:
            out = ui.search_multimodal(value[0], os.path.join(QUERY_IMAGES, value[1]))
    if not out:
        return "-", None
    top = out[0]
    if "order_id" in top:
        return top["order_id"], None
    return top["product"]["name"], top["score"]


def main():
    ui = build_app()
    ok = 0
    print(f"{'#':>2}  {'Mode':<10} {'Query':<40} {'Top-1 result':<22} {'Score':>6}  Success")
    for i, (mode, value, expected) in enumerate(TESTS, 1):
        got, score = run(ui, mode, value)
        hit = got == expected
        ok += hit
        q = " + ".join(value) if isinstance(value, tuple) else value
        s = f"{score:.3f}" if score is not None else "-"
        print(f"{i:>2}  {mode:<10} {q:<40} {got:<22} {s:>6}  {'Yes' if hit else 'No (expected ' + expected + ')'}")
    print(f"\nTotal queries: {len(TESTS)}   Successful: {ok}   "
          f"Success rate: {ok / len(TESTS):.1%}")


if __name__ == "__main__":
    main()
