from datetime import datetime

class StockMovementRecord:
    def __init__(self, smr_id=None, product_id=None, from_location_id=None,
                 to_location_id=None, quantity_moved=0, unit_cost=0.0,
                 approved_by=None, movement_date=None, remarks=None):
        self.smr_id = smr_id
        self.product_id = product_id
        self.from_location_id = from_location_id
        self.to_location_id = to_location_id
        self.quantity_moved = quantity_moved
        self.unit_cost = unit_cost
        self.movement_amount = quantity_moved * unit_cost  # Generated column
        self.approved_by = approved_by
        self.movement_date = movement_date or datetime.now()
        self.remarks = remarks

    def validate(self):
        if not self.product_id:
            raise ValueError("Product ID is required.")
        if not self.from_location_id:
            raise ValueError("From location ID is required.")
        if not self.to_location_id:
            raise ValueError("To location ID is required.")
        if self.quantity_moved <= 0:
            raise ValueError("Quantity moved must be greater than 0.")
        if self.unit_cost < 0:
            raise ValueError("Unit cost cannot be negative.")
        if not self.approved_by:
            raise ValueError("Approved by (staff ID) is required.")
        return True