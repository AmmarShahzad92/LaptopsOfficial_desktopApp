from datetime import datetime

class Role:
    def __init__(self, role_id=None, role_name=None, description=None,
                 created_at=None, updated_at=None):
        self.role_id = role_id
        self.role_name = role_name
        self.description = description
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def validate(self):
        if not self.role_name or not self.role_name.strip():
            raise ValueError("Role name is required.")
        return True