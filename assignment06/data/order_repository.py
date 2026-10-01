"""Data layer: access to customer orders (the Order Database is an in-memory list)."""


class OrderRepository:

    def __init__(self):
        self.orders = [
            {"order_id": "O001", "customer_id": "C001", "date": "2026-09-20",
             "status": "Shipped", "total": 150,
             "items": [{"product_id": 4, "quantity": 2, "price": 75}]},
            {"order_id": "O002", "customer_id": "C002", "date": "2026-09-25",
             "status": "Delivered", "total": 80,
             "items": [{"product_id": 3, "quantity": 1, "price": 80}]},
            {"order_id": "O003", "customer_id": "C001", "date": "2026-09-28",
             "status": "Processing", "total": 135,
             "items": [{"product_id": 1, "quantity": 1, "price": 120},
                       {"product_id": 7, "quantity": 1, "price": 15}]},
            {"order_id": "20261001", "customer_id": "C001", "date": "2026-10-01",
             "status": "Pending", "total": 25,
             "items": [{"product_id": 9, "quantity": 1, "price": 25}]},
        ]

    def find_order(self, order_id):
        for order in self.orders:
            if order["order_id"].lower() == order_id.lower():
                return order
        return None

    def latest_order(self, customer_id):
        own = [o for o in self.orders if o["customer_id"] == customer_id]
        return max(own, key=lambda o: o["date"]) if own else None

    def find_by_status(self, status):
        return [o for o in self.orders if o["status"].lower() == status.lower()]
