# from app.models.invoices import Invoice
# from app.models.invoice_items import InvoiceItem
# from datetime import datetime

# class InvoiceController:
#     def __init__(self, db):
#         self.db = db

#     def create_invoice(self, invoice: Invoice, items: list[InvoiceItem]):
#         """Create a new invoice"""
#         try:
#             invoice.validate()
            
#             # Validate items
#             for item in items:
#                 item.validate()
            
#             with self.db.conn:
#                 # Insert invoice
#                 cursor = self.db.execute(
#                     """INSERT INTO invoices 
#                        (order_id, customer_id, customer_name, customer_contact,
#                         customer_email, payment_method, delivery_method,
#                         subtotal, shipping_fee, discount_amount,
#                         created_by, location_id, notes)
#                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
#                     (invoice.order_id, invoice.customer_id,
#                      invoice.customer_name, invoice.customer_contact,
#                      invoice.customer_email, invoice.payment_method,
#                      invoice.delivery_method, invoice.subtotal,
#                      invoice.shipping_fee, invoice.discount_amount,
#                      invoice.created_by, invoice.location_id,
#                      invoice.notes)
#                 )
#                 invoice_id = cursor.lastrowid
                
#                 # Insert invoice items
#                 for item in items:
#                     self.db.execute(
#                         """INSERT INTO invoice_items 
#                            (invoice_id, order_item_id, product_id,
#                             quantity_sold, unit_price)
#                            VALUES (?, ?, ?, ?, ?)""",
#                         (invoice_id, item.order_item_id, item.product_id,
#                          item.quantity_sold, item.unit_price)
#                     )
                
#                 return invoice_id
#         except Exception as e:
#             raise e

#     def list_invoices(self, start_date=None, end_date=None):
#         """List invoices with filters"""
#         query = """
#         SELECT 
#             i.*,
#             c.customer_name,
#             c.contact_no as customer_phone,
#             l.location_name,
#             s.staff_name as created_by_name,
#             COUNT(ii.invoice_item_id) as item_count,
#             SUM(ii.quantity_sold) as total_qty
#         FROM invoices i
#         LEFT JOIN customers c ON i.customer_id = c.customer_id
#         JOIN locations l ON i.location_id = l.location_id
#         JOIN staff s ON i.created_by = s.staff_id
#         LEFT JOIN invoice_items ii ON i.invoice_id = ii.invoice_id
#         WHERE 1=1
#         """
#         params = []
        
#         if start_date:
#             query += " AND DATE(i.invoice_date) >= ?"
#             params.append(start_date)
        
#         if end_date:
#             query += " AND DATE(i.invoice_date) <= ?"
#             params.append(end_date)
        
#         query += " GROUP BY i.invoice_id ORDER BY i.invoice_date DESC"
        
#         return self.db.fetchall(query, params)

#     def get_invoice(self, invoice_id: int):
#         """Get a specific invoice with items"""
#         query = """
#         SELECT 
#             i.*,
#             c.customer_name,
#             c.contact_no as customer_phone,
#             c.email as customer_email,
#             c.address as customer_address,
#             l.location_name,
#             l.location_type,
#             s.staff_name as created_by_name,
#             s.staff_contact as created_by_contact
#         FROM invoices i
#         LEFT JOIN customers c ON i.customer_id = c.customer_id
#         JOIN locations l ON i.location_id = l.location_id
#         JOIN staff s ON i.created_by = s.staff_id
#         WHERE i.invoice_id = ?
#         """
#         return self.db.fetchone(query, (invoice_id,))

#     def get_invoice_items(self, invoice_id: int):
#         """Get items for a specific invoice"""
#         query = """
#         SELECT 
#             ii.*,
#             p.product_name,
#             c.category_brand,
#             c.model_name
#         FROM invoice_items ii
#         JOIN products p ON ii.product_id = p.product_id
#         JOIN categories c ON p.category_id = c.category_id
#         WHERE ii.invoice_id = ?
#         ORDER BY ii.invoice_item_id
#         """
#         return self.db.fetchall(query, (invoice_id,))
    
#     def get_invoice_statistics(self):
#         """Get invoice statistics"""
#         stats = {}
        
#         # Total invoices
#         total = self.db.fetchone("SELECT COUNT(*) as count FROM invoices")
#         stats['total_invoices'] = total['count']
        
#         # Total invoice amount
#         total_amount = self.db.fetchone("SELECT SUM(grand_total) as total FROM invoices")
#         stats['total_amount'] = total_amount['total'] if total_amount['total'] else 0
        
#         # Invoices by payment method
#         by_payment = self.db.fetchall("""
#             SELECT payment_method, COUNT(*) as count, SUM(grand_total) as total
#             FROM invoices
#             GROUP BY payment_method
#             ORDER BY total DESC
#         """)
#         stats['by_payment'] = [dict(row) for row in by_payment]
        
#         # Monthly invoice trend
#         monthly_trend = self.db.fetchall("""
#             SELECT 
#                 strftime('%Y-%m', invoice_date) as month,
#                 COUNT(*) as invoice_count,
#                 SUM(grand_total) as monthly_total
#             FROM invoices
#             WHERE invoice_date >= DATE('now', '-12 months')
#             GROUP BY strftime('%Y-%m', invoice_date)
#             ORDER BY month
#         """)
#         stats['monthly_trend'] = [dict(row) for row in monthly_trend]
        
#         return stats

# ---- InvoiceItemsController ----
# ---- InvoiceController ----
from app.models.invoices import Invoice
from app.models.invoice_items import InvoiceItem

class InvoiceController:
    def __init__(self, db):
        self.db = db

    def create_invoice_from_order(self, order_id: int, user_id: int, discount=0.0):
        """Create invoice from order with proper calculations"""
        with self.db.conn:
            # Get order details
            order = self.db.fetchone("""
                SELECT o.*, c.customer_name, c.contact_no, c.email, l.location_name
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                JOIN locations l ON o.location_id = l.location_id
                WHERE o.order_id = ?
            """, (order_id,))
            
            if not order:
                raise ValueError("Order not found")
            
            # Get order items
            items = self.db.fetchall("""
                SELECT oi.*, p.product_name, p.product_code
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = ?
            """, (order_id,))
            
            # Calculate subtotal
            subtotal = sum(item['order_line_amount'] for item in items)
            
            # Create invoice
            cur = self.db.execute("""
                INSERT INTO invoices 
                (order_id, customer_id, customer_name, customer_contact, customer_email,
                 payment_method, delivery_method, subtotal, shipping_fee, discount_amount,
                 created_by, location_id, invoice_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (order_id, order['customer_id'], order['customer_name'], 
                  order['contact_no'], order['email'], order['payment_method'],
                  order['delivery_method'], subtotal, order['shipping_fee'], 
                  discount, user_id, order['location_id']))
            
            invoice_id = cur.lastrowid
            
            # Create invoice items
            for item in items:
                self.db.execute("""
                    INSERT INTO invoice_items 
                    (invoice_id, order_item_id, product_id, quantity_sold, unit_price)
                    VALUES (?, ?, ?, ?, ?)
                """, (invoice_id, item['item_id'], item['product_id'], 
                      item['qty'], item['unit_price']))
            
            # Update order status
            self.db.execute("""
                UPDATE orders SET status = 'delivered', updated_at = CURRENT_TIMESTAMP
                WHERE order_id = ?
            """, (order_id,))
            
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

