from datetime import datetime

class Order:
    def __init__(self, order_id=None, customer_id=None, order_date=None,
                 order_type=None, location_id=None, status='processing',
                 subtotal=0.0, shipping_fee=0.0, payment_method=None,
                 delivery_method=None, created_at=None, updated_at=None):
        self.order_id = order_id
        self.customer_id = customer_id
        self.order_date = order_date or datetime.now()
        self.order_type = order_type
        self.location_id = location_id
        self.status = status
        self.subtotal = subtotal
        self.shipping_fee = shipping_fee
        self.total = subtotal + shipping_fee  # Generated column in DB
        self.payment_method = payment_method
        self.delivery_method = delivery_method
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def validate(self):
        if not self.customer_id:
            raise ValueError("Customer ID is required.")
        if self.order_type not in ('online', 'physical'):
            raise ValueError("Order type must be 'online' or 'physical'.")
        if not self.location_id:
            raise ValueError("Location ID is required.")
        if self.status not in ('processing', 'delivered', 'returned'):
            raise ValueError("Status must be 'processing', 'delivered', or 'returned'.")
        if self.subtotal < 0:
            raise ValueError("Subtotal cannot be negative.")
        if self.shipping_fee < 0:
            raise ValueError("Shipping fee cannot be negative.")
        if self.payment_method not in ('cash', 'card', 'bank_transfer'):
            raise ValueError("Payment method must be 'cash', 'card', or 'bank_transfer'.")
        if self.delivery_method and self.delivery_method not in ('take_away', 'home_delivery'):
            raise ValueError("Delivery method must be 'take_away' or 'home_delivery'.")
        return True

    @classmethod
    def from_dict(cls, data):
        return cls(
            order_id=data.get('order_id'),
            customer_id=data.get('customer_id'),
            order_date=data.get('order_date'),
            order_type=data.get('order_type'),
            location_id=data.get('location_id'),
            status=data.get('status', 'processing'),
            subtotal=data.get('subtotal', 0.0),
            shipping_fee=data.get('shipping_fee', 0.0),
            payment_method=data.get('payment_method'),
            delivery_method=data.get('delivery_method'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )