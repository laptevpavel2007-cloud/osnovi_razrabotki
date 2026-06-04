import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packages.core.product import Product
from packages.core.cart import ShoppingCart, CartItem


class TestCartItem(unittest.TestCase):

    def test_create_valid(self):
        product = Product(1, 'Товар', 1000.0, 1, 10)
        item = CartItem.create(product, 2)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.total_price, 2000.0)
    
    def test_create_zero_quantity(self):
        product = Product(1, 'Товар', 1000.0, 1, 10)
        with self.assertRaises(ValueError):
            CartItem.create(product, 0)
    
    def test_create_negative_quantity(self):
        product = Product(1, 'Товар', 1000.0, 1, 10)
        with self.assertRaises(ValueError):
            CartItem.create(product, -1)
    
    def test_create_insufficient_stock(self):
        product = Product(1, 'Товар', 1000.0, 1, 5)
        with self.assertRaises(ValueError):
            CartItem.create(product, 10)


class TestShoppingCart(unittest.TestCase):
    
    def setUp(self):
        self.product1 = Product(1, 'Товар1', 1000.0, 1, 10)
        self.product2 = Product(2, 'Товар2', 2000.0, 1, 5)
        self.cart = ShoppingCart()
    
    def test_empty_cart(self):
        self.assertTrue(self.cart.is_empty)
        self.assertEqual(self.cart.total_sum, 0.0)
    
    def test_add_item(self):
        item = self.cart.add_item(self.product1, 2)
        self.assertEqual(len(self.cart.items), 1)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.total_price, 2000.0)
    
    def test_add_multiple_items(self):
        self.cart.add_item(self.product1, 2)
        self.cart.add_item(self.product2, 1)
        self.assertEqual(len(self.cart.items), 2)
        self.assertEqual(self.cart.total_sum, 4000.0)
    
    def test_clear_cart(self):
        self.cart.add_item(self.product1, 2)
        self.cart.clear()
        self.assertTrue(self.cart.is_empty)
    
    def test_get_tuples(self):
        self.cart.add_item(self.product1, 2)
        tuples = self.cart.get_tuples()
        self.assertEqual(len(tuples), 1)
        self.assertEqual(tuples[0], (1, 'Товар1', 2, 1000.0, 2000.0))
    
    def test_add_item_insufficient_stock(self):
        with self.assertRaises(ValueError):
            self.cart.add_item(self.product1, 15)


if __name__ == '__main__':
    unittest.main()