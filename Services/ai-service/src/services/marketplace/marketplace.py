import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Marketplace:
    def __init__(self):
        self.products = {}
        self.orders = []

    def add_product(self, product_id: str, product_info: Dict[str, Any]) -> None:
        if product_id in self.products:
            logger.warning(f"Product {product_id} already exists. Updating the product info.")
        self.products[product_id] = product_info
        logger.info(f"Product {product_id} added/updated successfully.")

    def remove_product(self, product_id: str) -> None:
        if product_id in self.products:
            del self.products[product_id]
            logger.info(f"Product {product_id} removed successfully.")
        else:
            logger.warning(f"Product {product_id} does not exist.")

    def list_products(self) -> List[Dict[str, Any]]:
        return list(self.products.values())

    def place_order(self, order_id: str, product_id: str, quantity: int) -> None:
        if product_id not in self.products:
            logger.error(f"Product {product_id} does not exist. Cannot place order.")
            return

        order = {
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity
        }
        self.orders.append(order)
        logger.info(f"Order {order_id} placed successfully.")

    def list_orders(self) -> List[Dict[str, Any]]:
        return self.orders

    def get_product_info(self, product_id: str) -> Dict[str, Any]:
        return self.products.get(product_id, {})

    def update_product_stock(self, product_id: str, quantity: int) -> None:
        if product_id in self.products:
            self.products[product_id]['stock'] = quantity
            logger.info(f"Product {product_id} stock updated to {quantity}.")
        else:
            logger.warning(f"Product {product_id} does not exist. Cannot update stock.")

if __name__ == "__main__":
    marketplace = Marketplace()
    marketplace.add_product("001", {"name": "Laptop", "price": 1000, "stock": 50})
    marketplace.add_product("002", {"name": "Smartphone", "price": 500, "stock": 100})
    marketplace.place_order("ord001", "001", 2)
    marketplace.update_product_stock("001", 48)
    print(marketplace.list_products())
    print(marketplace.list_orders())