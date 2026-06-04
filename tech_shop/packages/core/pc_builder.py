class PCBuilderService:
    COMPONENTS = {
        "Процессор": "Процессор",
        "Материнская плата": "Материнская",
        "Видеокарта": "Видеокарта",
        "Оперативная память": "память",
        "Накопитель": ["SSD", "HDD"],
        "Блок питания": "Блок питания",
        "Кулер": "Кулер",
        "Корпус": "Корпус"
    }

    ASSEMBLY_PRICE = 2000.0
    ASSEMBLY_NAME = "Сборка ПК"

    def __init__(self, db, product_service):
        self.db = db
        self.product_service = product_service

    def get_components(self, component_type):
        keywords = self.COMPONENTS.get(component_type, component_type)
        if isinstance(keywords, list):
            items = []
            for kw in keywords:
                items.extend(self._search_components(kw))
            uniq = {it[0]: it for it in items}
            return list(uniq.values())
        return self._search_components(keywords)

    def _search_components(self, keyword):
        cursor = self.db.execute("""
            SELECT id_product, name_of_product, price, quantity_at_storage
            FROM producrs
            WHERE id_category = 2 AND quantity_at_storage > 0 
            AND name_of_product LIKE ?""", (f'%{keyword}%',))
        return cursor.fetchall()

    def ensure_assembly_service(self):
        cursor = self.db.execute(
            "SELECT id_product, name_of_product, price, quantity_at_storage "
            "FROM producrs WHERE name_of_product = ?", 
            (self.ASSEMBLY_NAME,))
        service = cursor.fetchone()
        if not service:
            self.db.execute("""
                INSERT INTO producrs 
                (id_product, name_of_product, price, id_category, quantity_at_storage)
                VALUES (999, ?, ?, 4, 1000)""", (self.ASSEMBLY_NAME, self.ASSEMBLY_PRICE))
    
            cursor = self.db.execute(
                "SELECT id_product, name_of_product, price, quantity_at_storage "
                "FROM producrs WHERE name_of_product = ?", 
                (self.ASSEMBLY_NAME,))
            service = cursor.fetchone()
        return service

    def build_pc(self, selected_components, need_assembly=False):
        to_add = []

        for comp_type, prod_id in selected_components.items():
            product = self.product_service.get_by_id(prod_id)
            if not product:
                return {
                    'success': False, 
                    'message': f"Компонент '{comp_type}' не найден",
                    'items': [],
                    'total': 0
                }

            # ИСПРАВЛЕНО: quantity_at_storage вместо quantity
            if product.quantity_at_storage < 1:
                return {
                    'success': False,
                    'message': f"'{product.name_of_product}' закончился!",
                    'items': [],
                    'total': 0
                }

            to_add.append((product.id_product, product.name_of_product, product.price, 1))

        try:
            self.db.execute("BEGIN TRANSACTION")
            total_sum = 0

            for prod_id, name, price, qty in to_add:
                product = self.product_service.get_by_id(prod_id)
                product.reduce_stock(1)
                self.product_service.update_stock(prod_id, product.quantity_at_storage)
                total_sum += price

            if need_assembly:
                service = self.ensure_assembly_service()
                serv_id, serv_name, serv_price, serv_qty = service

                if serv_qty >= 1:
                    self.db.execute(
                        "UPDATE producrs SET quantity_at_storage = quantity_at_storage - 1 "
                        "WHERE id_product = ?", (serv_id,)
                    )
                    to_add.append((serv_id, serv_name, serv_price, 1))
                    total_sum += serv_price
                else:
                    return {
                        'success': False,
                        'message': "Услуга сборки временно недоступна",
                        'items': [],
                        'total': 0
                    }

            self.db.commit()
            return {
                'success': True,
                'message': f"ПК добавлен! Сумма: {total_sum:.2f} руб.",
                'items': to_add,
                'total': total_sum
            }
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'message': f"Ошибка: {e}", 'items': [], 'total': 0}