from datetime import datetime

class Stock:
    def __init__(self, stock_id=None, product_id=None, location_id=None,
                 qty_stocked=0, unit_cost=0.0, manager_id=None,
                 created_at=None, updated_at=None):
        self.stock_id = stock_id
        self.product_id = product_id
        self.location_id = location_id
        self.qty_stocked = qty_stocked
        self.unit_cost = unit_cost
        self.stock_line_amount = qty_stocked * unit_cost  # Generated column
        self.manager_id = manager_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def validate(self):
        if not self.product_id:
            raise ValueError("Product ID is required.")
        if not self.location_id:
            raise ValueError("Location ID is required.")
        if self.qty_stocked < 0:
            raise ValueError("Quantity stocked cannot be negative.")
        if self.unit_cost < 0:
            raise ValueError("Unit cost cannot be negative.")
        return True

    @classmethod
    def from_dict(cls, data):
        return cls(
            stock_id=data.get('stock_id'),
            product_id=data.get('product_id'),
            location_id=data.get('location_id'),
            qty_stocked=data.get('qty_stocked', 0),
            unit_cost=data.get('unit_cost', 0.0),
            manager_id=data.get('manager_id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )