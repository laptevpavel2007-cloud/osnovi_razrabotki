import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packages.core.database import Database
from packages.core.product import ProductService
from packages.core.warehouse import WarehouseService

class TestWarehouse(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
        self.db.init_schema()
        self.db.execute("INSERT INTO categories VALUES (1, 'Test')")
        self.db.execute("INSERT INTO producrs VALUES (1, 'Product', 100.0, 1, 10)")
        self.db.commit()
        self.product_service = ProductService(self.db)
        self.service = WarehouseService(self.product_service)
    
    def tearDown(self):
        self.db.close()
        os.unlink(self.temp_db.name)
    
    def test_add_to_warehouse(self):
        result = self.service.add_to_warehouse('Product', 5)
        self.assertTrue(result['success'])
        self.assertEqual(result['new_total'], 15)
    
    def test_add_not_found(self):
        result = self.service.add_to_warehouse('NotFound', 5)
        self.assertFalse(result['success'])
    
    def test_add_negative(self):
        with self.assertRaises(ValueError):
            self.service.add_to_warehouse('Product', -5)

if __name__ == '__main__':
    unittest.main()