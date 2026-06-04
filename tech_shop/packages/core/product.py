from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class Product:

    id_product: int
    name_of_product: str
    price: float
    id_category: int
    quantity_at_storage: float
    
    def total_value(self) -> float:
        return self.price * self.quantity_at_storage
    
    def is_available(self, quantity: float) -> bool:
        return self.quantity_at_storage >= quantity
    
    def reduce_stock(self, quantity: float) -> None:
        if not self.is_available(quantity):
            raise ValueError(f"Недостаточно товара: {self.quantity_at_storage} < {quantity}")
        self.quantity_at_storage -= quantity
    
    def add_stock(self, quantity: float) -> None:
        if quantity < 0:
            raise ValueError("Количество должно быть неотрицательным")
        self.quantity_at_storage += quantity


class ProductService:
    
    def __init__(self, database):
        self.database = database
    
    def get_all(self) -> List[Product]:
        rows = self.database.fetchall(
            "SELECT id_product, name_of_product, price, id_category, quantity_at_storage "
            "FROM producrs"
        )
        return [
            Product(
                id_product=row[0],
                name_of_product=row[1],
                price=row[2],
                id_category=row[3],
                quantity_at_storage=row[4]
            )
            for row in rows
        ]
    
    def get_by_id(self, product_id: int) -> Optional[Product]:
        row = self.database.fetchone(
            "SELECT id_product, name_of_product, price, id_category, quantity_at_storage "
            "FROM producrs WHERE id_product = ?",
            (product_id,)
        )
        if not row:
            return None
        return Product(
            id_product=row[0],
            name_of_product=row[1],
            price=row[2],
            id_category=row[3],
            quantity_at_storage=row[4]
        )
    
    def get_by_name(self, name: str) -> Optional[Product]:
        row = self.database.fetchone(
            "SELECT id_product, name_of_product, price, id_category, quantity_at_storage "
            "FROM producrs WHERE LOWER(name_of_product) = LOWER(?)",
            (name,)
        )
        if not row:
            return None
        return Product(
            id_product=row[0],
            name_of_product=row[1],
            price=row[2],
            id_category=row[3],
            quantity_at_storage=row[4]
        )
    
    def update_stock(self, product_id: int, new_quantity: float) -> None:
        self.database.execute(
            "UPDATE producrs SET quantity_at_storage = ? WHERE id_product = ?",
            (new_quantity, product_id)
        )
        self.database.commit()
    
    def reduce_stock(self, product_id: int, quantity: float) -> None:
        product = self.get_by_id(product_id)
        if not product:
            raise ValueError(f"Товар с ID {product_id} не найден")
        if not product.is_available(quantity):
            raise ValueError(f"Недостаточно товара '{product.name_of_product}' на складе: "f"доступно {product.quantity_at_storage}, запрошено {quantity}")
        self.update_stock(product_id, product.quantity_at_storage - quantity)
    
    def add_stock(self, product_id: int, quantity: float) -> None:
        if quantity < 0:
            raise ValueError("Количество должно быть неотрицательным")
        product = self.get_by_id(product_id)
        if not product:
            raise ValueError(f"Товар с ID {product_id} не найден")
        self.update_stock(product_id, product.quantity_at_storage + quantity)