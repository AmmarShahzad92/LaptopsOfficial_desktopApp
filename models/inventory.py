from datetime import datetime

class Inventory:
    def __init__(self, inventory_id=None, product_id=None, total_qty=0,
                 unit_cost=0.0, last_updated=None):
        self.inventory_id = inventory_id
        self.product_id = product_id
        self.total_qty = total_qty
        self.unit_cost = unit_cost
        self.inventory_amount = total_qty * unit_cost  # Generated column
        self.last_updated = last_updated or datetime.now()

    def validate(self):
        if not self.product_id:
            raise ValueError("Product ID is required.")
        if self.total_qty < 0:
            raise ValueError("Total quantity cannot be negative.")
        if self.unit_cost < 0:
            raise ValueError("Unit cost cannot be negative.")
        return True