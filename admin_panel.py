from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import styles
from widgets import *
from app.database.db import Database
 # Create Product object
from app.models.products import Product
from app.controllers.products_controller import ProductController

class AdminPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laptops Official - Admin Panel")
        self.setGeometry(150, 150, 1400, 900)
        
        # Initialize database connection
        self.db = Database("inventory.db")
        
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = SectionTitle("Laptops Official - Admin Panel")
        main_layout.addWidget(title)

        tagline = QLabel("Know It. Test It. Own It.")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet("font-size: 14px; color: #b0b0b0; margin-bottom: 8px;")
        main_layout.addWidget(tagline)
        
        # Tab widget for different modules
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_staff_tab()
        self.create_products_tab()
        self.create_customers_tab()
        self.create_suppliers_tab()
        self.create_locations_tab()
        self.create_roles_tab()
        self.create_dashboard_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
    def create_staff_tab(self):
        """Create staff management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search and buttons
        top_layout = QHBoxLayout()
        
        self.staff_search = SearchBox("Search staff...")
        self.staff_search.textEdited.connect(self.search_staff)  # Changed from textChanged
        top_layout.addWidget(self.staff_search)
        
        add_btn = ModernButton("Add New Staff")
        add_btn.clicked.connect(self.add_staff)
        top_layout.addWidget(add_btn)
        
        edit_btn = ModernButton("Edit Selected")
        edit_btn.clicked.connect(self.edit_staff)
        top_layout.addWidget(edit_btn)
        
        delete_btn = ModernButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_staff)
        top_layout.addWidget(delete_btn)
        
        refresh_btn = ModernButton("Refresh")
        refresh_btn.clicked.connect(self.load_staff)
        top_layout.addWidget(refresh_btn)
        
        layout.addLayout(top_layout)
        
        # Staff table
        self.staff_table = DataTable()
        self.staff_table.doubleClicked.connect(self.edit_staff)
        layout.addWidget(self.staff_table)
        
        self.tab_widget.addTab(tab, "👥 Staff Management")
        
    def create_products_tab(self):
        """Create products management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search and buttons
        top_layout = QHBoxLayout()
        
        self.product_search = SearchBox("Search products...")
        self.product_search.textEdited.connect(self.search_products)  # Changed from textChanged
        top_layout.addWidget(self.product_search)
        
        add_btn = ModernButton("Add New Product")
        add_btn.clicked.connect(self.add_product)
        top_layout.addWidget(add_btn)
        
        edit_btn = ModernButton("Edit Selected")
        edit_btn.clicked.connect(self.edit_product)
        top_layout.addWidget(edit_btn)
        
        delete_btn = ModernButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_product)
        top_layout.addWidget(delete_btn)
        
        import_btn = ModernButton("Import Products")
        top_layout.addWidget(import_btn)
        
        layout.addLayout(top_layout)
        
        # Products table
        self.products_table = DataTable()
        self.products_table.doubleClicked.connect(self.edit_product)
        layout.addWidget(self.products_table)
        
        self.tab_widget.addTab(tab, "📦 Product Management")
        
    def create_customers_tab(self):
        """Create customers management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search and buttons
        top_layout = QHBoxLayout()
        
        self.customer_search = SearchBox("Search customers...")
        self.customer_search.textEdited.connect(self.search_customers)  # Changed from textChanged
        top_layout.addWidget(self.customer_search)
        
        add_btn = ModernButton("Add New Customer")
        add_btn.clicked.connect(self.add_customer)
        top_layout.addWidget(add_btn)
        
        edit_btn = ModernButton("Edit Selected")
        edit_btn.clicked.connect(self.edit_customer)
        top_layout.addWidget(edit_btn)
        
        delete_btn = ModernButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_customer)
        top_layout.addWidget(delete_btn)
        
        layout.addLayout(top_layout)
        
        # Customers table
        self.customers_table = DataTable()
        self.customers_table.doubleClicked.connect(self.edit_customer)
        layout.addWidget(self.customers_table)
        
        self.tab_widget.addTab(tab, "👤 Customer Management")
        
    def create_suppliers_tab(self):
        """Create suppliers management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search and buttons
        top_layout = QHBoxLayout()
        
        self.supplier_search = SearchBox("Search suppliers...")
        self.supplier_search.textEdited.connect(self.search_suppliers)  # Changed from textChanged
        top_layout.addWidget(self.supplier_search)
        
        add_btn = ModernButton("Add New Supplier")
        add_btn.clicked.connect(self.add_supplier)
        top_layout.addWidget(add_btn)
        
        edit_btn = ModernButton("Edit Selected")
        edit_btn.clicked.connect(self.edit_supplier)
        top_layout.addWidget(edit_btn)
        
        delete_btn = ModernButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_supplier)
        top_layout.addWidget(delete_btn)
        
        layout.addLayout(top_layout)
        
        # Suppliers table
        self.suppliers_table = DataTable()
        self.suppliers_table.doubleClicked.connect(self.edit_supplier)
        layout.addWidget(self.suppliers_table)
        
        self.tab_widget.addTab(tab, "🏭 Supplier Management")
        
    def create_locations_tab(self):
        """Create locations management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search and buttons
        top_layout = QHBoxLayout()
        
        self.location_search = SearchBox("Search locations...")
        self.location_search.textEdited.connect(self.search_locations)  # Changed from textChanged
        top_layout.addWidget(self.location_search)
        
        add_btn = ModernButton("Add New Location")
        add_btn.clicked.connect(self.add_location)
        top_layout.addWidget(add_btn)
        
        edit_btn = ModernButton("Edit Selected")
        edit_btn.clicked.connect(self.edit_location)
        top_layout.addWidget(edit_btn)
        
        delete_btn = ModernButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_location)
        top_layout.addWidget(delete_btn)
        
        layout.addLayout(top_layout)
        
        # Locations table
        self.locations_table = DataTable()
        self.locations_table.doubleClicked.connect(self.edit_location)
        layout.addWidget(self.locations_table)
        
        self.tab_widget.addTab(tab, "📍 Location Management")
        
    def create_roles_tab(self):
        """Create roles management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search and buttons
        top_layout = QHBoxLayout()
        
        self.role_search = SearchBox("Search roles...")
        self.role_search.textEdited.connect(self.search_roles)  # Changed from textChanged
        top_layout.addWidget(self.role_search)
        
        add_btn = ModernButton("Add New Role")
        add_btn.clicked.connect(self.add_role)
        top_layout.addWidget(add_btn)
        
        edit_btn = ModernButton("Edit Selected")
        edit_btn.clicked.connect(self.edit_role)
        top_layout.addWidget(edit_btn)
        
        delete_btn = ModernButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_role)
        top_layout.addWidget(delete_btn)
        
        layout.addLayout(top_layout)
        
        # Roles table
        self.roles_table = DataTable()
        self.roles_table.doubleClicked.connect(self.edit_role)
        layout.addWidget(self.roles_table)
        
        self.tab_widget.addTab(tab, "👔 Role Management")
        
    def create_dashboard_tab(self):
        """Create dashboard tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Stats cards
        stats_layout = QGridLayout()
        
        # Total Staff
        self.staff_card = StatsCard("👥 Total Staff", "0", "#4CAF50")
        stats_layout.addWidget(self.staff_card, 0, 0)
        
        # Total Products
        self.products_card = StatsCard("📦 Total Products", "0", "#2196F3")
        stats_layout.addWidget(self.products_card, 0, 1)
        
        # Total Customers
        self.customers_card = StatsCard("👤 Total Customers", "0", "#FF9800")
        stats_layout.addWidget(self.customers_card, 0, 2)
        
        # Total Sales
        self.sales_card = StatsCard("💰 Total Sales", "$0", "#9C27B0")
        stats_layout.addWidget(self.sales_card, 1, 0)
        
        # Active Locations
        self.locations_card = StatsCard("📍 Active Locations", "0", "#F44336")
        stats_layout.addWidget(self.locations_card, 1, 1)
        
        # Suppliers
        self.suppliers_card = StatsCard("🏭 Suppliers", "0", "#009688")
        stats_layout.addWidget(self.suppliers_card, 1, 2)
        
        layout.addLayout(stats_layout)
        
        # Recent activity
        activity_label = QLabel("📊 Recent Activity")
        activity_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(activity_label)
        
        self.activity_table = DataTable()
        layout.addWidget(self.activity_table)
        
        self.tab_widget.addTab(tab, "📊 Dashboard")
        
    def load_data(self):
        """Load all data into tables"""
        self.load_staff()
        self.load_products()
        self.load_customers()
        self.load_suppliers()
        self.load_locations()
        self.load_roles()
        self.load_dashboard()
        
    def load_staff(self):
        """Load staff data from database"""
        try:
            staff = self.db.fetchall("""
                SELECT s.staff_id, s.username, s.staff_name, r.role_name, 
                       l.location_name, s.staff_contact, s.staff_email,
                       s.staff_status, s.staff_salary, s.staff_hiring_date
                FROM staff s
                JOIN roles r ON s.role_id = r.role_id
                JOIN locations l ON s.location_id = l.location_id
                ORDER BY s.staff_name
            """)
            
            # Create model
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels([
                'ID', 'Username', 'Name', 'Role', 'Location', 
                'Contact', 'Email', 'Status', 'Salary', 'Hire Date'
            ])
            
            for row in staff:
                status_item = QStandardItem(row['staff_status'])
                if row['staff_status'] == 'active':
                    status_item.setForeground(QColor('green'))
                elif row['staff_status'] == 'suspended':
                    status_item.setForeground(QColor('orange'))
                else:
                    status_item.setForeground(QColor('red'))
                
                salary_item = QStandardItem(f"${row['staff_salary']:,.2f}")
                salary_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                
                model.appendRow([
                    QStandardItem(str(row['staff_id'])),
                    QStandardItem(row['username'] or ''),
                    QStandardItem(row['staff_name']),
                    QStandardItem(row['role_name']),
                    QStandardItem(row['location_name']),
                    QStandardItem(row['staff_contact']),
                    QStandardItem(row['staff_email']),
                    status_item,
                    salary_item,
                    QStandardItem(row['staff_hiring_date'])
                ])
            
            self.staff_table.setModel(model)
            self.staff_table.resizeColumnsToContents()
            self.status_bar.showMessage(f"Loaded {len(staff)} staff members")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load staff: {str(e)}")
            
    def load_products(self):
        """Load products data from database"""
        try:
            products = self.db.fetchall("""
                SELECT p.product_id, p.product_code, p.product_name, 
                       c.category_brand, c.model_name, s.supplier_name,
                       p.cost_price, p.wholesale_price, p.sale_price,
                       p.is_active, p.created_at
                FROM products p
                JOIN categories c ON p.category_id = c.category_id
                JOIN suppliers s ON p.supplier_id = s.supplier_id
                WHERE p.is_active = 1
                ORDER BY p.product_name
            """)
            
            # Create model
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels([
                'ID', 'Code', 'Name', 'Brand', 'Model', 'Supplier',
                'Cost', 'Wholesale', 'Sale', 'Active', 'Created'
            ])
            
            for row in products:
                cost_item = QStandardItem(f"${row['cost_price']:,.2f}")
                wholesale_item = QStandardItem(f"${row['wholesale_price']:,.2f}")
                sale_item = QStandardItem(f"${row['sale_price']:,.2f}")
                
                for item in [cost_item, wholesale_item, sale_item]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                
                active_item = QStandardItem('Yes' if row['is_active'] else 'No')
                if row['is_active']:
                    active_item.setForeground(QColor('green'))
                else:
                    active_item.setForeground(QColor('red'))
                
                model.appendRow([
                    QStandardItem(str(row['product_id'])),
                    QStandardItem(row['product_code']),
                    QStandardItem(row['product_name']),
                    QStandardItem(row['category_brand']),
                    QStandardItem(row['model_name']),
                    QStandardItem(row['supplier_name']),
                    cost_item,
                    wholesale_item,
                    sale_item,
                    active_item,
                    QStandardItem(row['created_at'][:10])
                ])
            
            self.products_table.setModel(model)
            self.products_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load products: {str(e)}")
            
    def load_customers(self):
        """Load customers data from database"""
        try:
            customers = self.db.fetchall("""
                SELECT c.*, COUNT(o.order_id) as order_count,
                       COALESCE(SUM(o.total), 0) as total_spent
                FROM customers c
                LEFT JOIN orders o ON c.customer_id = o.customer_id
                GROUP BY c.customer_id
                ORDER BY c.customer_name
            """)
            
            # Create model
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels([
                'ID', 'Name', 'Contact', 'Email', 'Address', 'Orders', 'Total Spent', 'Created'
            ])
            
            for row in customers:
                total_spent_item = QStandardItem(f"${row['total_spent']:,.2f}")
                total_spent_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                
                model.appendRow([
                    QStandardItem(str(row['customer_id'])),
                    QStandardItem(row['customer_name']),
                    QStandardItem(row['contact_no'] or ''),
                    QStandardItem(row['email'] or ''),
                    QStandardItem(row['address'] or ''),
                    QStandardItem(str(row['order_count'])),
                    total_spent_item,
                    QStandardItem(row['created_at'][:10])
                ])
            
            self.customers_table.setModel(model)
            self.customers_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load customers: {str(e)}")
            
    def load_suppliers(self):
        """Load suppliers data from database"""
        try:
            suppliers = self.db.fetchall("""
                SELECT s.*, COUNT(p.product_id) as product_count,
                       COUNT(po.purchase_id) as purchase_count
                FROM suppliers s
                LEFT JOIN products p ON s.supplier_id = p.supplier_id
                LEFT JOIN purchases po ON s.supplier_id = po.supplier_id
                GROUP BY s.supplier_id
                ORDER BY s.supplier_name
            """)
            
            # Create model
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels([
                'ID', 'Name', 'Contact', 'Email', 'Warehouse', 'Bank Account', 'Products', 'Purchases'
            ])
            
            for row in suppliers:
                model.appendRow([
                    QStandardItem(str(row['supplier_id'])),
                    QStandardItem(row['supplier_name']),
                    QStandardItem(row['contact_no']),
                    QStandardItem(row['email'] or ''),
                    QStandardItem(row['warehouse_address']),
                    QStandardItem(row['bank_ac_no']),
                    QStandardItem(str(row['product_count'])),
                    QStandardItem(str(row['purchase_count']))
                ])
            
            self.suppliers_table.setModel(model)
            self.suppliers_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load suppliers: {str(e)}")
            
    def load_locations(self):
        """Load locations data from database"""
        try:
            locations = self.db.fetchall("""
                SELECT l.*, s.staff_name as manager_name,
                       COUNT(st.stock_id) as stock_items,
                       SUM(st.qty_stocked) as total_stock
                FROM locations l
                LEFT JOIN staff s ON l.managed_by = s.staff_id
                LEFT JOIN stocks st ON l.location_id = st.location_id
                WHERE l.location_status = 'active'
                GROUP BY l.location_id
                ORDER BY l.location_name
            """)
            
            # Create model
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels([
                'ID', 'Name', 'Type', 'Address', 'Contact', 
                'Manager', 'Staff Capacity', 'Stock Items', 'Total Stock', 'Status'
            ])
            
            for row in locations:
                status_item = QStandardItem(row['location_status'])
                if row['location_status'] == 'active':
                    status_item.setForeground(QColor('green'))
                elif row['location_status'] == 'closed':
                    status_item.setForeground(QColor('red'))
                else:
                    status_item.setForeground(QColor('orange'))
                
                model.appendRow([
                    QStandardItem(str(row['location_id'])),
                    QStandardItem(row['location_name']),
                    QStandardItem(row['location_type']),
                    QStandardItem(row['address'] or ''),
                    QStandardItem(row['contact_no'] or ''),
                    QStandardItem(row['manager_name'] or 'N/A'),
                    QStandardItem(str(row['staff_capacity'])),
                    QStandardItem(str(row['stock_items'])),
                    QStandardItem(str(row['total_stock'] or 0)),
                    status_item
                ])
            
            self.locations_table.setModel(model)
            self.locations_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load locations: {str(e)}")
            
    def load_roles(self):
        """Load roles data from database"""
        try:
            roles = self.db.fetchall("""
                SELECT r.*, COUNT(s.staff_id) as staff_count
                FROM roles r
                LEFT JOIN staff s ON r.role_id = s.role_id
                GROUP BY r.role_id
                ORDER BY r.role_name
            """)
            
            # Create model
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels([
                'ID', 'Role Name', 'Description', 'Staff Count', 'Created'
            ])
            
            for row in roles:
                model.appendRow([
                    QStandardItem(str(row['role_id'])),
                    QStandardItem(row['role_name']),
                    QStandardItem(row['description'] or ''),
                    QStandardItem(str(row['staff_count'])),
                    QStandardItem(row['created_at'][:10])
                ])
            
            self.roles_table.setModel(model)
            self.roles_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load roles: {str(e)}")
            
    def load_dashboard(self):
        """Load dashboard statistics"""
        try:
            # Get staff count
            staff_count = self.db.fetchone("SELECT COUNT(*) as count FROM staff WHERE staff_status = 'active'")
            self.staff_card.set_value(str(staff_count['count']))
            
            # Get product count
            product_count = self.db.fetchone("SELECT COUNT(*) as count FROM products WHERE is_active = 1")
            self.products_card.set_value(str(product_count['count']))
            
            # Get customer count
            customer_count = self.db.fetchone("SELECT COUNT(*) as count FROM customers")
            self.customers_card.set_value(str(customer_count['count']))
            
            # Get total sales
            total_sales = self.db.fetchone("SELECT COALESCE(SUM(total), 0) as total FROM orders")
            self.sales_card.set_value(f"${total_sales['total']:,.2f}")
            
            # Get location count
            location_count = self.db.fetchone("SELECT COUNT(*) as count FROM locations WHERE location_status = 'active'")
            self.locations_card.set_value(str(location_count['count']))
            
            # Get supplier count
            supplier_count = self.db.fetchone("SELECT COUNT(*) as count FROM suppliers")
            self.suppliers_card.set_value(str(supplier_count['count']))
            
            # Load recent activity
            activity = self.db.fetchall("""
                SELECT 'Order' as type, order_id as id, total as amount, order_date as date
                FROM orders 
                WHERE DATE(order_date) = DATE('now')
                UNION ALL
                SELECT 'Return' as type, return_id as id, return_amount as amount, return_date as date
                FROM returns 
                WHERE DATE(return_date) = DATE('now')
                UNION ALL
                SELECT 'Purchase' as type, purchase_id as id, total_amount as amount, purchase_date as date
                FROM purchases 
                WHERE DATE(purchase_date) = DATE('now')
                ORDER BY date DESC
                LIMIT 10
            """)
            
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(['Type', 'ID', 'Amount', 'Date', 'Time'])
            
            for row in activity:
                date_obj = QDateTime.fromString(row['date'], "yyyy-MM-dd HH:mm:ss")
                
                type_item = QStandardItem(row['type'])
                if row['type'] == 'Order':
                    type_item.setForeground(QColor('green'))
                elif row['type'] == 'Return':
                    type_item.setForeground(QColor('red'))
                else:
                    type_item.setForeground(QColor('blue'))
                
                amount_item = QStandardItem(f"${row['amount']:,.2f}")
                amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                
                model.appendRow([
                    type_item,
                    QStandardItem(str(row['id'])),
                    amount_item,
                    QStandardItem(date_obj.toString("yyyy-MM-dd")),
                    QStandardItem(date_obj.toString("HH:mm:ss"))
                ])
            
            self.activity_table.setModel(model)
            self.activity_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load dashboard: {str(e)}")
    
    # Search Functions
    def search_staff(self):
        """Search staff by name, username, or email"""
        search_term = self.staff_search.text()
        if not search_term:
            self.load_staff()
            return
            
        try:
            staff = self.db.fetchall("""
                SELECT s.staff_id, s.username, s.staff_name, r.role_name, 
                       l.location_name, s.staff_contact, s.staff_email,
                       s.staff_status, s.staff_salary, s.staff_hiring_date
                FROM staff s
                JOIN roles r ON s.role_id = r.role_id
                JOIN locations l ON s.location_id = l.location_id
                WHERE s.staff_name LIKE ? OR s.username LIKE ? OR s.staff_email LIKE ?
                ORDER BY s.staff_name
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels([
                'ID', 'Username', 'Name', 'Role', 'Location', 
                'Contact', 'Email', 'Status', 'Salary', 'Hire Date'
            ])
            
            for row in staff:
                status_item = QStandardItem(row['staff_status'])
                if row['staff_status'] == 'active':
                    status_item.setForeground(QColor('green'))
                elif row['staff_status'] == 'suspended':
                    status_item.setForeground(QColor('orange'))
                else:
                    status_item.setForeground(QColor('red'))
                
                salary_item = QStandardItem(f"${row['staff_salary']:,.2f}")
                salary_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                
                model.appendRow([
                    QStandardItem(str(row['staff_id'])),
                    QStandardItem(row['username'] or ''),
                    QStandardItem(row['staff_name']),
                    QStandardItem(row['role_name']),
                    QStandardItem(row['location_name']),
                    QStandardItem(row['staff_contact']),
                    QStandardItem(row['staff_email']),
                    status_item,
                    salary_item,
                    QStandardItem(row['staff_hiring_date'])
                ])
            
            self.staff_table.setModel(model)
            self.staff_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")
    
    def search_products(self):
        """Search products by name or code"""
        search_term = self.product_search.text()
        if not search_term:
            self.load_products()
            return
            
        try:
            products = self.db.fetchall("""
                SELECT p.product_id, p.product_code, p.product_name, 
                       c.category_brand, c.model_name, s.supplier_name,
                       p.cost_price, p.wholesale_price, p.sale_price,
                       p.is_active, p.created_at
                FROM products p
                JOIN categories c ON p.category_id = c.category_id
                JOIN suppliers s ON p.supplier_id = s.supplier_id
                WHERE p.product_name LIKE ? OR p.product_code LIKE ? OR c.category_brand LIKE ?
                ORDER BY p.product_name
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels([
                'ID', 'Code', 'Name', 'Brand', 'Model', 'Supplier',
                'Cost', 'Wholesale', 'Sale', 'Active', 'Created'
            ])
            
            for row in products:
                cost_item = QStandardItem(f"${row['cost_price']:,.2f}")
                wholesale_item = QStandardItem(f"${row['wholesale_price']:,.2f}")
                sale_item = QStandardItem(f"${row['sale_price']:,.2f}")
                
                for item in [cost_item, wholesale_item, sale_item]:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                
                active_item = QStandardItem('Yes' if row['is_active'] else 'No')
                if row['is_active']:
                    active_item.setForeground(QColor('green'))
                else:
                    active_item.setForeground(QColor('red'))
                
                model.appendRow([
                    QStandardItem(str(row['product_id'])),
                    QStandardItem(row['product_code']),
                    QStandardItem(row['product_name']),
                    QStandardItem(row['category_brand']),
                    QStandardItem(row['model_name']),
                    QStandardItem(row['supplier_name']),
                    cost_item,
                    wholesale_item,
                    sale_item,
                    active_item,
                    QStandardItem(row['created_at'][:10])
                ])
            
            self.products_table.setModel(model)
            self.products_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")
    
    def search_customers(self):
        """Search customers by name or email"""
        search_term = self.customer_search.text()
        if not search_term:
            self.load_customers()
            return
            
        try:
            customers = self.db.fetchall("""
                SELECT c.*, COUNT(o.order_id) as order_count
                FROM customers c
                LEFT JOIN orders o ON c.customer_id = o.customer_id
                WHERE c.customer_name LIKE ? OR c.email LIKE ? OR c.contact_no LIKE ?
                GROUP BY c.customer_id
                ORDER BY c.customer_name
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels([
                'ID', 'Name', 'Contact', 'Email', 'Address', 'Orders', 'Created'
            ])
            
            for row in customers:
                model.appendRow([
                    QStandardItem(str(row['customer_id'])),
                    QStandardItem(row['customer_name']),
                    QStandardItem(row['contact_no'] or ''),
                    QStandardItem(row['email'] or ''),
                    QStandardItem(row['address'] or ''),
                    QStandardItem(str(row['order_count'])),
                    QStandardItem(row['created_at'][:10])
                ])
            
            self.customers_table.setModel(model)
            self.customers_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")
    
    def search_suppliers(self):
        """Search suppliers by name or email"""
        search_term = self.supplier_search.text()
        if not search_term:
            self.load_suppliers()
            return
            
        try:
            suppliers = self.db.fetchall("""
                SELECT s.*, COUNT(p.product_id) as product_count
                FROM suppliers s
                LEFT JOIN products p ON s.supplier_id = p.supplier_id
                WHERE s.supplier_name LIKE ? OR s.email LIKE ? OR s.contact_no LIKE ?
                GROUP BY s.supplier_id
                ORDER BY s.supplier_name
            """, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))
            
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels([
                'ID', 'Name', 'Contact', 'Email', 'Warehouse', 'Bank Account', 'Products'
            ])
            
            for row in suppliers:
                model.appendRow([
                    QStandardItem(str(row['supplier_id'])),
                    QStandardItem(row['supplier_name']),
                    QStandardItem(row['contact_no']),
                    QStandardItem(row['email'] or ''),
                    QStandardItem(row['warehouse_address']),
                    QStandardItem(row['bank_ac_no']),
                    QStandardItem(str(row['product_count']))
                ])
            
            self.suppliers_table.setModel(model)
            self.suppliers_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")
    
    def search_locations(self):
        """Search locations by name"""
        search_term = self.location_search.text()
        if not search_term:
            self.load_locations()
            return
            
        try:
            locations = self.db.fetchall("""
                SELECT l.*, s.staff_name as manager_name,
                       COUNT(st.stock_id) as stock_items
                FROM locations l
                LEFT JOIN staff s ON l.managed_by = s.staff_id
                LEFT JOIN stocks st ON l.location_id = st.location_id
                WHERE l.location_name LIKE ? OR l.location_type LIKE ?
                GROUP BY l.location_id
                ORDER BY l.location_name
            """, (f"%{search_term}%", f"%{search_term}%"))
            
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels([
                'ID', 'Name', 'Type', 'Address', 'Contact', 
                'Manager', 'Staff Capacity', 'Stock Items', 'Status'
            ])
            
            for row in locations:
                model.appendRow([
                    QStandardItem(str(row['location_id'])),
                    QStandardItem(row['location_name']),
                    QStandardItem(row['location_type']),
                    QStandardItem(row['address'] or ''),
                    QStandardItem(row['contact_no'] or ''),
                    QStandardItem(row['manager_name'] or ''),
                    QStandardItem(str(row['staff_capacity'])),
                    QStandardItem(str(row['stock_items'])),
                    QStandardItem(row['location_status'])
                ])
            
            self.locations_table.setModel(model)
            self.locations_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")
    
    def search_roles(self):
        """Search roles by name"""
        search_term = self.role_search.text()
        if not search_term:
            self.load_roles()
            return
            
        try:
            roles = self.db.fetchall("""
                SELECT r.*, COUNT(s.staff_id) as staff_count
                FROM roles r
                LEFT JOIN staff s ON r.role_id = s.role_id
                WHERE r.role_name LIKE ? OR r.description LIKE ?
                GROUP BY r.role_id
                ORDER BY r.role_name
            """, (f"%{search_term}%", f"%{search_term}%"))
            
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels([
                'ID', 'Role Name', 'Description', 'Staff Count', 'Created'
            ])
            
            for row in roles:
                model.appendRow([
                    QStandardItem(str(row['role_id'])),
                    QStandardItem(row['role_name']),
                    QStandardItem(row['description'] or ''),
                    QStandardItem(str(row['staff_count'])),
                    QStandardItem(row['created_at'][:10])
                ])
            
            self.roles_table.setModel(model)
            self.roles_table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {str(e)}")
    
    # Add/Edit/Delete Functions
    def add_staff(self):
        """Open dialog to add new staff"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Staff")
        dialog.setFixedSize(500, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        username_input = QLineEdit()
        username_input.setPlaceholderText("Enter unique username")
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setPlaceholderText("Enter password")
        name_input = QLineEdit()
        name_input.setPlaceholderText("Full name")
        
        # Role dropdown
        role_combo = QComboBox()
        roles = self.db.fetchall("SELECT role_id, role_name FROM roles ORDER BY role_name")
        role_combo.addItem("Select Role", None)
        for role in roles:
            role_combo.addItem(role['role_name'], role['role_id'])
            
        # Location dropdown
        location_combo = QComboBox()
        locations = self.db.fetchall("SELECT location_id, location_name FROM locations WHERE location_status = 'active' ORDER BY location_name")
        location_combo.addItem("Select Location", None)
        for loc in locations:
            location_combo.addItem(loc['location_name'], loc['location_id'])
            
        contact_input = QLineEdit()
        contact_input.setPlaceholderText("e.g., +92-300-1234567")
        email_input = QLineEdit()
        email_input.setPlaceholderText("email@example.com")
        cnic_input = QLineEdit()
        cnic_input.setPlaceholderText("12345-6789012-3")
        bank_input = QLineEdit()
        bank_input.setPlaceholderText("Bank account number")
        salary_input = QDoubleSpinBox()
        salary_input.setMaximum(999999)
        salary_input.setMinimum(0)
        salary_input.setValue(30000)
        salary_input.setPrefix("$ ")
        
        hiring_date = QDateEdit()
        hiring_date.setCalendarPopup(True)
        hiring_date.setDate(QDate.currentDate())
        
        status_combo = QComboBox()
        status_combo.addItems(['active', 'inactive', 'suspended'])
        
        # Add fields to form
        form_layout.addRow("Username*:", username_input)
        form_layout.addRow("Password*:", password_input)
        form_layout.addRow("Full Name*:", name_input)
        form_layout.addRow("Role*:", role_combo)
        form_layout.addRow("Location*:", location_combo)
        form_layout.addRow("Contact*:", contact_input)
        form_layout.addRow("Email*:", email_input)
        form_layout.addRow("CNIC*:", cnic_input)
        form_layout.addRow("Bank Account*:", bank_input)
        form_layout.addRow("Salary*:", salary_input)
        form_layout.addRow("Hiring Date:", hiring_date)
        form_layout.addRow("Status:", status_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = ModernButton("Save")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        save_btn.clicked.connect(lambda: self.save_staff(
            dialog, username_input.text(), password_input.text(),
            name_input.text(), role_combo.currentData(),
            location_combo.currentData(), contact_input.text(),
            email_input.text(), cnic_input.text(), bank_input.text(),
            salary_input.value(), hiring_date.date().toString("yyyy-MM-dd"),
            status_combo.currentText()
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.setStyleSheet(styles.STYLES["form"])
        dialog.exec_()
    
    def save_staff(self, dialog, username, password, name, role_id, 
                   location_id, contact, email, cnic, bank, salary, 
                   hire_date, status):
        """Save new staff member to database"""
        try:
            # Validation
            if not all([username, password, name, role_id, location_id, contact, email, cnic, bank]):
                QMessageBox.warning(self, "Validation Error", "Please fill all required fields (*)")
                return
            
            # Hash password
            import hashlib
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            with self.db.transaction() as cursor:
                cursor.execute("""
                    INSERT INTO staff 
                    (username, password_hash, staff_name, role_id, location_id,
                     staff_contact, staff_email, staff_cnic, staff_bank_acno,
                     staff_salary, staff_hiring_date, staff_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (username, password_hash, name, role_id, location_id,
                      contact, email, cnic, bank, salary, hire_date, status))
                
            QMessageBox.information(self, "Success", "Staff member added successfully!")
            dialog.accept()
            self.load_staff()
            self.load_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save staff: {str(e)}")
    
    def edit_staff(self):
        """Edit selected staff member"""
        selection = self.staff_table.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "Warning", "Please select a staff member to edit")
            return
            
        index = selection.currentIndex()
        model = self.staff_table.model()
        staff_id = model.data(model.index(index.row(), 0))
        
        # Fetch staff details
        staff = self.db.fetchone("""
            SELECT * FROM staff WHERE staff_id = ?
        """, (staff_id,))
        
        if not staff:
            QMessageBox.warning(self, "Warning", "Staff member not found")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Staff: {staff['staff_name']}")
        dialog.setFixedSize(500, 550)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        name_input = QLineEdit(staff['staff_name'])
        name_input.setPlaceholderText("Full name")
        
        # Role dropdown
        role_combo = QComboBox()
        roles = self.db.fetchall("SELECT role_id, role_name FROM roles ORDER BY role_name")
        for role in roles:
            role_combo.addItem(role['role_name'], role['role_id'])
        # Set current role
        role_index = role_combo.findData(staff['role_id'])
        if role_index >= 0:
            role_combo.setCurrentIndex(role_index)
            
        # Location dropdown
        location_combo = QComboBox()
        locations = self.db.fetchall("SELECT location_id, location_name FROM locations WHERE location_status = 'active' ORDER BY location_name")
        for loc in locations:
            location_combo.addItem(loc['location_name'], loc['location_id'])
        # Set current location
        location_index = location_combo.findData(staff['location_id'])
        if location_index >= 0:
            location_combo.setCurrentIndex(location_index)
            
        contact_input = QLineEdit(staff['staff_contact'])
        email_input = QLineEdit(staff['staff_email'])
        cnic_input = QLineEdit(staff['staff_cnic'])
        bank_input = QLineEdit(staff['staff_bank_acno'])
        salary_input = QDoubleSpinBox()
        salary_input.setMaximum(999999)
        salary_input.setMinimum(0)
        salary_input.setValue(float(staff['staff_salary']))
        salary_input.setPrefix("$ ")
        
        hiring_date = QDateEdit()
        hiring_date.setCalendarPopup(True)
        hiring_date.setDate(QDate.fromString(staff['staff_hiring_date'], "yyyy-MM-dd"))
        
        status_combo = QComboBox()
        status_combo.addItems(['active', 'inactive', 'suspended'])
        status_combo.setCurrentText(staff['staff_status'])
        
        # Add fields to form
        form_layout.addRow("Full Name*:", name_input)
        form_layout.addRow("Role*:", role_combo)
        form_layout.addRow("Location*:", location_combo)
        form_layout.addRow("Contact*:", contact_input)
        form_layout.addRow("Email*:", email_input)
        form_layout.addRow("CNIC*:", cnic_input)
        form_layout.addRow("Bank Account*:", bank_input)
        form_layout.addRow("Salary*:", salary_input)
        form_layout.addRow("Hiring Date:", hiring_date)
        form_layout.addRow("Status:", status_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = ModernButton("Update")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        save_btn.clicked.connect(lambda: self.update_staff(
            dialog, staff_id, name_input.text(), role_combo.currentData(),
            location_combo.currentData(), contact_input.text(),
            email_input.text(), cnic_input.text(), bank_input.text(),
            salary_input.value(), hiring_date.date().toString("yyyy-MM-dd"),
            status_combo.currentText()
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.setStyleSheet(styles.STYLES["form"])
        dialog.exec_()
    def update_staff(self, dialog, staff_id, name, role_id, location_id, 
                     contact, email, cnic, bank, salary, hire_date, status):
        """Update staff member in database"""
        try:
            # Validation
            if not all([name, role_id, location_id, contact, email, cnic, bank]):
                QMessageBox.warning(self, "Validation Error", "Please fill all required fields (*)")
                return
            
            with self.db.transaction() as cursor:
                cursor.execute("""
                    UPDATE staff SET
                    staff_name = ?, role_id = ?, location_id = ?,
                    staff_contact = ?, staff_email = ?, staff_cnic = ?, staff_bank_acno = ?,
                    staff_salary = ?, staff_hiring_date = ?, staff_status = ?
                    WHERE staff_id = ?
                """, (name, role_id, location_id, contact, email, cnic, bank, 
                      salary, hire_date, status, staff_id))
                
            QMessageBox.information(self, "Success", "Staff member updated successfully!")
            dialog.accept()
            self.load_staff()
            self.load_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update staff: {str(e)}")
    
    def delete_staff(self):
        """Delete selected staff member"""
        selection = self.staff_table.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "Warning", "Please select a staff member to delete")
            return
            
        index = selection.currentIndex()
        model = self.staff_table.model()
        staff_id = model.data(model.index(index.row(), 0))
        staff_name = model.data(model.index(index.row(), 2))
        
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f"Are you sure you want to delete {staff_name}?\nThis will set their status to 'inactive'.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with self.db.transaction() as cursor:
                    cursor.execute("""
                        UPDATE staff SET staff_status = 'inactive' WHERE staff_id = ?
                    """, (staff_id,))
                    
                QMessageBox.information(self, "Success", "Staff member deactivated successfully!")
                self.load_staff()
                self.load_dashboard()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete staff: {str(e)}")
    
    def add_product(self):
        """Open dialog to add new product"""

        categories = self.db.fetchall("SELECT * FROM categories ORDER BY category_brand, model_name")
        suppliers = self.db.fetchall("SELECT * FROM suppliers ORDER BY supplier_name")
    
        if not categories:
            QMessageBox.critical(self, "Error", "No categories found! Please add categories first.")
            return
        
        if not suppliers:
            QMessageBox.critical(self, "Error", "No suppliers found! Please add suppliers first.")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Product")
        dialog.setFixedSize(600, 650)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Product name")
        
        # Category dropdown - FIXED
        category_combo = QComboBox()
        for cat in categories:
            display_text = f"{cat['category_brand']} {cat['model_name']} ({cat['product_type']})"
            category_combo.addItem(display_text, cat['category_id'])
        
        # Supplier dropdown - FIXED
        supplier_combo = QComboBox()
        for sup in suppliers:
            supplier_combo.addItem(sup['supplier_name'], sup['supplier_id'])
            dialog = QDialog(self)
            dialog.setWindowTitle("Add New Product")
            dialog.setFixedSize(600, 650)
            
            layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Product name")
        
        # Category dropdown
        category_combo = QComboBox()
        categories = self.db.fetchall("SELECT category_id, category_brand || ' ' || model_name as display FROM categories ORDER BY category_brand")
        category_combo.addItem("Select Category", None)
        for cat in categories:
            category_combo.addItem(cat['display'], cat['category_id'])
            
        # Supplier dropdown
        supplier_combo = QComboBox()
        suppliers = self.db.fetchall("SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_name")
        supplier_combo.addItem("Select Supplier", None)
        for sup in suppliers:
            supplier_combo.addItem(sup['supplier_name'], sup['supplier_id'])
        
        # Specifications
        screen_combo = QComboBox()
        screen_combo.addItems(["", "13.3", "14", "15.6", "17"])
        
        color_input = QLineEdit()
        color_input.setPlaceholderText("e.g., Black, Silver")
        
        processor_input = QLineEdit()
        processor_input.setPlaceholderText("e.g., Intel Core i5-1145G7")
        
        ram_input = QLineEdit()
        ram_input.setPlaceholderText("e.g., 8GB DDR4")
        
        storage_input = QLineEdit()
        storage_input.setPlaceholderText("e.g., 256GB SSD")
        
        gpu_input = QLineEdit()
        gpu_input.setPlaceholderText("e.g., Intel Iris Xe")
        
        # Prices
        cost_input = QDoubleSpinBox()
        cost_input.setMaximum(999999)
        cost_input.setMinimum(0)
        cost_input.setPrefix("$ ")
        
        wholesale_input = QDoubleSpinBox()
        wholesale_input.setMaximum(999999)
        wholesale_input.setMinimum(0)
        wholesale_input.setPrefix("$ ")
        
        sale_input = QDoubleSpinBox()
        sale_input.setMaximum(999999)
        sale_input.setMinimum(0)
        sale_input.setPrefix("$ ")
        
        # Add fields to form
        form_layout.addRow("Product Name*:", name_input)
        form_layout.addRow("Category*:", category_combo)
        form_layout.addRow("Supplier*:", supplier_combo)
        form_layout.addRow("Screen Size:", screen_combo)
        form_layout.addRow("Color:", color_input)
        form_layout.addRow("Processor:", processor_input)
        form_layout.addRow("RAM:", ram_input)
        form_layout.addRow("Storage:", storage_input)
        form_layout.addRow("GPU:", gpu_input)
        form_layout.addRow("Cost Price*:", cost_input)
        form_layout.addRow("Wholesale Price*:", wholesale_input)
        form_layout.addRow("Sale Price*:", sale_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = ModernButton("Save")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        save_btn.clicked.connect(lambda: self.save_product(
            dialog, name_input.text(), category_combo.currentData(),
            supplier_combo.currentData(), screen_combo.currentText(),
            color_input.text(), processor_input.text(), ram_input.text(),
            storage_input.text(), "", gpu_input.text(),
            cost_input.value(), wholesale_input.value(), sale_input.value()
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.setStyleSheet(styles.STYLES["form"])
        dialog.exec_()
    
    def save_product(self, dialog, name, category_id, supplier_id, screen_size, 
                 color, processor, ram, primary_storage, secondary_storage, 
                    gpu, cost_price, wholesale_price, sale_price):
        """Save new product to database"""
        try:
            # Validation
            if not all([name, category_id, supplier_id]):
                QMessageBox.warning(self, "Validation Error", "Please fill all required fields (*)")
                return
            
            if wholesale_price < cost_price:
                QMessageBox.warning(self, "Validation Error", "Wholesale price must be >= cost price")
                return
            
            if sale_price < wholesale_price:
                QMessageBox.warning(self, "Validation Error", "Sale price must be >= wholesale price")
                return
            
        
            
            product = Product(
                product_name=name,
                category_id=category_id,
                supplier_id=supplier_id,
                screen_size=float(screen_size) if screen_size else None,
                color=color or None,
                processor=processor or None,
                ram=ram or None,
                primary_storage=primary_storage or None,
                secondary_storage=secondary_storage or None,
                gpu=gpu or None,
                cost_price=cost_price,
                wholesale_price=wholesale_price,
                sale_price=sale_price,
                is_active=True
            )
            
            # Use ProductController
            controller = ProductController(self.db)
            product_id = controller.create_product(product)
            
            QMessageBox.information(self, "Success", f"Product added successfully! Product ID: {product_id}")
            dialog.accept()
            self.load_products()
            self.load_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save product: {str(e)}")
    
    def edit_product(self):
        """Edit selected product"""
        selection = self.products_table.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "Warning", "Please select a product to edit")
            return
            
        index = selection.currentIndex()
        model = self.products_table.model()
        product_id = model.data(model.index(index.row(), 0))
        
        # Fetch product details
        product = self.db.fetchone("""
            SELECT * FROM products WHERE product_id = ?
        """, (product_id,))
        
        if not product:
            QMessageBox.warning(self, "Warning", "Product not found")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Product: {product['product_name']}")
        dialog.setFixedSize(600, 650)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        name_input = QLineEdit(product['product_name'])
        
        # Category dropdown
        category_combo = QComboBox()
        categories = self.db.fetchall("SELECT category_id, category_brand || ' ' || model_name as display FROM categories ORDER BY category_brand")
        for cat in categories:
            category_combo.addItem(cat['display'], cat['category_id'])
        # Set current category
        cat_display = self.db.fetchone("SELECT category_brand || ' ' || model_name as display FROM categories WHERE category_id = ?", (product['category_id'],))
        if cat_display:
            category_combo.setCurrentText(cat_display['display'])
            
        # Supplier dropdown
        supplier_combo = QComboBox()
        suppliers = self.db.fetchall("SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_name")
        for sup in suppliers:
            supplier_combo.addItem(sup['supplier_name'], sup['supplier_id'])
        # Set current supplier
        sup_name = self.db.fetchone("SELECT supplier_name FROM suppliers WHERE supplier_id = ?", (product['supplier_id'],))
        if sup_name:
            supplier_combo.setCurrentText(sup_name['supplier_name'])
        
        # Specifications
        screen_combo = QComboBox()
        screen_combo.addItems(["", "13.3", "14", "15.6", "17"])
        if product['screen_size']:
            screen_combo.setCurrentText(str(product['screen_size']))
        
        color_input = QLineEdit(product['color'] or "")
        processor_input = QLineEdit(product['processor'] or "")
        ram_input = QLineEdit(product['ram'] or "")
        storage_input = QLineEdit(product['primary_storage'] or "")
        gpu_input = QLineEdit(product['gpu'] or "")
        
        # Prices
        cost_input = QDoubleSpinBox()
        cost_input.setMaximum(999999)
        cost_input.setMinimum(0)
        cost_input.setValue(float(product['cost_price']))
        cost_input.setPrefix("$ ")
        
        wholesale_input = QDoubleSpinBox()
        wholesale_input.setMaximum(999999)
        wholesale_input.setMinimum(0)
        wholesale_input.setValue(float(product['wholesale_price']))
        wholesale_input.setPrefix("$ ")
        
        sale_input = QDoubleSpinBox()
        sale_input.setMaximum(999999)
        sale_input.setMinimum(0)
        sale_input.setValue(float(product['sale_price']))
        sale_input.setPrefix("$ ")
        
        active_check = QCheckBox("Active")
        active_check.setChecked(bool(product['is_active']))
        
        # Add fields to form
        form_layout.addRow("Product Name*:", name_input)
        form_layout.addRow("Category*:", category_combo)
        form_layout.addRow("Supplier*:", supplier_combo)
        form_layout.addRow("Screen Size:", screen_combo)
        form_layout.addRow("Color:", color_input)
        form_layout.addRow("Processor:", processor_input)
        form_layout.addRow("RAM:", ram_input)
        form_layout.addRow("Storage:", storage_input)
        form_layout.addRow("GPU:", gpu_input)
        form_layout.addRow("Cost Price*:", cost_input)
        form_layout.addRow("Wholesale Price*:", wholesale_input)
        form_layout.addRow("Sale Price*:", sale_input)
        form_layout.addRow("", active_check)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = ModernButton("Update")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        save_btn.clicked.connect(lambda: self.update_product(
            dialog, product_id, name_input.text(), category_combo.currentData(),
            supplier_combo.currentData(), screen_combo.currentText(),
            color_input.text(), processor_input.text(), ram_input.text(),
            storage_input.text(), "", gpu_input.text(),
            cost_input.value(), wholesale_input.value(), sale_input.value(),
            active_check.isChecked()
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.setStyleSheet(styles.STYLES["form"])
        dialog.exec_()
    
    def update_product(self, dialog, product_id, name, category_id, supplier_id, 
                       screen_size, color, processor, ram, primary_storage, 
                       secondary_storage, gpu, cost_price, wholesale_price, 
                       sale_price, is_active):
        """Update product in database"""
        try:
            # Validation
            if not all([name, category_id, supplier_id]):
                QMessageBox.warning(self, "Validation Error", "Please fill all required fields (*)")
                return
            
            if wholesale_price < cost_price:
                QMessageBox.warning(self, "Validation Error", "Wholesale price must be >= cost price")
                return
            
            if sale_price < wholesale_price:
                QMessageBox.warning(self, "Validation Error", "Sale price must be >= wholesale price")
                return
            
            with self.db.transaction() as cursor:
                cursor.execute("""
                    UPDATE products SET
                    product_name = ?, category_id = ?, supplier_id = ?,
                    screen_size = ?, color = ?, processor = ?, ram = ?,
                    primary_storage = ?, secondary_storage = ?, gpu = ?,
                    cost_price = ?, wholesale_price = ?, sale_price = ?,
                    is_active = ?
                    WHERE product_id = ?
                """, (name, category_id, supplier_id,
                      float(screen_size) if screen_size else None,
                      color or None, processor or None, ram or None,
                      primary_storage or None, secondary_storage or None,
                      gpu or None, cost_price, wholesale_price, sale_price,
                      1 if is_active else 0, product_id))
                
            QMessageBox.information(self, "Success", "Product updated successfully!")
            dialog.accept()
            self.load_products()
            self.load_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update product: {str(e)}")
    
    def delete_product(self):
        """Delete selected product"""
        selection = self.products_table.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "Warning", "Please select a product to delete")
            return
            
        index = selection.currentIndex()
        model = self.products_table.model()
        product_id = model.data(model.index(index.row(), 0))
        product_name = model.data(model.index(index.row(), 2))
        
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f"Are you sure you want to delete {product_name}?\nThis will deactivate the product.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with self.db.transaction() as cursor:
                    cursor.execute("""
                        UPDATE products SET is_active = 0 WHERE product_id = ?
                    """, (product_id,))
                    
                QMessageBox.information(self, "Success", "Product deactivated successfully!")
                self.load_products()
                self.load_dashboard()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete product: {str(e)}")
    
    def add_customer(self):
        """Open dialog to add new customer"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Customer")
        dialog.setFixedSize(400, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Customer name")
        
        contact_input = QLineEdit()
        contact_input.setPlaceholderText("Phone number")
        
        email_input = QLineEdit()
        email_input.setPlaceholderText("email@example.com")
        
        address_input = QTextEdit()
        address_input.setMaximumHeight(80)
        address_input.setPlaceholderText("Full address")
        
        # Add fields to form
        form_layout.addRow("Name*:", name_input)
        form_layout.addRow("Contact:", contact_input)
        form_layout.addRow("Email:", email_input)
        form_layout.addRow("Address:", address_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = ModernButton("Save")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        save_btn.clicked.connect(lambda: self.save_customer(
            dialog, name_input.text(), contact_input.text(),
            email_input.text(), address_input.toPlainText()
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.setStyleSheet(styles.STYLES["form"])
        dialog.exec_()
    
    def save_customer(self, dialog, name, contact, email, address):
        """Save new customer to database"""
        try:
            if not name:
                QMessageBox.warning(self, "Validation Error", "Customer name is required")
                return
            
            with self.db.transaction() as cursor:
                cursor.execute("""
                    INSERT INTO customers 
                    (customer_name, contact_no, email, address)
                    VALUES (?, ?, ?, ?)
                """, (name, contact or None, email or None, address or None))
                
            QMessageBox.information(self, "Success", "Customer added successfully!")
            dialog.accept()
            self.load_customers()
            self.load_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save customer: {str(e)}")
    
    def edit_customer(self):
        """Edit selected customer"""
        selection = self.customers_table.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "Warning", "Please select a customer to edit")
            return
            
        index = selection.currentIndex()
        model = self.customers_table.model()
        customer_id = model.data(model.index(index.row(), 0))
        
        # Fetch customer details
        customer = self.db.fetchone("""
            SELECT * FROM customers WHERE customer_id = ?
        """, (customer_id,))
        
        if not customer:
            QMessageBox.warning(self, "Warning", "Customer not found")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Customer: {customer['customer_name']}")
        dialog.setFixedSize(400, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        name_input = QLineEdit(customer['customer_name'])
        contact_input = QLineEdit(customer['contact_no'] or "")
        email_input = QLineEdit(customer['email'] or "")
        address_input = QTextEdit(customer['address'] or "")
        address_input.setMaximumHeight(80)
        
        # Add fields to form
        form_layout.addRow("Name*:", name_input)
        form_layout.addRow("Contact:", contact_input)
        form_layout.addRow("Email:", email_input)
        form_layout.addRow("Address:", address_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = ModernButton("Update")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        save_btn.clicked.connect(lambda: self.update_customer(
            dialog, customer_id, name_input.text(), contact_input.text(),
            email_input.text(), address_input.toPlainText()
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.setStyleSheet(styles.STYLES["form"])
        dialog.exec_()
    
    def update_customer(self, dialog, customer_id, name, contact, email, address):
        """Update customer in database"""
        try:
            if not name:
                QMessageBox.warning(self, "Validation Error", "Customer name is required")
                return
            
            with self.db.transaction() as cursor:
                cursor.execute("""
                    UPDATE customers SET
                    customer_name = ?, contact_no = ?, email = ?, address = ?
                    WHERE customer_id = ?
                """, (name, contact or None, email or None, address or None, customer_id))
                
            QMessageBox.information(self, "Success", "Customer updated successfully!")
            dialog.accept()
            self.load_customers()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update customer: {str(e)}")
    
    def delete_customer(self):
        """Delete selected customer"""
        selection = self.customers_table.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "Warning", "Please select a customer to delete")
            return
            
        index = selection.currentIndex()
        model = self.customers_table.model()
        customer_id = model.data(model.index(index.row(), 0))
        customer_name = model.data(model.index(index.row(), 1))
        
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f"Are you sure you want to delete {customer_name}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Check if customer has orders
                orders = self.db.fetchone("SELECT COUNT(*) as count FROM orders WHERE customer_id = ?", (customer_id,))
                if orders and orders['count'] > 0:
                    QMessageBox.warning(self, "Warning", "Cannot delete customer with existing orders. Please deactivate instead.")
                    return
                
                with self.db.transaction() as cursor:
                    cursor.execute("DELETE FROM customers WHERE customer_id = ?", (customer_id,))
                    
                QMessageBox.information(self, "Success", "Customer deleted successfully!")
                self.load_customers()
                self.load_dashboard()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete customer: {str(e)}")
    
    def add_supplier(self):
        """Open dialog to add new supplier"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Supplier")
        dialog.setFixedSize(500, 450)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Supplier name")
        
        contact_input = QLineEdit()
        contact_input.setPlaceholderText("Phone number")
        
        email_input = QLineEdit()
        email_input.setPlaceholderText("email@example.com")
        
        warehouse_input = QTextEdit()
        warehouse_input.setMaximumHeight(80)
        warehouse_input.setPlaceholderText("Warehouse address")
        
        bank_input = QLineEdit()
        bank_input.setPlaceholderText("Bank account number")
        
        # Add fields to form
        form_layout.addRow("Name*:", name_input)
        form_layout.addRow("Contact*:", contact_input)
        form_layout.addRow("Email:", email_input)
        form_layout.addRow("Warehouse*:", warehouse_input)
        form_layout.addRow("Bank Account*:", bank_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = ModernButton("Save")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        save_btn.clicked.connect(lambda: self.save_supplier(
            dialog, name_input.text(), contact_input.text(),
            email_input.text(), warehouse_input.toPlainText(),
            bank_input.text()
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.setStyleSheet(styles.STYLES["form"])
        dialog.exec_()
    
    def save_supplier(self, dialog, name, contact, email, warehouse, bank):
        """Save new supplier to database"""
        try:
            if not all([name, contact, warehouse, bank]):
                QMessageBox.warning(self, "Validation Error", "Please fill all required fields (*)")
                return
            
            with self.db.transaction() as cursor:
                cursor.execute("""
                    INSERT INTO suppliers 
                    (supplier_name, contact_no, email, warehouse_address, bank_ac_no)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, contact, email or None, warehouse, bank))
                
            QMessageBox.information(self, "Success", "Supplier added successfully!")
            dialog.accept()
            self.load_suppliers()
            self.load_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save supplier: {str(e)}")
    
    def edit_supplier(self):
        """Edit selected supplier"""
        selection = self.suppliers_table.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "Warning", "Please select a supplier to edit")
            return
            
        index = selection.currentIndex()
        model = self.suppliers_table.model()
        supplier_id = model.data(model.index(index.row(), 0))
        
        # Fetch supplier details
        supplier = self.db.fetchone("""
            SELECT * FROM suppliers WHERE supplier_id = ?
        """, (supplier_id,))
        
        if not supplier:
            QMessageBox.warning(self, "Warning", "Supplier not found")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Supplier: {supplier['supplier_name']}")
        dialog.setFixedSize(500, 450)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        name_input = QLineEdit(supplier['supplier_name'])
        contact_input = QLineEdit(supplier['contact_no'])
        email_input = QLineEdit(supplier['email'] or "")
        warehouse_input = QTextEdit(supplier['warehouse_address'])
        warehouse_input.setMaximumHeight(80)
        bank_input = QLineEdit(supplier['bank_ac_no'])
        
        # Add fields to form
        form_layout.addRow("Name*:", name_input)
        form_layout.addRow("Contact*:", contact_input)
        form_layout.addRow("Email:", email_input)
        form_layout.addRow("Warehouse*:", warehouse_input)
        form_layout.addRow("Bank Account*:", bank_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = ModernButton("Update")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        save_btn.clicked.connect(lambda: self.update_supplier(
            dialog, supplier_id, name_input.text(), contact_input.text(),
            email_input.text(), warehouse_input.toPlainText(),
            bank_input.text()
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.setStyleSheet(styles.STYLES["form"])
        dialog.exec_()
    
    def update_supplier(self, dialog, supplier_id, name, contact, email, warehouse, bank):
        """Update supplier in database"""
        try:
            if not all([name, contact, warehouse, bank]):
                QMessageBox.warning(self, "Validation Error", "Please fill all required fields (*)")
                return
            
            with self.db.transaction() as cursor:
                cursor.execute("""
                    UPDATE suppliers SET
                    supplier_name = ?, contact_no = ?, email = ?, 
                    warehouse_address = ?, bank_ac_no = ?
                    WHERE supplier_id = ?
                """, (name, contact, email or None, warehouse, bank, supplier_id))
                
            QMessageBox.information(self, "Success", "Supplier updated successfully!")
            dialog.accept()
            self.load_suppliers()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update supplier: {str(e)}")
    
    def delete_supplier(self):
        """Delete selected supplier"""
        selection = self.suppliers_table.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "Warning", "Please select a supplier to delete")
            return
            
        index = selection.currentIndex()
        model = self.suppliers_table.model()
        supplier_id = model.data(model.index(index.row(), 0))
        supplier_name = model.data(model.index(index.row(), 1))
        
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f"Are you sure you want to delete {supplier_name}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Check if supplier has products
                products = self.db.fetchone("SELECT COUNT(*) as count FROM products WHERE supplier_id = ?", (supplier_id,))
                if products and products['count'] > 0:
                    QMessageBox.warning(self, "Warning", "Cannot delete supplier with associated products")
                    return
                
                with self.db.transaction() as cursor:
                    cursor.execute("DELETE FROM suppliers WHERE supplier_id = ?", (supplier_id,))
                    
                QMessageBox.information(self, "Success", "Supplier deleted successfully!")
                self.load_suppliers()
                self.load_dashboard()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete supplier: {str(e)}")
    
    def add_location(self):
        """Open dialog to add new location"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Location")
        dialog.setFixedSize(500, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Location name")
        
        type_combo = QComboBox()
        type_combo.addItems(['store', 'platform', 'warehouse'])
        
        address_input = QTextEdit()
        address_input.setMaximumHeight(80)
        address_input.setPlaceholderText("Full address")
        
        contact_input = QLineEdit()
        contact_input.setPlaceholderText("Phone number")
        
        # Manager dropdown
        manager_combo = QComboBox()
        managers = self.db.fetchall("SELECT staff_id, staff_name FROM staff WHERE staff_status = 'active' ORDER BY staff_name")
        manager_combo.addItem("None", None)
        for mgr in managers:
            manager_combo.addItem(mgr['staff_name'], mgr['staff_id'])
        
        capacity_input = QSpinBox()
        capacity_input.setMinimum(0)
        capacity_input.setMaximum(1000)
        capacity_input.setValue(10)
        
        status_combo = QComboBox()
        status_combo.addItems(['active', 'inactive', 'closed'])
        
        # Add fields to form
        form_layout.addRow("Name*:", name_input)
        form_layout.addRow("Type*:", type_combo)
        form_layout.addRow("Address:", address_input)
        form_layout.addRow("Contact:", contact_input)
        form_layout.addRow("Manager:", manager_combo)
        form_layout.addRow("Staff Capacity:", capacity_input)
        form_layout.addRow("Status:", status_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = ModernButton("Save")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        save_btn.clicked.connect(lambda: self.save_location(
            dialog, name_input.text(), type_combo.currentText(),
            address_input.toPlainText(), contact_input.text(),
            manager_combo.currentData(), capacity_input.value(),
            status_combo.currentText()
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.setStyleSheet(styles.STYLES["form"])
        dialog.exec_()
    
    def save_location(self, dialog, name, location_type, address, contact, 
                      manager_id, capacity, status):
        """Save new location to database"""
        try:
            if not name:
                QMessageBox.warning(self, "Validation Error", "Location name is required")
                return
            
            with self.db.transaction() as cursor:
                cursor.execute("""
                    INSERT INTO locations 
                    (location_name, location_type, address, contact_no,
                     managed_by, staff_capacity, location_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, location_type, address or None, contact or None,
                      manager_id, capacity, status))
                
            QMessageBox.information(self, "Success", "Location added successfully!")
            dialog.accept()
            self.load_locations()
            self.load_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save location: {str(e)}")
    
    def edit_location(self):
        """Edit selected location"""
        selection = self.locations_table.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "Warning", "Please select a location to edit")
            return
            
        index = selection.currentIndex()
        model = self.locations_table.model()
        location_id = model.data(model.index(index.row(), 0))
        
        # Fetch location details
        location = self.db.fetchone("""
            SELECT * FROM locations WHERE location_id = ?
        """, (location_id,))
        
        if not location:
            QMessageBox.warning(self, "Warning", "Location not found")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Location: {location['location_name']}")
        dialog.setFixedSize(500, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        name_input = QLineEdit(location['location_name'])
        
        type_combo = QComboBox()
        type_combo.addItems(['store', 'platform', 'warehouse'])
        type_combo.setCurrentText(location['location_type'])
        
        address_input = QTextEdit(location['address'] or "")
        address_input.setMaximumHeight(80)
        
        contact_input = QLineEdit(location['contact_no'] or "")
        
        # Manager dropdown
        manager_combo = QComboBox()
        managers = self.db.fetchall("SELECT staff_id, staff_name FROM staff WHERE staff_status = 'active' ORDER BY staff_name")
        manager_combo.addItem("None", None)
        for mgr in managers:
            manager_combo.addItem(mgr['staff_name'], mgr['staff_id'])
        # Set current manager
        if location['managed_by']:
            mgr_name = self.db.fetchone("SELECT staff_name FROM staff WHERE staff_id = ?", (location['managed_by'],))
            if mgr_name:
                manager_combo.setCurrentText(mgr_name['staff_name'])
        
        capacity_input = QSpinBox()
        capacity_input.setMinimum(0)
        capacity_input.setMaximum(1000)
        capacity_input.setValue(location['staff_capacity'])
        
        status_combo = QComboBox()
        status_combo.addItems(['active', 'inactive', 'closed'])
        status_combo.setCurrentText(location['location_status'])
        
        # Add fields to form
        form_layout.addRow("Name*:", name_input)
        form_layout.addRow("Type*:", type_combo)
        form_layout.addRow("Address:", address_input)
        form_layout.addRow("Contact:", contact_input)
        form_layout.addRow("Manager:", manager_combo)
        form_layout.addRow("Staff Capacity:", capacity_input)
        form_layout.addRow("Status:", status_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = ModernButton("Update")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        save_btn.clicked.connect(lambda: self.update_location(
            dialog, location_id, name_input.text(), type_combo.currentText(),
            address_input.toPlainText(), contact_input.text(),
            manager_combo.currentData(), capacity_input.value(),
            status_combo.currentText()
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.setStyleSheet(styles.STYLES["form"])
        dialog.exec_()
    
    def update_location(self, dialog, location_id, name, location_type, address, 
                        contact, manager_id, capacity, status):
        """Update location in database"""
        try:
            if not name:
                QMessageBox.warning(self, "Validation Error", "Location name is required")
                return
            
            with self.db.transaction() as cursor:
                cursor.execute("""
                    UPDATE locations SET
                    location_name = ?, location_type = ?, address = ?, contact_no = ?,
                    managed_by = ?, staff_capacity = ?, location_status = ?
                    WHERE location_id = ?
                """, (name, location_type, address or None, contact or None,
                      manager_id, capacity, status, location_id))
                
            QMessageBox.information(self, "Success", "Location updated successfully!")
            dialog.accept()
            self.load_locations()
            self.load_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update location: {str(e)}")
    
    def delete_location(self):
        """Delete selected location"""
        selection = self.locations_table.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "Warning", "Please select a location to delete")
            return
            
        index = selection.currentIndex()
        model = self.locations_table.model()
        location_id = model.data(model.index(index.row(), 0))
        location_name = model.data(model.index(index.row(), 1))
        
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f"Are you sure you want to delete {location_name}?\nThis will close the location.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Check if location has stock
                stock = self.db.fetchone("SELECT COUNT(*) as count FROM stocks WHERE location_id = ?", (location_id,))
                if stock and stock['count'] > 0:
                    QMessageBox.warning(self, "Warning", "Cannot delete location with stock. Please transfer stock first.")
                    return
                
                with self.db.transaction() as cursor:
                    cursor.execute("""
                        UPDATE locations SET location_status = 'closed' WHERE location_id = ?
                    """, (location_id,))
                    
                QMessageBox.information(self, "Success", "Location closed successfully!")
                self.load_locations()
                self.load_dashboard()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete location: {str(e)}")
    
    def add_role(self):
        """Open dialog to add new role"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Role")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Role name")
        
        desc_input = QTextEdit()
        desc_input.setMaximumHeight(100)
        desc_input.setPlaceholderText("Role description")
        
        # Add fields to form
        form_layout.addRow("Role Name*:", name_input)
        form_layout.addRow("Description:", desc_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = ModernButton("Save")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        save_btn.clicked.connect(lambda: self.save_role(
            dialog, name_input.text(), desc_input.toPlainText()
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.setStyleSheet(styles.STYLES["form"])
        dialog.exec_()
    
    def save_role(self, dialog, name, description):
        """Save new role to database"""
        try:
            if not name:
                QMessageBox.warning(self, "Validation Error", "Role name is required")
                return
            
            with self.db.transaction() as cursor:
                cursor.execute("""
                    INSERT INTO roles (role_name, description)
                    VALUES (?, ?)
                """, (name, description or None))
                
            QMessageBox.information(self, "Success", "Role added successfully!")
            dialog.accept()
            self.load_roles()
            self.load_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save role: {str(e)}")
    
    def edit_role(self):
        """Edit selected role"""
        selection = self.roles_table.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "Warning", "Please select a role to edit")
            return
            
        index = selection.currentIndex()
        model = self.roles_table.model()
        role_id = model.data(model.index(index.row(), 0))
        
        # Fetch role details
        role = self.db.fetchone("""
            SELECT * FROM roles WHERE role_id = ?
        """, (role_id,))
        
        if not role:
            QMessageBox.warning(self, "Warning", "Role not found")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit Role: {role['role_name']}")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Form fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        name_input = QLineEdit(role['role_name'])
        desc_input = QTextEdit(role['description'] or "")
        desc_input.setMaximumHeight(100)
        
        # Add fields to form
        form_layout.addRow("Role Name*:", name_input)
        form_layout.addRow("Description:", desc_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = ModernButton("Update")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect signals
        save_btn.clicked.connect(lambda: self.update_role(
            dialog, role_id, name_input.text(), desc_input.toPlainText()
        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.setStyleSheet(styles.STYLES["form"])
        dialog.exec_()
    
    def update_role(self, dialog, role_id, name, description):
        """Update role in database"""
        try:
            if not name:
                QMessageBox.warning(self, "Validation Error", "Role name is required")
                return
            
            with self.db.transaction() as cursor:
                cursor.execute("""
                    UPDATE roles SET role_name = ?, description = ?
                    WHERE role_id = ?
                """, (name, description or None, role_id))
                
            QMessageBox.information(self, "Success", "Role updated successfully!")
            dialog.accept()
            self.load_roles()
            self.load_dashboard()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update role: {str(e)}")
    
    def delete_role(self):
        """Delete selected role"""
        selection = self.roles_table.selectionModel()
        if not selection.hasSelection():
            QMessageBox.warning(self, "Warning", "Please select a role to delete")
            return
            
        index = selection.currentIndex()
        model = self.roles_table.model()
        role_id = model.data(model.index(index.row(), 0))
        role_name = model.data(model.index(index.row(), 1))
        
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f"Are you sure you want to delete {role_name}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Check if role has staff
                staff = self.db.fetchone("SELECT COUNT(*) as count FROM staff WHERE role_id = ?", (role_id,))
                if staff and staff['count'] > 0:
                    QMessageBox.warning(self, "Warning", "Cannot delete role with assigned staff")
                    return
                
                with self.db.transaction() as cursor:
                    cursor.execute("DELETE FROM roles WHERE role_id = ?", (role_id,))
                    
                QMessageBox.information(self, "Success", "Role deleted successfully!")
                self.load_roles()
                self.load_dashboard()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete role: {str(e)}")
    
    def closeEvent(self, event):
        """Close database connection when window closes"""
        if hasattr(self, 'db'):
            self.db.close()
        event.accept()


# Stats Card Widget
class StatsCard(QWidget):
    def __init__(self, title, value, color):
        super().__init__()
        self.init_ui(title, value, color)
    
    def init_ui(self, title, value, color):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 14px; color: #666;")
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {color};")
        layout.addWidget(self.value_label)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 10px;
                border: 1px solid #ddd;
            }
        """)
        self.setFixedHeight(100)
    
    def set_value(self, value):
        self.value_label.setText(value)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = AdminPanel()
    window.show()
    
    sys.exit(app.exec_())