from datetime import datetime

class Purchase:
    def __init__(self, purchase_id=None, supplier_id=None, product_id=None,
                 quantity=0, unit_cost=0.0, purchase_date=None,
                 received_by=None, location_id=None, remarks=None):
        self.purchase_id = purchase_id
        self.supplier_id = supplier_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_cost = unit_cost
        self.total_amount = quantity * unit_cost  # Generated column
        self.purchase_date = purchase_date or datetime.now()
        self.received_by = received_by
        self.location_id = location_id
        self.remarks = remarks

    def validate(self):
        if not self.supplier_id:
            raise ValueError("Supplier ID is required.")
        if not self.product_id:
            raise ValueError("Product ID is required.")
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        if self.unit_cost < 0:
            raise ValueError("Unit cost cannot be negative.")
        if not self.received_by:
            raise ValueError("Received by (staff ID) is required.")
        if not self.location_id:
            raise ValueError("Location ID is required.")
        return True

    @classmethod
    def from_dict(cls, data):
        return cls(
            purchase_id=data.get('purchase_id'),
            supplier_id=data.get('supplier_id'),
            product_id=data.get('product_id'),
            quantity=data.get('quantity', 0),
            unit_cost=data.get('unit_cost', 0.0),
            purchase_date=data.get('purchase_date'),
            received_by=data.get('received_by'),
            location_id=data.get('location_id'),
            remarks=data.get('remarks')
        )