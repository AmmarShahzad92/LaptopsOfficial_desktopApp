from datetime import datetime

class Staff:
    def __init__(self, staff_id=None, staff_name=None, role_id=None, location_id=None,
                 staff_contact=None, staff_email=None, staff_cnic=None,
                 staff_bank_acno=None, staff_salary=0.0, staff_hiring_date=None,
                 staff_status='active', created_at=None, updated_at=None, staff_work_exp=None):
        self.staff_id = staff_id
        self.staff_name = staff_name
        self.role_id = role_id
        self.staff_contact = staff_contact
        self.staff_email = staff_email
        self.staff_cnic = staff_cnic
        self.location_id = location_id
        self.staff_bank_acno = staff_bank_acno
        self.staff_salary = staff_salary
        self.staff_hiring_date = staff_hiring_date or datetime.now().date()
        self.staff_status = staff_status
        self.staff_work_exp = staff_work_exp
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def validate(self):
        if not self.staff_name or not self.staff_name.strip():
            raise ValueError("Staff name is required.")
        if not self.role_id:
            raise ValueError("Role is required.")
        if not self.staff_contact or not self.staff_contact.strip():
            raise ValueError("Contact number is required.")
        if not self.staff_email or not self.staff_email.strip():
            raise ValueError("Email is required.")
        if not self.staff_cnic or not self.staff_cnic.strip():
            raise ValueError("CNIC is required.")
        if not self.staff_bank_acno or not self.staff_bank_acno.strip():
            raise ValueError("Bank account number is required.")
        if not self.location_id:  # ADD THIS
            raise ValueError("Location is required.")
        if self.staff_salary < 0:
            raise ValueError("Salary cannot be negative.")
        if self.staff_status not in ('active', 'inactive', 'suspended'):
            raise ValueError("Status must be one of: active, inactive, suspended.")
        return True

    @classmethod
    def from_dict(cls, data):
        return cls(
            staff_id=data.get('staff_id'),
            staff_name=data.get('staff_name'),
            role_id=data.get('role_id'),
            staff_contact=data.get('staff_contact'),
            staff_email=data.get('staff_email'),
            staff_cnic=data.get('staff_cnic'),
            staff_bank_acno=data.get('staff_bank_acno'),
            staff_salary=data.get('staff_salary', 0.0),
            staff_hiring_date=data.get('staff_hiring_date'),
            staff_status=data.get('staff_status', 'active'),
            staff_work_exp=data.get('staff_work_exp'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )