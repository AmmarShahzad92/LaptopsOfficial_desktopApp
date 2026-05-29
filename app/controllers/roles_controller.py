# from app.models.roles import Role

# class RoleController:
#     def __init__(self, db):
#         self.db = db

#     def create_role(self, role: Role):
#         """Create a new role"""
#         try:
#             role.validate()
            
#             # Check if role already exists
#             existing = self.db.fetchone(
#                 "SELECT role_id FROM roles WHERE role_name = ?",
#                 (role.role_name,)
#             )
            
#             if existing:
#                 raise ValueError("Role already exists")
            
#             with self.db.conn:
#                 cursor = self.db.execute(
#                     """INSERT INTO roles (role_name, description)
#                        VALUES (?, ?)""",
#                     (role.role_name, role.description)
#                 )
#                 role_id = cursor.lastrowid
#                 return role_id
#         except Exception as e:
#             raise e

#     def update_role(self, role: Role):
#         """Update an existing role"""
#         try:
#             role.validate()
            
#             with self.db.conn:
#                 self.db.execute(
#                     """UPDATE roles 
#                        SET role_name = ?, description = ?, 
#                            updated_at = CURRENT_TIMESTAMP
#                        WHERE role_id = ?""",
#                     (role.role_name, role.description, role.role_id)
#                 )
#         except Exception as e:
#             raise e

#     def delete_role(self, role_id: int):
#         """Delete a role (check for references first)"""
#         try:
#             # Check if role is used by staff
#             staff_count = self.db.fetchone(
#                 "SELECT COUNT(*) as count FROM staff WHERE role_id = ?",
#                 (role_id,)
#             )
            
#             if staff_count and staff_count['count'] > 0:
#                 raise ValueError("Cannot delete role: It is being used by staff")
            
#             with self.db.conn:
#                 self.db.execute(
#                     "DELETE FROM roles WHERE role_id = ?",
#                     (role_id,)
#                 )
#         except Exception as e:
#             raise e

#     def list_roles(self):
#         """Get all roles"""
#         query = """
#         SELECT r.*,
#                COUNT(s.staff_id) as staff_count
#         FROM roles r
#         LEFT JOIN staff s ON r.role_id = s.role_id
#         GROUP BY r.role_id
#         ORDER BY r.role_name
#         """
#         return self.db.fetchall(query)

#     def get_role(self, role_id: int):
#         """Get a specific role by ID"""
#         query = """
#         SELECT r.*,
#                COUNT(s.staff_id) as staff_count,
#                GROUP_CONCAT(s.staff_name) as staff_members
#         FROM roles r
#         LEFT JOIN staff s ON r.role_id = s.role_id
#         WHERE r.role_id = ?
#         GROUP BY r.role_id
#         """
#         return self.db.fetchone(query, (role_id,))

# ---- RoleController ----
from app.models.roles import Role

class RoleController:
    def __init__(self, db):
        self.db = db

    def create_role(self, role: Role):
        role.validate()
        existing = self.db.fetchone("SELECT role_id FROM roles WHERE role_name = ?", (role.role_name,))
        if existing:
            raise ValueError("Role already exists")
        with self.db.conn:
            cur = self.db.execute("INSERT INTO roles (role_name, description) VALUES (?, ?)", (role.role_name, role.description))
            return cur.lastrowid

    def update_role(self, role: Role):
        role.validate()
        with self.db.conn:
            self.db.execute("UPDATE roles SET role_name=?, description=?, updated_at=CURRENT_TIMESTAMP WHERE role_id=?", (role.role_name, role.description, role.role_id))

    def delete_role(self, role_id: int):
        staff_count = self.db.fetchone("SELECT COUNT(*) as count FROM staff WHERE role_id = ?", (role_id,))
        if staff_count and staff_count['count'] > 0:
            raise ValueError("Cannot delete role: It is being used by staff")
        with self.db.conn:
            self.db.execute("DELETE FROM roles WHERE role_id = ?", (role_id,))

    def list_roles(self):
        q = "SELECT r.*, COUNT(s.staff_id) as staff_count FROM roles r LEFT JOIN staff s ON r.role_id = s.role_id GROUP BY r.role_id ORDER BY r.role_name"
        return self.db.fetchall(q)

    def get_role(self, role_id: int):
        q = "SELECT r.*, COUNT(s.staff_id) as staff_count, GROUP_CONCAT(s.staff_name) as staff_members FROM roles r LEFT JOIN staff s ON r.role_id = s.role_id WHERE r.role_id = ? GROUP BY r.role_id"
        return self.db.fetchone(q, (role_id,))