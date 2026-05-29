from datetime import datetime

class Location:
    def __init__(self, location_id=None, location_name=None, location_type=None,
                 address=None, contact_no=None, managed_by=None,
                 staff_capacity=0, location_status='active',
                 created_at=None, updated_at=None):
        self.location_id = location_id
        self.location_name = location_name
        self.location_type = location_type
        self.address = address
        self.contact_no = contact_no
        self.managed_by = managed_by
        self.staff_capacity = staff_capacity
        self.location_status = location_status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def validate(self):
        if not self.location_name or not self.location_name.strip():
            raise ValueError("Location name is required.")
        if self.location_type not in ('store', 'platform', 'warehouse'):
            raise ValueError("Location type must be 'store', 'platform', or 'warehouse'.")
        if self.staff_capacity < 0:
            raise ValueError("Staff capacity cannot be negative.")
        if self.location_status not in ('active', 'inactive', 'closed'):
            raise ValueError("Location status must be 'active', 'inactive', or 'closed'.")
        return True

    @classmethod
    def from_dict(cls, data):
        return cls(
            location_id=data.get('location_id'),
            location_name=data.get('location_name'),
            location_type=data.get('location_type'),
            address=data.get('address'),
            contact_no=data.get('contact_no'),
            managed_by=data.get('managed_by'),
            staff_capacity=data.get('staff_capacity', 0),
            location_status=data.get('location_status', 'active'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )