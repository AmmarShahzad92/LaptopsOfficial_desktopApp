# from app.models.categories import Category

# class CategoryController:
#     def __init__(self, db):
#         self.db = db

#     def create_category(self, category: Category):
#         """Create a new category"""
#         try:
#             category.validate()
            
#             # Check if category already exists
#             existing = self.db.fetchone(
#                 """SELECT category_id FROM categories 
#                    WHERE category_brand = ? AND model_name = ? AND product_type = ?""",
#                 (category.category_brand, category.model_name, category.product_type)
#             )
            
#             if existing:
#                 raise ValueError("Category already exists")
            
#             with self.db.conn:
#                 cursor = self.db.execute(
#                     """INSERT INTO categories 
#                        (category_brand, model_name, product_type, 
#                         screen_size, color)
#                        VALUES (?, ?, ?, ?, ?)""",
#                     (category.category_brand, category.model_name, 
#                      category.product_type, category.screen_size, 
#                      category.color)
#                 )
#                 category_id = cursor.lastrowid
#                 return category_id
#         except Exception as e:
#             raise e

#     def update_category(self, category: Category):
#         """Update an existing category"""
#         try:
#             category.validate()
            
#             with self.db.conn:
#                 self.db.execute(
#                     """UPDATE categories 
#                        SET category_brand = ?, model_name = ?, 
#                            product_type = ?, screen_size = ?, 
#                            color = ?, updated_at = CURRENT_TIMESTAMP
#                        WHERE category_id = ?""",
#                     (category.category_brand, category.model_name, 
#                      category.product_type, category.screen_size, 
#                      category.color, category.category_id)
#                 )
#         except Exception as e:
#             raise e

#     def delete_category(self, category_id: int):
#         """Delete a category (soft delete if referenced by products)"""
#         try:
#             # Check if category is used by products
#             products = self.db.fetchone(
#                 "SELECT COUNT(*) as count FROM products WHERE category_id = ?",
#                 (category_id,)
#             )
            
#             if products and products['count'] > 0:
#                 raise ValueError("Cannot delete category: It is being used by products")
            
#             with self.db.conn:
#                 self.db.execute(
#                     "DELETE FROM categories WHERE category_id = ?",
#                     (category_id,)
#                 )
#         except Exception as e:
#             raise e

#     def list_categories(self):
#         """Get all categories"""
#         query = """
#         SELECT c.*, 
#                COUNT(p.product_id) as product_count
#         FROM categories c
#         LEFT JOIN products p ON c.category_id = p.category_id
#         GROUP BY c.category_id
#         ORDER BY c.category_brand, c.model_name
#         """
#         return self.db.fetchall(query)

#     def get_category(self, category_id: int):
#         """Get a specific category by ID"""
#         query = """
#         SELECT c.*,
#                COUNT(p.product_id) as product_count,
#                GROUP_CONCAT(DISTINCT s.supplier_name) as suppliers
#         FROM categories c
#         LEFT JOIN products p ON c.category_id = p.category_id
#         LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
#         WHERE c.category_id = ?
#         GROUP BY c.category_id
#         """
#         return self.db.fetchone(query, (category_id,))

#     def search_categories(self, search_term: str):
#         """Search categories by brand or model name"""
#         query = """
#         SELECT c.*,
#                COUNT(p.product_id) as product_count
#         FROM categories c
#         LEFT JOIN products p ON c.category_id = p.category_id
#         WHERE c.category_brand LIKE ? OR c.model_name LIKE ?
#         GROUP BY c.category_id
#         ORDER BY c.category_brand, c.model_name
#         """
#         params = [f"%{search_term}%", f"%{search_term}%"]
#         return self.db.fetchall(query, params)

#     def get_category_statistics(self):
#         """Get category statistics"""
#         stats = {}
        
#         # Total categories
#         total = self.db.fetchone("SELECT COUNT(*) as count FROM categories")
#         stats['total_categories'] = total['count']
        
#         # Categories by product type
#         by_type = self.db.fetchall("""
#             SELECT product_type, COUNT(*) as count 
#             FROM categories 
#             GROUP BY product_type 
#             ORDER BY count DESC
#         """)
#         stats['by_product_type'] = [dict(row) for row in by_type]
        
#         # Top brands
#         top_brands = self.db.fetchall("""
#             SELECT category_brand, COUNT(*) as count 
#             FROM categories 
#             GROUP BY category_brand 
#             ORDER BY count DESC 
#             LIMIT 10
#         """)
#         stats['top_brands'] = [dict(row) for row in top_brands]
        
#         return stats

from datetime import datetime
import json

# ---- CategoryController ----
from app.models.categories import Category

class CategoryController:
    def __init__(self, db):
        self.db = db

    def create_category(self, category: Category):
        category.validate()
        # Unique constraint is (category_brand, model_name, product_type) in your DDL
        existing = self.db.fetchone(
            "SELECT category_id FROM categories WHERE category_brand=? AND model_name=? AND product_type=?",
            (category.category_brand, category.model_name, category.product_type)
        )
        if existing:
            raise ValueError("Category already exists")
        with self.db.conn:
            cur = self.db.execute(
                """INSERT INTO categories
                   (category_brand, model_name, product_type, screen_size, color)
                   VALUES (?, ?, ?, ?, ?)""",
                (category.category_brand, category.model_name, category.product_type,
                 category.screen_size, category.color)
            )
            return cur.lastrowid

    def update_category(self, category: Category):
        category.validate()
        with self.db.conn:
            self.db.execute(
                """UPDATE categories
                   SET category_brand=?, model_name=?, product_type=?, screen_size=?,
                       color=?, updated_at=CURRENT_TIMESTAMP
                   WHERE category_id=?""",
                (category.category_brand, category.model_name, category.product_type,
                 category.screen_size, category.color, category.category_id)
            )

    def delete_category(self, category_id: int):
        # Prevent deletion when products reference category
        products = self.db.fetchone(
            "SELECT COUNT(*) as count FROM products WHERE category_id = ?",
            (category_id,)
        )
        if products and products['count'] > 0:
            raise ValueError("Cannot delete category: It is being used by products")
        with self.db.conn:
            self.db.execute("DELETE FROM categories WHERE category_id = ?", (category_id,))

    def list_categories(self):
        q = """
        SELECT c.*, COUNT(p.product_id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.category_id = p.category_id
        GROUP BY c.category_id
        ORDER BY c.category_brand, c.model_name
        """
        return self.db.fetchall(q)

    def get_category(self, category_id: int):
        q = """
        SELECT c.*,
               COUNT(p.product_id) as product_count,
               GROUP_CONCAT(DISTINCT s.supplier_name) as suppliers
        FROM categories c
        LEFT JOIN products p ON c.category_id = p.category_id
        LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
        WHERE c.category_id = ?
        GROUP BY c.category_id
        """
        return self.db.fetchone(q, (category_id,))

    def search_categories(self, search_term: str):
        q = """
        SELECT c.*, COUNT(p.product_id) as product_count
        FROM categories c
        LEFT JOIN products p ON c.category_id = p.category_id
        WHERE c.category_brand LIKE ? OR c.model_name LIKE ?
        GROUP BY c.category_id
        ORDER BY c.category_brand, c.model_name
        """
        params = [f"%{search_term}%", f"%{search_term}%"]
        return self.db.fetchall(q, params)

    def get_category_statistics(self):
        stats = {}
        total = self.db.fetchone("SELECT COUNT(*) as count FROM categories")
        stats['total_categories'] = total['count'] if total else 0
        by_type = self.db.fetchall("""
            SELECT product_type, COUNT(*) as count FROM categories
            GROUP BY product_type ORDER BY count DESC
        """)
        stats['by_product_type'] = [dict(r) for r in by_type]
        top_brands = self.db.fetchall("""
            SELECT category_brand, COUNT(*) as count FROM categories
            GROUP BY category_brand ORDER BY count DESC LIMIT 10
        """)
        stats['top_brands'] = [dict(r) for r in top_brands]
        return stats

