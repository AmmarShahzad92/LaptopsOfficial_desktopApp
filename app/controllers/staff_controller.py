# ---- StaffController ----
from app.models.staff import Staff

class StaffController:
    def __init__(self, db):
        self.db = db

    def create_staff(self, staff: Staff):
        staff.validate()
        existing_email = self.db.fetchone("SELECT staff_id FROM staff WHERE staff_email = ?", (staff.staff_email,))
        if existing_email:
            raise ValueError("Staff email already exists")
        existing_cnic = self.db.fetchone("SELECT staff_id FROM staff WHERE staff_cnic = ?", (staff.staff_cnic,))
        if existing_cnic:
            raise ValueError("Staff CNIC already exists")
        with self.db.conn:
            cur = self.db.execute("""INSERT INTO staff (staff_name, role_id, location_id, staff_contact, staff_email, staff_cnic, staff_bank_acno, staff_salary, staff_hiring_date, staff_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                  (staff.staff_name, staff.role_id, staff.location_id, staff.staff_contact, staff.staff_email, staff.staff_cnic, staff.staff_bank_acno, staff.staff_salary, staff.staff_hiring_date, staff.staff_status))
            return cur.lastrowid

    def update_staff(self, staff: Staff):
        staff.validate()
        with self.db.conn:
            self.db.execute("""UPDATE staff SET staff_name=?, role_id=?, location_id=?, staff_contact=?, staff_email=?, staff_cnic=?, staff_bank_acno=?, staff_salary=?, staff_hiring_date=?, staff_status=?, updated_at=CURRENT_TIMESTAMP WHERE staff_id = ?""",
                            (staff.staff_name, staff.role_id, staff.location_id, staff.staff_contact, staff.staff_email, staff.staff_cnic, staff.staff_bank_acno, staff.staff_salary, staff.staff_hiring_date, staff.staff_status, staff.staff_id))

    def delete_staff(self, staff_id: int):
        locations = self.db.fetchone("SELECT COUNT(*) as count FROM locations WHERE managed_by = ?", (staff_id,))
        if locations and locations['count'] > 0:
            raise ValueError("Cannot delete staff: They are managing locations")
        stocks = self.db.fetchone("SELECT COUNT(*) as count FROM stocks WHERE manager_id = ?", (staff_id,))
        if stocks and stocks['count'] > 0:
            raise ValueError("Cannot delete staff: They are managing stock")
        with self.db.conn:
            self.db.execute("UPDATE staff SET staff_status = 'inactive', updated_at=CURRENT_TIMESTAMP WHERE staff_id = ?", (staff_id,))

    def list_staff(self, active_only=True):
        q = """
        SELECT s.*, r.role_name, l.location_name, COUNT(DISTINCT lm.location_id) as locations_managed, COUNT(DISTINCT st.stock_id) as stocks_managed
        FROM staff s JOIN roles r ON s.role_id = r.role_id JOIN locations l ON s.location_id = l.location_id
        LEFT JOIN locations lm ON s.staff_id = lm.managed_by
        LEFT JOIN stocks st ON s.staff_id = st.manager_id
        WHERE 1=1
        """
        params = []
        if active_only:
            q += " AND s.staff_status = 'active'"
        q += " GROUP BY s.staff_id ORDER BY s.staff_name"
        return self.db.fetchall(q, params)

    def get_staff(self, staff_id: int):
        q = """
        SELECT s.*, r.role_name, l.location_name, GROUP_CONCAT(DISTINCT lm.location_name) as locations_managed
        FROM staff s JOIN roles r ON s.role_id = r.role_id JOIN locations l ON s.location_id = l.location_id
        LEFT JOIN locations lm ON s.staff_id = lm.managed_by
        WHERE s.staff_id = ?
        GROUP BY s.staff_id
        """
        return self.db.fetchone(q, (staff_id,))

    def search_staff(self, search_term: str):
        q = """
        SELECT s.*, r.role_name, l.location_name
        FROM staff s JOIN roles r ON s.role_id = r.role_id JOIN locations l ON s.location_id = l.location_id
        WHERE (s.staff_name LIKE ? OR s.staff_contact LIKE ? OR s.staff_email LIKE ?) AND s.staff_status = 'active'
        ORDER BY s.staff_name
        """
        params = [f"%{search_term}%"] * 3
        return self.db.fetchall(q, params)

    def get_staff_statistics(self):
        stats = {}
        total = self.db.fetchone("SELECT COUNT(*) as count FROM staff WHERE staff_status = 'active'")
        stats['total_staff'] = total['count'] if total else 0
        by_role = self.db.fetchall("""
            SELECT r.role_name, COUNT(*) as count FROM staff s JOIN roles r ON s.role_id = r.role_id WHERE s.staff_status = 'active' GROUP BY r.role_id ORDER BY count DESC
        """)
        stats['by_role'] = [dict(r) for r in by_role]
        avg_salary = self.db.fetchone("SELECT AVG(staff_salary) as avg_salary FROM staff WHERE staff_status = 'active'")
        stats['avg_salary'] = avg_salary['avg_salary'] if avg_salary and avg_salary['avg_salary'] else 0
        by_experience = self.db.fetchall("""
            SELECT CASE WHEN staff_work_exp < 1 THEN 'Under 1 year' WHEN staff_work_exp < 3 THEN '1-3 years' WHEN staff_work_exp < 5 THEN '3-5 years' ELSE 'Over 5 years' END as experience, COUNT(*) as count
            FROM staff WHERE staff_status = 'active' GROUP BY experience ORDER BY count DESC
        """)
        stats['by_experience'] = [dict(r) for r in by_experience]
        return stats