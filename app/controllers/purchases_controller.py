from app.models.purchases import Purchase
from datetime import datetime

class PurchaseController:
    def __init__(self, db):
        self.db = db

    def create_purchase(self, purchase: Purchase):
        """Create a new purchase"""
        try:
            purchase.validate()
            
            with self.db.conn:
                cursor = self.db.execute(
                    """INSERT INTO purchases 
                       (supplier_id, product_id, quantity, unit_cost,
                        received_by, location_id, remarks)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (purchase.supplier_id, purchase.product_id,
                     purchase.quantity, purchase.unit_cost,
                     purchase.received_by, purchase.location_id,
                     purchase.remarks)
                )
                purchase_id = cursor.lastrowid
                
                # Add stock to location
                self._add_stock_from_purchase(purchase)
                
                # Update inventory
                self._update_inventory_from_purchase(purchase)
                
                return purchase_id
        except Exception as e:
            raise e

    def _add_stock_from_purchase(self, purchase: Purchase):
        """Add stock from purchase to location"""
        # Check if stock already exists at this location
        existing = self.db.fetchone(
            """SELECT stock_id, qty_stocked 
               FROM stocks 
               WHERE product_id = ? AND location_id = ?""",
            (purchase.product_id, purchase.location_id)
        )
        
        if existing:
            # Update existing stock
            new_qty = existing['qty_stocked'] + purchase.quantity
            self.db.execute(
                """UPDATE stocks 
                   SET qty_stocked = ?, unit_cost = ?, 
                       updated_at = CURRENT_TIMESTAMP
                   WHERE stock_id = ?""",
                (new_qty, purchase.unit_cost, existing['stock_id'])
            )
            
            # Record stock history
            self.db.execute(
                """INSERT INTO stocks_history 
                   (stock_id, product_id, location_id, old_qty, new_qty,
                    change_type, changed_by, remarks)
                   VALUES (?, ?, ?, ?, ?, 'add', ?, 'Purchase received')""",
                (existing['stock_id'], purchase.product_id, 
                 purchase.location_id, existing['qty_stocked'], new_qty,
                 purchase.received_by)
            )
        else:
            # Create new stock record
            cursor = self.db.execute(
                """INSERT INTO stocks 
                   (product_id, location_id, qty_stocked, unit_cost, manager_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (purchase.product_id, purchase.location_id,
                 purchase.quantity, purchase.unit_cost, purchase.received_by)
            )
            stock_id = cursor.lastrowid
            
            # Record stock history
            self.db.execute(
                """INSERT INTO stocks_history 
                   (stock_id, product_id, location_id, old_qty, new_qty,
                    change_type, changed_by, remarks)
                   VALUES (?, ?, ?, 0, ?, 'add', ?, 'Purchase received')""",
                (stock_id, purchase.product_id, purchase.location_id,
                 purchase.quantity, purchase.received_by)
            )

    def _update_inventory_from_purchase(self, purchase: Purchase):
        """Update inventory after purchase"""
        # Get total stock across all locations for this product
        total_stock = self.db.fetchone(
            """SELECT 
                  SUM(qty_stocked) as total_qty,
                  AVG(unit_cost) as avg_cost
               FROM stocks 
               WHERE product_id = ?""",
            (purchase.product_id,)
        )
        
        if total_stock:
            # Update or insert inventory record
            existing = self.db.fetchone(
                "SELECT inventory_id FROM inventory WHERE product_id = ?",
                (purchase.product_id,)
            )
            
            if existing:
                old_inventory = self.db.fetchone(
                    "SELECT total_qty FROM inventory WHERE product_id = ?",
                    (purchase.product_id,)
                )
                
                self.db.execute(
                    """UPDATE inventory 
                       SET total_qty = ?, unit_cost = ?, 
                           last_updated = CURRENT_TIMESTAMP
                       WHERE product_id = ?""",
                    (total_stock['total_qty'] or 0, 
                     total_stock['avg_cost'] or 0, purchase.product_id)
                )
                
                # Record inventory history
                self.db.execute(
                    """INSERT INTO inventory_history 
                       (inventory_id, product_id, old_total_qty, new_total_qty,
                        change_type, changed_by, remarks)
                       VALUES (?, ?, ?, ?, 'add', ?, 'Updated from purchase')""",
                    (existing['inventory_id'], purchase.product_id,
                     old_inventory['total_qty'] if old_inventory else 0,
                     total_stock['total_qty'] or 0, purchase.received_by)
                )
            else:
                cursor = self.db.execute(
                    """INSERT INTO inventory 
                       (product_id, total_qty, unit_cost)
                       VALUES (?, ?, ?)""",
                    (purchase.product_id, total_stock['total_qty'] or 0,
                     total_stock['avg_cost'] or 0)
                )
                
                # Record inventory history
                self.db.execute(
                    """INSERT INTO inventory_history 
                       (inventory_id, product_id, old_total_qty, new_total_qty,
                        change_type, changed_by, remarks)
                       VALUES (?, ?, 0, ?, 'add', ?, 'Created from purchase')""",
                    (cursor.lastrowid, purchase.product_id, 
                     total_stock['total_qty'] or 0, purchase.received_by)
                )

    def list_purchases(self, supplier_id=None, start_date=None, end_date=None):
        """List purchases with filters"""
        query = """
        SELECT 
            p.*,
            s.supplier_name,
            pr.product_name,
            pr.product_code,
            cat.category_brand,
            cat.model_name,
            loc.location_name,
            st.staff_name as received_by_name
        FROM purchases p
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        JOIN products pr ON p.product_id = pr.product_id
        JOIN categories cat ON pr.category_id = cat.category_id
        JOIN locations loc ON p.location_id = loc.location_id
        JOIN staff st ON p.received_by = st.staff_id
        WHERE 1=1
        """
        params = []
        
        if supplier_id:
            query += " AND p.supplier_id = ?"
            params.append(supplier_id)
        
        if start_date:
            query += " AND DATE(p.purchase_date) >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND DATE(p.purchase_date) <= ?"
            params.append(end_date)
        
        query += " ORDER BY p.purchase_date DESC"
        
        return self.db.fetchall(query, params)

    def get_purchase_statistics(self):
        """Get purchase statistics"""
        stats = {}
        
        # Total purchases
        total_purchases = self.db.fetchone("SELECT COUNT(*) as count FROM purchases")
        stats['total_purchases'] = total_purchases['count']
        
        # Total purchase amount
        total_amount = self.db.fetchone("SELECT SUM(total_amount) as total FROM purchases")
        stats['total_amount'] = total_amount['total'] if total_amount['total'] else 0
        
        # Purchases by supplier
        by_supplier = self.db.fetchall("""
            SELECT 
                s.supplier_name,
                COUNT(p.purchase_id) as purchase_count,
                SUM(p.total_amount) as total_amount
            FROM purchases p
            JOIN suppliers s ON p.supplier_id = s.supplier_id
            GROUP BY p.supplier_id
            ORDER BY total_amount DESC
        """)
        stats['by_supplier'] = [dict(row) for row in by_supplier]
        
        # Purchases by location
        by_location = self.db.fetchall("""
            SELECT 
                l.location_name,
                COUNT(p.purchase_id) as purchase_count,
                SUM(p.total_amount) as total_amount,
                SUM(p.quantity) as total_quantity
            FROM purchases p
            JOIN locations l ON p.location_id = l.location_id
            GROUP BY p.location_id
            ORDER BY total_amount DESC
        """)
        stats['by_location'] = [dict(row) for row in by_location]
        
        # Monthly purchase trend (last 12 months)
        monthly_trend = self.db.fetchall("""
            SELECT 
                strftime('%Y-%m', purchase_date) as month,
                COUNT(*) as purchase_count,
                SUM(total_amount) as monthly_total,
                SUM(quantity) as monthly_quantity
            FROM purchases
            WHERE purchase_date >= DATE('now', '-12 months')
            GROUP BY strftime('%Y-%m', purchase_date)
            ORDER BY month
        """)
        stats['monthly_trend'] = [dict(row) for row in monthly_trend]
        
        # Top products purchased
        top_products = self.db.fetchall("""
            SELECT 
                pr.product_name,
                pr.product_code,
                cat.category_brand,
                cat.model_name,
                COUNT(p.purchase_id) as purchase_count,
                SUM(p.quantity) as total_quantity,
                SUM(p.total_amount) as total_amount
            FROM purchases p
            JOIN products pr ON p.product_id = pr.product_id
            JOIN categories cat ON pr.category_id = cat.category_id
            GROUP BY p.product_id
            ORDER BY total_quantity DESC
            LIMIT 10
        """)
        stats['top_products'] = [dict(row) for row in top_products]
        
        return stats