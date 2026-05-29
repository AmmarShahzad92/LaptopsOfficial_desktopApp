import re
from datetime import datetime

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

class Supplier:
    def __init__(self, supplier_id=None, supplier_name=None, contact_no=None,
                 email=None, warehouse_address=None, bank_ac_no=None,
                 created_at=None, updated_at=None):
        self.supplier_id = supplier_id
        self.supplier_name = supplier_name
        self.contact_no = contact_no
        self.email = email
        self.warehouse_address = warehouse_address
        self.bank_ac_no = bank_ac_no
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def validate(self):
        if not self.supplier_name or not self.supplier_name.strip():
            raise ValueError("Supplier name is required.")
        if self.email and not is_valid_email(self.email):
            raise ValueError("Invalid email format.")
        if not self.contact_no or not self.contact_no.strip():
            raise ValueError("Contact number is required.")
        if not self.warehouse_address or not self.warehouse_address.strip():
            raise ValueError("Warehouse address is required.")
        if not self.bank_ac_no or not self.bank_ac_no.strip():
            raise ValueError("Bank account number is required.")
        return True

    @classmethod
    def from_dict(cls, data):
        return cls(
            supplier_id=data.get('supplier_id'),
            supplier_name=data.get('supplier_name'),
            contact_no=data.get('contact_no'),
            email=data.get('email'),
            warehouse_address=data.get('warehouse_address'),
            bank_ac_no=data.get('bank_ac_no'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )