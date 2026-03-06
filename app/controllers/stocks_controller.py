# from app.models.stocks import Stock
# from app.models.stocks_history import StockHistory
# from datetime import datetime

# class StockController:
#     def __init__(self, db):
#         self.db = db

#     def add_stock(self, stock: Stock):
#         """Add new stock to a location"""
#         try:
#             stock.validate()
            
#             # Check if stock already exists at this location
#             existing = self.db.fetchone(
#                 """SELECT stock_id, qty_stocked 
#                    FROM stocks 
#                    WHERE product_id = ? AND location_id = ?""",
#                 (stock.product_id, stock.location_id)
#             )
            
#             with self.db.conn:
#                 if existing:
#                     # Update existing stock
#                     new_qty = existing['qty_stocked'] + stock.qty_stocked
#                     self.db.execute(
#                         """UPDATE stocks 
#                            SET qty_stocked = ?, unit_cost = ?, 
#                                manager_id = ?, updated_at = CURRENT_TIMESTAMP
#                            WHERE stock_id = ?""",
#                         (new_qty, stock.unit_cost, stock.manager_id, 
#                          existing['stock_id'])
#                     )
                    
#                     # Record history
#                     self._record_stock_history(
#                         existing['stock_id'], stock.product_id, 
#                         stock.location_id, existing['qty_stocked'], 
#                         new_qty, 'add', stock.manager_id, 
#                         f"Stock added: {stock.qty_stocked} units"
#                     )
                    
#                     stock_id = existing['stock_id']
#                 else:
#                     # Insert new stock record
#                     cursor = self.db.execute(
#                         """INSERT INTO stocks 
#                            (product_id, location_id, qty_stocked, unit_cost, manager_id)
#                            VALUES (?, ?, ?, ?, ?)""",
#                         (stock.product_id, stock.location_id, 
#                          stock.qty_stocked, stock.unit_cost, stock.manager_id)
#                     )
#                     stock_id = cursor.lastrowid
                    
#                     # Record history
#                     self._record_stock_history(
#                         stock_id, stock.product_id, stock.location_id,
#                         0, stock.qty_stocked, 'add', stock.manager_id,
#                         f"New stock: {stock.qty_stocked} units"
#                     )
                
#                 # Update inventory
#                 self._update_inventory(stock.product_id, stock.manager_id)
                
#                 return stock_id
#         except Exception as e:
#             raise e

#     def update_stock(self, stock: Stock):
#         """Update existing stock"""
#         try:
#             stock.validate()
            
#             with self.db.conn:
#                 # Get current stock
#                 current = self.db.fetchone(
#                     """SELECT qty_stocked, unit_cost 
#                        FROM stocks 
#                        WHERE stock_id = ?""",
#                     (stock.stock_id,)
#                 )
                
#                 if not current:
#                     raise ValueError("Stock record not found")
                
#                 # Update stock
#                 self.db.execute(
#                     """UPDATE stocks 
#                        SET qty_stocked = ?, unit_cost = ?, manager_id = ?,
#                            updated_at = CURRENT_TIMESTAMP
#                        WHERE stock_id = ?""",
#                     (stock.qty_stocked, stock.unit_cost, 
#                      stock.manager_id, stock.stock_id)
#                 )
                
#                 # Record history
#                 self._record_stock_history(
#                     stock.stock_id, stock.product_id, stock.location_id,
#                     current['qty_stocked'], stock.qty_stocked, 'adjust',
#                     stock.manager_id, f"Stock adjusted"
#                 )
                
#                 # Update inventory
#                 self._update_inventory(stock.product_id, stock.manager_id)
#         except Exception as e:
#             raise e

#     def remove_stock(self, stock_id: int, quantity: int, 
#                     manager_id: int, remarks: str = None):
#         """Remove stock from a location"""
#         try:
#             if quantity <= 0:
#                 raise ValueError("Quantity must be greater than 0")
            
#             with self.db.conn:
#                 # Get current stock
#                 current = self.db.fetchone(
#                     """SELECT qty_stocked, product_id, location_id 
#                        FROM stocks 
#                        WHERE stock_id = ?""",
#                     (stock_id,)
#                 )
                
#                 if not current:
#                     raise ValueError("Stock record not found")
                
#                 if current['qty_stocked'] < quantity:
#                     raise ValueError("Insufficient stock to remove")
                
#                 new_qty = current['qty_stocked'] - quantity
                
#                 # Update stock
#                 self.db.execute(
#                     """UPDATE stocks 
#                        SET qty_stocked = ?, updated_at = CURRENT_TIMESTAMP
#                        WHERE stock_id = ?""",
#                     (new_qty, stock_id)
#                 )
                
#                 # Record history
#                 self._record_stock_history(
#                     stock_id, current['product_id'], current['location_id'],
#                     current['qty_stocked'], new_qty, 'remove', manager_id,
#                     remarks or f"Stock removed: {quantity} units"
#                 )
                
#                 # Update inventory
#                 self._update_inventory(current['product_id'], manager_id)
#         except Exception as e:
#             raise e

#     def _record_stock_history(self, stock_id: int, product_id: str, 
#                              location_id: int, old_qty: int, new_qty: int,
#                              change_type: str, changed_by: int, remarks: str):
#         """Record stock change history"""
#         self.db.execute(
#             """INSERT INTO stocks_history 
#                (stock_id, product_id, location_id, old_qty, new_qty,
#                 change_type, changed_by, remarks)
#                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
#             (stock_id, product_id, location_id, old_qty, new_qty,
#              change_type, changed_by, remarks)
#         )

#     def _update_inventory(self, product_id: str, changed_by: int):
#         """Update inventory after stock change"""
#         # Get total stock across all locations
#         total_stock = self.db.fetchone(
#             """SELECT 
#                   SUM(qty_stocked) as total_qty,
#                   AVG(unit_cost) as avg_cost
#                FROM stocks 
#                WHERE product_id = ?""",
#             (product_id,)
#         )
        
#         if total_stock:
#             # Update or insert inventory record
#             existing = self.db.fetchone(
#                 "SELECT inventory_id FROM inventory WHERE product_id = ?",
#                 (product_id,)
#             )
            
#             if existing:
#                 old_inventory = self.db.fetchone(
#                     "SELECT total_qty FROM inventory WHERE product_id = ?",
#                     (product_id,)
#                 )
                
#                 self.db.execute(
#                     """UPDATE inventory 
#                        SET total_qty = ?, unit_cost = ?, 
#                            last_updated = CURRENT_TIMESTAMP
#                        WHERE product_id = ?""",
#                     (total_stock['total_qty'] or 0, 
#                      total_stock['avg_cost'] or 0, product_id)
#                 )
                
#                 # Record inventory history
#                 self.db.execute(
#                     """INSERT INTO inventory_history 
#                        (inventory_id, product_id, old_total_qty, new_total_qty,
#                         change_type, changed_by, remarks)
#                        VALUES (?, ?, ?, ?, 'adjust', ?, 'Updated from stock changes')""",
#                     (existing['inventory_id'], product_id,
#                      old_inventory['total_qty'] if old_inventory else 0,
#                      total_stock['total_qty'] or 0, changed_by)
#                 )
#             else:
#                 cursor = self.db.execute(
#                     """INSERT INTO inventory 
#                        (product_id, total_qty, unit_cost)
#                        VALUES (?, ?, ?)""",
#                     (product_id, total_stock['total_qty'] or 0,
#                      total_stock['avg_cost'] or 0)
#                 )
                
#                 # Record inventory history
#                 self.db.execute(
#                     """INSERT INTO inventory_history 
#                        (inventory_id, product_id, old_total_qty, new_total_qty,
#                         change_type, changed_by, remarks)
#                        VALUES (?, ?, 0, ?, 'add', ?, 'Created from stock')""",
#                     (cursor.lastrowid, product_id, 
#                      total_stock['total_qty'] or 0, changed_by)
#                 )

#     def list_stock(self, location_id=None):
#         """List all stock"""
#         query = """
#         SELECT 
#             st.*,
#             p.product_name,
#             p.product_code,
#             c.category_brand,
#             c.model_name,
#             l.location_name,
#             l.location_type,
#             s.staff_name as manager_name
#         FROM stocks st
#         JOIN products p ON st.product_id = p.product_id
#         JOIN categories c ON p.category_id = c.category_id
#         JOIN locations l ON st.location_id = l.location_id
#         LEFT JOIN staff s ON st.manager_id = s.staff_id
#         WHERE 1=1
#         """
#         params = []
        
#         if location_id:
#             query += " AND st.location_id = ?"
#             params.append(location_id)
        
#         query += " ORDER BY p.product_name"
        
#         return self.db.fetchall(query, params)

#     def get_stock_history(self, stock_id: int):
#         """Get history for a specific stock item"""
#         query = """
#         SELECT 
#             sh.*,
#             s.staff_name as changed_by_name
#         FROM stocks_history sh
#         LEFT JOIN staff s ON sh.changed_by = s.staff_id
#         WHERE sh.stock_id = ?
#         ORDER BY sh.changed_at DESC
#         """
#         return self.db.fetchall(query, (stock_id,))

#     def get_stock_statistics(self):
#         """Get stock statistics"""
#         stats = {}
        
#         # Total stock items
#         total_items = self.db.fetchone("SELECT COUNT(*) as count FROM stocks")
#         stats['total_stock_items'] = total_items['count']
        
#         # Total quantity in stock
#         total_qty = self.db.fetchone("SELECT SUM(qty_stocked) as total FROM stocks")
#         stats['total_quantity'] = total_qty['total'] if total_qty['total'] else 0
        
#         # Total stock value
#         total_value = self.db.fetchone("SELECT SUM(stock_line_amount) as total FROM stocks")
#         stats['total_value'] = total_value['total'] if total_value['total'] else 0
        
#         # Stock by location
#         by_location = self.db.fetchall("""
#             SELECT 
#                 l.location_name,
#                 l.location_type,
#                 COUNT(st.stock_id) as item_count,
#                 SUM(st.qty_stocked) as total_qty,
#                 SUM(st.stock_line_amount) as total_value
#             FROM stocks st
#             JOIN locations l ON st.location_id = l.location_id
#             GROUP BY st.location_id
#             ORDER BY total_value DESC
#         """)
#         stats['by_location'] = [dict(row) for row in by_location]
        
#         # Low stock items
#         low_stock = self.db.fetchall("""
#             SELECT 
#                 st.*,
#                 p.product_name,
#                 l.location_name,
#                 (SELECT total_qty FROM inventory WHERE product_id = st.product_id) as total_inventory
#             FROM stocks st
#             JOIN products p ON st.product_id = p.product_id
#             JOIN locations l ON st.location_id = l.location_id
#             WHERE st.qty_stocked <= 5
#             ORDER BY st.qty_stocked
#             LIMIT 20
#         """)
#         stats['low_stock'] = [dict(row) for row in low_stock]
        
#         return stats

# ---- StockController (fixed) ----
from app.models.stocks import Stock
from app.models.stocks_history import StockHistory

class StockController:
    def __init__(self, db):
        self.db = db

    def add_stock(self, stock: Stock):
        stock.validate()
        with self.db.conn:
            existing = self.db.fetchone("SELECT stock_id, qty_stocked FROM stocks WHERE product_id = ? AND location_id = ?", (stock.product_id, stock.location_id))
            if existing:
                old_qty = existing['qty_stocked']
                new_qty = old_qty + stock.qty_stocked
                self.db.execute("UPDATE stocks SET qty_stocked = ?, unit_cost = ?, manager_id = ?, updated_at=CURRENT_TIMESTAMP WHERE stock_id = ?",
                                (new_qty, stock.unit_cost, stock.manager_id, existing['stock_id']))
                stock_id = existing['stock_id']
            else:
                cur = self.db.execute("INSERT INTO stocks (product_id, location_id, qty_stocked, unit_cost, manager_id) VALUES (?, ?, ?, ?, ?)",
                                      (stock.product_id, stock.location_id, stock.qty_stocked, stock.unit_cost, stock.manager_id))
                stock_id = cur.lastrowid
                old_qty = 0
                new_qty = stock.qty_stocked
            # record history
            self.db.execute("INSERT INTO stocks_history (stock_id, product_id, location_id, old_qty, new_qty, change_type, changed_by, remarks) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                            (stock_id, stock.product_id, stock.location_id, old_qty, new_qty, 'add', stock.manager_id, f"Stock added: {stock.qty_stocked} units"))
            # update inventory using weighted average calculation
            totals = self.db.fetchone("SELECT SUM(qty_stocked) as total_qty, CASE WHEN SUM(qty_stocked)=0 THEN 0 ELSE SUM(qty_stocked*unit_cost)/SUM(qty_stocked) END as weighted_cost FROM stocks WHERE product_id = ?", (stock.product_id,))
            if totals:
                inv = self.db.fetchone("SELECT inventory_id, total_qty FROM inventory WHERE product_id = ?", (stock.product_id,))
                if inv:
                    old_qty_inv = inv['total_qty'] or 0
                    new_qty_inv = totals['total_qty'] or 0
                    self.db.execute("UPDATE inventory SET total_qty = ?, unit_cost = ?, last_updated=CURRENT_TIMESTAMP WHERE product_id = ?", (new_qty_inv, totals['weighted_cost'] or 0, stock.product_id))
                    self.db.execute("INSERT INTO inventory_history (inventory_id, product_id, old_total_qty, new_total_qty, change_type, changed_by, remarks) VALUES (?, ?, ?, ?, 'adjust', ?, ?)",
                                    (inv['inventory_id'], stock.product_id, old_qty_inv, new_qty_inv, stock.manager_id, "Stock update"))
                else:
                    cur2 = self.db.execute("INSERT INTO inventory (product_id, total_qty, unit_cost) VALUES (?, ?, ?)", (stock.product_id, totals['total_qty'] or 0, totals['weighted_cost'] or 0))
                    self.db.execute("INSERT INTO inventory_history (inventory_id, product_id, old_total_qty, new_total_qty, change_type, changed_by, remarks) VALUES (?, ?, 0, ?, 'add', ?, ?)",
                                    (cur2.lastrowid, stock.product_id, totals['total_qty'] or 0, stock.manager_id, "Initial inventory from stock"))
            return stock_id

    def update_stock(self, stock: Stock):
        stock.validate()
        with self.db.conn:
            current = self.db.fetchone("SELECT qty_stocked, unit_cost, product_id, location_id FROM stocks WHERE stock_id = ?", (stock.stock_id,))
            if not current:
                raise ValueError("Stock record not found")
            self.db.execute("UPDATE stocks SET qty_stocked = ?, unit_cost = ?, manager_id = ?, updated_at=CURRENT_TIMESTAMP WHERE stock_id = ?", (stock.qty_stocked, stock.unit_cost, stock.manager_id, stock.stock_id))
            self.db.execute("INSERT INTO stocks_history (stock_id, product_id, location_id, old_qty, new_qty, change_type, changed_by, remarks) VALUES (?, ?, ?, ?, ?, 'adjust', ?, ?)",
                            (stock.stock_id, stock.product_id, stock.location_id, current['qty_stocked'], stock.qty_stocked, stock.manager_id, "Stock adjusted"))
            # Update inventory similarly (weighted)
            totals = self.db.fetchone("SELECT SUM(qty_stocked) as total_qty, CASE WHEN SUM(qty_stocked)=0 THEN 0 ELSE SUM(qty_stocked*unit_cost)/SUM(qty_stocked) END as weighted_cost FROM stocks WHERE product_id = ?", (stock.product_id,))
            if totals:
                inv = self.db.fetchone("SELECT inventory_id, total_qty FROM inventory WHERE product_id = ?", (stock.product_id,))
                if inv:
                    old_qty_inv = inv['total_qty'] or 0
                    self.db.execute("UPDATE inventory SET total_qty=?, unit_cost=?, last_updated=CURRENT_TIMESTAMP WHERE product_id = ?", (totals['total_qty'] or 0, totals['weighted_cost'] or 0, stock.product_id))
                    self.db.execute("INSERT INTO inventory_history (inventory_id, product_id, old_total_qty, new_total_qty, change_type, changed_by, remarks) VALUES (?, ?, ?, ?, 'adjust', ?, ?)",
                                    (inv['inventory_id'], stock.product_id, old_qty_inv, totals['total_qty'] or 0, stock.manager_id, "Stock update"))
                else:
                    cur3 = self.db.execute("INSERT INTO inventory (product_id, total_qty, unit_cost) VALUES (?, ?, ?)", (stock.product_id, totals['total_qty'] or 0, totals['weighted_cost'] or 0))
                    self.db.execute("INSERT INTO inventory_history (inventory_id, product_id, old_total_qty, new_total_qty, change_type, changed_by, remarks) VALUES (?, ?, 0, ?, 'add', ?, ?)",
                                    (cur3.lastrowid, stock.product_id, totals['total_qty'] or 0, stock.manager_id, "Initial inventory"))

    def remove_stock(self, stock_id: int, quantity: int, manager_id: int, remarks: str = None):
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        with self.db.conn:
            current = self.db.fetchone("SELECT qty_stocked, product_id, location_id FROM stocks WHERE stock_id = ?", (stock_id,))
            if not current:
                raise ValueError("Stock record not found")
            if current['qty_stocked'] < quantity:
                raise ValueError("Insufficient stock to remove")
            new_qty = current['qty_stocked'] - quantity
            self.db.execute("UPDATE stocks SET qty_stocked = ?, updated_at=CURRENT_TIMESTAMP WHERE stock_id = ?", (new_qty, stock_id))
            self.db.execute("INSERT INTO stocks_history (stock_id, product_id, location_id, old_qty, new_qty, change_type, changed_by, remarks) VALUES (?, ?, ?, ?, ?, 'remove', ?, ?)",
                            (stock_id, current['product_id'], current['location_id'], current['qty_stocked'], new_qty, manager_id, remarks or f"Stock removed: {quantity} units"))
            # Update inventory
            totals = self.db.fetchone("SELECT SUM(qty_stocked) as total_qty, CASE WHEN SUM(qty_stocked)=0 THEN 0 ELSE SUM(qty_stocked*unit_cost)/SUM(qty_stocked) END as weighted_cost FROM stocks WHERE product_id = ?", (current['product_id'],))
            if totals:
                inv = self.db.fetchone("SELECT inventory_id, total_qty FROM inventory WHERE product_id = ?", (current['product_id'],))
                if inv:
                    old_qty_inv = inv['total_qty'] or 0
                    new_qty_inv = totals['total_qty'] or 0
                    self.db.execute("UPDATE inventory SET total_qty=?, unit_cost=?, last_updated=CURRENT_TIMESTAMP WHERE product_id = ?", (new_qty_inv, totals['weighted_cost'] or 0, current['product_id']))
                    self.db.execute("INSERT INTO inventory_history (inventory_id, product_id, old_total_qty, new_total_qty, change_type, changed_by, remarks) VALUES (?, ?, ?, ?, 'remove', ?, ?)",
                                    (inv['inventory_id'], current['product_id'], old_qty_inv, new_qty_inv, manager_id, remarks or "Stock removal"))

    def list_stock(self, location_id=None):
        q = """
        SELECT st.*, p.product_name, c.category_brand, c.model_name, l.location_name, l.location_type, s.staff_name as manager_name
        FROM stocks st
        JOIN products p ON st.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        JOIN locations l ON st.location_id = l.location_id
        LEFT JOIN staff s ON st.manager_id = s.staff_id
        WHERE 1=1
        """
        params = []
        if location_id:
            q += " AND st.location_id = ?"; params.append(location_id)
        q += " ORDER BY p.product_name"
        return self.db.fetchall(q, params)

    def get_stock_history(self, stock_id: int):
        q = """
        SELECT sh.*, s.staff_name as changed_by_name
        FROM stocks_history sh
        LEFT JOIN staff s ON sh.changed_by = s.staff_id
        WHERE sh.stock_id = ?
        ORDER BY sh.changed_at DESC
        """
        return self.db.fetchall(q, (stock_id,))

    def get_stock_statistics(self):
        stats = {}
        total_items = self.db.fetchone("SELECT COUNT(*) as count FROM stocks")
        stats['total_stock_items'] = total_items['count'] if total_items else 0
        total_qty = self.db.fetchone("SELECT SUM(qty_stocked) as total FROM stocks")
        stats['total_quantity'] = total_qty['total'] if total_qty and total_qty['total'] else 0
        total_value = self.db.fetchone("SELECT SUM(qty_stocked*unit_cost) as total FROM stocks")
        stats['total_value'] = total_value['total'] if total_value and total_value['total'] else 0
        by_location = self.db.fetchall("""SELECT l.location_name, l.location_type, COUNT(st.stock_id) as item_count, SUM(st.qty_stocked) as total_qty, SUM(st.qty_stocked*st.unit_cost) as total_value FROM stocks st JOIN locations l ON st.location_id = l.location_id GROUP BY st.location_id ORDER BY total_value DESC""")
        stats['by_location'] = [dict(r) for r in by_location]
        low_stock = self.db.fetchall("""SELECT st.*, p.product_name, l.location_name, (SELECT total_qty FROM inventory WHERE product_id = st.product_id) as total_inventory FROM stocks st JOIN products p ON st.product_id = p.product_id JOIN locations l ON st.location_id = l.location_id WHERE st.qty_stocked <= 5 ORDER BY st.qty_stocked LIMIT 20""")
        stats['low_stock'] = [dict(r) for r in low_stock]
        return stats