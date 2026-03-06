class DashboardController:
    def __init__(self, db):
        self.db = db
    
    def get_daily_dashboard(self):
        """Get daily dashboard statistics"""
        query = "SELECT * FROM vw_daily_dashboard"
        return self.db.fetchone(query)
    
    def get_sales_summary(self, days=30):
        """Get sales summary for last N days"""
        query = """
        SELECT * FROM vw_sales_summary 
        WHERE sale_date >= DATE('now', ?)
        ORDER BY sale_date DESC
        """
        return self.db.fetchall(query, (f"-{days} days",))
    
    def get_product_sales_performance(self, limit=10):
        """Get top selling products"""
        query = f"SELECT * FROM vw_product_sales LIMIT ?"
        return self.db.fetchall(query, (limit,))
    
    def get_low_stock_alerts(self):
        """Get low stock alerts"""
        query = "SELECT * FROM vw_low_stock_alert"
        return self.db.fetchall(query)
    
    def get_customer_orders_summary(self):
        """Get customer order summary"""
        query = "SELECT * FROM vw_customer_orders"
        return self.db.fetchall(query)
    
    def get_product_inventory(self):
        """Get product inventory view"""
        query = "SELECT * FROM vw_product_inventory"
        return self.db.fetchall(query)
    
    def get_staff_performance(self):
        """Get staff performance"""
        query = "SELECT * FROM vw_staff_performance"
        return self.db.fetchall(query)
    
    def get_stock_by_location(self):
        """Get stock by location"""
        query = "SELECT * FROM vw_stock_by_location"
        return self.db.fetchall(query)
    
    def get_comprehensive_dashboard(self):
        """Get comprehensive dashboard data"""
        dashboard = {}
        
        # Daily stats
        dashboard['daily'] = self.get_daily_dashboard()
        
        # Recent sales
        dashboard['recent_sales'] = self.get_sales_summary(days=7)
        
        # Top products
        dashboard['top_products'] = self.get_product_sales_performance(5)
        
        # Low stock alerts
        dashboard['low_stock'] = self.get_low_stock_alerts()
        
        # Recent customers
        recent_customers = self.db.fetchall("""
            SELECT customer_name, contact_no, email, created_at
            FROM customers 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        dashboard['recent_customers'] = [dict(row) for row in recent_customers]
        
        # Recent orders
        recent_orders = self.db.fetchall("""
            SELECT o.order_id, c.customer_name, o.total, o.status, o.order_date
            FROM orders o
            JOIN customers c ON o.customer_id = c.customer_id
            ORDER BY o.order_date DESC 
            LIMIT 5
        """)
        dashboard['recent_orders'] = [dict(row) for row in recent_orders]
        
        # Inventory summary
        inventory_summary = self.db.fetchone("""
            SELECT 
                COUNT(*) as total_products,
                SUM(total_qty) as total_quantity,
                SUM(inventory_amount) as total_value
            FROM inventory
        """)
        dashboard['inventory_summary'] = dict(inventory_summary)
        
        return dashboard