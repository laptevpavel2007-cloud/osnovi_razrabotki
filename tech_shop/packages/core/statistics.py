class StatisticsService:
    def __init__(self, db):
        self.db = db
    
    def get_best_seller(self, date_str):
        if not self._validate_date(date_str):
            raise ValueError("Неверный формат даты. Используйте ГГГГ-ММ-ДД")
        
        cursor = self.db.execute("""
            SELECT p.name_of_product, SUM(si.quantity) as total_sold
            FROM sale_items si
            JOIN producrs p ON si.id_product = p.id_product
            WHERE DATE(si.date) = ?
            GROUP BY si.id_product
            ORDER BY total_sold DESC
            LIMIT 1""", (date_str,))
        
        return cursor.fetchone()
    
    @staticmethod
    def _validate_date(date_str):
        if len(date_str) != 10 or date_str[4] != '-' or date_str[7] != '-':
            return False
        try:
            import datetime
            datetime.datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False