class WarehouseService:
    def __init__(self, product_service):
        self.product_service = product_service

    def add_to_warehouse(self, product_name, quantity):
        if quantity <= 0:
            raise ValueError("Количество должно быть > 0")

        product = self.product_service.get_by_name(product_name)
        if not product:
            return {'success': False, 'message': f"Товар '{product_name}' не найден"}

        product.add_stock(quantity)
        # ИСПРАВЛЕНО: id_product и quantity_at_storage вместо id и quantity
        self.product_service.update_stock(product.id_product, product.quantity_at_storage)

        return {
            'success': True,
            'message': f"{product.name_of_product}: +{quantity} шт. (Всего: {product.quantity_at_storage})",
            'product_name': product.name_of_product,
            'new_total': product.quantity_at_storage
        }