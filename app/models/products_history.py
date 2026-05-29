from datetime import datetime

class ProductHistory:
    def __init__(self, ph_id=None, product_id=None, old_cost=None,
                 new_cost=None, old_wholesale=None, new_wholesale=None,
                 old_sale=None, new_sale=None, old_qty=None, new_qty=None,
                 change_type=None, changed_by=None, changed_at=None, remarks=None):
        self.ph_id = ph_id
        self.product_id = product_id
        self.old_cost = old_cost
        self.new_cost = new_cost
        self.old_wholesale = old_wholesale
        self.new_wholesale = new_wholesale
        self.old_sale = old_sale
        self.new_sale = new_sale
        self.old_qty = old_qty
        self.new_qty = new_qty
        self.change_type = change_type
        self.changed_by = changed_by
        self.changed_at = changed_at or datetime.now()
        self.remarks = remarks

    def validate(self):
        if not self.product_id:
            raise ValueError("Product ID is required.")
        if not self.change_type or self.change_type not in ('add', 'edit', 'delete'):
            raise ValueError("Change type must be one of: add, edit, delete.")
        if not self.changed_by:
            raise ValueError("Changed by (staff ID) is required.")
        return True