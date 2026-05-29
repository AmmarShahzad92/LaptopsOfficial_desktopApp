from datetime import datetime

class StockMovementHistory:
    def __init__(self, smh_id=None, smr_id=None, product_id=None,
                 from_location_id=None, to_location_id=None,
                 old_quantity=0, new_quantity=0, change_type=None,
                 changed_by=None, changed_at=None, remarks=None):
        self.smh_id = smh_id
        self.smr_id = smr_id
        self.product_id = product_id
        self.from_location_id = from_location_id
        self.to_location_id = to_location_id
        self.old_quantity = old_quantity
        self.new_quantity = new_quantity
        self.change_type = change_type
        self.changed_by = changed_by
        self.changed_at = changed_at or datetime.now()
        self.remarks = remarks

    def validate(self):
        if not self.smr_id:
            raise ValueError("Stock movement record ID is required.")
        if not self.change_type or self.change_type not in ('add', 'remove', 'adjust'):
            raise ValueError("Change type must be one of: add, remove, adjust.")
        if not self.changed_by:
            raise ValueError("Changed by (staff ID) is required.")
        return True