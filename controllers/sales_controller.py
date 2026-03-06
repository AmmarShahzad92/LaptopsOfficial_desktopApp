# from app.models.sales import Sale
# from datetime import datetime

# class SalesController:
#     def __init__(self, db):
#         self.db = db

#     def record_sale(self, sale: Sale):
#         """Record a sale (can be from order or return)"""
#         try:
#             sale.validate()
            
#             with self.db.conn:
#                 cursor = self.db.execute(
#                     """INSERT INTO sales 
#                        (order_id, order_item_id, return_id, return_item_id,
#                         product_id, quantity, cost_price, wholesale_price,
#                         sales_price, amount, sale_date, location_id,
#                         created_by, notes)
#                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
#                     (sale.order_id, sale.order_item_id, sale.return_id,
#                      sale.return_item_id, sale.product_id, sale.quantity,
#                      sale.cost_price, sale.wholesale_price, sale.sales_price,
#                      sale.amount, sale.sale_date, sale.location_id,
#                      sale.created_by, sale.notes)
#                 )
#                 sales_id = cursor.lastrowid
#                 return sales_id
#         except Exception as e:
#             raise e

#     def list_sales(self, start_date=None, end_date=None, product_id=None):
#         """List sales with filters"""
#         query = """
#         SELECT 
#             s.*,
#             p.product_name,
#             p.product_code,
#             c.category_brand,
#             c.model_name,
#             l.location_name,
#             st.staff_name as created_by_name
#         FROM sales s
#         JOIN products p ON s.product_id = p.product_id
#         JOIN categories c ON p.category_id = c.category_id
#         JOIN locations l ON s.location_id = l.location_id
#         JOIN staff st ON s.created_by = st.staff_id
#         WHERE 1=1
#         """
#         params = []
        
#         if start_date:
#             query += " AND DATE(s.sale_date) >= ?"
#             params.append(start_date)
        
#         if end_date:
#             query += " AND DATE(s.sale_date) <= ?"
#             params.append(end_date)
        
#         if product_id:
#             query += " AND s.product_id = ?"
#             params.append(product_id)
        
#         query += " ORDER BY s.sale_date DESC"
        
#         return self.db.fetchall(query, params)

#     def get_sales_statistics(self):
#         """Get sales statistics"""
#         stats = {}
        
#         # Total sales
#         total_sales = self.db.fetchone("SELECT COUNT(*) as count FROM sales")
#         stats['total_sales'] = total_sales['count']
        
#         # Total sales amount
#         total_amount = self.db.fetchone("SELECT SUM(amount) as total FROM sales")
#         stats['total_amount'] = total_amount['total'] if total_amount['total'] else 0
        
#         # Total profit
#         total_profit = self.db.fetchone("SELECT SUM(profit_loss) as total FROM sales")
#         stats['total_profit'] = total_profit['total'] if total_profit['total'] else 0
        
#         # Sales by product
#         by_product = self.db.fetchall("""
#             SELECT 
#                 p.product_name,
#                 p.product_code,
#                 cat.category_brand,
#                 cat.model_name,
#                 COUNT(s.sales_id) as sale_count,
#                 SUM(s.quantity) as total_quantity,
#                 SUM(s.amount) as total_amount,
#                 SUM(s.profit_loss) as total_profit
#             FROM sales s
#             JOIN products p ON s.product_id = p.product_id
#             JOIN categories cat ON p.category_id = cat.category_id
#             GROUP BY s.product_id
#             ORDER BY total_amount DESC
#             LIMIT 10
#         """)
#         stats['by_product'] = [dict(row) for row in by_product]
        
#         # Sales by location
#         by_location = self.db.fetchall("""
#             SELECT 
#                 l.location_name,
#                 l.location_type,
#                 COUNT(s.sales_id) as sale_count,
#                 SUM(s.quantity) as total_quantity,
#                 SUM(s.amount) as total_amount,
#                 SUM(s.profit_loss) as total_profit
#             FROM sales s
#             JOIN locations l ON s.location_id = l.location_id
#             GROUP BY s.location_id
#             ORDER BY total_amount DESC
#         """)
#         stats['by_location'] = [dict(row) for row in by_location]
        
#         # Monthly sales trend (last 12 months)
#         monthly_trend = self.db.fetchall("""
#             SELECT 
#                 strftime('%Y-%m', sale_date) as month,
#                 COUNT(*) as sale_count,
#                 SUM(quantity) as monthly_quantity,
#                 SUM(amount) as monthly_amount,
#                 SUM(profit_loss) as monthly_profit
#             FROM sales
#             WHERE sale_date >= DATE('now', '-12 months')
#             GROUP BY strftime('%Y-%m', sale_date)
#             ORDER BY month
#         """)
#         stats['monthly_trend'] = [dict(row) for row in monthly_trend]
        
#         # Average sale value
#         avg_sale = self.db.fetchone("""
#             SELECT 
#                 AVG(amount) as avg_amount,
#                 AVG(profit_loss) as avg_profit,
#                 AVG(quantity) as avg_quantity
#             FROM sales
#         """)
#         stats['averages'] = dict(avg_sale) if avg_sale else {}
        
#         return stats

# ---- SalesController (fixed) ----
from app.models.sales import Sale
from datetime import datetime

class SalesController:
    def __init__(self, db):
        self.db = db

    def record_sale(self, sale: Sale):
        sale.validate()
        with self.db.conn:
            cur = self.db.execute(
                """INSERT INTO sales (order_id, order_item_id, return_id, return_item_id, product_id, quantity, cost_price, wholesale_price, sales_price, amount, sale_date, location_id, created_by, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (sale.order_id, sale.order_item_id, sale.return_id, sale.return_item_id, sale.product_id,
                 sale.quantity, sale.cost_price, sale.wholesale_price, sale.sales_price, sale.amount,
                 sale.sale_date or datetime.now().isoformat(), sale.location_id, sale.created_by, sale.notes)
            )
            sales_id = cur.lastrowid
            return sales_id

    def list_sales(self, start_date=None, end_date=None, product_id=None):
        q = """
        SELECT s.*, p.product_name, c.category_brand, c.model_name, l.location_name, st.staff_name as created_by_name
        FROM sales s
        JOIN products p ON s.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        JOIN locations l ON s.location_id = l.location_id
        JOIN staff st ON s.created_by = st.staff_id
        WHERE 1=1
        """
        params = []
        if start_date:
            q += " AND DATE(s.sale_date) >= ?"; params.append(start_date)
        if end_date:
            q += " AND DATE(s.sale_date) <= ?"; params.append(end_date)
        if product_id:
            q += " AND s.product_id = ?"; params.append(product_id)
        q += " ORDER BY s.sale_date DESC"
        return self.db.fetchall(q, params)

    def get_sales_statistics(self):
        stats = {}
        total_sales = self.db.fetchone("SELECT COUNT(*) as count FROM sales")
        stats['total_sales'] = total_sales['count'] if total_sales else 0
        total_amount = self.db.fetchone("SELECT SUM(amount) as total FROM sales")
        stats['total_amount'] = total_amount['total'] if total_amount and total_amount['total'] else 0
        total_profit = self.db.fetchone("SELECT SUM(amount - (cost_price * quantity)) as total FROM sales")
        stats['total_profit'] = total_profit['total'] if total_profit and total_profit['total'] else 0
        by_product = self.db.fetchall("""
            SELECT p.product_name, c.category_brand, c.model_name, COUNT(s.sales_id) as sale_count, SUM(s.quantity) as total_quantity, SUM(s.amount) as total_amount, SUM(s.amount - (s.cost_price * s.quantity)) as total_profit
            FROM sales s JOIN products p ON s.product_id = p.product_id JOIN categories c ON p.category_id = c.category_id
            GROUP BY s.product_id ORDER BY total_amount DESC LIMIT 10
        """)
        stats['by_product'] = [dict(r) for r in by_product]
        by_location = self.db.fetchall("""
            SELECT l.location_name, l.location_type, COUNT(s.sales_id) as sale_count, SUM(s.quantity) as total_quantity, SUM(s.amount) as total_amount, SUM(s.amount - (s.cost_price * s.quantity)) as total_profit
            FROM sales s JOIN locations l ON s.location_id = l.location_id GROUP BY s.location_id ORDER BY total_amount DESC
        """)
        stats['by_location'] = [dict(r) for r in by_location]
        monthly_trend = self.db.fetchall("""
            SELECT strftime('%Y-%m', sale_date) as month, COUNT(*) as sale_count, SUM(quantity) as monthly_quantity, SUM(amount) as monthly_amount, SUM(amount - (cost_price * quantity)) as monthly_profit
            FROM sales WHERE sale_date >= DATE('now', '-12 months') GROUP BY month ORDER BY month
        """)
        stats['monthly_trend'] = [dict(r) for r in monthly_trend]
        avg_sale = self.db.fetchone("SELECT AVG(amount) as avg_amount, AVG(amount - (cost_price * quantity)) as avg_profit, AVG(quantity) as avg_quantity FROM sales")
        stats['averages'] = dict(avg_sale) if avg_sale else {}
        return stats
