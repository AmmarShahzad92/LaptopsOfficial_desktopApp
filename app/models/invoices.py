from datetime import datetime

class Invoice:
    def __init__(self, invoice_id=None, order_id=None, customer_id=None,
                 customer_name=None, customer_contact=None, customer_email=None,
                 invoice_date=None, payment_method=None, delivery_method=None,
                 subtotal=0.0, shipping_fee=0.0, discount_amount=0.0,
                 created_by=None, location_id=None, notes=None,
                 created_at=None, updated_at=None):
        self.invoice_id = invoice_id
        self.order_id = order_id
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.customer_contact = customer_contact
        self.customer_email = customer_email
        self.invoice_date = invoice_date or datetime.now()
        self.payment_method = payment_method
        self.delivery_method = delivery_method
        self.subtotal = subtotal
        self.shipping_fee = shipping_fee
        self.discount_amount = discount_amount
        self.grand_total = subtotal + shipping_fee - discount_amount  # Generated
        self.created_by = created_by
        self.location_id = location_id
        self.notes = notes
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def validate(self):
        if not self.payment_method or self.payment_method not in ('cash', 'card', 'bank_transfer'):
            raise ValueError("Payment method must be 'cash', 'card', or 'bank_transfer'.")
        if self.subtotal < 0:
            raise ValueError("Subtotal cannot be negative.")
        if self.shipping_fee < 0:
            raise ValueError("Shipping fee cannot be negative.")
        if self.discount_amount < 0:
            raise ValueError("Discount amount cannot be negative.")
        if not self.created_by:
            raise ValueError("Created by (staff ID) is required.")
        if not self.location_id:
            raise ValueError("Location ID is required.")
        return True