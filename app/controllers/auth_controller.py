# app/controllers/auth_controller.py
import hashlib
from datetime import datetime
from app.models.user_model import User

class AuthController:
    def __init__(self, db):
        self.db = db
        self.current_user = None
    
    def authenticate(self, username, password):
        """Authenticate user and return User object if successful"""
        try:
            # Get user from database
            user_data = self.db.fetchone(
                """SELECT * FROM staff 
                   WHERE username = ? AND is_active = 1""",
                (username,)
            )
            
            if not user_data:
                return None
            
            user_data = dict(user_data)
            
            # Verify password
            password_hash = self._hash_password(password)
            if user_data['password_hash'] == password_hash:
                # Update last login
                self.db.execute(
                    "UPDATE staff SET last_login = CURRENT_TIMESTAMP WHERE staff_id = ?",
                    (user_data['staff_id'],)
                )
                self.db.conn.commit()
                
                # Create User object
                user = User.from_dict(user_data)
                self.current_user = user
                return user
            
            return None
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def _hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def change_password(self, user_id, old_password, new_password):
        """Change user password"""
        try:
            # Verify old password
            user = self.db.fetchone(
                "SELECT password_hash FROM staff WHERE staff_id = ?",
                (user_id,)
            )
            
            if not user:
                raise ValueError("User not found")
            
            if user['password_hash'] != self._hash_password(old_password):
                raise ValueError("Old password is incorrect")
            
            # Update password
            new_hash = self._hash_password(new_password)
            self.db.execute(
                "UPDATE staff SET password_hash = ? WHERE staff_id = ?",
                (new_hash, user_id)
            )
            self.db.conn.commit()
            return True
            
        except Exception as e:
            self.db.conn.rollback()
            raise e
    
    def create_user(self, user_data, created_by):
        """Create new user (Admin only)"""
        try:
            # Validate required fields
            required_fields = ['username', 'password', 'role', 'full_name']
            for field in required_fields:
                if field not in user_data or not user_data[field]:
                    raise ValueError(f"{field} is required")
            
            # Check if username exists
            existing = self.db.fetchone(
                "SELECT username FROM staff WHERE username = ?",
                (user_data['username'],)
            )
            if existing:
                raise ValueError("Username already exists")
            
            # Hash password
            password_hash = self._hash_password(user_data['password'])
            
            with self.db.conn:
                cursor = self.db.execute(
                    """INSERT INTO staff 
                       (username, password_hash, role, full_name, 
                        contact_no, email, created_by)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (user_data['username'], password_hash, user_data['role'],
                     user_data['full_name'], user_data.get('contact_no'),
                     user_data.get('email'), created_by)
                )
                return cursor.lastrowid
                
        except Exception as e:
            raise e
    
    def update_user(self, user_id, user_data):
        """Update user information"""
        try:
            with self.db.conn:
                # Build update query dynamically
                fields = []
                params = []
                
                if 'full_name' in user_data:
                    fields.append("full_name = ?")
                    params.append(user_data['full_name'])
                
                if 'contact_no' in user_data:
                    fields.append("contact_no = ?")
                    params.append(user_data['contact_no'])
                
                if 'email' in user_data:
                    fields.append("email = ?")
                    params.append(user_data['email'])
                
                if 'role' in user_data:
                    if user_data['role'] not in ['Admin', 'StoreManager', 'SalesStaff']:
                        raise ValueError("Invalid role")
                    fields.append("role = ?")
                    params.append(user_data['role'])
                
                if 'is_active' in user_data:
                    fields.append("is_active = ?")
                    params.append(int(user_data['is_active']))
                
                if not fields:
                    return  # Nothing to update
                
                params.append(user_id)
                query = f"UPDATE staff SET {', '.join(fields)} WHERE staff_id = ?"
                self.db.execute(query, params)
                
        except Exception as e:
            raise e
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
    
    def is_authenticated(self):
        """Check if user is authenticated"""
        return self.current_user is not None
    
    def has_permission(self, required_role):
        """Check if current user has required permission"""
        if not self.current_user:
            return False
        return self.current_user.has_permission(required_role)