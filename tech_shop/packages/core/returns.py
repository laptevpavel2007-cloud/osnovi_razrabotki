import datetime as dt

class ReturnsService:
    def __init__(self, db, product_service):
        self.db = db
        self.product_service = product_service
    
    def get_check_items(self, check_id):
        cursor = self.db.execute("""
            SELECT si.id_sale, p.name_of_product, si.quantity,
            COALESCE(SUM(r.quantity_returned), 0) as returned, p.price
            FROM sale_items si
            JOIN producrs p ON si.id_product = p.id_product
            LEFT JOIN returns r ON si.id_sale = r.id_sale
            WHERE si.id_check = ?
            GROUP BY si.id_sale""", (check_id,))
        return cursor.fetchall()
    
    def check_exists(self, check_id):
        cursor = self.db.execute("SELECT id_check FROM reseipts WHERE id_check = ?", (check_id,))
        return cursor.fetchone() is not None
    
    def get_available_for_return(self, check_id):
        if not self.check_exists(check_id):
            return []
        
        items = self.get_check_items(check_id)
        available = []
        for sale_id, name, qty_sold, returned, price in items:
            avail = qty_sold - returned
            if avail > 0:
                available.append({
                    'sale_id': sale_id,
                    'name': name,
                    'available': avail,
                    'price': price
                })
        return available
    
    def process_return(self, sale_id, quantity, reason):
        if quantity <= 0:
            raise ValueError("Количество должно быть > 0")
        
        items = self.get_check_items(sale_id)
        if not items:
            return {'success': False, 'message': 'Продажа не найдена'}
        
        sale_id_db, product_name, qty_sold, returned, price = items[0]
        max_avail = qty_sold - returned
        
        if quantity > max_avail:
            return {'success': False, 'message': f"Можно вернуть максимум {max_avail} шт."}
        
        now_ts = dt.datetime.now().timestamp()
        now_str = dt.datetime.now().isoformat()
        
        try:
            self.db.execute("""
                INSERT INTO returns (id_sale, return_date, date, quantity_returned, reason)
                VALUES (?, ?, ?, ?, ?)""", (sale_id, now_ts, now_str, quantity, reason))
            
            self.db.execute("""
                UPDATE producrs 
                SET quantity_at_storage = quantity_at_storage + ?
                WHERE id_product = (
                SELECT id_product FROM sale_items WHERE id_sale = ?)
                """, (quantity, sale_id))
            
            self.db.commit()
            return {
                'success': True,
                'message': f"Успешно возвращено {quantity} шт. '{product_name}'"
            }
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'message': f"Ошибка: {e}"}