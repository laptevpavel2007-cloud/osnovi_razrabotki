import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packages.core.database import Database


class TestDatabase(unittest.TestCase):
    
    def setUp(self):

        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
        self.db.init_schema()
    
    def tearDown(self):

        self.db.close()
        os.unlink(self.temp_db.name)
    
    def test_create_tables(self):
        
        cursor = self.db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'categories', 'emploees', 'jobs_titles', 
            'producrs', 'reseipts', 'returns', 'sale_items'
        ]
        
        for table in expected_tables:
            self.assertIn(table, tables, f"Таблица {table} не создана")
    
    def test_insert_and_select_product(self):

        self.db.execute(
            "INSERT INTO categories (id_category, name_category) VALUES (1, 'Тест')")
        self.db.execute("""
            INSERT INTO producrs 
            (id_product, name_of_product, price, id_category, quantity_at_storage) 
            VALUES (1, 'Тестовый товар', 1500.0, 1, 10)""")
        self.db.commit()
        
        cursor = self.db.execute("SELECT * FROM producrs WHERE id_product = 1")
        row = cursor.fetchone()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 1)
        self.assertEqual(row[1], 'Тестовый товар')
        self.assertEqual(row[2], 1500.0)
    
    def test_foreign_keys_enabled(self):

        cursor = self.db.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()
        self.assertEqual(result[0], 1)
    
    def test_transaction_commit(self):

        self.db.execute(
            "INSERT INTO categories (id_category, name_category) VALUES (1, 'Test')")
        self.db.commit()
        
        cursor = self.db.execute("SELECT COUNT(*) FROM categories")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)
    
    def test_transaction_rollback(self):

        self.db.execute(
            "INSERT INTO categories (id_category, name_category) VALUES (1, 'Test')")
        self.db.commit()
        
        try:
            with self.db.transaction() as conn:
                conn.execute(
                    "INSERT INTO categories (id_category, name_category) VALUES (2, 'Test2')")
                raise Exception("Тестовая ошибка")
        except:
            pass
        
        cursor = self.db.execute("SELECT COUNT(*) FROM categories")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)


if __name__ == '__main__':
    unittest.main()