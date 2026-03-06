# from app.models.suppliers import Supplier

# class SupplierController:
#     def __init__(self, db):
#         self.db = db

#     def create_supplier(self, supplier: Supplier):
#         """Create a new supplier"""
#         try:
#             supplier.validate()
            
#             # Check if supplier already exists (by email or name)
#             existing = self.db.fetchone(
#                 """SELECT supplier_id FROM suppliers 
#                    WHERE supplier_name = ? OR email = ?""",
#                 (supplier.supplier_name, supplier.email)
#             )
            
#             if existing:
#                 raise ValueError("Supplier already exists")
            
#             with self.db.conn:
#                 cursor = self.db.execute(
#                     """INSERT INTO suppliers 
#                        (supplier_name, contact_no, email,
#                         warehouse_address, bank_ac_no)
#                        VALUES (?, ?, ?, ?, ?)""",
#                     (supplier.supplier_name, supplier.contact_no,
#                      supplier.email, supplier.warehouse_address,
#                      supplier.bank_ac_no)
#                 )
#                 supplier_id = cursor.lastrowid
                
#                 # Generate supplier code
#                 supplier_code = f"SUP-{supplier_id:06d}"
#                 self.db.execute(
#                     "UPDATE suppliers SET supplier_code = ? WHERE supplier_id = ?",
#                     (supplier_code, supplier_id)
#                 )
#                 return supplier_id
#         except Exception as e:
#             raise e

#     def update_supplier(self, supplier: Supplier):
#         """Update an existing supplier"""
#         try:
#             supplier.validate()
            
#             with self.db.conn:
#                 self.db.execute(
#                     """UPDATE suppliers 
#                        SET supplier_name = ?, contact_no = ?, email = ?,
#                            warehouse_address = ?, bank_ac_no = ?,
#                            updated_at = CURRENT_TIMESTAMP
#                        WHERE supplier_id = ?""",
#                     (supplier.supplier_name, supplier.contact_no,
#                      supplier.email, supplier.warehouse_address,
#                      supplier.bank_ac_no, supplier.supplier_id)
#                 )
#         except Exception as e:
#             raise e

#     def delete_supplier(self, supplier_id: int):
#         """Delete a supplier (check for references first)"""
#         try:
#             # Check if supplier is used by products
#             products = self.db.fetchone(
#                 "SELECT COUNT(*) as count FROM products WHERE supplier_id = ?",
#                 (supplier_id,)
#             )
            
#             if products and products['count'] > 0:
#                 raise ValueError("Cannot delete supplier: It is being used by products")
            
#             # Check if supplier is used by purchases
#             purchases = self.db.fetchone(
#                 "SELECT COUNT(*) as count FROM purchases WHERE supplier_id = ?",
#                 (supplier_id,)
#             )
            
#             if purchases and purchases['count'] > 0:
#                 raise ValueError("Cannot delete supplier: It has associated purchases")
            
#             with self.db.conn:
#                 self.db.execute(
#                     "DELETE FROM suppliers WHERE supplier_id = ?",
#                     (supplier_id,)
#                 )
#         except Exception as e:
#             raise e

#     def list_suppliers(self):
#         """Get all suppliers"""
#         query = """
#         SELECT s.*,
#                COUNT(p.product_id) as product_count,
#                COUNT(po.purchase_id) as purchase_count,
#                COALESCE(SUM(po.total_amount), 0) as total_purchases
#         FROM suppliers s
#         LEFT JOIN products p ON s.supplier_id = p.supplier_id
#         LEFT JOIN purchases po ON s.supplier_id = po.supplier_id
#         GROUP BY s.supplier_id
#         ORDER BY s.supplier_name
#         """
#         return self.db.fetchall(query)

#     def get_supplier(self, supplier_id: int):
#         """Get a specific supplier by ID"""
#         query = """
#         SELECT s.*,
#                COUNT(p.product_id) as product_count,
#                COALESCE(SUM(po.total_amount), 0) as total_purchases,
#                COUNT(po.purchase_id) as purchase_count
#         FROM suppliers s
#         LEFT JOIN products p ON s.supplier_id = p.supplier_id
#         LEFT JOIN purchases po ON s.supplier_id = po.supplier_id
#         WHERE s.supplier_id = ?
#         GROUP BY s.supplier_id
#         """
#         return self.db.fetchone(query, (supplier_id,))

#     def search_suppliers(self, search_term: str):
#         """Search suppliers by name, contact, or email"""
#         query = """
#         SELECT s.*,
#                COUNT(p.product_id) as product_count
#         FROM suppliers s
#         LEFT JOIN products p ON s.supplier_id = p.supplier_id
#         WHERE s.supplier_name LIKE ? OR s.contact_no LIKE ? OR s.email LIKE ?
#         GROUP BY s.supplier_id
#         ORDER BY s.supplier_name
#         """
#         params = [f"%{search_term}%"] * 3
#         return self.db.fetchall(query, params)

#     def get_supplier_statistics(self):
#         """Get supplier statistics"""
#         stats = {}
        
#         # Total suppliers
#         total = self.db.fetchone("SELECT COUNT(*) as count FROM suppliers")
#         stats['total_suppliers'] = total['count']
        
#         # Suppliers with most products
#         top_suppliers = self.db.fetchall("""
#             SELECT s.supplier_name, COUNT(p.product_id) as product_count
#             FROM suppliers s
#             LEFT JOIN products p ON s.supplier_id = p.supplier_id
#             GROUP BY s.supplier_id
#             ORDER BY product_count DESC
#             LIMIT 10
#         """)
#         stats['top_suppliers'] = [dict(row) for row in top_suppliers]
        
#         # Suppliers by purchase value
#         top_by_purchase = self.db.fetchall("""
#             SELECT s.supplier_name, 
#                    COALESCE(SUM(po.total_amount), 0) as total_purchases
#             FROM suppliers s
#             LEFT JOIN purchases po ON s.supplier_id = po.supplier_id
#             GROUP BY s.supplier_id
#             ORDER BY total_purchases DESC
#             LIMIT 10
#         """)
#         stats['top_by_purchase'] = [dict(row) for row in top_by_purchase]
        
#         return stats

# ---- SupplierController (fixed) ----
from app.models.suppliers import Supplier

class SupplierController:
    def __init__(self, db):
        self.db = db

    def create_supplier(self, supplier: Supplier):
        supplier.validate()
        existing = self.db.fetchone("SELECT supplier_id FROM suppliers WHERE supplier_name = ? OR email = ?", (supplier.supplier_name, supplier.email))
        if existing:
            raise ValueError("Supplier already exists")
        with self.db.conn:
            cur = self.db.execute("INSERT INTO suppliers (supplier_name, contact_no, email, warehouse_address, bank_ac_no) VALUES (?, ?, ?, ?, ?)",
                                  (supplier.supplier_name, supplier.contact_no, supplier.email, supplier.warehouse_address, supplier.bank_ac_no))
            supplier_id = cur.lastrowid
            code = f"SUP-{supplier_id:06d}"
            self.db.execute("UPDATE suppliers SET supplier_code = ? WHERE supplier_id = ?", (code, supplier_id))
            return supplier_id

    def update_supplier(self, supplier: Supplier):
        supplier.validate()
        with self.db.conn:
            self.db.execute("UPDATE suppliers SET supplier_name=?, contact_no=?, email=?, warehouse_address=?, bank_ac_no=?, updated_at=CURRENT_TIMESTAMP WHERE supplier_id = ?",
                            (supplier.supplier_name, supplier.contact_no, supplier.email, supplier.warehouse_address, supplier.bank_ac_no, supplier.supplier_id))

    def delete_supplier(self, supplier_id: int):
        products = self.db.fetchone("SELECT COUNT(*) as count FROM products WHERE supplier_id = ?", (supplier_id,))
        if products and products['count'] > 0:
            raise ValueError("Cannot delete supplier: It is being used by products")
        purchases = self.db.fetchone("SELECT COUNT(*) as count FROM purchases WHERE supplier_id = ?", (supplier_id,))
        if purchases and purchases['count'] > 0:
            raise ValueError("Cannot delete supplier: It has associated purchases")
        with self.db.conn:
            self.db.execute("DELETE FROM suppliers WHERE supplier_id = ?", (supplier_id,))

    def list_suppliers(self):
        q = """
        SELECT s.*, COUNT(p.product_id) as product_count, COUNT(po.purchase_id) as purchase_count, COALESCE(SUM(po.quantity*po.unit_cost), 0) as total_purchases
        FROM suppliers s
        LEFT JOIN products p ON s.supplier_id = p.supplier_id
        LEFT JOIN purchases po ON s.supplier_id = po.supplier_id
        GROUP BY s.supplier_id ORDER BY s.supplier_name
        """
        return self.db.fetchall(q)

    def get_supplier(self, supplier_id: int):
        q = """
        SELECT s.*, COUNT(p.product_id) as product_count, COALESCE(SUM(po.quantity*po.unit_cost), 0) as total_purchases, COUNT(po.purchase_id) as purchase_count
        FROM suppliers s
        LEFT JOIN products p ON s.supplier_id = p.supplier_id
        LEFT JOIN purchases po ON s.supplier_id = po.supplier_id
        WHERE s.supplier_id = ?
        GROUP BY s.supplier_id
        """
        return self.db.fetchone(q, (supplier_id,))

    def search_suppliers(self, search_term: str):
        q = """
        SELECT s.*, COUNT(p.product_id) as product_count
        FROM suppliers s
        LEFT JOIN products p ON s.supplier_id = p.supplier_id
        WHERE s.supplier_name LIKE ? OR s.contact_no LIKE ? OR s.email LIKE ?
        GROUP BY s.supplier_id
        ORDER BY s.supplier_name
        """
        params = [f"%{search_term}%"] * 3
        return self.db.fetchall(q, params)

    def get_supplier_statistics(self):
        stats = {}
        total = self.db.fetchone("SELECT COUNT(*) as count FROM suppliers")
        stats['total_suppliers'] = total['count'] if total else 0
        top_suppliers = self.db.fetchall("SELECT s.supplier_name, COUNT(p.product_id) as product_count FROM suppliers s LEFT JOIN products p ON s.supplier_id = p.supplier_id GROUP BY s.supplier_id ORDER BY product_count DESC LIMIT 10")
        stats['top_suppliers'] = [dict(r) for r in top_suppliers]
        top_by_purchase = self.db.fetchall("SELECT s.supplier_name, COALESCE(SUM(po.quantity*po.unit_cost),0) as total_purchases FROM suppliers s LEFT JOIN purchases po ON s.supplier_id = po.supplier_id GROUP BY s.supplier_id ORDER BY total_purchases DESC LIMIT 10")
        stats['top_by_purchase'] = [dict(r) for r in top_by_purchase]
        return stats

