from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class CartItem:
    product_id: int
    name: str
    quantity: float
    price: float
    total: float


class ShoppingCart:

    def __init__(self):
        self.items: List[CartItem] = []

    @property
    def total_sum(self) -> float:
        return sum(item.total for item in self.items)

    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0

    def add_item(self, product, quantity: float) -> CartItem:
        if quantity <= 0:
            raise ValueError("Количество должно быть больше 0")
        total = product.price * quantity
        item = CartItem(
            product_id=product.id_product,
            name=product.name_of_product,
            quantity=quantity,
            price=product.price,
            total=total,)
        self.items.append(item)
        return item

    def add_raw_item(
        self, product_id: int, name: str, quantity: float, price: float) -> CartItem:
        if quantity <= 0:
            raise ValueError("Количество должно быть больше 0")
        total = price * quantity
        item = CartItem(
            product_id=product_id,
            name=name,
            quantity=quantity,
            price=price,
            total=total,
        )
        self.items.append(item)
        return item

    def clear(self) -> None:
        self.items.clear()

    def get_tuples(self) -> List[Tuple[int, str, float, float, float]]:
        return [
            (item.product_id, item.name, item.quantity, item.price, item.total)
            for item in self.items]