# from app.models.order_items import OrderItem

# class OrderItemsController:
#     def __init__(self, db):
#         self.db = db
    
#     def get_order_item(self, item_id: int):
#         """Get a specific order item by ID"""
#         query = """
#         SELECT oi.*, p.product_name, c.category_brand, c.model_name
#         FROM order_items oi
#         JOIN products p ON oi.product_id = p.product_id
#         JOIN categories c ON p.category_id = c.category_id
#         WHERE oi.item_id = ?
#         """
#         return self.db.fetchone(query, (item_id,))
    
#     def update_order_item(self, item_id: int, qty: int, unit_price: float):
#         """Update an order item"""
#         try:
#             if qty <= 0:
#                 raise ValueError("Quantity must be greater than 0")
#             if unit_price < 0:
#                 raise ValueError("Unit price cannot be negative")
            
#             with self.db.conn:
#                 self.db.execute(
#                     """UPDATE order_items 
#                        SET qty = ?, unit_price = ?, updated_at = CURRENT_TIMESTAMP
#                        WHERE item_id = ?""",
#                     (qty, unit_price, item_id)
#                 )
#         except Exception as e:
#             raise e
    
#     def delete_order_item(self, item_id: int):
#         """Delete an order item"""
#         try:
#             with self.db.conn:
#                 self.db.execute(
#                     "DELETE FROM order_items WHERE item_id = ?",
#                     (item_id,)
#                 )
#         except Exception as e:
#             raise e
    
#     def get_order_items_by_order(self, order_id: int):
#         """Get all items for an order"""
#         query = """
#         SELECT oi.*, p.product_name, p.product_id, c.category_brand, c.model_name
#         FROM order_items oi
#         JOIN products p ON oi.product_id = p.product_id
#         JOIN categories c ON p.category_id = c.category_id
#         WHERE oi.order_id = ?
#         ORDER BY oi.item_id
#         """
#         return self.db.fetchall(query, (order_id,))
    
#     def get_order_items_by_product(self, product_id: str):
#         """Get all order items for a specific product"""
#         query = """
#         SELECT oi.*, o.order_date, c.customer_name, o.status
#         FROM order_items oi
#         JOIN orders o ON oi.order_id = o.order_id
#         JOIN customers c ON o.customer_id = c.customer_id
#         WHERE oi.product_id = ?
#         ORDER BY o.order_date DESC
#         """
#         return self.db.fetchall(query, (product_id,))

# ---- OrderItemsController ----
from app.models.order_items import OrderItem

class OrderItemsController:
    def __init__(self, db):
        self.db = db

    def get_order_item(self, item_id: int):
        q = """
        SELECT oi.*, p.product_name, c.category_brand, c.model_name
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        WHERE oi.item_id = ?
        """
        return self.db.fetchone(q, (item_id,))

    def update_order_item(self, item_id: int, qty: int, unit_price: float):
        if qty <= 0:
            raise ValueError("Quantity must be > 0")
        if unit_price < 0:
            raise ValueError("Unit price cannot be negative")
        with self.db.conn:
            self.db.execute("UPDATE order_items SET qty=?, unit_price=?, updated_at=CURRENT_TIMESTAMP WHERE item_id=?", (qty, unit_price, item_id))

    def delete_order_item(self, item_id: int):
        with self.db.conn:
            self.db.execute("DELETE FROM order_items WHERE item_id = ?", (item_id,))

    def get_order_items_by_order(self, order_id: int):
        q = """
        SELECT oi.*, p.product_name, p.product_id, c.category_brand, c.model_name
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        WHERE oi.order_id = ?
        ORDER BY oi.item_id
        """
        return self.db.fetchall(q, (order_id,))

    def get_order_items_by_product(self, product_id: int):
        q = """
        SELECT oi.*, o.order_date, c.customer_name, o.status
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        WHERE oi.product_id = ?
        ORDER BY o.order_date DESC
        """
        return self.db.fetchall(q, (product_id,))
