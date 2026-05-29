from datetime import datetime

class Category:
    def __init__(self, category_id=None, category_brand=None, model_name=None, 
                 product_type=None, screen_size=None, color=None,
                 created_at=None, updated_at=None):
        self.category_id = category_id
        self.category_brand = category_brand
        self.model_name = model_name
        self.product_type = product_type
        self.screen_size = screen_size
        self.color = color
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def validate(self):
        """Validate category data"""
        if not self.category_brand or not self.category_brand.strip():
            raise ValueError("Category brand is required.")
        if not self.model_name or not self.model_name.strip():
            raise ValueError("Model name is required.")
        if self.product_type not in ('laptop', 'desktop', 'tower'):
            raise ValueError("Type must be one of: 'laptop', 'desktop', 'tower'.")
        return True

    @classmethod
    def from_dict(cls, data):
        """Create Category instance from dictionary"""
        return cls(
            category_id=data.get('category_id'),
            category_brand=data.get('category_brand'),
            model_name=data.get('model_name'),
            product_type=data.get('product_type'),
            screen_size=data.get('screen_size'),
            color=data.get('color'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )