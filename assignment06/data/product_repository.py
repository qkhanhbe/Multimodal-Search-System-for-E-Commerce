"""Data layer: access to the product catalogue (products.json)."""
import json
import os

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


class ProductRepository:

    def __init__(self, path=os.path.join(DATA_DIR, "products.json")):
        with open(path, encoding="utf-8") as f:
            self.products = json.load(f)

    def all_products(self):
        return self.products

    def find_by_id(self, product_id):
        for product in self.products:
            if product["id"] == product_id:
                return product
        return None
