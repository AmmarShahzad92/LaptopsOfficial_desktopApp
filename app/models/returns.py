from datetime import datetime

class Return:
    def __init__(self, return_id=None, order_id=None, customer_id=None,
                 location_id=None, return_date=None, order_date=None,
                 return_amount=0.0, return_reason=None, notes=None):
        self.return_id = return_id
        self.order_id = order_id
        self.customer_id = customer_id
        self.location_id = location_id
        self.return_date = return_date or datetime.now()
        self.order_date = order_date
        self.return_amount = return_amount
        self.return_reason = return_reason
        self.notes = notes

    def validate(self):
        if not self.order_id:
            raise ValueError("Order ID is required.")
        if not self.customer_id:
            raise ValueError("Customer ID is required.")
        if not self.location_id:
            raise ValueError("Location ID is required.")
        if not self.return_reason or self.return_reason not in ('damaged', 'wrong_order', 'warranty_claim'):
            raise ValueError("Return reason must be 'damaged', 'wrong_order', or 'warranty_claim'.")
        if self.return_amount < 0:
            raise ValueError("Return amount cannot be negative.")
        return True