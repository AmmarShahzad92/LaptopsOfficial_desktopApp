# class HistoryController:
#     def __init__(self, db):
#         self.db = db
    
#     def get_product_history(self, product_id: str = None, limit: int = 100):
#         """Get product price change history"""
#         query = """
#         SELECT ph.*, s.staff_name as changed_by_name
#         FROM products_history ph
#         LEFT JOIN staff s ON ph.changed_by = s.staff_id
#         WHERE 1=1
#         """
#         params = []
        
#         if product_id:
#             query += " AND ph.product_id = ?"
#             params.append(product_id)
        
#         query += " ORDER BY ph.changed_at DESC LIMIT ?"
#         params.append(limit)
        
#         return self.db.fetchall(query, params)
    
#     def get_order_history(self, order_id: int = None, limit: int = 100):
#         """Get order change history"""
#         query = """
#         SELECT oh.*, s.staff_name as changed_by_name
#         FROM orders_history oh
#         LEFT JOIN staff s ON oh.changed_by = s.staff_id
#         WHERE 1=1
#         """
#         params = []
        
#         if order_id:
#             query += " AND oh.order_id = ?"
#             params.append(order_id)
        
#         query += " ORDER BY oh.changed_at DESC LIMIT ?"
#         params.append(limit)
        
#         return self.db.fetchall(query, params)
    
#     def get_stock_history(self, stock_id: int = None, product_id: str = None, limit: int = 100):
#         """Get stock change history"""
#         query = """
#         SELECT sh.*, s.staff_name as changed_by_name
#         FROM stocks_history sh
#         LEFT JOIN staff s ON sh.changed_by = s.staff_id
#         WHERE 1=1
#         """
#         params = []
        
#         if stock_id:
#             query += " AND sh.stock_id = ?"
#             params.append(stock_id)
        
#         if product_id:
#             query += " AND sh.product_id = ?"
#             params.append(product_id)
        
#         query += " ORDER BY sh.changed_at DESC LIMIT ?"
#         params.append(limit)
        
#         return self.db.fetchall(query, params)
    
#     def get_inventory_history(self, inventory_id: int = None, product_id: str = None, limit: int = 100):
#         """Get inventory change history"""
#         query = """
#         SELECT ih.*, s.staff_name as changed_by_name
#         FROM inventory_history ih
#         LEFT JOIN staff s ON ih.changed_by = s.staff_id
#         WHERE 1=1
#         """
#         params = []
        
#         if inventory_id:
#             query += " AND ih.inventory_id = ?"
#             params.append(inventory_id)
        
#         if product_id:
#             query += " AND ih.product_id = ?"
#             params.append(product_id)
        
#         query += " ORDER BY ih.changed_at DESC LIMIT ?"
#         params.append(limit)
        
#         return self.db.fetchall(query, params)
    
#     def get_audit_log(self, start_date=None, end_date=None, user_id=None, limit=100):
#         """Get comprehensive audit log"""
#         query = """
#         SELECT 
#             'product' as type,
#             ph.changed_at as timestamp,
#             s.staff_name as user,
#             ph.product_id as entity_id,
#             p.product_name as entity_name,
#             ph.change_type as action,
#             ph.remarks as description
#         FROM products_history ph
#         LEFT JOIN staff s ON ph.changed_by = s.staff_id
#         LEFT JOIN products p ON ph.product_id = p.product_id
        
#         UNION ALL
        
#         SELECT 
#             'order' as type,
#             oh.changed_at as timestamp,
#             s.staff_name as user,
#             oh.order_id as entity_id,
#             'Order #' || oh.order_id as entity_name,
#             oh.change_type as action,
#             oh.remarks as description
#         FROM orders_history oh
#         LEFT JOIN staff s ON oh.changed_by = s.staff_id
        
#         UNION ALL
        
#         SELECT 
#             'stock' as type,
#             sh.changed_at as timestamp,
#             s.staff_name as user,
#             sh.stock_id as entity_id,
#             p.product_name as entity_name,
#             sh.change_type as action,
#             sh.remarks as description
#         FROM stocks_history sh
#         LEFT JOIN staff s ON sh.changed_by = s.staff_id
#         LEFT JOIN products p ON sh.product_id = p.product_id
        
#         WHERE 1=1
#         """
        
#         params = []
#         conditions = []
        
#         if start_date:
#             conditions.append("timestamp >= ?")
#             params.append(start_date)
        
#         if end_date:
#             conditions.append("timestamp <= ?")
#             params.append(end_date)
        
#         if user_id:
#             conditions.append("user = ?")
#             params.append(user_id)
        
#         if conditions:
#             query = query.replace("WHERE 1=1", "WHERE " + " AND ".join(conditions))
        
#         query += " ORDER BY timestamp DESC LIMIT ?"
#         params.append(limit)
        
#         return self.db.fetchall(query, params)


# ---- HistoryController ----
class HistoryController:
    def __init__(self, db):
        self.db = db

    def get_product_history(self, product_id: int = None, limit: int = 100):
        q = "SELECT ph.*, s.staff_name as changed_by_name FROM products_history ph LEFT JOIN staff s ON ph.changed_by = s.staff_id WHERE 1=1"
        params = []
        if product_id:
            q += " AND ph.product_id = ?"; params.append(product_id)
        q += " ORDER BY ph.changed_at DESC LIMIT ?"; params.append(limit)
        return self.db.fetchall(q, params)

    def get_order_history(self, order_id: int = None, limit: int = 100):
        q = "SELECT oh.*, s.staff_name as changed_by_name FROM orders_history oh LEFT JOIN staff s ON oh.changed_by = s.staff_id WHERE 1=1"
        params = []
        if order_id:
            q += " AND oh.order_id = ?"; params.append(order_id)
        q += " ORDER BY oh.changed_at DESC LIMIT ?"; params.append(limit)
        return self.db.fetchall(q, params)

    def get_stock_history(self, stock_id: int = None, product_id: int = None, limit: int = 100):
        q = "SELECT sh.*, s.staff_name as changed_by_name FROM stocks_history sh LEFT JOIN staff s ON sh.changed_by = s.staff_id WHERE 1=1"
        params = []
        if stock_id:
            q += " AND sh.stock_id = ?"; params.append(stock_id)
        if product_id:
            q += " AND sh.product_id = ?"; params.append(product_id)
        q += " ORDER BY sh.changed_at DESC LIMIT ?"; params.append(limit)
        return self.db.fetchall(q, params)

    def get_inventory_history(self, inventory_id: int = None, product_id: int = None, limit: int = 100):
        q = "SELECT ih.*, s.staff_name as changed_by_name FROM inventory_history ih LEFT JOIN staff s ON ih.changed_by = s.staff_id WHERE 1=1"
        params = []
        if inventory_id:
            q += " AND ih.inventory_id = ?"; params.append(inventory_id)
        if product_id:
            q += " AND ih.product_id = ?"; params.append(product_id)
        q += " ORDER BY ih.changed_at DESC LIMIT ?"; params.append(limit)
        return self.db.fetchall(q, params)

    def get_audit_log(self, start_date=None, end_date=None, user_id=None, limit=100):
        # build UNION inside subquery then filter
        union_q = """
        SELECT 'product' as type, ph.changed_at as timestamp, s.staff_name as user, ph.product_id as entity_id, p.product_name as entity_name, ph.change_type as action, ph.remarks as description
        FROM products_history ph LEFT JOIN staff s ON ph.changed_by = s.staff_id LEFT JOIN products p ON ph.product_id = p.product_id
        UNION ALL
        SELECT 'order' as type, oh.changed_at as timestamp, s.staff_name as user, oh.order_id as entity_id, 'Order #' || oh.order_id as entity_name, oh.change_type as action, oh.remarks as description
        FROM orders_history oh LEFT JOIN staff s ON oh.changed_by = s.staff_id
        UNION ALL
        SELECT 'stock' as type, sh.changed_at as timestamp, s.staff_name as user, sh.stock_id as entity_id, p.product_name as entity_name, sh.change_type as action, sh.remarks as description
        FROM stocks_history sh LEFT JOIN staff s ON sh.changed_by = s.staff_id LEFT JOIN products p ON sh.product_id = p.product_id
        """
        where_clauses = []
        params = []
        if start_date:
            where_clauses.append("timestamp >= ?"); params.append(start_date)
        if end_date:
            where_clauses.append("timestamp <= ?"); params.append(end_date)
        if user_id:
            where_clauses.append("user = ?"); params.append(user_id)
        if where_clauses:
            union_q = f"SELECT * FROM ({union_q}) WHERE " + " AND ".join(where_clauses)
        union_q += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        return self.db.fetchall(union_q, params)
