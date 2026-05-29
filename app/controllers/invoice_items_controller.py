# from app.models.invoice_items import InvoiceItem

# class InvoiceItemsController:
#     def __init__(self, db):
#         self.db = db
    
#     def get_invoice_item(self, invoice_item_id: int):
#         """Get a specific invoice item by ID"""
#         query = """
#         SELECT ii.*, p.product_name, c.category_brand, c.model_name
#         FROM invoice_items ii
#         JOIN products p ON ii.product_id = p.product_id
#         JOIN categories c ON p.category_id = c.category_id
#         WHERE ii.invoice_item_id = ?
#         """
#         return self.db.fetchone(query, (invoice_item_id,))
    
#     def update_invoice_item(self, invoice_item_id: int, quantity_sold: int, unit_price: float):
#         """Update an invoice item"""
#         try:
#             if quantity_sold <= 0:
#                 raise ValueError("Quantity must be greater than 0")
#             if unit_price < 0:
#                 raise ValueError("Unit price cannot be negative")
            
#             with self.db.conn:
#                 self.db.execute(
#                     """UPDATE invoice_items 
#                        SET quantity_sold = ?, unit_price = ?, updated_at = CURRENT_TIMESTAMP
#                        WHERE invoice_item_id = ?""",
#                     (quantity_sold, unit_price, invoice_item_id)
#                 )
#         except Exception as e:
#             raise e
    
#     def delete_invoice_item(self, invoice_item_id: int):
#         """Delete an invoice item"""
#         try:
#             with self.db.conn:
#                 self.db.execute(
#                     "DELETE FROM invoice_items WHERE invoice_item_id = ?",
#                     (invoice_item_id,)
#                 )
#         except Exception as e:
#             raise e
    
#     def get_invoice_items_by_invoice(self, invoice_id: int):
#         """Get all items for an invoice"""
#         query = """
#         SELECT ii.*, p.product_name, p.product_id, c.category_brand, c.model_name
#         FROM invoice_items ii
#         JOIN products p ON ii.product_id = p.product_id
#         JOIN categories c ON p.category_id = c.category_id
#         WHERE ii.invoice_id = ?
#         ORDER BY ii.invoice_item_id
#         """
#         return self.db.fetchall(query, (invoice_id,))
    
#     def get_invoice_items_by_product(self, product_id: str):
#         """Get all invoice items for a specific product"""
#         query = """
#         SELECT ii.*, i.invoice_date, c.customer_name, i.payment_method
#         FROM invoice_items ii
#         JOIN invoices i ON ii.invoice_id = i.invoice_id
#         JOIN customers c ON i.customer_id = c.customer_id
#         WHERE ii.product_id = ?
#         ORDER BY i.invoice_date DESC
#         """
#         return self.db.fetchall(query, (product_id,))

# ---- InvoiceController ----
from app.models.invoices import Invoice
from app.models.invoice_items import InvoiceItem

class InvoiceController:
    def __init__(self, db):
        self.db = db

    def create_invoice(self, invoice: Invoice, items: list[InvoiceItem]):
        invoice.validate()
        for it in items:
            it.validate()
        with self.db.conn:
            cur = self.db.execute(
                """INSERT INTO invoices
                   (order_id, customer_id, customer_name, customer_contact, customer_email,
                    payment_method, delivery_method, subtotal, shipping_fee, discount_amount,
                    created_by, location_id, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (invoice.order_id, invoice.customer_id, invoice.customer_name,
                 invoice.customer_contact, invoice.customer_email, invoice.payment_method,
                 invoice.delivery_method, invoice.subtotal, invoice.shipping_fee,
                 invoice.discount_amount, invoice.created_by, invoice.location_id,
                 invoice.notes)
            )
            invoice_id = cur.lastrowid
            for it in items:
                self.db.execute(
                    """INSERT INTO invoice_items (invoice_id, order_item_id, product_id, quantity_sold, unit_price)
                       VALUES (?, ?, ?, ?, ?)""",
                    (invoice_id, it.order_item_id, it.product_id, it.quantity_sold, it.unit_price)
                )
            return invoice_id

    def list_invoices(self, start_date=None, end_date=None):
        q = """
        SELECT i.*, c.customer_name, c.contact_no as customer_phone,
               l.location_name, s.staff_name as created_by_name,
               COUNT(ii.invoice_item_id) as item_count, SUM(ii.quantity_sold) as total_qty
        FROM invoices i
        LEFT JOIN customers c ON i.customer_id = c.customer_id
        JOIN locations l ON i.location_id = l.location_id
        JOIN staff s ON i.created_by = s.staff_id
        LEFT JOIN invoice_items ii ON i.invoice_id = ii.invoice_id
        WHERE 1=1
        """
        params = []
        if start_date:
            q += " AND DATE(i.invoice_date) >= ?"; params.append(start_date)
        if end_date:
            q += " AND DATE(i.invoice_date) <= ?"; params.append(end_date)
        q += " GROUP BY i.invoice_id ORDER BY i.invoice_date DESC"
        return self.db.fetchall(q, params)

    def get_invoice(self, invoice_id: int):
        q = """
        SELECT i.*, c.customer_name, c.contact_no as customer_phone, c.email as customer_email, c.address as customer_address,
               l.location_name, l.location_type, s.staff_name as created_by_name, s.staff_contact as created_by_contact
        FROM invoices i
        LEFT JOIN customers c ON i.customer_id = c.customer_id
        JOIN locations l ON i.location_id = l.location_id
        JOIN staff s ON i.created_by = s.staff_id
        WHERE i.invoice_id = ?
        """
        return self.db.fetchone(q, (invoice_id,))

    def get_invoice_items(self, invoice_id: int):
        q = """
        SELECT ii.*, p.product_name, c.category_brand, c.model_name
        FROM invoice_items ii
        JOIN products p ON ii.product_id = p.product_id
        JOIN categories c ON p.category_id = c.category_id
        WHERE ii.invoice_id = ?
        ORDER BY ii.invoice_item_id
        """
        return self.db.fetchall(q, (invoice_id,))

    def get_invoice_statistics(self):
        stats = {}
        total = self.db.fetchone("SELECT COUNT(*) as count FROM invoices")
        stats['total_invoices'] = total['count'] if total else 0
        total_amount = self.db.fetchone("SELECT SUM(subtotal + shipping_fee - discount_amount) as total FROM invoices")
        stats['total_amount'] = total_amount['total'] if total_amount and total_amount['total'] else 0
        by_payment = self.db.fetchall("""
            SELECT payment_method, COUNT(*) as count, SUM(subtotal + shipping_fee - discount_amount) as total
            FROM invoices GROUP BY payment_method ORDER BY total DESC
        """)
        stats['by_payment'] = [dict(r) for r in by_payment]
        monthly_trend = self.db.fetchall("""
            SELECT strftime('%Y-%m', invoice_date) as month, COUNT(*) as invoice_count, SUM(subtotal + shipping_fee - discount_amount) as monthly_total
            FROM invoices WHERE invoice_date >= DATE('now', '-12 months')
            GROUP BY month ORDER BY month
        """)
        stats['monthly_trend'] = [dict(r) for r in monthly_trend]
        return stats
