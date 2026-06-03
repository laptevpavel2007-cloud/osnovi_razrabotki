import csv
import os

class CSVLoader:
    def __init__(self, db):
        self.db = db
    
    @staticmethod
    def read_csv(filename):
        if not os.path.exists(filename):
            return []
        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader)
            return list(reader)
    
    def fill_if_empty(self, table_name, csv_file, columns, converter=None):
        cursor = self.db.execute(f"SELECT COUNT(*) FROM {table_name}")
        if cursor.fetchone()[0] == 0:
            rows = self.read_csv(csv_file)
            for row in rows:
                if converter:
                    row = converter(row)
                placeholders = ','.join(['?'] * len(row))
                self.db.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", row)
    
    @staticmethod
    def convert_prod(row):
        return (int(row[0]), row[1], float(row[2]), int(row[3]), float(row[4]))
    
    def load_all(self, data_dir='data'):
        self.fill_if_empty('jobs_titles', f'{data_dir}/jobs_titles.csv', 'id_job_title, name')
        self.fill_if_empty('categories', f'{data_dir}/categories.csv', 'id_category, name_category')
        self.fill_if_empty('emploees', f'{data_dir}/employees.csv', 'id_employee, name, surname, id_job_title')
        self.fill_if_empty('producrs', f'{data_dir}/products.csv', 'id_product, name_of_product, price, id_category, quantity_at_storage', self.convert_prod)