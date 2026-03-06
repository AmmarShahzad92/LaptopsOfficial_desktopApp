from datetime import datetime

class Customer:
    def __init__(self, customer_id=None, customer_name=None, contact_no=None,
                 email=None, address=None, created_at=None, updated_at=None):
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.contact_no = contact_no
        self.email = email
        self.address = address
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def validate(self):
        if not self.customer_name or not self.customer_name.strip():
            raise ValueError("Customer name is required.")
        return True

    @classmethod
    def from_dict(cls, data):
        return cls(
            customer_id=data.get('customer_id'),
            customer_name=data.get('customer_name'),
            contact_no=data.get('contact_no'),
            email=data.get('email'),
            address=data.get('address'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )