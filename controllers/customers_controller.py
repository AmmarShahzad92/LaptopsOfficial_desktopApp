# ---- CustomerController ----
from app.models.customers import Customer

class CustomerController:
    def __init__(self, db):
        self.db = db

    def create_customer(self, customer: Customer):
        customer.validate()
        if customer.email:
            existing = self.db.fetchone("SELECT customer_id FROM customers WHERE email = ?", (customer.email,))
            if existing:
                raise ValueError("Customer email already exists")
        with self.db.conn:
            cur = self.db.execute(
                """INSERT INTO customers (customer_name, contact_no, email, address)
                   VALUES (?, ?, ?, ?)""",
                (customer.customer_name, customer.contact_no, customer.email, customer.address)
            )
            return cur.lastrowid

    def update_customer(self, customer: Customer):
        customer.validate()
        with self.db.conn:
            self.db.execute(
                """UPDATE customers
                   SET customer_name=?, contact_no=?, email=?, address=?, updated_at=CURRENT_TIMESTAMP
                   WHERE customer_id = ?""",
                (customer.customer_name, customer.contact_no, customer.email, customer.address, customer.customer_id)
            )

    def delete_customer(self, customer_id: int):
        orders = self.db.fetchone("SELECT COUNT(*) as count FROM orders WHERE customer_id = ?", (customer_id,))
        if orders and orders['count'] > 0:
            raise ValueError("Cannot delete customer: They have associated orders")
        with self.db.conn:
            self.db.execute("DELETE FROM customers WHERE customer_id = ?", (customer_id,))

    def list_customers(self):
        q = """
        SELECT c.*, COUNT(o.order_id) as order_count, COALESCE(SUM(o.total), 0) as total_spent, MAX(o.order_date) as last_order_date
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id
        ORDER BY c.customer_name
        """
        return self.db.fetchall(q)

    def get_customer(self, customer_id: int):
        q = """
        SELECT c.*, COUNT(o.order_id) as order_count, COALESCE(SUM(o.total), 0) as total_spent,
               MAX(o.order_date) as last_order_date, MIN(o.order_date) as first_order_date, AVG(o.total) as avg_order_value
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        WHERE c.customer_id = ?
        GROUP BY c.customer_id
        """
        return self.db.fetchone(q, (customer_id,))

    def search_customers(self, search_term: str):
        q = """
        SELECT c.*, COUNT(o.order_id) as order_count, COALESCE(SUM(o.total), 0) as total_spent
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        WHERE c.customer_name LIKE ? OR c.contact_no LIKE ? OR c.email LIKE ?
        GROUP BY c.customer_id
        ORDER BY c.customer_name
        """
        params = [f"%{search_term}%"] * 3
        return self.db.fetchall(q, params)

    def get_customer_orders(self, customer_id: int):
        q = """
        SELECT o.*, l.location_name, COUNT(oi.item_id) as item_count, SUM(oi.qty) as total_qty
        FROM orders o
        JOIN locations l ON o.location_id = l.location_id
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.customer_id = ?
        GROUP BY o.order_id
        ORDER BY o.order_date DESC
        """
        return self.db.fetchall(q, (customer_id,))

    def get_customer_statistics(self):
        stats = {}
        total_customers = self.db.fetchone("SELECT COUNT(*) as count FROM customers")
        stats['total_customers'] = total_customers['count'] if total_customers else 0
        customers_with_orders = self.db.fetchone("SELECT COUNT(DISTINCT customer_id) as count FROM orders")
        stats['customers_with_orders'] = customers_with_orders['count'] if customers_with_orders else 0
        top_customers = self.db.fetchall("""
            SELECT c.customer_name, COUNT(o.order_id) as order_count, COALESCE(SUM(o.total),0) as total_spent, AVG(o.total) as avg_order_value
            FROM customers c
            LEFT JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id
            ORDER BY total_spent DESC
            LIMIT 10
        """)
        stats['top_customers'] = [dict(r) for r in top_customers]
        acquisition_trend = self.db.fetchall("""
            SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as new_customers
            FROM customers WHERE created_at >= DATE('now', '-12 months')
            GROUP BY month ORDER BY month
        """)
        stats['acquisition_trend'] = [dict(r) for r in acquisition_trend]
        return stats
