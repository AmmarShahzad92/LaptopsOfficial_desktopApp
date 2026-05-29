# app/models/user_model.py
import hashlib
from datetime import datetime

class User:
    def __init__(self, user_id=None, username=None, password_hash=None, 
                 role=None, full_name=None, contact_no=None, email=None, 
                 is_active=True, last_login=None):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.role = role
        self.full_name = full_name
        self.contact_no = contact_no
        self.email = email
        self.is_active = is_active
        self.last_login = last_login or datetime.now()
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate(self):
        """Validate user data"""
        if not self.username or not self.username.strip():
            raise ValueError("Username is required.")
        if not self.password_hash:
            raise ValueError("Password hash is required.")
        if self.role not in ('Admin', 'StoreManager', 'SalesStaff'):
            raise ValueError("Role must be one of: Admin, StoreManager, SalesStaff.")
        if not self.full_name or not self.full_name.strip():
            raise ValueError("Full name is required.")
        return True
    
    def has_permission(self, required_role):
        """Check if user has required role permission"""
        role_hierarchy = {
            'SalesStaff': ['SalesStaff'],
            'StoreManager': ['SalesStaff', 'StoreManager'],
            'Admin': ['SalesStaff', 'StoreManager', 'Admin']
        }
        return required_role in role_hierarchy.get(self.role, [])
    
    @classmethod
    def from_dict(cls, data):
        """Create User instance from dictionary"""
        return cls(
            user_id=data.get('staff_id'),
            username=data.get('username'),
            password_hash=data.get('password_hash'),
            role=data.get('role'),
            full_name=data.get('full_name'),
            contact_no=data.get('contact_no'),
            email=data.get('email'),
            is_active=bool(data.get('is_active', True)),
            last_login=data.get('last_login')
        )