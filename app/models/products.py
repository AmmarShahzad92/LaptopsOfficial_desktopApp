from datetime import datetime

class Product:
    def __init__(self, product_id=None, product_name=None, category_id=None,
                 supplier_id=None, screen_size=None, color=None, processor=None,
                 ram=None, primary_storage=None, secondary_storage=None, gpu=None,
                 cost_price=0.0, wholesale_price=0.0, sale_price=0.0,
                 is_active=True, created_at=None, updated_at=None):
        self.product_id = product_id
        self.product_name = product_name
        self.category_id = category_id
        self.supplier_id = supplier_id
        self.screen_size = screen_size
        self.color = color
        self.processor = processor
        self.ram = ram
        self.primary_storage = primary_storage
        self.secondary_storage = secondary_storage
        self.gpu = gpu
        self.cost_price = cost_price
        self.wholesale_price = wholesale_price
        self.sale_price = sale_price
        self.is_active = is_active
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def validate(self):
        if not self.product_name or not self.product_name.strip():
            raise ValueError("Product name is required.")
        if not self.category_id:
            raise ValueError("Category is required.")
        if not self.supplier_id:
            raise ValueError("Supplier is required.")
        
        # Price validation
        if self.cost_price < 0:
            raise ValueError("Cost price cannot be negative.")
        if self.wholesale_price < self.cost_price:
            raise ValueError("Wholesale price must be >= cost price.")
        if self.sale_price < self.wholesale_price:
            raise ValueError("Sale price must be >= wholesale price.")
        
        # Screen size validation
        if self.screen_size and self.screen_size not in (13.3, 14, 15.6, 17):
            raise ValueError("Screen size must be one of: 13.3, 14, 15.6, 17 inches.")
        
        return True

    @classmethod
    def from_dict(cls, data):
        return cls(
            product_id=data.get('product_id'),
            product_name=data.get('product_name'),
            category_id=data.get('category_id'),
            supplier_id=data.get('supplier_id'),
            screen_size=data.get('screen_size'),
            color=data.get('color'),
            processor=data.get('processor'),
            ram=data.get('ram'),
            primary_storage=data.get('primary_storage'),
            secondary_storage=data.get('secondary_storage'),
            gpu=data.get('gpu'),
            cost_price=data.get('cost_price', 0.0),
            wholesale_price=data.get('wholesale_price', 0.0),
            sale_price=data.get('sale_price', 0.0),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )