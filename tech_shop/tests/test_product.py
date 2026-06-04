import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packages.core.database import Database
from packages.core.product import Product, ProductService


class TestProductModel(unittest.TestCase):

    def setUp(self):
        self.product = Product(
            id_product=1,
            name_of_product="Холодильник Samsung",
            price=35000.0,
            id_category=1,
            quantity_at_storage=5
        )

    def test_total_value(self):
        self.assertEqual(self.product.total_value(), 175000.0)

    def test_is_available_true(self):
        self.assertTrue(self.product.is_available(3))

    def test_is_available_exact(self):
        self.assertTrue(self.product.is_available(5))

    def test_is_available_false(self):
        self.assertFalse(self.product.is_available(10))

    def test_reduce_stock(self):
        self.product.reduce_stock(2)
        self.assertEqual(self.product.quantity_at_storage, 3)

    def test_reduce_stock_insufficient(self):
        with self.assertRaises(ValueError) as context:
            self.product.reduce_stock(10)
        self.assertIn("Недостаточно", str(context.exception))

    def test_add_stock(self):
        self.product.add_stock(5)
        self.assertEqual(self.product.quantity_at_storage, 10)

    def test_add_stock_negative(self):
        with self.assertRaises(ValueError) as context:
            self.product.add_stock(-5)
        self.assertIn("должно быть", str(context.exception))


class TestProductService(unittest.TestCase):

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
        self.db.init_schema()

        self.db.execute(
            "INSERT INTO categories (id_category, name_category) VALUES (1, 'Бытовая техника')")
        self.db.execute("""
            INSERT INTO producrs 
            (id_product, name_of_product, price, id_category, quantity_at_storage) 
            VALUES (1, 'Холодильник Samsung', 35000.0, 1, 5)""")
        self.db.execute("""
            INSERT INTO producrs 
            (id_product, name_of_product, price, id_category, quantity_at_storage) 
            VALUES (2, 'Микроволновка LG', 6500.0, 1, 10)""")
        self.db.commit()

        self.service = ProductService(self.db)

    def tearDown(self):
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_get_all_products(self):
        products = self.service.get_all()
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0].name_of_product, 'Холодильник Samsung')

    def test_get_by_id(self):
        product = self.service.get_by_id(1)
        self.assertIsNotNone(product)
        self.assertEqual(product.name_of_product, 'Холодильник Samsung')
        self.assertEqual(product.price, 35000.0)

    def test_get_by_id_not_found(self):
        product = self.service.get_by_id(999)
        self.assertIsNone(product)

    def test_get_by_name(self):
        product = self.service.get_by_name('холодильник samsung')
        self.assertIsNotNone(product)
        self.assertEqual(product.id_product, 1)

    def test_get_by_name_not_found(self):
        product = self.service.get_by_name('Несуществующий товар')
        self.assertIsNone(product)

    def test_update_stock(self):
        self.service.update_stock(1, 15)
        product = self.service.get_by_id(1)
        self.assertEqual(product.quantity_at_storage, 15)


if __name__ == '__main__':
    unittest.main()