# class InventoryController:
#     def __init__(self, db):
#         self.db = db

#     def get_inventory(self, product_id=None):
#         """Get inventory information"""
#         query = """
#         SELECT 
#             i.*,
#             p.product_name,
#             p.product_code,
#             p.cost_price,
#             p.wholesale_price,
#             p.sale_price,
#             cat.category_brand,
#             cat.model_name,
#             s.supplier_name,
#             (SELECT COUNT(*) FROM stocks WHERE product_id = i.product_id) as location_count,
#             (SELECT GROUP_CONCAT(l.location_name || ': ' || st.qty_stocked) 
#              FROM stocks st 
#              JOIN locations l ON st.location_id = l.location_id
#              WHERE st.product_id = i.product_id) as stock_details
#         FROM inventory i
#         JOIN products p ON i.product_id = p.product_id
#         JOIN categories cat ON p.category_id = cat.category_id
#         JOIN suppliers s ON p.supplier_id = s.supplier_id
#         WHERE p.is_active = 1
#         """
#         params = []
        
#         if product_id:
#             query += " AND i.product_id = ?"
#             params.append(product_id)
        
#         query += " ORDER BY p.product_name"
        
#         return self.db.fetchall(query, params)

#     def get_inventory_history(self, inventory_id: int):
#         """Get history for a specific inventory item"""
#         query = """
#         SELECT 
#             ih.*,
#             s.staff_name as changed_by_name
#         FROM inventory_history ih
#         LEFT JOIN staff s ON ih.changed_by = s.staff_id
#         WHERE ih.inventory_id = ?
#         ORDER BY ih.changed_at DESC
#         """
#         return self.db.fetchall(query, (inventory_id,))

#     def get_inventory_statistics(self):
#         """Get inventory statistics"""
#         stats = {}
        
#         # Total inventory items
#         total_items = self.db.fetchone("SELECT COUNT(*) as count FROM inventory")
#         stats['total_items'] = total_items['count']
        
#         # Total quantity in inventory
#         total_qty = self.db.fetchone("SELECT SUM(total_qty) as total FROM inventory")
#         stats['total_quantity'] = total_qty['total'] if total_qty['total'] else 0
        
#         # Total inventory value
#         total_value = self.db.fetchone("SELECT SUM(inventory_amount) as total FROM inventory")
#         stats['total_value'] = total_value['total'] if total_value['total'] else 0
        
#         # Inventory by category
#         by_category = self.db.fetchall("""
#             SELECT 
#                 cat.category_brand,
#                 cat.model_name,
#                 COUNT(i.inventory_id) as item_count,
#                 SUM(i.total_qty) as total_qty,
#                 SUM(i.inventory_amount) as total_value
#             FROM inventory i
#             JOIN products p ON i.product_id = p.product_id
#             JOIN categories cat ON p.category_id = cat.category_id
#             WHERE p.is_active = 1
#             GROUP BY p.category_id
#             ORDER BY total_value DESC
#         """)
#         stats['by_category'] = [dict(row) for row in by_category]
        
#         # Inventory by supplier
#         by_supplier = self.db.fetchall("""
#             SELECT 
#                 s.supplier_name,
#                 COUNT(i.inventory_id) as item_count,
#                 SUM(i.total_qty) as total_qty,
#                 SUM(i.inventory_amount) as total_value
#             FROM inventory i
#             JOIN products p ON i.product_id = p.product_id
#             JOIN suppliers s ON p.supplier_id = s.supplier_id
#             WHERE p.is_active = 1
#             GROUP BY p.supplier_id
#             ORDER BY total_value DESC
#         """)
#         stats['by_supplier'] = [dict(row) for row in by_supplier]
        
#         # Low inventory items (below 5)
#         low_inventory = self.db.fetchall("""
#             SELECT 
#                 i.*,
#                 p.product_name,
#                 p.product_code,
#                 cat.category_brand,
#                 cat.model_name
#             FROM inventory i
#             JOIN products p ON i.product_id = p.product_id
#             JOIN categories cat ON p.category_id = cat.category_id
#             WHERE p.is_active = 1 AND i.total_qty <= 5
#             ORDER BY i.total_qty
#             LIMIT 20
#         """)
#         stats['low_inventory'] = [dict(row) for row in low_inventory]
        
#         # High inventory items (above 50)
#         high_inventory = self.db.fetchall("""
#             SELECT 
#                 i.*,
#                 p.product_name,
#                 p.product_code,
#                 cat.category_brand,
#                 cat.model_name
#             FROM inventory i
#             JOIN products p ON i.product_id = p.product_id
#             JOIN categories cat ON p.category_id = cat.category_id
#             WHERE p.is_active = 1 AND i.total_qty >= 50
#             ORDER BY i.total_qty DESC
#             LIMIT 20
#         """)
#         stats['high_inventory'] = [dict(row) for row in high_inventory]
        
#         # Inventory value distribution
#         value_distribution = self.db.fetchall("""
#             SELECT 
#                 CASE 
#                     WHEN inventory_amount < 1000 THEN 'Under $1000'
#                     WHEN inventory_amount < 5000 THEN '$1000-$5000'
#                     WHEN inventory_amount < 10000 THEN '$5000-$10000'
#                     WHEN inventory_amount < 50000 THEN '$10000-$50000'
#                     ELSE 'Over $50000'
#                 END as value_range,
#                 COUNT(*) as item_count,
#                 SUM(inventory_amount) as total_value
#             FROM inventory
#             GROUP BY value_range
#             ORDER BY total_value DESC
#         """)
#         stats['value_distribution'] = [dict(row) for row in value_distribution]
        
#         return stats

#     def get_inventory_report(self, min_qty=None, max_qty=None, 
#                            min_value=None, max_value=None):
#         """Generate inventory report with filters"""
#         query = """
#         SELECT 
#             i.*,
#             p.product_name,
#             p.product_code,
#             p.cost_price,
#             p.wholesale_price,
#             p.sale_price,
#             cat.category_brand,
#             cat.model_name,
#             s.supplier_name
#         FROM inventory i
#         JOIN products p ON i.product_id = p.product_id
#         JOIN categories cat ON p.category_id = cat.category_id
#         JOIN suppliers s ON p.supplier_id = s.supplier_id
#         WHERE p.is_active = 1
#         """
#         params = []
        
#         if min_qty is not None:
#             query += " AND i.total_qty >= ?"
#             params.append(min_qty)
        
#         if max_qty is not None:
#             query += " AND i.total_qty <= ?"
#             params.append(max_qty)
        
#         if min_value is not None:
#             query += " AND i.inventory_amount >= ?"
#             params.append(min_value)
        
#         if max_value is not None:
#             query += " AND i.inventory_amount <= ?"
#             params.append(max_value)
        
#         query += " ORDER BY i.inventory_amount DESC"
        
#         return self.db.fetchall(query, params)

# ---- InventoryController ----
class InventoryController:
    def __init__(self, db):
        self.db = db

    def get_inventory(self, product_id=None):
        q = """
        SELECT i.*, p.product_name, p.cost_price, p.wholesale_price, p.sale_price,
               c.category_brand, c.model_name, s.supplier_name,
               (SELECT COUNT(*) FROM stocks WHERE product_id = i.product_id) as location_count,
               (SELECT GROUP_CONCAT(l.location_name || ': ' || st.qty_stocked)
                FROM stocks st JOIN locations l ON st.location_id = l.location_id
                WHERE st.product_id = i.product_id) as stock_details
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        WHERE p.is_active = 1
        """
        params = []
        if product_id:
            q += " AND i.product_id = ?"
            params.append(product_id)
        q += " ORDER BY p.product_name"
        return self.db.fetchall(q, params)

    def get_inventory_history(self, inventory_id: int):
        q = """
        SELECT ih.*, s.staff_name as changed_by_name
        FROM inventory_history ih
        LEFT JOIN staff s ON ih.changed_by = s.staff_id
        WHERE ih.inventory_id = ?
        ORDER BY ih.changed_at DESC
        """
        return self.db.fetchall(q, (inventory_id,))

    def get_inventory_statistics(self):
        stats = {}
        total_items = self.db.fetchone("SELECT COUNT(*) as count FROM inventory")
        stats['total_items'] = total_items['count'] if total_items else 0
        total_qty = self.db.fetchone("SELECT SUM(total_qty) as total FROM inventory")
        stats['total_quantity'] = total_qty['total'] if total_qty and total_qty['total'] else 0
        total_value = self.db.fetchone("SELECT SUM(inventory_amount) as total FROM inventory")
        stats['total_value'] = total_value['total'] if total_value and total_value['total'] else 0
        by_category = self.db.fetchall("""
            SELECT cat.category_brand, cat.model_name, COUNT(i.inventory_id) as item_count,
                   SUM(i.total_qty) as total_qty, SUM(i.inventory_amount) as total_value
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            JOIN categories cat ON p.category_id = cat.category_id
            WHERE p.is_active = 1
            GROUP BY p.category_id ORDER BY total_value DESC
        """)
        stats['by_category'] = [dict(r) for r in by_category]
        by_supplier = self.db.fetchall("""
            SELECT s.supplier_name, COUNT(i.inventory_id) as item_count,
                   SUM(i.total_qty) as total_qty, SUM(i.inventory_amount) as total_value
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            JOIN suppliers s ON p.supplier_id = s.supplier_id
            WHERE p.is_active = 1
            GROUP BY p.supplier_id ORDER BY total_value DESC
        """)
        stats['by_supplier'] = [dict(r) for r in by_supplier]
        low_inventory = self.db.fetchall("""
            SELECT i.*, p.product_name, cat.category_brand, cat.model_name
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            JOIN categories cat ON p.category_id = cat.category_id
            WHERE p.is_active = 1 AND i.total_qty <= 5
            ORDER BY i.total_qty LIMIT 20
        """)
        stats['low_inventory'] = [dict(r) for r in low_inventory]
        high_inventory = self.db.fetchall("""
            SELECT i.*, p.product_name, cat.category_brand, cat.model_name
            FROM inventory i
            JOIN products p ON i.product_id = p.product_id
            JOIN categories cat ON p.category_id = cat.category_id
            WHERE p.is_active = 1 AND i.total_qty >= 50
            ORDER BY i.total_qty DESC LIMIT 20
        """)
        stats['high_inventory'] = [dict(r) for r in high_inventory]
        value_distribution = self.db.fetchall("""
            SELECT CASE WHEN inventory_amount < 1000 THEN 'Under $1000'
                        WHEN inventory_amount < 5000 THEN '$1000-$5000'
                        WHEN inventory_amount < 10000 THEN '$5000-$10000'
                        WHEN inventory_amount < 50000 THEN '$10000-$50000'
                        ELSE 'Over $50000' END as value_range,
                   COUNT(*) as item_count, SUM(inventory_amount) as total_value
            FROM inventory GROUP BY value_range ORDER BY total_value DESC
        """)
        stats['value_distribution'] = [dict(r) for r in value_distribution]
        return stats

    def get_inventory_report(self, min_qty=None, max_qty=None, min_value=None, max_value=None):
        q = """
        SELECT i.*, p.product_name, p.cost_price, p.wholesale_price, p.sale_price,
               c.category_brand, c.model_name, s.supplier_name
        FROM inventory i
        JOIN products p ON i.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        WHERE p.is_active = 1
        """
        params = []
        if min_qty is not None:
            q += " AND i.total_qty >= ?"; params.append(min_qty)
        if max_qty is not None:
            q += " AND i.total_qty <= ?"; params.append(max_qty)
        if min_value is not None:
            q += " AND i.inventory_amount >= ?"; params.append(min_value)
        if max_value is not None:
            q += " AND i.inventory_amount <= ?"; params.append(max_value)
        q += " ORDER BY i.inventory_amount DESC"
        return self.db.fetchall(q, params)

