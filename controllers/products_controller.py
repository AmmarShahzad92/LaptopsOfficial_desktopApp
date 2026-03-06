from app.models.products import Product

class ProductController:
    def __init__(self, db):
        self.db = db

    def create_product(self, product: Product):
        product.validate()
        
        # Generate product_id manually since it's TEXT PRIMARY KEY
        # Get the next available product_id
        last_product = self.db.fetchone("SELECT product_id FROM products WHERE product_id LIKE 'PROD%' ORDER BY product_id DESC LIMIT 1")
        
        if last_product and last_product['product_id']:
            last_num = int(last_product['product_id'].replace('PROD', ''))
            new_num = last_num + 1
            product_id = f"PROD{new_num:03d}"
        else:
            product_id = "PROD001"
        
        # Generate product_code similarly
        product_code = product_id
        
        with self.db.conn:
            cur = self.db.execute(
                """INSERT INTO products
                (product_id, product_name, category_id, supplier_id, screen_size, color,
                    processor, ram, primary_storage, secondary_storage, gpu,
                    cost_price, wholesale_price, sale_price, is_active, product_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (product_id, product.product_name, product.category_id, product.supplier_id,
                product.screen_size, product.color, product.processor, product.ram,
                product.primary_storage, product.secondary_storage, product.gpu,
                product.cost_price, product.wholesale_price, product.sale_price,
                1 if product.is_active else 0, product_code)
            )
            
            # Also create an initial inventory entry
            self.db.execute(
                "INSERT INTO inventory (product_id, total_qty, unit_cost) VALUES (?, 0, ?)",
                (product_id, product.cost_price)
            )
            
            return product_id
    def update_product(self, product: Product):
        product.validate()
        with self.db.conn:
            # Update product fields
            self.db.execute(
                """UPDATE products SET
                       product_name=?, category_id=?, supplier_id=?, screen_size=?, color=?,
                       processor=?, ram=?, primary_storage=?, secondary_storage=?, gpu=?,
                       cost_price=?, wholesale_price=?, sale_price=?, is_active=?, updated_at=CURRENT_TIMESTAMP
                   WHERE product_id=?""",
                (product.product_name, product.category_id, product.supplier_id, product.screen_size, product.color,
                 product.processor, product.ram, product.primary_storage, product.secondary_storage, product.gpu,
                 product.cost_price, product.wholesale_price, product.sale_price, 1 if product.is_active else 0,
                 product.product_id)
            )

    def delete_product(self, product_id: int):
        # Check stock totals, not simply presence of stock records
        stock = self.db.fetchone("SELECT SUM(qty_stocked) as total_qty FROM stocks WHERE product_id = ?", (product_id,))
        if stock and stock['total_qty'] and stock['total_qty'] > 0:
            raise ValueError("Cannot delete product: There is stock for this product")
        sales = self.db.fetchone("SELECT COUNT(*) as count FROM sales WHERE product_id = ?", (product_id,))
        if sales and sales['count'] > 0:
            raise ValueError("Cannot delete product: It has sales records")
        with self.db.conn:
            # Soft delete: set is_active = 0
            self.db.execute("UPDATE products SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE product_id = ?", (product_id,))

    def list_products(self, active_only=True):
        q = """
        SELECT p.*, c.category_brand, c.model_name, c.product_type, s.supplier_name,
               COALESCE(i.total_qty,0) AS total_inventory, COALESCE(i.inventory_amount,0) AS inventory_value
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        LEFT JOIN inventory i ON p.product_id = i.product_id
        WHERE 1=1
        """
        params = []
        if active_only:
            q += " AND p.is_active = 1"
        q += " ORDER BY p.product_name"
        return self.db.fetchall(q, params)

    def get_product(self, product_id: int):
        q = """
        SELECT p.*, c.category_brand, c.model_name, c.product_type, s.supplier_name, s.contact_no as supplier_contact,
               COALESCE(i.total_qty,0) AS total_inventory, COALESCE(i.inventory_amount,0) AS inventory_value,
               COALESCE(SUM(st.qty_stocked),0) as total_stock,
               GROUP_CONCAT(DISTINCT l.location_name || ': ' || st.qty_stocked) as stock_locations
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        LEFT JOIN inventory i ON p.product_id = i.product_id
        LEFT JOIN stocks st ON p.product_id = st.product_id
        LEFT JOIN locations l ON st.location_id = l.location_id
        WHERE p.product_id = ?
        GROUP BY p.product_id
        """
        return self.db.fetchone(q, (product_id,))

    def search_products(self, search_term: str):
        q = """
        SELECT p.*, c.category_brand, c.model_name, s.supplier_name, COALESCE(i.total_qty,0) as total_inventory
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        LEFT JOIN inventory i ON p.product_id = i.product_id
        WHERE (p.product_name LIKE ? OR p.product_id LIKE ? OR c.category_brand LIKE ? OR c.model_name LIKE ? OR p.processor LIKE ? OR p.ram LIKE ?)
          AND p.is_active = 1
        ORDER BY p.product_name
        """
        params = [f"%{search_term}%"] * 6
        return self.db.fetchall(q, params)

    def get_product_statistics(self):
        stats = {}
        total = self.db.fetchone("SELECT COUNT(*) as count FROM products WHERE is_active = 1")
        stats['total_products'] = total['count'] if total else 0
        by_category = self.db.fetchall("""
            SELECT c.category_brand, c.model_name, COUNT(*) as count
            FROM products p JOIN categories c ON p.category_id = c.category_id
            WHERE p.is_active = 1
            GROUP BY c.category_id ORDER BY count DESC
        """)
        stats['by_category'] = [dict(r) for r in by_category]
        price_ranges = self.db.fetchall("""
            SELECT CASE WHEN sale_price < 1000 THEN 'Under $1000'
                        WHEN sale_price < 2000 THEN '$1000-$2000'
                        WHEN sale_price < 3000 THEN '$2000-$3000'
                        ELSE 'Over $3000' END as price_range, COUNT(*) as count
            FROM products WHERE is_active = 1 GROUP BY price_range ORDER BY count DESC
        """)
        stats['by_price_range'] = [dict(r) for r in price_ranges]
        low_stock = self.db.fetchall("""
            SELECT p.product_id, p.product_name, COALESCE(i.total_qty,0) as total_qty
            FROM products p JOIN inventory i ON p.product_id = i.product_id
            WHERE p.is_active = 1 AND i.total_qty <= 5 ORDER BY i.total_qty LIMIT 10
        """)
        stats['low_stock'] = [dict(r) for r in low_stock]
        return stats

