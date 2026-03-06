# test_categories.py
from app.database.db import Database

def test_database():
    print("Testing database connection...")
    db = Database("inventory.db")
    
    try:
        # Check if categories table exists
        categories = db.fetchall("SELECT * FROM categories")
        print(f"Number of categories found: {len(categories)}")
        
        for cat in categories:
            print(f"Category: {cat['category_brand']} {cat['model_name']} ({cat['product_type']})")
        
        # Check if products table exists
        products = db.fetchall("SELECT * FROM products WHERE is_active = 1")
        print(f"\nNumber of active products: {len(products)}")
        
        for prod in products:
            print(f"Product: {prod['product_name']} - ${prod['sale_price']}")
        
        # Check if suppliers table exists
        suppliers = db.fetchall("SELECT * FROM suppliers")
        print(f"\nNumber of suppliers: {len(suppliers)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_database()