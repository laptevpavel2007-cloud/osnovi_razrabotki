import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packages.core.database import Database
from packages.core.product import ProductService
from packages.core.pc_builder import PCBuilderService


class TestPCBuilderService(unittest.TestCase):
    
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
        self.db.init_schema()

        self.db.execute(
            "INSERT INTO categories (id_category, name_category) VALUES (2, 'Комплектующие для ПК')")
        
        self.db.execute("""
            INSERT INTO producrs 
            (id_product, name_of_product, price, id_category, quantity_at_storage) 
            VALUES (17, 'Процессор Intel Core i3-12100', 10500.0, 2, 20)""")
        self.db.execute("""
            INSERT INTO producrs 
            (id_product, name_of_product, price, id_category, quantity_at_storage) 
            VALUES (22, 'Материнская плата ASUS B660', 12500.0, 2, 12)""")
        self.db.execute("""
            INSERT INTO producrs 
            (id_product, name_of_product, price, id_category, quantity_at_storage) 
            VALUES (31, 'Видеокарта NVIDIA RTX 3060', 42000.0, 2, 8)""")
        self.db.commit()
        
        self.product_service = ProductService(self.db)
        self.service = PCBuilderService(self.db, self.product_service)
    
    def tearDown(self):
        self.db.close()
        os.unlink(self.temp_db.name)
    
    def test_get_components_processor(self):
        components = self.service.get_components("Процессор")
        self.assertGreater(len(components), 0)
        self.assertEqual(components[0][0], 17)
    
    def test_get_components_storage(self):
        components = self.service.get_components("Накопитель")
        self.assertGreater(len(components), 0)
    
    def test_build_pc_success(self):
        selected = {
            "Процессор": 17,
            "Материнская плата": 22
        }
        result = self.service.build_pc(selected, need_assembly=False)
        self.assertTrue(result['success'])
        self.assertEqual(len(result['items']), 2)
        self.assertGreater(result['total'], 0)
    
    def test_build_pc_with_assembly(self):
        selected = {
            "Процессор": 17
            }
        result = self.service.build_pc(selected, need_assembly=True)
        self.assertTrue(result['success'])

        self.assertEqual(len(result['items']), 2)
    
    def test_build_pc_component_not_found(self):
        selected = {
            "Процессор": 999
            }
        result = self.service.build_pc(selected, need_assembly=False)
        self.assertFalse(result['success'])
        self.assertIn('не найден', result['message'])


if __name__ == '__main__':
    unittest.main()