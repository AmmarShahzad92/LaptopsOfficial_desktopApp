# from app.models.returns import Return
# from app.models.return_items import ReturnItem
# from datetime import datetime

# class ReturnsController:
#     def __init__(self, db):
#         self.db = db

#     def create_return(self, return_obj: Return, items: list[ReturnItem]):
#         """Create a new return"""
#         try:
#             return_obj.validate()
            
#             # Validate items
#             for item in items:
#                 item.validate()
            
#             # Check if order exists and is not already returned
#             order = self.db.fetchone(
#                 "SELECT order_date, status FROM orders WHERE order_id = ?",
#                 (return_obj.order_id,)
#             )
            
#             if not order:
#                 raise ValueError("Order not found")
            
#             if order['status'] == 'returned':
#                 raise ValueError("Order is already returned")
            
#             with self.db.conn:
#                 # Insert return
#                 cursor = self.db.execute(
#                     """INSERT INTO returns 
#                        (order_id, customer_id, location_id, order_date,
#                         return_amount, return_reason, notes)
#                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
#                     (return_obj.order_id, return_obj.customer_id,
#                      return_obj.location_id, order['order_date'],
#                      return_obj.return_amount, return_obj.return_reason,
#                      return_obj.notes)
#                 )
#                 return_id = cursor.lastrowid
                
#                 # Insert return items
#                 total_return_amount = 0
#                 for item in items:
#                     # Get original order item details
#                     order_item = self.db.fetchone(
#                         """SELECT qty, unit_price 
#                            FROM order_items 
#                            WHERE item_id = ?""",
#                         (item.item_id,)
#                     )
                    
#                     if not order_item:
#                         raise ValueError(f"Order item {item.item_id} not found")
                    
#                     # Verify quantities
#                     if item.qty_bought != order_item['qty']:
#                         raise ValueError(f"Quantity bought mismatch for item {item.item_id}")
                    
#                     if item.qty_returned > item.qty_bought:
#                         raise ValueError(f"Cannot return more than purchased for item {item.item_id}")
                    
#                     # Use original unit price if not specified
#                     unit_price = item.unit_price or order_item['unit_price']
                    
#                     self.db.execute(
#                         """INSERT INTO return_items 
#                            (return_id, item_id, qty_bought, qty_returned, unit_price, notes)
#                            VALUES (?, ?, ?, ?, ?, ?)""",
#                         (return_id, item.item_id, item.qty_bought,
#                          item.qty_returned, unit_price, item.notes)
#                     )
                    
#                     # Update product quantity (restock)
#                     product_id = self.db.fetchone(
#                         "SELECT product_id FROM order_items WHERE item_id = ?",
#                         (item.item_id,)
#                     )['product_id']
                    
#                     self.db.execute(
#                         "UPDATE products SET qty = qty + ? WHERE product_id = ?",
#                         (item.qty_returned, product_id)
#                     )
                    
#                     # Update inventory
#                     self.db.execute(
#                         """UPDATE inventory 
#                            SET total_qty = total_qty + ?, last_updated = CURRENT_TIMESTAMP
#                            WHERE product_id = ?""",
#                         (item.qty_returned, product_id)
#                     )
                    
#                     # Record inventory history
#                     inventory = self.db.fetchone(
#                         "SELECT total_qty FROM inventory WHERE product_id = ?",
#                         (product_id,)
#                     )
#                     if inventory:
#                         old_qty = inventory['total_qty'] - item.qty_returned
#                         new_qty = inventory['total_qty']
                        
#                         self.db.execute(
#                             """INSERT INTO inventory_history 
#                                (inventory_id, product_id, old_total_qty, new_total_qty,
#                                 change_type, changed_by, remarks)
#                                VALUES ((SELECT inventory_id FROM inventory WHERE product_id = ?),
#                                        ?, ?, ?, 'add', ?, 'Return: ' || ?)""",
#                             (product_id, product_id, old_qty, new_qty,
#                              return_obj.customer_id, return_id)
#                         )
                    
#                     total_return_amount += item.qty_returned * unit_price
                
#                 # Update return amount
#                 self.db.execute(
#                     "UPDATE returns SET return_amount = ? WHERE return_id = ?",
#                     (total_return_amount, return_id)
#                 )
                
#                 # Update order status
#                 self.db.execute(
#                     "UPDATE orders SET status = 'returned' WHERE order_id = ?",
#                     (return_obj.order_id,)
#                 )
                
#                 return return_id
#         except Exception as e:
#             raise e

#     def list_returns(self, start_date=None, end_date=None):
#         """List returns with filters"""
#         query = """
#         SELECT 
#             r.*,
#             c.customer_name,
#             l.location_name,
#             o.order_number,
#             (SELECT COUNT(*) FROM return_items WHERE return_id = r.return_id) as item_count
#         FROM returns r
#         JOIN customers c ON r.customer_id = c.customer_id
#         JOIN locations l ON r.location_id = l.location_id
#         JOIN orders o ON r.order_id = o.order_id
#         WHERE 1=1
#         """
#         params = []
        
#         if start_date:
#             query += " AND DATE(r.return_date) >= ?"
#             params.append(start_date)
        
#         if end_date:
#             query += " AND DATE(r.return_date) <= ?"
#             params.append(end_date)
        
#         query += " ORDER BY r.return_date DESC"
        
#         return self.db.fetchall(query, params)

#     def get_return_items(self, return_id: int):
#         """Get items for a specific return"""
#         query = """
#         SELECT 
#             ri.*,
#             p.product_name,
#             p.product_code,
#             c.category_brand,
#             c.model_name,
#             oi.qty as original_qty,
#             oi.unit_price as original_price
#         FROM return_items ri
#         JOIN order_items oi ON ri.item_id = oi.item_id
#         JOIN products p ON oi.product_id = p.product_id
#         JOIN categories c ON p.category_id = c.category_id
#         WHERE ri.return_id = ?
#         ORDER BY ri.ri_id
#         """
#         return self.db.fetchall(query, (return_id,))

#     def get_return_statistics(self):
#         """Get return statistics"""
#         stats = {}
        
#         # Total returns
#         total_returns = self.db.fetchone("SELECT COUNT(*) as count FROM returns")
#         stats['total_returns'] = total_returns['count']
        
#         # Return amount
#         total_amount = self.db.fetchone("SELECT SUM(return_amount) as total FROM returns")
#         stats['total_return_amount'] = total_amount['total'] if total_amount['total'] else 0
        
#         # Returns by reason
#         by_reason = self.db.fetchall("""
#             SELECT return_reason, COUNT(*) as count, SUM(return_amount) as total
#             FROM returns
#             GROUP BY return_reason
#             ORDER BY count DESC
#         """)
#         stats['by_reason'] = [dict(row) for row in by_reason]
        
#         # Returns by location
#         by_location = self.db.fetchall("""
#             SELECT l.location_name, COUNT(r.return_id) as count,
#                    SUM(r.return_amount) as total
#             FROM returns r
#             JOIN locations l ON r.location_id = l.location_id
#             GROUP BY l.location_id
#             ORDER BY count DESC
#         """)
#         stats['by_location'] = [dict(row) for row in by_location]
        
#         # Monthly return trend (last 12 months)
#         monthly_trend = self.db.fetchall("""
#             SELECT 
#                 strftime('%Y-%m', return_date) as month,
#                 COUNT(*) as return_count,
#                 SUM(return_amount) as monthly_total
#             FROM returns
#             WHERE return_date >= DATE('now', '-12 months')
#             GROUP BY strftime('%Y-%m', return_date)
#             ORDER BY month
#         """)
#         stats['monthly_trend'] = [dict(row) for row in monthly_trend]
        
#         return stats

# ---- ReturnsController (fixed) ----
from app.models.returns import Return
from app.models.return_items import ReturnItem

class ReturnsController:
    def __init__(self, db):
        self.db = db

    def create_return(self, return_obj: Return, items: list[ReturnItem]):
        return_obj.validate()
        for it in items:
            it.validate()
        order = self.db.fetchone("SELECT order_date, status FROM orders WHERE order_id = ?", (return_obj.order_id,))
        if not order:
            raise ValueError("Order not found")
        if order['status'] == 'returned':
            raise ValueError("Order is already returned")
        with self.db.conn:
            cur = self.db.execute("""INSERT INTO returns (order_id, customer_id, location_id, order_date, return_amount, return_reason, notes) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                                  (return_obj.order_id, return_obj.customer_id, return_obj.location_id, order['order_date'], return_obj.return_amount, return_obj.return_reason, return_obj.notes))
            return_id = cur.lastrowid
            total_return_amount = 0
            for it in items:
                order_item = self.db.fetchone("SELECT qty, unit_price, product_id FROM order_items WHERE item_id = ?", (it.item_id,))
                if not order_item:
                    raise ValueError(f"Order item {it.item_id} not found")
                if it.qty_returned > order_item['qty']:
                    raise ValueError("Cannot return more than purchased")
                unit_price = it.unit_price or order_item['unit_price']
                self.db.execute("INSERT INTO return_items (return_id, item_id, qty_bought, qty_returned, unit_price, notes) VALUES (?, ?, ?, ?, ?, ?)",
                                (return_id, it.item_id, order_item['qty'], it.qty_returned, unit_price, it.notes))
                # Restock: add to stocks at the return location
                existing_stock = self.db.fetchone("SELECT stock_id, qty_stocked FROM stocks WHERE product_id = ? AND location_id = ?",
                                                 (order_item['product_id'], return_obj.location_id))
                if existing_stock:
                    new_qty = existing_stock['qty_stocked'] + it.qty_returned
                    self.db.execute("UPDATE stocks SET qty_stocked=?, updated_at=CURRENT_TIMESTAMP WHERE stock_id=?", (new_qty, existing_stock['stock_id']))
                    self.db.execute("INSERT INTO stocks_history (stock_id, product_id, location_id, old_qty, new_qty, change_type, changed_by, remarks) VALUES (?, ?, ?, ?, ?, 'add', ?, 'Return received')",
                                    (existing_stock['stock_id'], order_item['product_id'], return_obj.location_id, existing_stock['qty_stocked'], new_qty, return_obj.customer_id))
                else:
                    curst = self.db.execute("INSERT INTO stocks (product_id, location_id, qty_stocked, unit_cost, manager_id) VALUES (?, ?, ?, ?, ?)",
                                            (order_item['product_id'], return_obj.location_id, it.qty_returned, unit_price, return_obj.customer_id))
                    self.db.execute("INSERT INTO stocks_history (stock_id, product_id, location_id, old_qty, new_qty, change_type, changed_by, remarks) VALUES (?, ?, ?, 0, ?, 'add', ?, 'Return received')",
                                    (curst.lastrowid, order_item['product_id'], return_obj.location_id, it.qty_returned, return_obj.customer_id))
                # Update inventory totals (increase)
                inv = self.db.fetchone("SELECT inventory_id, total_qty FROM inventory WHERE product_id = ?", (order_item['product_id'],))
                if inv:
                    old_qty = inv['total_qty'] or 0
                    new_qty = old_qty + it.qty_returned
                    self.db.execute("UPDATE inventory SET total_qty = ?, last_updated=CURRENT_TIMESTAMP WHERE product_id = ?", (new_qty, order_item['product_id']))
                    self.db.execute("INSERT INTO inventory_history (inventory_id, product_id, old_total_qty, new_total_qty, change_type, changed_by, remarks) VALUES (?, ?, ?, ?, 'add', ?, ?)",
                                    (inv['inventory_id'], order_item['product_id'], old_qty, new_qty, return_obj.customer_id, f"Return: {return_id}"))
                total_return_amount += it.qty_returned * unit_price
            # Update returns.total
            self.db.execute("UPDATE returns SET return_amount = ? WHERE return_id = ?", (total_return_amount, return_id))
            # Update order status
            self.db.execute("UPDATE orders SET status = 'returned', updated_at=CURRENT_TIMESTAMP WHERE order_id = ?", (return_obj.order_id,))
            return return_id

    def list_returns(self, start_date=None, end_date=None):
        q = """
        SELECT r.*, c.customer_name, l.location_name, o.order_id, (SELECT COUNT(*) FROM return_items WHERE return_id = r.return_id) as item_count
        FROM returns r
        JOIN customers c ON r.customer_id = c.customer_id
        JOIN locations l ON r.location_id = l.location_id
        JOIN orders o ON r.order_id = o.order_id
        WHERE 1=1
        """
        params = []
        if start_date:
            q += " AND DATE(r.return_date) >= ?"; params.append(start_date)
        if end_date:
            q += " AND DATE(r.return_date) <= ?"; params.append(end_date)
        q += " ORDER BY r.return_date DESC"
        return self.db.fetchall(q, params)

    def get_return_items(self, return_id: int):
        q = """
        SELECT ri.*, p.product_name, c.category_brand, c.model_name, oi.qty as original_qty, oi.unit_price as original_price
        FROM return_items ri
        JOIN order_items oi ON ri.item_id = oi.item_id
        JOIN products p ON oi.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        WHERE ri.return_id = ?
        ORDER BY ri.ri_id
        """
        return self.db.fetchall(q, (return_id,))

    def get_return_statistics(self):
        stats = {}
        total_returns = self.db.fetchone("SELECT COUNT(*) as count FROM returns")
        stats['total_returns'] = total_returns['count'] if total_returns else 0
        total_amount = self.db.fetchone("SELECT SUM(return_amount) as total FROM returns")
        stats['total_return_amount'] = total_amount['total'] if total_amount and total_amount['total'] else 0
        by_reason = self.db.fetchall("SELECT return_reason, COUNT(*) as count, SUM(return_amount) as total FROM returns GROUP BY return_reason ORDER BY count DESC")
        stats['by_reason'] = [dict(r) for r in by_reason]
        by_location = self.db.fetchall("SELECT l.location_name, COUNT(r.return_id) as count, SUM(r.return_amount) as total FROM returns r JOIN locations l ON r.location_id = l.location_id GROUP BY l.location_id ORDER BY count DESC")
        stats['by_location'] = [dict(r) for r in by_location]
        monthly_trend = self.db.fetchall("SELECT strftime('%Y-%m', return_date) as month, COUNT(*) as return_count, SUM(return_amount) as monthly_total FROM returns WHERE return_date >= DATE('now', '-12 months') GROUP BY month ORDER BY month")
        stats['monthly_trend'] = [dict(r) for r in monthly_trend]
        return stats

