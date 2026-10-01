"""Multimodal e-commerce search - demo entry point.

    python main.py                      # full demo (text, voice, image, multimodal, order)
    python main.py --text "black shoes"
    python main.py --voice "find running shoes"
    python main.py --image data/query_images/query_black_shoe.png
    python main.py --text "running shoes" --image data/query_images/query_red_shoe.png
    python main.py --text "find my order O001"
"""
import argparse
import os

from application.image_service import ImageService
from application.query_service import QueryService
from application.ranking_service import RankingService
from application.search_service import SearchService
from application.speech_service import SpeechService
from data.image_storage import ImageStorage
from data.order_repository import OrderRepository
from data.product_repository import ProductRepository
from data.vector_index import VectorIndex
from presentation.search_ui import SearchUI

HERE = os.path.dirname(os.path.abspath(__file__))
QUERY_IMAGES = os.path.join(HERE, "data", "query_images")


def build_app(customer_id="C001"):
    # Data layer
    repository = ProductRepository()
    orders = OrderRepository()
    storage = ImageStorage()
    index = VectorIndex()

    # Application / Intelligence layer
    image_service = ImageService(storage)
    image_service.index_products(repository, index)
    search_service = SearchService(repository, index, orders)

    # Presentation layer
    return SearchUI(QueryService(), SpeechService(), image_service, search_service,
                    RankingService(), customer_id=customer_id)


def demo(ui):
    print("=== E-Commerce Search Demo ===")
    ui.search_text("black shoes")
    ui.search_voice("find running shoes")
    ui.search_text("find Nike shoes under 100 dollars")
    ui.search_image(os.path.join(QUERY_IMAGES, "query_black_shoe.png"))
    ui.search_multimodal("running shoes", os.path.join(QUERY_IMAGES, "query_red_shoe.png"))
    ui.search_text("find my order O001")
    ui.search_voice("where is my latest order")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--text")
    ap.add_argument("--voice", help="spoken sentence (speech-to-text is simulated)")
    ap.add_argument("--image", help="path of a query image")
    ap.add_argument("--weight", type=float, default=0.5, help="lambda_t for text+image")
    ap.add_argument("--customer", default="C001")
    args = ap.parse_args()

    ui = build_app(args.customer)
    if args.text and args.image:
        ui.search_multimodal(args.text, args.image, args.weight)
    elif args.text:
        ui.search_text(args.text)
    elif args.voice:
        ui.search_voice(args.voice)
    elif args.image:
        ui.search_image(args.image)
    else:
        demo(ui)


if __name__ == "__main__":
    main()
