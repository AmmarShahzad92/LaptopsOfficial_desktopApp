from datetime import datetime

class OrderItem:
    def __init__(self, item_id=None, order_id=None, product_id=None,
                 qty=0, unit_price=0.0, created_at=None, updated_at=None):
        self.item_id = item_id
        self.order_id = order_id
        self.product_id = product_id
        self.qty = qty
        self.unit_price = unit_price
        self.order_line_amount = qty * unit_price  # Generated column in DB
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def validate(self):
        if not self.order_id:
            raise ValueError("Order ID is required.")
        if not self.product_id:
            raise ValueError("Product ID is required.")
        if self.qty <= 0:
            raise ValueError("Quantity must be greater than 0.")
        if self.unit_price < 0:
            raise ValueError("Unit price cannot be negative.")
        return True

    @classmethod
    def from_dict(cls, data):
        return cls(
            item_id=data.get('item_id'),
            order_id=data.get('order_id'),
            product_id=data.get('product_id'),
            qty=data.get('qty', 0),
            unit_price=data.get('unit_price', 0.0),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )