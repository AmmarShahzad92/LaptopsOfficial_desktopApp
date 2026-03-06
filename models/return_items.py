from datetime import datetime

class ReturnItem:
    def __init__(self, ri_id=None, return_id=None, item_id=None,
                 qty_bought=0, qty_returned=0, unit_price=0.0,
                 notes=None, created_at=None, updated_at=None):
        self.ri_id = ri_id
        self.return_id = return_id
        self.item_id = item_id
        self.qty_bought = qty_bought
        self.qty_returned = qty_returned
        self.unit_price = unit_price
        self.return_line_amount = qty_returned * unit_price  # Generated column
        self.notes = notes
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def validate(self):
        if not self.return_id:
            raise ValueError("Return ID is required.")
        if not self.item_id:
            raise ValueError("Item ID is required.")
        if self.qty_bought < 0:
            raise ValueError("Quantity bought cannot be negative.")
        if self.qty_returned < 0 or self.qty_returned > self.qty_bought:
            raise ValueError("Quantity returned must be between 0 and quantity bought.")
        if self.unit_price < 0:
            raise ValueError("Unit price cannot be negative.")
        return True