from datetime import datetime

class StockHistory:
    def __init__(self, sh_id=None, stock_id=None, product_id=None,
                 location_id=None, old_qty=0, new_qty=0,
                 change_type=None, changed_by=None, changed_at=None, remarks=None):
        self.sh_id = sh_id
        self.stock_id = stock_id
        self.product_id = product_id
        self.location_id = location_id
        self.old_qty = old_qty
        self.new_qty = new_qty
        self.change_type = change_type
        self.changed_by = changed_by
        self.changed_at = changed_at or datetime.now()
        self.remarks = remarks

    def validate(self):
        if not self.stock_id:
            raise ValueError("Stock ID is required.")
        if not self.change_type or self.change_type not in ('add', 'remove', 'adjust'):
            raise ValueError("Change type must be one of: add, remove, adjust.")
        if not self.changed_by:
            raise ValueError("Changed by (staff ID) is required.")
        return True