# from app.models.orders import Order
# from app.models.order_items import OrderItem
# from datetime import datetime

# class OrderController:
#     def __init__(self, db):
#         self.db = db

#     def create_order(self, order: Order, items: list[OrderItem]):
#         """Create a new order with items"""
#         try:
#             order.validate()
            
#             # Validate items
#             for item in items:
#                 item.validate()
            
#             with self.db.conn:
#                 # Insert order
#                 cursor = self.db.execute(
#                     """INSERT INTO orders 
#                        (customer_id, order_type, location_id, status,
#                         subtotal, shipping_fee, payment_method, delivery_method)
#                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
#                     (order.customer_id, order.order_type, order.location_id,
#                      order.status, order.subtotal, order.shipping_fee,
#                      order.payment_method, order.delivery_method)
#                 )
#                 order_id = cursor.lastrowid
                
#                 # Insert items
#                 for item in items:
#                     self.db.execute(
#                         """INSERT INTO order_items 
#                            (order_id, product_id, qty, unit_price)
#                            VALUES (?, ?, ?, ?)""",
#                         (order_id, item.product_id, item.qty, item.unit_price)
#                     )
                    
#                     # Update inventory
#                     inventory = self.db.fetchone(
#                         "SELECT total_qty FROM inventory WHERE product_id = ?",
#                         (item.product_id,)
#                     )
#                     if inventory:
#                         old_qty = inventory['total_qty']
#                         new_qty = max(0, old_qty - item.qty)
                        
#                         self.db.execute(
#                             """UPDATE inventory 
#                                SET total_qty = ?, last_updated = CURRENT_TIMESTAMP
#                                WHERE product_id = ?""",
#                             (new_qty, item.product_id)
#                         )
                        
#                         # Record inventory history
#                         self.db.execute(
#                             """INSERT INTO inventory_history 
#                                (inventory_id, product_id, old_total_qty, new_total_qty,
#                                 change_type, changed_by, remarks)
#                                VALUES ((SELECT inventory_id FROM inventory WHERE product_id = ?),
#                                        ?, ?, ?, 'remove', ?, 'Order: ' || ?)""",
#                             (item.product_id, item.product_id, old_qty, new_qty,
#                              order.customer_id, order_id)
#                         )
                
#                 # Record order history
#                 self.db.execute(
#                     """INSERT INTO orders_history 
#                        (order_id, customer_id, order_date, order_type,
#                         location_id, status, subtotal, shipping_fee, total,
#                         payment_method, delivery_method, changed_by, change_type)
#                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'add')""",
#                     (order_id, order.customer_id, order.order_date,
#                      order.order_type, order.location_id, order.status,
#                      order.subtotal, order.shipping_fee, order.subtotal + order.shipping_fee,
#                      order.payment_method, order.delivery_method,
#                      order.customer_id)
#                 )
                
#                 return order_id
#         except Exception as e:
#             raise e

#     def update_order_status(self, order_id: int, status: str, changed_by: int):
#         """Update order status"""
#         try:
#             valid_statuses = ['processing', 'delivered', 'returned']
#             if status not in valid_statuses:
#                 raise ValueError(f"Status must be one of: {', '.join(valid_statuses)}")
            
#             with self.db.conn:
#                 # Get current order
#                 order = self.db.fetchone(
#                     "SELECT * FROM orders WHERE order_id = ?",
#                     (order_id,)
#                 )
                
#                 if not order:
#                     raise ValueError("Order not found")
                
#                 # Update order status
#                 self.db.execute(
#                     """UPDATE orders 
#                        SET status = ?, updated_at = CURRENT_TIMESTAMP
#                        WHERE order_id = ?""",
#                     (status, order_id)
#                 )
                
#                 # Record order history
#                 self.db.execute(
#                     """INSERT INTO orders_history 
#                        (order_id, customer_id, order_date, order_type,
#                         location_id, status, subtotal, shipping_fee, total,
#                         payment_method, delivery_method, changed_by, change_type,
#                         remarks)
#                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'edit', 
#                                'Status changed from ' || ? || ' to ' || ?)""",
#                     (order['order_id'], order['customer_id'], order['order_date'],
#                      order['order_type'], order['location_id'], status,
#                      order['subtotal'], order['shipping_fee'], order['total'],
#                      order['payment_method'], order['delivery_method'],
#                      changed_by, order['status'], status)
#                 )
#         except Exception as e:
#             raise e

#     def get_order(self, order_id: int):
#         """Get a specific order with items"""
#         query = """
#         SELECT 
#             o.*,
#             c.customer_name,
#             c.contact_no as customer_contact,
#             l.location_name,
#             l.location_type,
#             (SELECT GROUP_CONCAT(p.product_name || ' x' || oi.qty) 
#              FROM order_items oi 
#              JOIN products p ON oi.product_id = p.product_id
#              WHERE oi.order_id = o.order_id) as products
#         FROM orders o
#         JOIN customers c ON o.customer_id = c.customer_id
#         JOIN locations l ON o.location_id = l.location_id
#         WHERE o.order_id = ?
#         """
#         return self.db.fetchone(query, (order_id,))

#     def get_order_items(self, order_id: int):
#         """Get items for a specific order"""
#         query = """
#         SELECT 
#             oi.*,
#             p.product_name,
#             c.category_brand,
#             c.model_name
#         FROM order_items oi
#         JOIN products p ON oi.product_id = p.product_id
#         JOIN categories c ON p.category_id = c.category_id
#         WHERE oi.order_id = ?
#         ORDER BY oi.item_id
#         """
#         return self.db.fetchall(query, (order_id,))

#     def list_orders(self, start_date=None, end_date=None, status=None):
#         """List orders with filters"""
#         query = """
#         SELECT 
#             o.*,
#             c.customer_name,
#             l.location_name,
#             COUNT(oi.item_id) as item_count,
#             SUM(oi.qty) as total_qty
#         FROM orders o
#         JOIN customers c ON o.customer_id = c.customer_id
#         JOIN locations l ON o.location_id = l.location_id
#         LEFT JOIN order_items oi ON o.order_id = oi.order_id
#         WHERE 1=1
#         """
#         params = []
        
#         if start_date:
#             query += " AND DATE(o.order_date) >= ?"
#             params.append(start_date)
        
#         if end_date:
#             query += " AND DATE(o.order_date) <= ?"
#             params.append(end_date)
        
#         if status:
#             query += " AND o.status = ?"
#             params.append(status)
        
#         query += " GROUP BY o.order_id ORDER BY o.order_date DESC"
        
#         return self.db.fetchall(query, params)

#     def get_order_statistics(self):
#         """Get order statistics"""
#         stats = {}
        
#         # Total orders
#         total_orders = self.db.fetchone("SELECT COUNT(*) as count FROM orders")
#         stats['total_orders'] = total_orders['count']
        
#         # Orders by status
#         by_status = self.db.fetchall("""
#             SELECT status, COUNT(*) as count, SUM(total) as total_value
#             FROM orders
#             GROUP BY status
#             ORDER BY count DESC
#         """)
#         stats['by_status'] = [dict(row) for row in by_status]
        
#         # Orders by location
#         by_location = self.db.fetchall("""
#             SELECT l.location_name, l.location_type, 
#                    COUNT(o.order_id) as order_count,
#                    SUM(o.total) as total_value
#             FROM orders o
#             JOIN locations l ON o.location_id = l.location_id
#             GROUP BY l.location_id
#             ORDER BY order_count DESC
#         """)
#         stats['by_location'] = [dict(row) for row in by_location]
        
#         # Daily order trend (last 30 days)
#         daily_trend = self.db.fetchall("""
#             SELECT 
#                 DATE(order_date) as date,
#                 COUNT(*) as order_count,
#                 SUM(total) as daily_total
#             FROM orders
#             WHERE DATE(order_date) >= DATE('now', '-30 days')
#             GROUP BY DATE(order_date)
#             ORDER BY date
#         """)
#         stats['daily_trend'] = [dict(row) for row in daily_trend]
        
#         # Average order value
#         avg_order = self.db.fetchone("""
#             SELECT 
#                 AVG(total) as avg_order_value,
#                 MIN(total) as min_order_value,
#                 MAX(total) as max_order_value
#             FROM orders
#             WHERE status != 'returned'
#         """)
#         stats['order_values'] = dict(avg_order)
        
#         return stats

# ---- OrderController (aligned) ----
from app.models.orders import Order
from app.models.order_items import OrderItem
from datetime import datetime

class OrderController:
    def __init__(self, db):
        self.db = db

    def create_order(self, order: Order, items: list[OrderItem], user_id: int):
        """Create order with stock validation"""
        order.validate()
        
        # Validate each item has sufficient stock
        for item in items:
            item.validate()
            
            # Check stock availability at location
            stock = self.db.fetchone("""
                SELECT SUM(qty_stocked) as available_qty 
                FROM stocks 
                WHERE product_id = ? AND location_id = ?
            """, (item.product_id, order.location_id))
            
            if not stock or stock['available_qty'] < item.qty:
                raise ValueError(f"Insufficient stock for product {item.product_id}")
        
        with self.db.conn:
            # Create order
            cur = self.db.execute(
                """INSERT INTO orders (customer_id, order_type, location_id, status, 
                    subtotal, shipping_fee, payment_method, delivery_method, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (order.customer_id, order.order_type, order.location_id, 'processing',
                 order.subtotal, order.shipping_fee, order.payment_method, 
                 order.delivery_method, user_id)
            )
            order_id = cur.lastrowid
            
            # Add order items and update stock
            for item in items:
                self.db.execute(
                    """INSERT INTO order_items (order_id, product_id, qty, unit_price)
                    VALUES (?, ?, ?, ?)""",
                    (order_id, item.product_id, item.qty, item.unit_price)
                )
                
                # Update stock at location
                self.db.execute("""
                    UPDATE stocks 
                    SET qty_stocked = qty_stocked - ?
                    WHERE product_id = ? AND location_id = ?
                """, (item.qty, item.product_id, order.location_id))
            
            # Record history
            self.db.execute("""
                INSERT INTO orders_history 
                (order_id, customer_id, order_date, order_type, location_id, status, 
                 subtotal, shipping_fee, total, payment_method, delivery_method, 
                 changed_by, change_type, remarks)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'create', 'Order created')
            """, (order_id, order.customer_id, datetime.now(), order.order_type,
                  order.location_id, 'processing', order.subtotal, order.shipping_fee,
                  order.subtotal + order.shipping_fee, order.payment_method,
                  order.delivery_method, user_id))
            
            return order_id

    def update_order_status(self, order_id: int, status: str, changed_by: int):
        valid_statuses = ['processing', 'delivered', 'returned']
        if status not in valid_statuses:
            raise ValueError("Invalid status")
        with self.db.conn:
            order = self.db.fetchone("SELECT * FROM orders WHERE order_id = ?", (order_id,))
            if not order:
                raise ValueError("Order not found")
            self.db.execute("UPDATE orders SET status=?, updated_at=CURRENT_TIMESTAMP WHERE order_id=?", (status, order_id))
            # Record history
            self.db.execute(
                """INSERT INTO orders_history
                   (order_id, customer_id, order_date, order_type, location_id, status, subtotal, shipping_fee, total, payment_method, delivery_method, changed_by, change_type, remarks)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'edit', ?)""",
                (order['order_id'], order['customer_id'], order['order_date'], order['order_type'], order['location_id'], status,
                 order['subtotal'], order['shipping_fee'], order['total'], order['payment_method'], order['delivery_method'], changed_by,
                 f"Status changed from {order['status']} to {status}")
            )

    def get_order(self, order_id: int):
        q = """
        SELECT o.*, c.customer_name, c.contact_no as customer_contact, l.location_name, l.location_type,
               (SELECT GROUP_CONCAT(p.product_name || ' x' || oi.qty)
                FROM order_items oi JOIN products p ON oi.product_id = p.product_id WHERE oi.order_id = o.order_id) as products
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN locations l ON o.location_id = l.location_id
        WHERE o.order_id = ?
        """
        return self.db.fetchone(q, (order_id,))

    def get_order_items(self, order_id: int):
        q = """
        SELECT oi.*, p.product_name, c.category_brand, c.model_name
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        WHERE oi.order_id = ?
        ORDER BY oi.item_id
        """
        return self.db.fetchall(q, (order_id,))

    def list_orders(self, start_date=None, end_date=None, status=None):
        q = """
        SELECT o.*, c.customer_name, l.location_name, COUNT(oi.item_id) as item_count, SUM(oi.qty) as total_qty
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        JOIN locations l ON o.location_id = l.location_id
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        WHERE 1=1
        """
        params = []
        if start_date:
            q += " AND DATE(o.order_date) >= ?"; params.append(start_date)
        if end_date:
            q += " AND DATE(o.order_date) <= ?"; params.append(end_date)
        if status:
            q += " AND o.status = ?"; params.append(status)
        q += " GROUP BY o.order_id ORDER BY o.order_date DESC"
        return self.db.fetchall(q, params)

    def get_order_statistics(self):
        stats = {}
        total_orders = self.db.fetchone("SELECT COUNT(*) as count FROM orders")
        stats['total_orders'] = total_orders['count'] if total_orders else 0
        by_status = self.db.fetchall("SELECT status, COUNT(*) as count, SUM(total) as total_value FROM orders GROUP BY status ORDER BY count DESC")
        stats['by_status'] = [dict(r) for r in by_status]
        by_location = self.db.fetchall("""
            SELECT l.location_name, l.location_type, COUNT(o.order_id) as order_count, SUM(o.total) as total_value
            FROM orders o JOIN locations l ON o.location_id = l.location_id
            GROUP BY l.location_id ORDER BY order_count DESC
        """)
        stats['by_location'] = [dict(r) for r in by_location]
        daily_trend = self.db.fetchall("""
            SELECT DATE(order_date) as date, COUNT(*) as order_count, SUM(total) as daily_total
            FROM orders WHERE DATE(order_date) >= DATE('now', '-30 days') GROUP BY DATE(order_date) ORDER BY date
        """)
        stats['daily_trend'] = [dict(r) for r in daily_trend]
        avg_order = self.db.fetchone("SELECT AVG(total) as avg_order_value, MIN(total) as min_order_value, MAX(total) as max_order_value FROM orders WHERE status != 'returned'")
        stats['order_values'] = dict(avg_order) if avg_order else {}
        return stats