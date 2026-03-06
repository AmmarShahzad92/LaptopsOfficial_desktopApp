# from app.models.stock_movement_records import StockMovementRecord
# from app.models.stock_movement_history import StockMovementHistory
# from datetime import datetime

# class StockMovementController:
#     def __init__(self, db):
#         self.db = db

#     def create_movement(self, movement: StockMovementRecord):
#         """Create a stock movement record"""
#         try:
#             movement.validate()
            
#             # Check if source has enough stock
#             source_stock = self.db.fetchone(
#                 """SELECT qty_stocked 
#                    FROM stocks 
#                    WHERE product_id = ? AND location_id = ?""",
#                 (movement.product_id, movement.from_location_id)
#             )
            
#             if not source_stock or source_stock['qty_stocked'] < movement.quantity_moved:
#                 raise ValueError("Insufficient stock at source location")
            
#             with self.db.conn:
#                 # Insert movement record
#                 cursor = self.db.execute(
#                     """INSERT INTO stock_movement_records 
#                        (product_id, from_location_id, to_location_id,
#                         quantity_moved, unit_cost, approved_by, remarks)
#                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
#                     (movement.product_id, movement.from_location_id,
#                      movement.to_location_id, movement.quantity_moved,
#                      movement.unit_cost, movement.approved_by,
#                      movement.remarks)
#                 )
#                 smr_id = cursor.lastrowid
                
#                 # Process the movement
#                 self._process_movement(smr_id, movement)
                
#                 return smr_id
#         except Exception as e:
#             raise e

#     def _process_movement(self, smr_id: int, movement: StockMovementRecord):
#         """Process the stock movement"""
#         # Remove from source location
#         source_stock = self.db.fetchone(
#             """SELECT stock_id, qty_stocked 
#                FROM stocks 
#                WHERE product_id = ? AND location_id = ?""",
#             (movement.product_id, movement.from_location_id)
#         )
        
#         if source_stock:
#             new_source_qty = source_stock['qty_stocked'] - movement.quantity_moved
            
#             self.db.execute(
#                 """UPDATE stocks 
#                    SET qty_stocked = ?, updated_at = CURRENT_TIMESTAMP
#                    WHERE stock_id = ?""",
#                 (new_source_qty, source_stock['stock_id'])
#             )
            
#             # Record stock history for source
#             self.db.execute(
#                 """INSERT INTO stocks_history 
#                    (stock_id, product_id, location_id, old_qty, new_qty,
#                     change_type, changed_by, remarks)
#                    VALUES (?, ?, ?, ?, ?, 'remove', ?, ?)""",
#                 (source_stock['stock_id'], movement.product_id,
#                  movement.from_location_id, source_stock['qty_stocked'],
#                  new_source_qty, movement.approved_by,
#                  f"Stock movement to location {movement.to_location_id}")
#             )
        
#         # Add to destination location
#         dest_stock = self.db.fetchone(
#             """SELECT stock_id, qty_stocked 
#                FROM stocks 
#                WHERE product_id = ? AND location_id = ?""",
#             (movement.product_id, movement.to_location_id)
#         )
        
#         if dest_stock:
#             new_dest_qty = dest_stock['qty_stocked'] + movement.quantity_moved
            
#             self.db.execute(
#                 """UPDATE stocks 
#                    SET qty_stocked = ?, unit_cost = ?, updated_at = CURRENT_TIMESTAMP
#                    WHERE stock_id = ?""",
#                 (new_dest_qty, movement.unit_cost, dest_stock['stock_id'])
#             )
            
#             # Record stock history for destination
#             self.db.execute(
#                 """INSERT INTO stocks_history 
#                    (stock_id, product_id, location_id, old_qty, new_qty,
#                     change_type, changed_by, remarks)
#                    VALUES (?, ?, ?, ?, ?, 'add', ?, ?)""",
#                 (dest_stock['stock_id'], movement.product_id,
#                  movement.to_location_id, dest_stock['qty_stocked'],
#                  new_dest_qty, movement.approved_by,
#                  f"Stock movement from location {movement.from_location_id}")
#             )
#         else:
#             # Create new stock record at destination
#             cursor = self.db.execute(
#                 """INSERT INTO stocks 
#                    (product_id, location_id, qty_stocked, unit_cost)
#                    VALUES (?, ?, ?, ?)""",
#                 (movement.product_id, movement.to_location_id,
#                  movement.quantity_moved, movement.unit_cost)
#             )
#             dest_stock_id = cursor.lastrowid
            
#             # Record stock history for destination
#             self.db.execute(
#                 """INSERT INTO stocks_history 
#                    (stock_id, product_id, location_id, old_qty, new_qty,
#                     change_type, changed_by, remarks)
#                    VALUES (?, ?, ?, 0, ?, 'add', ?, ?)""",
#                 (dest_stock_id, movement.product_id,
#                  movement.to_location_id, movement.quantity_moved,
#                  movement.approved_by,
#                  f"Stock movement from location {movement.from_location_id}")
#             )
        
#         # Update inventory
#         self._update_inventory_from_movement(movement)
        
#         # Record movement history
#         self._record_movement_history(smr_id, movement)

#     def _update_inventory_from_movement(self, movement: StockMovementRecord):
#         """Update inventory after movement (total quantity unchanged)"""
#         # Update inventory last_updated timestamp
#         self.db.execute(
#             """UPDATE inventory 
#                SET last_updated = CURRENT_TIMESTAMP
#                WHERE product_id = ?""",
#             (movement.product_id,)
#         )
        
#         # Record inventory history
#         inventory = self.db.fetchone(
#             "SELECT inventory_id, total_qty FROM inventory WHERE product_id = ?",
#             (movement.product_id,)
#         )
        
#         if inventory:
#             self.db.execute(
#                 """INSERT INTO inventory_history 
#                    (inventory_id, product_id, old_total_qty, new_total_qty,
#                     change_type, changed_by, remarks)
#                    VALUES (?, ?, ?, ?, 'adjust', ?, 'Stock movement between locations')""",
#                 (inventory['inventory_id'], movement.product_id,
#                  inventory['total_qty'], inventory['total_qty'],
#                  movement.approved_by)
#             )

#     def _record_movement_history(self, smr_id: int, movement: StockMovementRecord):
#         """Record movement history"""
#         # Since quantity doesn't change in inventory for movements,
#         # we record the movement itself
#         self.db.execute(
#             """INSERT INTO stock_movement_history 
#                (smr_id, product_id, from_location_id, to_location_id,
#                 old_quantity, new_quantity, change_type, changed_by, remarks)
#                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
#             (smr_id, movement.product_id, movement.from_location_id,
#              movement.to_location_id, movement.quantity_moved,
#              movement.quantity_moved, 'move', movement.approved_by,
#              movement.remarks)
#         )

#     def list_movements(self, product_id=None, start_date=None, end_date=None):
#         """List stock movements with filters"""
#         query = """
#         SELECT 
#             smr.*,
#             p.product_name,
#             p.product_code,
#             cat.category_brand,
#             cat.model_name,
#             from_loc.location_name as from_location_name,
#             to_loc.location_name as to_location_name,
#             s.staff_name as approved_by_name
#         FROM stock_movement_records smr
#         JOIN products p ON smr.product_id = p.product_id
#         JOIN categories cat ON p.category_id = cat.category_id
#         JOIN locations from_loc ON smr.from_location_id = from_loc.location_id
#         JOIN locations to_loc ON smr.to_location_id = to_loc.location_id
#         JOIN staff s ON smr.approved_by = s.staff_id
#         WHERE 1=1
#         """
#         params = []
        
#         if product_id:
#             query += " AND smr.product_id = ?"
#             params.append(product_id)
        
#         if start_date:
#             query += " AND DATE(smr.movement_date) >= ?"
#             params.append(start_date)
        
#         if end_date:
#             query += " AND DATE(smr.movement_date) <= ?"
#             params.append(end_date)
        
#         query += " ORDER BY smr.movement_date DESC"
        
#         return self.db.fetchall(query, params)

#     def get_movement_history(self, smr_id: int):
#         """Get history for a specific movement"""
#         query = """
#         SELECT 
#             smh.*,
#             s.staff_name as changed_by_name
#         FROM stock_movement_history smh
#         LEFT JOIN staff s ON smh.changed_by = s.staff_id
#         WHERE smh.smr_id = ?
#         ORDER BY smh.changed_at DESC
#         """
#         return self.db.fetchall(query, (smr_id,))

#     def get_movement_statistics(self):
#         """Get movement statistics"""
#         stats = {}
        
#         # Total movements
#         total_movements = self.db.fetchone("SELECT COUNT(*) as count FROM stock_movement_records")
#         stats['total_movements'] = total_movements['count']
        
#         # Total quantity moved
#         total_qty = self.db.fetchone("SELECT SUM(quantity_moved) as total FROM stock_movement_records")
#         stats['total_quantity_moved'] = total_qty['total'] if total_qty['total'] else 0
        
#         # Movements by location
#         from_location = self.db.fetchall("""
#             SELECT 
#                 l.location_name,
#                 COUNT(smr.smr_id) as movement_count,
#                 SUM(smr.quantity_moved) as total_qty,
#                 SUM(smr.movement_amount) as total_value
#             FROM stock_movement_records smr
#             JOIN locations l ON smr.from_location_id = l.location_id
#             GROUP BY smr.from_location_id
#             ORDER BY movement_count DESC
#         """)
#         stats['from_location'] = [dict(row) for row in from_location]
        
#         to_location = self.db.fetchall("""
#             SELECT 
#                 l.location_name,
#                 COUNT(smr.smr_id) as movement_count,
#                 SUM(smr.quantity_moved) as total_qty,
#                 SUM(smr.movement_amount) as total_value
#             FROM stock_movement_records smr
#             JOIN locations l ON smr.to_location_id = l.location_id
#             GROUP BY smr.to_location_id
#             ORDER BY movement_count DESC
#         """)
#         stats['to_location'] = [dict(row) for row in to_location]
        
#         # Monthly movement trend (last 6 months)
#         monthly_trend = self.db.fetchall("""
#             SELECT 
#                 strftime('%Y-%m', movement_date) as month,
#                 COUNT(*) as movement_count,
#                 SUM(quantity_moved) as monthly_qty,
#                 SUM(movement_amount) as monthly_value
#             FROM stock_movement_records
#             WHERE movement_date >= DATE('now', '-6 months')
#             GROUP BY strftime('%Y-%m', movement_date)
#             ORDER BY month
#         """)
#         stats['monthly_trend'] = [dict(row) for row in monthly_trend]
        
#         # Top products moved
#         top_products = self.db.fetchall("""
#             SELECT 
#                 p.product_name,
#                 p.product_code,
#                 cat.category_brand,
#                 cat.model_name,
#                 COUNT(smr.smr_id) as movement_count,
#                 SUM(smr.quantity_moved) as total_qty,
#                 SUM(smr.movement_amount) as total_value
#             FROM stock_movement_records smr
#             JOIN products p ON smr.product_id = p.product_id
#             JOIN categories cat ON p.category_id = cat.category_id
#             GROUP BY smr.product_id
#             ORDER BY total_qty DESC
#             LIMIT 10
#         """)
#         stats['top_products'] = [dict(row) for row in top_products]
        
#         return stats


# ---- StockMovementController (aligned) ----
from app.models.stock_movement_records import StockMovementRecord
from datetime import datetime

class StockMovementController:
    def __init__(self, db):
        self.db = db

    def create_movement(self, movement: StockMovementRecord):
        movement.validate()
        source_stock = self.db.fetchone("SELECT qty_stocked FROM stocks WHERE product_id = ? AND location_id = ?", (movement.product_id, movement.from_location_id))
        if not source_stock or source_stock['qty_stocked'] < movement.quantity_moved:
            raise ValueError("Insufficient stock at source location")
        with self.db.conn:
            cur = self.db.execute("""INSERT INTO stock_movement_records (product_id, from_location_id, to_location_id, quantity_moved, unit_cost, approved_by, movement_date, remarks) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                  (movement.product_id, movement.from_location_id, movement.to_location_id, movement.quantity_moved, movement.unit_cost, movement.approved_by, movement.movement_date or datetime.now().isoformat(), movement.remarks))
            smr_id = cur.lastrowid
            # Process: remove from source
            src = self.db.fetchone("SELECT stock_id, qty_stocked FROM stocks WHERE product_id = ? AND location_id = ?", (movement.product_id, movement.from_location_id))
            if src:
                new_src_qty = src['qty_stocked'] - movement.quantity_moved
                self.db.execute("UPDATE stocks SET qty_stocked=?, updated_at=CURRENT_TIMESTAMP WHERE stock_id = ?", (new_src_qty, src['stock_id']))
                self.db.execute("INSERT INTO stocks_history (stock_id, product_id, location_id, old_qty, new_qty, change_type, changed_by, remarks) VALUES (?, ?, ?, ?, ?, 'remove', ?, ?)",
                                (src['stock_id'], movement.product_id, movement.from_location_id, src['qty_stocked'], new_src_qty, movement.approved_by, f"Stock movement to location {movement.to_location_id}"))
            # Add to dest
            dest = self.db.fetchone("SELECT stock_id, qty_stocked FROM stocks WHERE product_id = ? AND location_id = ?", (movement.product_id, movement.to_location_id))
            if dest:
                new_dest_qty = dest['qty_stocked'] + movement.quantity_moved
                self.db.execute("UPDATE stocks SET qty_stocked=?, unit_cost=?, updated_at=CURRENT_TIMESTAMP WHERE stock_id = ?", (new_dest_qty, movement.unit_cost, dest['stock_id']))
                self.db.execute("INSERT INTO stocks_history (stock_id, product_id, location_id, old_qty, new_qty, change_type, changed_by, remarks) VALUES (?, ?, ?, ?, ?, 'add', ?, ?)",
                                (dest['stock_id'], movement.product_id, movement.to_location_id, dest['qty_stocked'], new_dest_qty, movement.approved_by, f"Stock movement from location {movement.from_location_id}"))
            else:
                cur2 = self.db.execute("INSERT INTO stocks (product_id, location_id, qty_stocked, unit_cost) VALUES (?, ?, ?, ?)",
                                       (movement.product_id, movement.to_location_id, movement.quantity_moved, movement.unit_cost))
                dest_stock_id = cur2.lastrowid
                self.db.execute("INSERT INTO stocks_history (stock_id, product_id, location_id, old_qty, new_qty, change_type, changed_by, remarks) VALUES (?, ?, ?, 0, ?, 'add', ?, ?)",
                                (dest_stock_id, movement.product_id, movement.to_location_id, movement.quantity_moved, movement.approved_by, f"Stock movement from location {movement.from_location_id}"))
            # Update inventory last_updated and add history entry (quantity unchanged)
            inv = self.db.fetchone("SELECT inventory_id, total_qty FROM inventory WHERE product_id = ?", (movement.product_id,))
            if inv:
                self.db.execute("UPDATE inventory SET last_updated=CURRENT_TIMESTAMP WHERE product_id = ?", (movement.product_id,))
                self.db.execute("INSERT INTO inventory_history (inventory_id, product_id, old_total_qty, new_total_qty, change_type, changed_by, remarks) VALUES (?, ?, ?, ?, 'adjust', ?, 'Stock movement between locations')",
                                (inv['inventory_id'], movement.product_id, inv['total_qty'], inv['total_qty'], movement.approved_by))
            # Record movement history
            self.db.execute("INSERT INTO stock_movement_history (smr_id, product_id, from_location_id, to_location_id, old_quantity, new_quantity, change_type, changed_by, remarks) VALUES (?, ?, ?, ?, ?, ?, 'move', ?, ?)",
                            (smr_id, movement.product_id, movement.from_location_id, movement.to_location_id, movement.quantity_moved, movement.quantity_moved, movement.approved_by, movement.remarks))
            return smr_id

    def list_movements(self, product_id=None, start_date=None, end_date=None):
        q = """
        SELECT smr.*, p.product_name, cat.category_brand, cat.model_name, from_loc.location_name as from_location_name, to_loc.location_name as to_location_name, s.staff_name as approved_by_name
        FROM stock_movement_records smr
        JOIN products p ON smr.product_id = p.product_id
        JOIN categories cat ON p.category_id = cat.category_id
        JOIN locations from_loc ON smr.from_location_id = from_loc.location_id
        JOIN locations to_loc ON smr.to_location_id = to_loc.location_id
        JOIN staff s ON smr.approved_by = s.staff_id
        WHERE 1=1
        """
        params = []
        if product_id:
            q += " AND smr.product_id = ?"; params.append(product_id)
        if start_date:
            q += " AND DATE(smr.movement_date) >= ?"; params.append(start_date)
        if end_date:
            q += " AND DATE(smr.movement_date) <= ?"; params.append(end_date)
        q += " ORDER BY smr.movement_date DESC"
        return self.db.fetchall(q, params)

    def get_movement_history(self, smr_id: int):
        q = "SELECT smh.*, s.staff_name as changed_by_name FROM stock_movement_history smh LEFT JOIN staff s ON smh.changed_by = s.staff_id WHERE smh.smr_id = ? ORDER BY smh.changed_at DESC"
        return self.db.fetchall(q, (smr_id,))

    def get_movement_statistics(self):
        stats = {}
        total_movements = self.db.fetchone("SELECT COUNT(*) as count FROM stock_movement_records")
        stats['total_movements'] = total_movements['count'] if total_movements else 0
        total_qty = self.db.fetchone("SELECT SUM(quantity_moved) as total FROM stock_movement_records")
        stats['total_quantity_moved'] = total_qty['total'] if total_qty and total_qty['total'] else 0
        from_location = self.db.fetchall("SELECT l.location_name, COUNT(smr.smr_id) as movement_count, SUM(smr.quantity_moved) as total_qty, SUM(smr.quantity_moved * smr.unit_cost) as total_value FROM stock_movement_records smr JOIN locations l ON smr.from_location_id = l.location_id GROUP BY smr.from_location_id ORDER BY movement_count DESC")
        stats['from_location'] = [dict(r) for r in from_location]
        to_location = self.db.fetchall("SELECT l.location_name, COUNT(smr.smr_id) as movement_count, SUM(smr.quantity_moved) as total_qty, SUM(smr.quantity_moved * smr.unit_cost) as total_value FROM stock_movement_records smr JOIN locations l ON smr.to_location_id = l.location_id GROUP BY smr.to_location_id ORDER BY movement_count DESC")
        stats['to_location'] = [dict(r) for r in to_location]
        monthly_trend = self.db.fetchall("SELECT strftime('%Y-%m', movement_date) as month, COUNT(*) as movement_count, SUM(quantity_moved) as monthly_qty, SUM(quantity_moved*unit_cost) as monthly_value FROM stock_movement_records WHERE movement_date >= DATE('now', '-6 months') GROUP BY strftime('%Y-%m', movement_date) ORDER BY month")
        stats['monthly_trend'] = [dict(r) for r in monthly_trend]
        top_products = self.db.fetchall("SELECT p.product_name, cat.category_brand, cat.model_name, COUNT(smr.smr_id) as movement_count, SUM(smr.quantity_moved) as total_qty, SUM(smr.quantity_moved*smr.unit_cost) as total_value FROM stock_movement_records smr JOIN products p ON smr.product_id = p.product_id JOIN categories cat ON p.category_id = cat.category_id GROUP BY smr.product_id ORDER BY total_qty DESC LIMIT 10")
        stats['top_products'] = [dict(r) for r in top_products]
        return stats

