import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packages.core.database import Database
from packages.core.product import ProductService
from packages.core.receipt import ReceiptService
from packages.core.returns import ReturnsService


class TestReturns(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
        self.db.init_schema()
        self.db.execute("INSERT INTO categories VALUES (1, 'Test')")
        self.db.execute("INSERT INTO producrs VALUES (1, 'Product', 100.0, 1, 10)")
        # ВАЖНО: сначала jobs_titles, потом emploees (из-за FOREIGN KEY)
        self.db.execute("INSERT INTO jobs_titles VALUES (1, 'Test')")
        self.db.execute("INSERT INTO emploees VALUES (1, 'Test', 'Test', 1)")
        self.db.commit()

        self.product_service = ProductService(self.db)
        self.receipt_service = ReceiptService(self.db)
        self.service = ReturnsService(self.db, self.product_service)

        # Создаём чек с продажей
        self.receipt = self.receipt_service.create_receipt(
            1, [(1, 'Product', 2, 100.0, 200.0)]
        )

        # Получаем ID продажи
        cursor = self.db.execute(
            "SELECT id_sale FROM sale_items WHERE id_check = ?",
            (self.receipt.id_check,)
        )
        self.sale_id = cursor.fetchone()[0]

    def tearDown(self):
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_get_available(self):
        items = self.service.get_available_for_return(self.receipt.id_check)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['available'], 2)

    def test_process_return(self):
        result = self.service.process_return(self.sale_id, 1, 'Test')
        self.assertTrue(result['success'])
        product = self.product_service.get_by_id(1)
        self.assertEqual(product.quantity_at_storage, 11)

    def test_return_exceeds(self):
        result = self.service.process_return(self.sale_id, 5, 'Test')
        self.assertFalse(result['success'])


if __name__ == '__main__':
    unittest.main()