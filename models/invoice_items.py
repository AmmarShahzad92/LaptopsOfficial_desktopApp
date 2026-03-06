from datetime import datetime

class InvoiceItem:
    def __init__(self, invoice_item_id=None, invoice_id=None, order_item_id=None,
                 product_id=None, quantity_sold=0, unit_price=0.0,
                 created_at=None, updated_at=None):
        self.invoice_item_id = invoice_item_id
        self.invoice_id = invoice_id
        self.order_item_id = order_item_id
        self.product_id = product_id
        self.quantity_sold = quantity_sold
        self.unit_price = unit_price
        self.line_total = quantity_sold * unit_price  # Generated column
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def validate(self):
        if not self.invoice_id:
            raise ValueError("Invoice ID is required.")
        if not self.product_id:
            raise ValueError("Product ID is required.")
        if self.quantity_sold <= 0:
            raise ValueError("Quantity sold must be greater than 0.")
        if self.unit_price < 0:
            raise ValueError("Unit price cannot be negative.")
        return True