import datetime as dt
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class ReceiptItem:
    product_name: str
    quantity: float
    price: float
    total: float


@dataclass
class Receipt:
    id_check: int
    created_at: str  # формат "ДД.ММ.ГГГГ ЧЧ:ММ:СС"
    cashier_id: int
    items: List[ReceiptItem]
    total_sum: float


class ReceiptService:
    def __init__(self, database):
        self.database = database

    def create_receipt(
        self,
        cashier_id: int,
        cart_items: List[Tuple[int, str, float, float, float]],) -> Receipt:

        if not cart_items:
            raise ValueError("Нельзя создать чек из пустой корзины")

        now_ts = dt.datetime.now().timestamp()
        now_iso = dt.datetime.now().isoformat()

        with self.database.transaction() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reseipts (created_at, date, id_cashier) "
                "VALUES (?, ?, ?)",
                (now_ts, now_iso, cashier_id),)
            check_id = cursor.lastrowid

            receipt_items = []
            for prod_id, name, qty, price, total in cart_items:
                cursor.execute(
                    "INSERT INTO sale_items "
                    "(id_check, id_product, quantity, date) "
                    "VALUES (?, ?, ?, ?)",
                    (check_id, prod_id, qty, now_iso),)
                receipt_items.append(
                    ReceiptItem(
                        product_name=name,
                        quantity=qty,
                        price=price,
                        total=total,
                    )
                )

        return Receipt(
            id_check=check_id,  # ← должно быть id_check, а не id
            created_at=dt.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            cashier_id=cashier_id,
            items=receipt_items,
            total_sum=sum(item.total for item in receipt_items),
        ) 

    def check_exists(self, check_id: int) -> bool:
        row = self.database.fetchone(
            "SELECT id_check FROM reseipts WHERE id_check = ?",
            (check_id,),
        )
        return row is not None

    def get_sale_items_for_return(self, check_id: int) -> List[tuple]:
        rows = self.database.fetchall(
            """
            SELECT si.id_sale, p.name_of_product, si.quantity,
                   COALESCE(SUM(r.quantity_returned), 0) as returned,
                   p.price
            FROM sale_items si
            JOIN producrs p ON si.id_product = p.id_product
            LEFT JOIN returns r ON si.id_sale = r.id_sale
            WHERE si.id_check = ?
            GROUP BY si.id_sale
            """,
            (check_id,),
        )
        return rows

    def get_available_for_return(self, check_id: int) -> List[dict]:
        if not self.check_exists(check_id):
            return []

        rows = self.get_sale_items_for_return(check_id)
        available = []
        for sale_id, name, qty_sold, returned, price in rows:
            avail = qty_sold - returned
            if avail > 0:
                available.append({
                    "sale_id": sale_id,
                    "name": name,
                    "available": avail,
                    "price": price,
                })
        return available

    def process_return(self, sale_id: int, quantity: float, reason: str) -> dict:
        if quantity <= 0:
            raise ValueError("Количество должно быть больше 0")

        rows = self.get_sale_items_for_return_by_sale_id(sale_id)
        if not rows:
            return {"success": False, "message": "Продажа не найдена"}

        sale_id_db, product_id, product_name, qty_sold, returned, price = rows[0]
        max_available = qty_sold - returned

        if quantity > max_available:
            return {
                "success": False,
                "message": f"Можно вернуть максимум {max_available} шт.",
            }

        now_ts = dt.datetime.now().timestamp()
        now_iso = dt.datetime.now().isoformat()

        try:
            with self.database.transaction() as conn:
                conn.execute(
                    "INSERT INTO returns "
                    "(id_sale, return_date, date, quantity_returned, reason) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (sale_id, now_ts, now_iso, quantity, reason),
                )
                conn.execute(
                    "UPDATE producrs "
                    "SET quantity_at_storage = quantity_at_storage + ? "
                    "WHERE id_product = ?",
                    (quantity, product_id),
                )
            return {
                "success": True,
                "message": f"Успешно возвращено {quantity} шт. '{product_name}'",
            }
        except Exception as e:
            return {"success": False, "message": f"Ошибка: {e}"}

    def get_sale_items_for_return_by_sale_id(self, sale_id: int) -> List[tuple]:
        rows = self.database.fetchall(
            """
            SELECT si.id_sale, si.id_product, p.name_of_product, si.quantity,
                   COALESCE(SUM(r.quantity_returned), 0) as returned,
                   p.price
            FROM sale_items si
            JOIN producrs p ON si.id_product = p.id_product
            LEFT JOIN returns r ON si.id_sale = r.id_sale
            WHERE si.id_sale = ?
            GROUP BY si.id_sale
            """, (sale_id,),)
        return rows