# from app.models.user_model import User
# import hashlib
# from datetime import datetime

# class UserController:
#     def __init__(self, db):
#         self.db = db
    
#     def authenticate_user(self, username: str, password: str):
#         """Authenticate user using staff table"""
#         try:
#             # In your case, we'll use staff_email as username
#             staff = self.db.fetchone(
#                 """SELECT s.*, r.role_name 
#                    FROM staff s 
#                    JOIN roles r ON s.role_id = r.role_id
#                    WHERE s.staff_email = ? AND s.staff_status = 'active'""",
#                 (username,)
#             )
            
#             if not staff:
#                 return None
            
#             # Simple password check - in production, use proper hashing
#             # This is a placeholder - you should implement proper password hashing
#             # For now, we'll just check if password matches staff_id (demo)
#             if str(staff['staff_id']) == password:  # Replace with proper authentication
#                 user = User(
#                     user_id=staff['staff_id'],
#                     username=staff['staff_email'],
#                     role=staff['role_name'],
#                     full_name=staff['staff_name'],
#                     contact_no=staff['staff_contact'],
#                     email=staff['staff_email']
#                 )
                
#                 # Update last login
#                 self.db.execute(
#                     """UPDATE staff SET updated_at = CURRENT_TIMESTAMP 
#                        WHERE staff_id = ?""",
#                     (staff['staff_id'],)
#                 )
                
#                 return user
            
#             return None
#         except Exception as e:
#             raise e
    
#     def get_user_by_id(self, user_id: int):
#         """Get user by ID"""
#         staff = self.db.fetchone(
#             """SELECT s.*, r.role_name 
#                FROM staff s 
#                JOIN roles r ON s.role_id = r.role_id
#                WHERE s.staff_id = ?""",
#             (user_id,)
#         )
        
#         if staff:
#             return User(
#                 user_id=staff['staff_id'],
#                 username=staff['staff_email'],
#                 role=staff['role_name'],
#                 full_name=staff['staff_name'],
#                 contact_no=staff['staff_contact'],
#                 email=staff['staff_email']
#             )
#         return None
    
#     def change_password(self, user_id: int, new_password: str):
#         """Change user password"""
#         # This is a placeholder - implement proper password hashing
#         # In your current schema, there's no password field in staff table
#         # You need to add a password_hash field to staff table
        
#         # For now, we'll just update the timestamp
#         self.db.execute(
#             "UPDATE staff SET updated_at = CURRENT_TIMESTAMP WHERE staff_id = ?",
#             (user_id,)
#         )
#         return True
    
#     def get_user_permissions(self, user_id: int):
#         """Get user permissions based on role"""
#         staff = self.db.fetchone(
#             """SELECT s.*, r.role_name 
#                FROM staff s 
#                JOIN roles r ON s.role_id = r.role_id
#                WHERE s.staff_id = ?""",
#             (user_id,)
#         )
        
#         if not staff:
#             return []
        
#         role_permissions = {
#             'Admin': ['manage_staff', 'manage_products', 'manage_orders', 
#                      'manage_inventory', 'view_reports', 'manage_settings'],
#             'Store Manager': ['manage_products', 'manage_orders', 
#                             'manage_inventory', 'view_reports'],
#             'Sales Staff': ['manage_orders', 'view_products'],
#             'Inventory Manager': ['manage_inventory', 'view_products'],
#             'Warehouse Staff': ['view_inventory', 'manage_stock_movement']
#         }
        
#         return role_permissions.get(staff['role_name'], [])
    
#     def get_active_users(self):
#         """Get all active users (staff)"""
#         query = """
#         SELECT s.staff_id, s.staff_name, s.staff_email, r.role_name, 
#                s.staff_status, s.last_login
#         FROM staff s
#         JOIN roles r ON s.role_id = r.role_id
#         WHERE s.staff_status = 'active'
#         ORDER BY s.staff_name
#         """
#         return self.db.fetchall(query)

# ---- UserController (schema-safe demo) ----
from app.models.user_model import User

class UserController:
    def __init__(self, db):
        self.db = db

    def authenticate_user(self, username: str, password: str):
        staff = self.db.fetchone("SELECT s.*, r.role_name FROM staff s JOIN roles r ON s.role_id = r.role_id WHERE s.staff_email = ? AND s.staff_status = 'active'", (username,))
        if not staff:
            return None
        # Demo auth: check password equals staff_id string
        if str(staff['staff_id']) != password:
            return None
        # update last login / updated_at
        self.db.execute("UPDATE staff SET updated_at = CURRENT_TIMESTAMP WHERE staff_id = ?", (staff['staff_id'],))
        return User(user_id=staff['staff_id'], username=staff['staff_email'], role=staff['role_name'], full_name=staff['staff_name'], contact_no=staff['staff_contact'], email=staff['staff_email'])

    def get_user_by_id(self, user_id: int):
        staff = self.db.fetchone("SELECT s.*, r.role_name FROM staff s JOIN roles r ON s.role_id = r.role_id WHERE s.staff_id = ?", (user_id,))
        if staff:
            return User(user_id=staff['staff_id'], username=staff['staff_email'], role=staff['role_name'], full_name=staff['staff_name'], contact_no=staff['staff_contact'], email=staff['staff_email'])
        return None

    def change_password(self, user_id: int, new_password: str):
        # Placeholder: need `password_hash` in staff table to store real password; currently we just update timestamp
        self.db.execute("UPDATE staff SET updated_at = CURRENT_TIMESTAMP WHERE staff_id = ?", (user_id,))
        return True

    def get_user_permissions(self, user_id: int):
        staff = self.db.fetchone("SELECT s.*, r.role_name FROM staff s JOIN roles r ON s.role_id = r.role_id WHERE s.staff_id = ?", (user_id,))
        if not staff:
            return []
        role_permissions = {
            'Admin': ['manage_staff', 'manage_products', 'manage_orders', 'manage_inventory', 'view_reports', 'manage_settings'],
            'Store Manager': ['manage_products', 'manage_orders', 'manage_inventory', 'view_reports'],
            'Sales Staff': ['manage_orders', 'view_products'],
            'Inventory Manager': ['manage_inventory', 'view_products'],
            'Warehouse Staff': ['view_inventory', 'manage_stock_movement']
        }
        return role_permissions.get(staff['role_name'], [])

    def get_active_users(self):
        q = "SELECT s.staff_id, s.staff_name, s.staff_email, r.role_name, s.staff_status FROM staff s JOIN roles r ON s.role_id = r.role_id WHERE s.staff_status = 'active' ORDER BY s.staff_name"
        return self.db.fetchall(q)