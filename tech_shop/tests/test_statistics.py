import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packages.core.database import Database
from packages.core.statistics import StatisticsService


class TestStatisticsService(unittest.TestCase):
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
        self.db.init_schema()
        
        self.db.execute(
            "INSERT INTO categories (id_category, name_category) VALUES (1, 'Тест')")
        
        self.db.execute("""
            INSERT INTO producrs 
            (id_product, name_of_product, price, id_category, quantity_at_storage) 
            VALUES (1, 'Товар1', 1000.0, 1, 10)""")
        
        self.db.execute("""
            INSERT INTO producrs 
            (id_product, name_of_product, price, id_category, quantity_at_storage) 
            VALUES (2, 'Товар2', 2000.0, 1, 5)""")
        
        self.db.execute(
            "INSERT INTO jobs_titles (id_job_title, name) VALUES (1, 'Тестер')")
        
        self.db.execute("""
            INSERT INTO emploees 
            (id_employee, name, surname, id_job_title) 
            VALUES (1, 'Тест', 'Тестов', 1)""")
        self.db.commit()
        
        self.db.execute("""
            INSERT INTO reseipts (created_at, date, id_cashier) 
            VALUES (1000.0, '2024-01-15T10:00:00', 1)""")
        check_id = self.db.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        self.db.execute("""
            INSERT INTO sale_items (id_check, id_product, quantity, date) 
            VALUES (?, 1, 3, '2024-01-15T10:00:00')""", (check_id,))
        
        self.db.execute("""
            INSERT INTO sale_items (id_check, id_product, quantity, date) 
            VALUES (?, 2, 2, '2024-01-15T10:00:00')""", (check_id,))
        self.db.commit()
        
        self.service = StatisticsService(self.db)
    
    def tearDown(self):
        self.db.close()
        os.unlink(self.temp_db.name)
    
    def test_get_best_seller(self):
        result = self.service.get_best_seller('2024-01-15')
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'Товар1')
        self.assertEqual(result[1], 3.0)
    
    def test_get_best_seller_no_sales(self):
        result = self.service.get_best_seller('2024-12-31')
        self.assertIsNone(result)
    
    def test_get_best_seller_invalid_date(self):
        with self.assertRaises(ValueError):
            self.service.get_best_seller('15-01-2024')
    
    def test_validate_date_correct(self):
        self.assertTrue(StatisticsService._validate_date('2024-01-15'))
    
    def test_validate_date_incorrect(self):
        self.assertFalse(StatisticsService._validate_date('15-01-2024'))
        self.assertFalse(StatisticsService._validate_date('2024/01/15'))


if __name__ == '__main__':
    unittest.main()