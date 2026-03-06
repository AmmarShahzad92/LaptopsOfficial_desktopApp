# initialize_database.py
from app.database.db import Database
import sqlite3

def initialize_data():
    print("Initializing database with essential data...")
    
    # Delete old database
    import os
    if os.path.exists("inventory.db"):
        os.remove("inventory.db")
        print("Old database removed")
    
    # Create new database
    db = Database("inventory.db")
    
    try:
        # Insert essential categories if not exists
        categories = [
            ('Dell', 'Latitude 5420', 'laptop', 14.0, 'Black'),
            ('HP', 'EliteBook 840', 'laptop', 14.0, 'Silver'),
            ('Lenovo', 'ThinkPad T14', 'laptop', 14.0, 'Black'),
            ('Apple', 'MacBook Pro', 'laptop', 13.3, 'Space Gray'),
        ]
        
        for cat in categories:
            db.execute(
                "INSERT OR IGNORE INTO categories (category_brand, model_name, product_type, screen_size, color) VALUES (?, ?, ?, ?, ?)",
                cat
            )
        
        print("Categories inserted successfully")
        
        # Insert suppliers
        suppliers = [
            ('Tech Distributors Ltd.', '+92-21-1234567', 'info@techdist.com', '789 Trade Center, Karachi', '1111222233334444'),
            ('Computer Solutions Inc.', '+92-21-9876543', 'sales@compsol.com', '321 Business Road, Lahore', '5555666677778888'),
        ]
        
        for sup in suppliers:
            db.execute(
                "INSERT OR IGNORE INTO suppliers (supplier_name, contact_no, email, warehouse_address, bank_ac_no) VALUES (?, ?, ?, ?, ?)",
                sup
            )
        
        print("Suppliers inserted successfully")
        
        db.conn.commit()
        print("Database initialized successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.conn.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    initialize_data()