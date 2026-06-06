from typing import Any

import psycopg
from psycopg.rows import dict_row

from .settings import get_settings

CREATE_ORDERS_TABLE = """
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL,
    subtotal NUMERIC(10, 2) NOT NULL,
    discount_percent NUMERIC(5, 2) NOT NULL DEFAULT 0,
    discount_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    total NUMERIC(10, 2) NOT NULL,
    discount_reason TEXT NOT NULL DEFAULT 'No discount applied',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now());"""


def get_database_url(database_url: str | None = None) -> str:
    return database_url or get_settings().database_url


def init_db(database_url: str | None = None) -> None:
    url = get_database_url(database_url)

    with psycopg.connect(url) as conn:
        conn.execute(CREATE_ORDERS_TABLE)


def save_order(
    order: dict[str, Any],
    database_url: str | None = None,) -> int:
    url = get_database_url(database_url)

    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orders (
                    product_id,
                    quantity,
                    unit_price,
                    subtotal,
                    discount_percent,
                    discount_amount,
                    total,
                    discount_reason)
                VALUES (
                    %(product_id)s,
                    %(quantity)s,
                    %(unit_price)s,
                    %(subtotal)s,
                    %(discount_percent)s,
                    %(discount_amount)s,
                    %(total)s,
                    %(discount_reason)s
                )RETURNING id;""",order,)
            row = cur.fetchone()

            return int(row[0])


def get_order(
    order_id: int,
    database_url: str | None = None,) -> dict[str, Any] | None:
    url = get_database_url(database_url)

    with psycopg.connect(url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    product_id,
                    quantity,
                    unit_price,
                    subtotal,
                    discount_percent,
                    discount_amount,
                    total,
                    discount_reason,
                    created_at
                FROM orders
                WHERE id = %s;""",(order_id,),)
            row = cur.fetchone()

            if row is None:
                return None

            return dict(row)


def count_orders(database_url: str | None = None) -> int:
    url = get_database_url(database_url)

    with psycopg.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM orders;")
            row = cur.fetchone()

            return int(row[0])