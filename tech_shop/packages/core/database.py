import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Tuple


class Database:

    def __init__(self, db_path: str = 'store.db'):
        self.db_path = db_path
        self._connection: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.execute("PRAGMA foreign_keys = ON;")
        return self._connection

    def close(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    @contextmanager
    def transaction(self):
        conn = self.connect()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e

    def init_schema(self) -> None:
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS jobs_titles (
            id_job_title INTEGER PRIMARY KEY NOT NULL UNIQUE,
            name TEXT NOT NULL)""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS emploees (
            id_employee INTEGER PRIMARY KEY NOT NULL UNIQUE,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            id_job_title INTEGER NOT NULL,
            FOREIGN KEY(id_job_title) REFERENCES jobs_titles(id_job_title))""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS categories (
            id_category INTEGER PRIMARY KEY NOT NULL UNIQUE,
            name_category TEXT NOT NULL)""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS producrs (
            id_product INTEGER PRIMARY KEY NOT NULL UNIQUE,
            name_of_product TEXT NOT NULL,
            price REAL NOT NULL,
            id_category INTEGER NOT NULL,
            quantity_at_storage REAL NOT NULL,
            FOREIGN KEY(id_category) REFERENCES categories(id_category))""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS reseipts (
            id_check INTEGER PRIMARY KEY NOT NULL UNIQUE,
            created_at REAL NOT NULL,
            date TEXT NOT NULL,
            id_cashier INTEGER NOT NULL,
            FOREIGN KEY(id_cashier) REFERENCES emploees(id_employee))""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS sale_items (
            id_sale INTEGER PRIMARY KEY NOT NULL UNIQUE,
            id_check INTEGER NOT NULL,
            id_product INTEGER NOT NULL,
            quantity REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY(id_check) REFERENCES reseipts(id_check),
            FOREIGN KEY(id_product) REFERENCES producrs(id_product))""")

        cursor.execute("""CREATE TABLE IF NOT EXISTS returns (
            id_return INTEGER PRIMARY KEY NOT NULL UNIQUE,
            id_sale INTEGER NOT NULL,
            return_date REAL NOT NULL,
            date TEXT NOT NULL,
            quantity_returned REAL NOT NULL,
            reason TEXT,
            FOREIGN KEY(id_sale) REFERENCES sale_items(id_sale))""")

        conn.commit()

    def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor

    def fetchall(self, query: str, params: Tuple = ()) -> List[Tuple]:
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def fetchone(self, query: str, params: Tuple = ()) -> Optional[Tuple]:
        cursor = self.execute(query, params)
        return cursor.fetchone()

    def commit(self):
        if self._connection:
            self._connection.commit()

    def rollback(self):
        if self._connection:
            self._connection.rollback()