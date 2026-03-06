import sqlite3
from pathlib import Path

DB_PATH = "inventory.db"

def seed_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("🔹 Inserting Roles...")
    cur.executemany("""
        INSERT OR IGNORE INTO roles (role_id, role_name, description)
        VALUES (?, ?, ?)
    """, [
        (1, 'Admin', 'Full system access'),
        (2, 'Store Manager', 'Manages store'),
        (3, 'Sales Staff', 'Handles sales'),
        (4, 'Inventory Manager', 'Manages inventory'),
        (5, 'Warehouse Staff', 'Warehouse operations'),
        (6, 'Accounts', 'Finance & billing'),
        (7, 'Support', 'Customer support'),
        (8, 'IT', 'System maintenance'),
        (9, 'Supervisor', 'Team supervision'),
        (10, 'Auditor', 'Audit & compliance'),
    ])

    print("🔹 Inserting Locations...")
    cur.executemany("""
        INSERT OR IGNORE INTO locations
        (location_id, location_name, location_type, address, managed_by)
        VALUES (?, ?, ?, ?, ?)
    """, [
        (1,'Main Store Karachi','store','Karachi',1),
        (2,'Lahore Store','store','Lahore',2),
        (3,'Islamabad Store','store','Islamabad',2),
        (4,'Central Warehouse','warehouse','Karachi Industrial Area',5),
        (5,'North Warehouse','warehouse','Lahore Industrial Zone',5),
        (6,'Online Platform','platform','https://shop.com',1),
        (7,'Hyderabad Store','store','Hyderabad',2),
        (8,'Multan Store','store','Multan',2),
        (9,'Faisalabad Store','store','Faisalabad',2),
        (10,'Peshawar Store','store','Peshawar',2),
    ])

    print("🔹 Inserting Staff...")
    cur.executemany("""
        INSERT OR IGNORE INTO staff
        (staff_id, username, password_hash, staff_name, role_id, location_id,
         staff_contact, staff_email, staff_cnic, staff_bank_acno,
         staff_salary, staff_hiring_date, staff_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        (1,'admin','admin','System Admin',1,1,'0300-0000001','admin@sys.com','11111-1111111-1','1111111111111111',80000,'2024-01-01','active'),
        (2,'manager1','123','Ali Khan',2,1,'0300-0000002','ali@store.com','22222-2222222-2','2222222222222222',60000,'2024-02-01','active'),
        (3,'sales1','123','Sara Ahmed',3,1,'0300-0000003','sara@sales.com','33333-3333333-3','3333333333333333',45000,'2024-03-01','active'),
        (4,'inv1','123','Usman Tariq',4,4,'0300-0000004','usman@inv.com','44444-4444444-4','4444444444444444',50000,'2024-02-10','active'),
        (5,'wh1','123','Bilal Hussain',5,4,'0300-0000005','bilal@wh.com','55555-5555555-5','5555555555555555',40000,'2024-01-15','active'),
        (6,'acc1','123','Ayesha Noor',6,1,'0300-0000006','ayesha@acc.com','66666-6666666-6','6666666666666666',55000,'2024-03-05','active'),
        (7,'support1','123','Hamza Ali',7,6,'0300-0000007','hamza@support.com','77777-7777777-7','7777777777777777',42000,'2024-04-01','active'),
        (8,'it1','123','Zain Raza',8,1,'0300-0000008','zain@it.com','88888-8888888-8','8888888888888888',70000,'2024-01-20','active'),
        (9,'sup1','123','Imran Sheikh',9,2,'0300-0000009','imran@sup.com','99999-9999999-9','9999999999999999',48000,'2024-02-15','active'),
        (10,'audit1','123','Nadia Malik',10,1,'0300-0000010','nadia@audit.com','10101-0101010-1','1010101010101010',65000,'2024-03-10','active'),
    ])

    print("🔹 Inserting Categories...")
    cur.executemany("""
        INSERT OR IGNORE INTO categories
        (category_id, category_brand, model_name, product_type, screen_size, color)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        (1,'Dell','Latitude 5420','laptop',14,'Black'),
        (2,'HP','EliteBook 840','laptop',14,'Silver'),
        (3,'Lenovo','ThinkPad T14','laptop',14,'Black'),
        (4,'Apple','MacBook Pro M1','laptop',13.3,'Gray'),
        (5,'Acer','Aspire 5','laptop',15.6,'Black'),
        (6,'Asus','VivoBook','laptop',14,'Blue'),
        (7,'MSI','Modern 14','laptop',14,'Gray'),
        (8,'Dell','OptiPlex 7090','desktop',None,'Black'),
        (9,'HP','ProDesk 600','desktop',None,'Black'),
        (10,'Lenovo','ThinkCentre M70','desktop',None,'Black'),
    ])

    print("🔹 Inserting Suppliers...")
    cur.executemany("""
        INSERT OR IGNORE INTO suppliers
        (supplier_id, supplier_name, contact_no, email, warehouse_address, bank_ac_no)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        (1,'Tech Distributors','021-1111','info@tech.com','Karachi','1111'),
        (2,'Pak Computers','021-2222','sales@pak.com','Lahore','2222'),
        (3,'IT Hub','021-3333','info@ithub.com','Islamabad','3333'),
        (4,'Mega Traders','021-4444','mega@trade.com','Karachi','4444'),
        (5,'Digital World','021-5555','digital@world.com','Lahore','5555'),
        (6,'System House','021-6666','sys@house.com','Karachi','6666'),
        (7,'CompZone','021-7777','zone@comp.com','Multan','7777'),
        (8,'NextGen IT','021-8888','next@gen.com','Faisalabad','8888'),
        (9,'Hardware City','021-9999','hard@city.com','Peshawar','9999'),
        (10,'Byte Solutions','021-1010','byte@sol.com','Karachi','1010'),
    ])

    print("🔹 Inserting Products...")
    cur.executemany("""
        INSERT OR IGNORE INTO products
        (product_id, product_name, category_id, supplier_id, product_code,
         screen_size, color, processor, ram, primary_storage, gpu,
         cost_price, wholesale_price, sale_price, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        ('PROD101','Dell Latitude i5',1,1,'P101',14,'Black','i5','8GB','256GB SSD','Intel',80000,90000,110000,1),
        ('PROD102','HP EliteBook i7',2,2,'P102',14,'Silver','i7','16GB','512GB SSD','Intel',100000,115000,140000,1),
        ('PROD103','Lenovo T14 Ryzen',3,3,'P103',14,'Black','Ryzen 5','16GB','512GB SSD','AMD',95000,110000,135000,1),
        ('PROD104','MacBook M1',4,1,'P104',13.3,'Gray','M1','8GB','256GB SSD','Apple',120000,140000,170000,1),
        ('PROD105','Acer Aspire 5',5,4,'P105',15.6,'Black','i5','8GB','512GB SSD','Intel',70000,82000,99000,1),
        ('PROD106','Asus VivoBook',6,5,'P106',14,'Blue','i5','8GB','256GB SSD','Intel',75000,88000,105000,1),
        ('PROD107','MSI Modern',7,6,'P107',14,'Gray','i7','16GB','512GB SSD','Intel',105000,120000,145000,1),
        ('PROD108','Dell OptiPlex',8,7,'P108',None,'Black','i5','8GB','1TB HDD','Intel',65000,75000,92000,1),
        ('PROD109','HP ProDesk',9,8,'P109',None,'Black','i5','16GB','512GB SSD','Intel',70000,82000,99000,1),
        ('PROD110','Lenovo ThinkCentre',10,9,'P110',None,'Black','i7','16GB','1TB SSD','Intel',90000,105000,130000,1),
    ])

    conn.commit()
    conn.close()
    print("✅ SEEDING COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    seed_data()
