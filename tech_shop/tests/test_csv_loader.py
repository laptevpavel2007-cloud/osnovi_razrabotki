import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packages.core.database import Database
from packages.core.csv_loader import CSVLoader


class TestCSVLoader(unittest.TestCase):
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
        self.db.init_schema()
        
        self.data_dir = tempfile.mkdtemp()
        
        with open(os.path.join(self.data_dir, 'categories.csv'), 'w', encoding='utf-8-sig') as f:
            f.write("id_category,name_category\n")
            f.write("1,Бытовая техника\n")
            f.write("2,Комплектующие\n")
        
        with open(os.path.join(self.data_dir, 'products.csv'), 'w', encoding='utf-8-sig') as f:
            f.write("id_product,name_of_product,price,id_category,quantity_at_storage\n")
            f.write("1,Холодильник,35000.0,1,5\n")
            f.write("2,Микроволновка,6500.0,1,10\n")
        
        self.loader = CSVLoader(self.db)
    
    def tearDown(self):
        self.db.close()
        os.unlink(self.temp_db.name)
        for file in os.listdir(self.data_dir):
            os.unlink(os.path.join(self.data_dir, file))
        os.rmdir(self.data_dir)
    
    def test_read_csv(self):
        rows = CSVLoader.read_csv(os.path.join(self.data_dir, 'categories.csv'))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][0], '1')
        self.assertEqual(rows[0][1], 'Бытовая техника')
    
    def test_read_csv_not_found(self):
        rows = CSVLoader.read_csv('nonexistent.csv')
        self.assertEqual(len(rows), 0)
    
    def test_fill_if_empty(self):
        self.loader.fill_if_empty(
            'categories',
            os.path.join(self.data_dir, 'categories.csv'),
            'id_category, name_category')
        
        cursor = self.db.execute("SELECT COUNT(*) FROM categories")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 2)
    
    def test_fill_if_empty_already_filled(self):
        self.db.execute(
            "INSERT INTO categories (id_category, name_category) VALUES (99, 'Существующая')")
        self.db.commit()
        
        self.loader.fill_if_empty(
            'categories',
            os.path.join(self.data_dir, 'categories.csv'),
            'id_category, name_category')
        
        cursor = self.db.execute("SELECT COUNT(*) FROM categories")
        count = cursor.fetchone()[0]
        self.assertEqual(count, 1)
    
    def test_convert_prod(self):

        row = ['1', 'Холодильник', '35000.0', '1', '5']
        result = CSVLoader.convert_prod(row)
        self.assertEqual(result, (1, 'Холодильник', 35000.0, 1, 5))


if __name__ == '__main__':
    unittest.main()