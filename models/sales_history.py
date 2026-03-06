from datetime import datetime

class SalesHistory:
    def __init__(self, sh_id=None, sales_id=None, old_quantity=0,
                 new_quantity=0, old_amount=0.0, new_amount=0.0,
                 change_type=None, changed_by=None, changed_at=None, remarks=None):
        self.sh_id = sh_id
        self.sales_id = sales_id
        self.old_quantity = old_quantity
        self.new_quantity = new_quantity
        self.old_amount = old_amount
        self.new_amount = new_amount
        self.change_type = change_type
        self.changed_by = changed_by
        self.changed_at = changed_at or datetime.now()
        self.remarks = remarks

    def validate(self):
        if not self.sales_id:
            raise ValueError("Sales ID is required.")
        if not self.change_type or self.change_type not in ('add', 'edit', 'delete'):
            raise ValueError("Change type must be one of: add, edit, delete.")
        if not self.changed_by:
            raise ValueError("Changed by (staff ID) is required.")
        return True