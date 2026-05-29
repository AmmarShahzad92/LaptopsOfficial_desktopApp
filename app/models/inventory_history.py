from datetime import datetime

class InventoryHistory:
    def __init__(self, ih_id=None, inventory_id=None, product_id=None,
                 old_total_qty=0, new_total_qty=0, change_type=None,
                 changed_by=None, changed_at=None, remarks=None):
        self.ih_id = ih_id
        self.inventory_id = inventory_id
        self.product_id = product_id
        self.old_total_qty = old_total_qty
        self.new_total_qty = new_total_qty
        self.change_type = change_type
        self.changed_by = changed_by
        self.changed_at = changed_at or datetime.now()
        self.remarks = remarks

    def validate(self):
        if not self.inventory_id:
            raise ValueError("Inventory ID is required.")
        if not self.change_type or self.change_type not in ('add', 'remove', 'adjust'):
            raise ValueError("Change type must be one of: add, remove, adjust.")
        if not self.changed_by:
            raise ValueError("Changed by (staff ID) is required.")
        return True