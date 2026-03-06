# ---- LocationController ----
from app.models.locations import Location

class LocationController:
    def __init__(self, db):
        self.db = db

    def create_location(self, location: Location):
        location.validate()
        existing = self.db.fetchone("SELECT location_id FROM locations WHERE location_name = ?", (location.location_name,))
        if existing:
            raise ValueError("Location name already exists")
        with self.db.conn:
            cur = self.db.execute(
                """INSERT INTO locations (location_name, location_type, address, contact_no, managed_by, staff_capacity, location_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (location.location_name, location.location_type, location.address, location.contact_no,
                 location.managed_by, location.staff_capacity, location.location_status)
            )
            return cur.lastrowid

    def update_location(self, location: Location):
        location.validate()
        with self.db.conn:
            self.db.execute(
                """UPDATE locations SET location_name=?, location_type=?, address=?, contact_no=?, managed_by=?, staff_capacity=?, location_status=?, updated_at=CURRENT_TIMESTAMP
                   WHERE location_id=?""",
                (location.location_name, location.location_type, location.address, location.contact_no,
                 location.managed_by, location.staff_capacity, location.location_status, location.location_id)
            )

    def delete_location(self, location_id: int):
        stock = self.db.fetchone("SELECT COUNT(*) as count FROM stocks WHERE location_id = ?", (location_id,))
        if stock and stock['count'] > 0:
            raise ValueError("Cannot delete location: It has stock records")
        orders = self.db.fetchone("SELECT COUNT(*) as count FROM orders WHERE location_id = ?", (location_id,))
        if orders and orders['count'] > 0:
            raise ValueError("Cannot delete location: It has associated orders")
        purchases = self.db.fetchone("SELECT COUNT(*) as count FROM purchases WHERE location_id = ?", (location_id,))
        if purchases and purchases['count'] > 0:
            raise ValueError("Cannot delete location: It has associated purchases")
        with self.db.conn:
            self.db.execute("UPDATE locations SET location_status = 'closed', updated_at=CURRENT_TIMESTAMP WHERE location_id = ?", (location_id,))

    def list_locations(self, active_only=True):
        q = """
        SELECT l.*, s.staff_name as manager_name, COUNT(st.stock_id) as stock_items, SUM(st.qty_stocked) as total_stock, COUNT(o.order_id) as order_count
        FROM locations l
        LEFT JOIN staff s ON l.managed_by = s.staff_id
        LEFT JOIN stocks st ON l.location_id = st.location_id
        LEFT JOIN orders o ON l.location_id = o.location_id
        WHERE 1=1
        """
        params = []
        if active_only:
            q += " AND l.location_status = 'active'"
        q += " GROUP BY l.location_id ORDER BY l.location_name"
        return self.db.fetchall(q, params)

    def get_location(self, location_id: int):
        q = """
        SELECT l.*, s.staff_name as manager_name, s.staff_contact as manager_contact, s.staff_email as manager_email,
               COUNT(st.stock_id) as stock_items, SUM(st.qty_stocked) as total_stock, SUM(st.qty_stocked * st.unit_cost) as stock_value
        FROM locations l
        LEFT JOIN staff s ON l.managed_by = s.staff_id
        LEFT JOIN stocks st ON l.location_id = st.location_id
        WHERE l.location_id = ?
        GROUP BY l.location_id
        """
        return self.db.fetchone(q, (location_id,))

    def get_location_stock(self, location_id: int):
        q = """
        SELECT st.*, p.product_name, c.category_brand, c.model_name, s.supplier_name
        FROM stocks st
        JOIN products p ON st.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        WHERE st.location_id = ?
        ORDER BY p.product_name
        """
        return self.db.fetchall(q, (location_id,))

    def get_location_statistics(self):
        stats = {}
        total = self.db.fetchone("SELECT COUNT(*) as count FROM locations WHERE location_status = 'active'")
        stats['total_locations'] = total['count'] if total else 0
        by_type = self.db.fetchall("""
            SELECT location_type, COUNT(*) as count FROM locations WHERE location_status='active' GROUP BY location_type ORDER BY count DESC
        """)
        stats['by_type'] = [dict(r) for r in by_type]
        stock_by_location = self.db.fetchall("""
            SELECT l.location_name, l.location_type, COUNT(st.stock_id) as product_count, SUM(st.qty_stocked) as total_quantity, SUM(st.qty_stocked * st.unit_cost) as total_value
            FROM locations l LEFT JOIN stocks st ON l.location_id = st.location_id
            WHERE l.location_status = 'active' GROUP BY l.location_id ORDER BY total_value DESC
        """)
        stats['stock_by_location'] = [dict(r) for r in stock_by_location]
        orders_by_location = self.db.fetchall("""
            SELECT l.location_name, l.location_type, COUNT(o.order_id) as order_count, SUM(o.total) as order_value
            FROM locations l LEFT JOIN orders o ON l.location_id = o.location_id
            WHERE l.location_status = 'active' GROUP BY l.location_id ORDER BY order_count DESC
        """)
        stats['orders_by_location'] = [dict(r) for r in orders_by_location]
        return stats

