from datetime import datetime

class Sale:
    def __init__(self, sales_id=None, order_id=None, order_item_id=None,
                 return_id=None, return_item_id=None, product_id=None,
                 quantity=0, cost_price=0.0, wholesale_price=0.0,
                 sales_price=0.0, amount=0.0, sale_date=None,
                 location_id=None, created_by=None, notes=None):
        self.sales_id = sales_id
        self.order_id = order_id
        self.order_item_id = order_item_id
        self.return_id = return_id
        self.return_item_id = return_item_id
        self.product_id = product_id
        self.quantity = quantity
        self.cost_price = cost_price
        self.wholesale_price = wholesale_price
        self.sales_price = sales_price
        self.amount = amount
        self.profit_loss = amount - (cost_price * quantity)  # Generated column
        self.sale_date = sale_date or datetime.now()
        self.location_id = location_id
        self.created_by = created_by
        self.notes = notes

    def validate(self):
        if not self.product_id:
            raise ValueError("Product ID is required.")
        if self.quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        if self.cost_price < 0:
            raise ValueError("Cost price cannot be negative.")
        if self.wholesale_price < 0:
            raise ValueError("Wholesale price cannot be negative.")
        if self.sales_price < 0:
            raise ValueError("Sales price cannot be negative.")
        if not self.location_id:
            raise ValueError("Location ID is required.")
        if not self.created_by:
            raise ValueError("Created by (staff ID) is required.")
        return True