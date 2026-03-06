from datetime import datetime

class OrderHistory:
    def __init__(self, oh_id=None, order_id=None, customer_id=None,
                 order_date=None, order_type=None, location_id=None,
                 status=None, subtotal=0.0, shipping_fee=0.0, total=0.0,
                 payment_method=None, delivery_method=None, changed_at=None,
                 changed_by=None, change_type=None, remarks=None):
        self.oh_id = oh_id
        self.order_id = order_id
        self.customer_id = customer_id
        self.order_date = order_date
        self.order_type = order_type
        self.location_id = location_id
        self.status = status
        self.subtotal = subtotal
        self.shipping_fee = shipping_fee
        self.total = total
        self.payment_method = payment_method
        self.delivery_method = delivery_method
        self.changed_at = changed_at or datetime.now()
        self.changed_by = changed_by
        self.change_type = change_type
        self.remarks = remarks

    def validate(self):
        if not self.order_id:
            raise ValueError("Order ID is required.")
        if not self.change_type or self.change_type not in ('add', 'edit', 'delete'):
            raise ValueError("Change type must be one of: add, edit, delete.")
        if not self.changed_by:
            raise ValueError("Changed by (staff ID) is required.")
        return True