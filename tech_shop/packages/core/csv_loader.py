import csv
import os


class CSVLoader:

    def __init__(self, database):
        self.database = database

    @staticmethod
    def read_csv(filename):

        if not os.path.exists(filename):
            print(f"⚠️  Файл не найден: {filename}")
            return []
        with open(filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader)
            return list(reader)

    def fill_if_empty(self, table_name, csv_file, columns, converter=None):

        cursor = self.database.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"📊 Таблица '{table_name}': {count} записей. Файл: {csv_file}")

        if count == 0:
            rows = self.read_csv(csv_file)
            print(f" Загружено строк из CSV: {len(rows)}")
            for row in rows:
                if converter:
                    row = converter(row)
                placeholders = ','.join(['?'] * len(row))
                self.database.execute(
                    f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})",
                    tuple(row))
                
            self.database.commit()
            print(f" Таблица '{table_name}' заполнена!")
        else:
            print(f" Таблица '{table_name}' уже заполнена, пропуск.")

    @staticmethod
    def convert_prod(row):
        return (int(row[0]), row[1], float(row[2]), int(row[3]), float(row[4]))

    def load_all(self, data_dir='data'):

        self.fill_if_empty(
            'jobs_titles',
            os.path.join(data_dir, 'jobs_titles.csv'),
            'id_job_title, name')
        
        self.fill_if_empty(
            'categories',
            os.path.join(data_dir, 'categories.csv'),
            'id_category, name_category')
        
        self.fill_if_empty(
            'emploees',
            os.path.join(data_dir, 'emploees.csv'),  # ← с опечаткой!
            'id_employee, name, surname, id_job_title')
        
        self.fill_if_empty(
            'producrs',
            os.path.join(data_dir, 'producrs.csv'),  # ← с опечаткой!
            'id_product, name_of_product, price, id_category, quantity_at_storage',
            self.convert_prod)
        
        print("\nЗагрузка данных завершена!\n")