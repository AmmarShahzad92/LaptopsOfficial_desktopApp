from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import styles
from widgets import *
from app.database.db import Database 
from app.controllers.report_controller import ReportController
from datetime import datetime, timedelta


class ReportsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audits & Reports - History & Analytics")
        self.setGeometry(150, 150, 1400, 900)

        self.db = Database()
        self.report_controller = ReportController(self.db)
        
        self.init_ui()
        self.load_dashboard()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = SectionTitle("Audits & Reports - History & Analytics")
        main_layout.addWidget(title)
        
        # Date filters
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("From:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel("To:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        filter_layout.addWidget(self.date_to)
        
        self.apply_filter_btn = ModernButton("Apply Filter")
        self.apply_filter_btn.clicked.connect(self.load_dashboard)
        filter_layout.addWidget(self.apply_filter_btn)
        
        self.export_btn = ModernButton("Export Report")
        self.export_btn.clicked.connect(self.export_report)
        filter_layout.addWidget(self.export_btn)
        
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)
        
        # Tab widget for different reports
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_sales_tab()
        self.create_inventory_tab()
        self.create_audit_tab()
        self.create_customer_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
    def create_dashboard_tab(self):
        """Create dashboard with key metrics"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Key metrics in a grid
        metrics_grid = QGridLayout()
        
        # Sales metrics
        self.sales_card = self.create_metric_card("Total Sales", "$0.00", "#4CAF50")
        metrics_grid.addWidget(self.sales_card, 0, 0)
        
        self.orders_card = self.create_metric_card("Total Orders", "0", "#2196F3")
        metrics_grid.addWidget(self.orders_card, 0, 1)
        
        self.profit_card = self.create_metric_card("Total Profit", "$0.00", "#FF9800")
        metrics_grid.addWidget(self.profit_card, 0, 2)
        
        self.customers_card = self.create_metric_card("New Customers", "0", "#9C27B0")
        metrics_grid.addWidget(self.customers_card, 0, 3)
        
        layout.addLayout(metrics_grid)
        
        # Charts area
        charts_layout = QHBoxLayout()
        
        # Sales chart (placeholder)
        sales_chart = QLabel("Sales Trend Chart\n(Would show chart here)")
        sales_chart.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #ddd;
                padding: 20px;
                font-size: 14px;
                color: #666;
                min-height: 300px;
            }
        """)
        sales_chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
        charts_layout.addWidget(sales_chart, 2)
        
        # Top products
        self.top_products_table = DataTable()
        charts_layout.addWidget(self.top_products_table, 1)
        
        layout.addLayout(charts_layout)
        
        # Recent transactions
        layout.addWidget(QLabel("<b>Recent Transactions:</b>"))
        self.recent_transactions = DataTable()
        layout.addWidget(self.recent_transactions)
        
        self.tab_widget.addTab(tab, "Dashboard")
        
    def create_sales_tab(self):
        """Create sales reports tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Sales report type
        report_type_layout = QHBoxLayout()
        report_type_layout.addWidget(QLabel("Report Type:"))
        
        self.sales_report_type = QComboBox()
        self.sales_report_type.addItems([
            "Daily Sales",
            "Monthly Sales", 
            "Product-wise Sales",
            "Location-wise Sales",
            "Payment Method Analysis"
        ])
        report_type_layout.addWidget(self.sales_report_type)
        
        self.generate_sales_btn = ModernButton("Generate Report")
        self.generate_sales_btn.clicked.connect(self.generate_sales_report)
        report_type_layout.addWidget(self.generate_sales_btn)
        
        report_type_layout.addStretch()
        layout.addLayout(report_type_layout)
        
        # Sales data table
        self.sales_table = DataTable()
        layout.addWidget(self.sales_table)
        
        self.tab_widget.addTab(tab, "Sales Reports")
        
    def create_inventory_tab(self):
        """Create inventory reports tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Inventory report type
        inv_layout = QHBoxLayout()
        inv_layout.addWidget(QLabel("Inventory Report:"))
        
        self.inv_report_type = QComboBox()
        self.inv_report_type.addItems([
            "Current Stock Levels",
            "Low Stock Alerts",
            "Stock Movement History",
            "Inventory Valuation",
            "Stock Aging Report"
        ])
        inv_layout.addWidget(self.inv_report_type)
        
        self.generate_inv_btn = ModernButton("Generate Report")
        self.generate_inv_btn.clicked.connect(self.generate_inventory_report)
        inv_layout.addWidget(self.generate_inv_btn)
        
        inv_layout.addStretch()
        layout.addLayout(inv_layout)
        
        # Inventory table
        self.inventory_table = DataTable()
        layout.addWidget(self.inventory_table)
        
        self.tab_widget.addTab(tab, "Inventory Reports")
        
    def create_audit_tab(self):
        """Create audit logs tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Audit filters
        audit_filter_layout = QHBoxLayout()
        
        audit_filter_layout.addWidget(QLabel("Audit Type:"))
        self.audit_type = QComboBox()
        self.audit_type.addItems(["All", "Product Changes", "Order Changes", 
                                 "Stock Changes", "User Actions"])
        audit_filter_layout.addWidget(self.audit_type)
        
        audit_filter_layout.addWidget(QLabel("User:"))
        self.audit_user = QComboBox()
        self.load_audit_users()
        audit_filter_layout.addWidget(self.audit_user)
        
        self.load_audit_btn = ModernButton("Load Audit Logs")
        self.load_audit_btn.clicked.connect(self.load_audit_logs)
        audit_filter_layout.addWidget(self.load_audit_btn)
        
        audit_filter_layout.addStretch()
        layout.addLayout(audit_filter_layout)
        
        # Audit log table
        self.audit_table = DataTable()
        layout.addWidget(self.audit_table)
        
        self.tab_widget.addTab(tab, "Audit Logs")
        
    def create_customer_tab(self):
        """Create customer reports tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Customer report type
        cust_layout = QHBoxLayout()
        cust_layout.addWidget(QLabel("Customer Report:"))
        
        self.cust_report_type = QComboBox()
        self.cust_report_type.addItems([
            "Customer List",
            "Customer Purchase History",
            "Top Customers by Spending",
            "Customer Acquisition",
            "Customer Segmentation"
        ])
        cust_layout.addWidget(self.cust_report_type)
        
        self.generate_cust_btn = ModernButton("Generate Report")
        self.generate_cust_btn.clicked.connect(self.generate_customer_report)
        cust_layout.addWidget(self.generate_cust_btn)
        
        cust_layout.addStretch()
        layout.addLayout(cust_layout)
        
        # Customer table
        self.customer_report_table = DataTable()
        layout.addWidget(self.customer_report_table)
        
        self.tab_widget.addTab(tab, "Customer Reports")
        
    def create_metric_card(self, title, value, color):
        """Create a metric card widget"""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card
        
    def load_dashboard(self):
        """Load dashboard data"""
        try:
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")
            
            # Load sales metrics using ReportController
            sales_data = self.report_controller.generate_sales_report(date_from, date_to, 'day')
            
            # Calculate totals from sales data
            total_sales = 0
            total_orders = 0
            avg_order_value = 0
            
            if sales_data:
                # Sum up the values from each row
                for row in sales_data:
                    # Access sqlite3.Row values by key directly
                    total_sales += row['total_sales'] if 'total_sales' in row else 0
                    total_orders += row['total_orders'] if 'total_orders' in row else 0
                
                # Calculate average order value if there are orders
                if total_orders > 0:
                    avg_order_value = total_sales / total_orders
            
            # Update metrics cards
            self.update_metric_card(self.sales_card, f"${total_sales:,.2f}")
            self.update_metric_card(self.orders_card, str(total_orders))
            self.update_metric_card(self.profit_card, f"${avg_order_value:,.2f}")
            
            # Load new customers
            customers_data = self.db.fetchone("""
                SELECT COUNT(*) as new_customers
                FROM customers 
                WHERE DATE(created_at) BETWEEN ? AND ?
            """, (date_from, date_to))
            
            if customers_data:
                # Access sqlite3.Row by index or key
                new_customers = customers_data[0] if customers_data else 0
                self.update_metric_card(self.customers_card, str(new_customers))
            else:
                self.update_metric_card(self.customers_card, "0")
            
            # Load top products using ReportController
            product_performance = self.report_controller.generate_product_performance_report(30)
            
            # Display top products (first 10)
            if product_performance:
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels(['Product', 'Category', 'Model', 'Sales Count', 'Quantity', 'Revenue', 'Avg Price'])
                
                for row in list(product_performance)[:10]:
                    model.appendRow([
                        QStandardItem(str(row['product_name']) if 'product_name' in row else ''),
                        QStandardItem(str(row['category_brand']) if 'category_brand' in row else ''),
                        QStandardItem(str(row['model_name']) if 'model_name' in row else ''),
                        QStandardItem(str(row['times_ordered']) if 'times_ordered' in row else '0'),
                        QStandardItem(str(row['total_sold']) if 'total_sold' in row else '0'),
                        QStandardItem(f"${row['total_revenue']:,.2f}" if 'total_revenue' in row else '$0.00'),
                        QStandardItem(f"${row['avg_sale_price']:,.2f}" if 'avg_sale_price' in row else '$0.00')
                    ])
                
                self.top_products_table.setModel(model)
            
            # Load recent transactions
            recent_orders = self.db.fetchall("""
                SELECT o.order_id, c.customer_name, o.total, o.status, 
                    o.order_date, o.payment_method
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                WHERE DATE(o.order_date) BETWEEN ? AND ?
                ORDER BY o.order_date DESC
                LIMIT 20
            """, (date_from, date_to))
            
            # Display recent transactions
            if recent_orders:
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels(['Order ID', 'Customer', 'Amount', 'Status', 'Date', 'Payment'])
                
                for row in recent_orders:
                    model.appendRow([
                        QStandardItem(str(row['order_id']) if 'order_id' in row else ''),
                        QStandardItem(str(row['customer_name']) if 'customer_name' in row else ''),
                        QStandardItem(f"${row['total']:,.2f}" if 'total' in row else '$0.00'),
                        QStandardItem(str(row['status']) if 'status' in row else ''),
                        QStandardItem(str(row['order_date'])[:19] if 'order_date' in row and row['order_date'] else ''),
                        QStandardItem(str(row['payment_method']) if 'payment_method' in row else '')
                    ])
                
                self.recent_transactions.setModel(model)
            
            self.status_bar.showMessage(f"Dashboard loaded for {date_from} to {date_to}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load dashboard: {str(e)}")
            import traceback
            traceback.print_exc()  # This will print the full traceback to console
            
    def update_metric_card(self, card, value):
        """Update metric card value"""
        value_label = card.layout().itemAt(1).widget()
        value_label.setText(value)
        
    def generate_sales_report(self):
        """Generate sales report based on selected type"""
        report_type = self.sales_report_type.currentText()
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        
        try:
            # Use ReportController for sales reports
            if report_type == "Daily Sales":
                data = self.report_controller.generate_sales_report(date_from, date_to, 'day')
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels(['Period', 'Total Orders', 'Total Sales', 'Avg Order Value', 'Unique Customers'])
                
            elif report_type == "Monthly Sales":
                data = self.report_controller.generate_sales_report(date_from, date_to, 'month')
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels(['Period', 'Total Orders', 'Total Sales', 'Avg Order Value', 'Unique Customers'])
                
            elif report_type == "Product-wise Sales":
                data = self.db.fetchall("""
                    SELECT p.product_name, p.product_code, c.category_brand,
                        COUNT(oi.item_id) as sales_count, SUM(oi.qty) as total_qty,
                        SUM(oi.order_line_amount) as total_revenue,
                        AVG(oi.unit_price) as avg_price
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.product_id
                    JOIN categories c ON p.category_id = c.category_id
                    JOIN orders o ON oi.order_id = o.order_id
                    WHERE DATE(o.order_date) BETWEEN ? AND ?
                    GROUP BY p.product_id
                    ORDER BY total_revenue DESC
                """, (date_from, date_to))
                
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels([
                    'Product', 'Code', 'Category', 'Sales Count', 
                    'Quantity', 'Revenue', 'Avg Price'
                ])
                
            elif report_type == "Location-wise Sales":
                data = self.db.fetchall("""
                    SELECT l.location_name, l.location_type,
                        COUNT(o.order_id) as order_count, SUM(o.total) as total_sales,
                        AVG(o.total) as avg_order
                    FROM orders o
                    JOIN locations l ON o.location_id = l.location_id
                    WHERE DATE(o.order_date) BETWEEN ? AND ?
                    GROUP BY l.location_id
                    ORDER BY total_sales DESC
                """, (date_from, date_to))
                
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels([
                    'Location', 'Type', 'Orders', 'Total Sales', 'Avg Order'
                ])
                
            else:  # Payment Method Analysis
                data = self.db.fetchall("""
                    SELECT payment_method, COUNT(*) as transaction_count,
                        SUM(total) as total_amount, AVG(total) as avg_transaction
                    FROM orders
                    WHERE DATE(order_date) BETWEEN ? AND ?
                    GROUP BY payment_method
                    ORDER BY total_amount DESC
                """, (date_from, date_to))
                
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels([
                    'Payment Method', 'Transactions', 'Total Amount', 'Avg Transaction'
                ])
            
            # Populate model
            if data:
                for row in data:
                    # sqlite3.Row objects can be accessed by key
                    items = []
                    if hasattr(row, '_fields'):  # It's a sqlite3.Row
                        for key in row.keys():
                            items.append(QStandardItem(str(row[key])))
                    else:  # It's already a dictionary or something else
                        items = [QStandardItem(str(value)) for value in row]
                    model.appendRow(items)
            
            self.sales_table.setModel(model)
            self.status_bar.showMessage(f"Generated {report_type} report")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def generate_inventory_report(self):
        """Generate inventory report"""
        report_type = self.inv_report_type.currentText()
        
        try:
            if report_type == "Current Stock Levels":
                # Use ReportController for inventory report
                data = self.report_controller.generate_inventory_report()
                
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels([
                    'Code', 'Product', 'Category', 'Supplier', 
                    'Quantity', 'Unit Cost', 'Total Value', 'Location Stock'
                ])
                
                for row in data:
                    model.appendRow([
                        QStandardItem(row['product_id']),
                        QStandardItem(row['product_name']),
                        QStandardItem(row['category_brand']),
                        QStandardItem(row['supplier_name']),
                        QStandardItem(str(row['total_qty'])),
                        QStandardItem(f"${row['unit_cost']:,.2f}"),
                        QStandardItem(f"${row['inventory_amount']:,.2f}"),
                        QStandardItem(row['location_stock'] or 'N/A')
                    ])
            
            elif report_type == "Low Stock Alerts":
                data = self.db.fetchall("""
                    SELECT * FROM vw_low_stock_alert
                """)
                
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels([
                    'Code', 'Product', 'Category', 'Stock', 
                    'Cost', 'Wholesale', 'Sale', 'Status'
                ])
                
            elif report_type == "Stock Movement History":
                date_from = self.date_from.date().toString("yyyy-MM-dd")
                date_to = self.date_to.date().toString("yyyy-MM-dd")
                
                data = self.db.fetchall("""
                    SELECT smr.movement_date, p.product_name, 
                           from_loc.location_name as from_location,
                           to_loc.location_name as to_location,
                           smr.quantity_moved, smr.unit_cost,
                           smr.movement_amount, s.staff_name as approved_by
                    FROM stock_movement_records smr
                    JOIN products p ON smr.product_id = p.product_id
                    JOIN locations from_loc ON smr.from_location_id = from_loc.location_id
                    JOIN locations to_loc ON smr.to_location_id = to_loc.location_id
                    JOIN staff s ON smr.approved_by = s.staff_id
                    WHERE DATE(smr.movement_date) BETWEEN ? AND ?
                    ORDER BY smr.movement_date DESC
                """, (date_from, date_to))
                
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels([
                    'Date', 'Product', 'From', 'To', 
                    'Quantity', 'Unit Cost', 'Amount', 'Approved By'
                ])
                
            elif report_type == "Inventory Valuation":
                data = self.db.fetchall("""
                    SELECT c.category_brand, c.model_name,
                           COUNT(DISTINCT i.product_id) as product_count,
                           SUM(i.total_qty) as total_quantity,
                           SUM(i.inventory_amount) as total_value,
                           AVG(i.unit_cost) as avg_cost
                    FROM inventory i
                    JOIN products p ON i.product_id = p.product_id
                    JOIN categories c ON p.category_id = c.category_id
                    WHERE p.is_active = 1
                    GROUP BY c.category_id
                    ORDER BY total_value DESC
                """)
                
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels([
                    'Category', 'Model', 'Products', 'Quantity', 
                    'Total Value', 'Avg Cost'
                ])
                
            else:  # Stock Aging Report
                data = self.db.fetchall("""
                    SELECT p.product_code, p.product_name, i.total_qty,
                           MIN(s.created_at) as first_stock_date,
                           MAX(s.created_at) as last_stock_date,
                           JULIANDAY('now') - JULIANDAY(MIN(s.created_at)) as days_in_stock
                    FROM inventory i
                    JOIN products p ON i.product_id = p.product_id
                    JOIN stocks s ON i.product_id = s.product_id
                    WHERE p.is_active = 1
                    GROUP BY i.product_id
                    HAVING days_in_stock > 90
                    ORDER BY days_in_stock DESC
                """)
                
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels([
                    'Code', 'Product', 'Quantity', 'First Stock', 
                    'Last Stock', 'Days in Stock'
                ])
            
            # Populate model for non-ReportController reports
            if report_type != "Current Stock Levels":
                for row in data:
                    items = [QStandardItem(str(value)) for value in row.values()]
                    model.appendRow(items)
            
            self.inventory_table.setModel(model)
            self.status_bar.showMessage(f"Generated {report_type} report")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")
    def generate_customer_report(self):
        """Generate customer report"""
        report_type = self.cust_report_type.currentText()
        date_from = self.date_from.date().toString("yyyy-MM-dd")
        date_to = self.date_to.date().toString("yyyy-MM-dd")
        
        try:
            if report_type == "Customer List":
                # Use ReportController for customer report
                data = self.report_controller.generate_customer_report()
                
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels([
                    'ID', 'Name', 'Contact', 'Email', 'Address',
                    'Orders', 'Total Spent', 'Last Order', 'First Order', 'Avg Order'
                ])
                
                for row in data:
                    model.appendRow([
                        QStandardItem(str(row['customer_id'])),
                        QStandardItem(row['customer_name'] or 'N/A'),
                        QStandardItem(row['contact_no'] or 'N/A'),
                        QStandardItem(row['email'] or 'N/A'),
                        QStandardItem(row['address'] or 'N/A'),
                        QStandardItem(str(row['total_orders'] or 0)),
                        QStandardItem(f"${float(row['total_spent'] or 0):,.2f}"),
                        QStandardItem(str(row['last_order_date'] or 'N/A')),
                        QStandardItem(str(row['first_order_date'] or 'N/A')),
                        QStandardItem(f"${float(row['avg_order_value'] or 0):,.2f}")
                    ])
            
            elif report_type == "Customer Purchase History":
                customer_id, ok = QInputDialog.getInt(
                    self, "Customer ID", "Enter Customer ID:", 1, 1, 999999, 1
                )
                
                if ok:
                    data = self.db.fetchall("""
                        SELECT o.order_id, o.order_date, o.total, o.status,
                            o.payment_method, COUNT(oi.item_id) as item_count,
                            COALESCE(SUM(oi.qty), 0) as total_qty
                        FROM orders o
                        JOIN order_items oi ON o.order_id = oi.order_id
                        WHERE o.customer_id = ?
                        GROUP BY o.order_id
                        ORDER BY o.order_date DESC
                    """, (customer_id,))
                    
                    model = QStandardItemModel()
                    model.setHorizontalHeaderLabels([
                        'Order ID', 'Date', 'Amount', 'Status', 
                        'Payment', 'Items', 'Quantity'
                    ])
                    
                    for row in data:
                        model.appendRow([
                            QStandardItem(str(row['order_id'])),
                            QStandardItem(row['order_date']),
                            QStandardItem(f"${float(row['total'] or 0):,.2f}"),
                            QStandardItem(row['status'] or 'N/A'),
                            QStandardItem(row['payment_method'] or 'N/A'),
                            QStandardItem(str(row['item_count'] or 0)),
                            QStandardItem(str(row['total_qty'] or 0))
                        ])
                else:
                    return
                    
            elif report_type == "Top Customers by Spending":
                data = self.db.fetchall("""
                    SELECT * FROM vw_customer_orders
                    ORDER BY COALESCE(total_spent, 0) DESC
                    LIMIT 20
                """)
                
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels([
                    'ID', 'Name', 'Contact', 'Email',
                    'Orders', 'Total Spent', 'Last Order', 'First Order', 'Avg Order'
                ])
                
                for row in data:
                    model.appendRow([
                        QStandardItem(str(row['customer_id'])),
                        QStandardItem(row['customer_name'] or 'N/A'),
                        QStandardItem(row['contact_no'] or 'N/A'),
                        QStandardItem(row['email'] or 'N/A'),
                        QStandardItem(str(row['total_orders'] or 0)),
                        QStandardItem(f"${float(row['total_spent'] or 0):,.2f}"),
                        QStandardItem(str(row['last_order_date'] or 'N/A')),
                        QStandardItem(str(row['first_order_date'] or 'N/A')),
                        QStandardItem(f"${float(row['avg_order_value'] or 0):,.2f}")
                    ])
                
            elif report_type == "Customer Acquisition":
                data = self.db.fetchall("""
                    SELECT strftime('%Y-%m', created_at) as month,
                        COUNT(*) as new_customers,
                        COUNT(DISTINCT o.customer_id) as customers_with_orders,
                        COALESCE(SUM(o.total), 0) as monthly_revenue
                    FROM customers c
                    LEFT JOIN orders o ON c.customer_id = o.customer_id 
                        AND strftime('%Y-%m', o.order_date) = strftime('%Y-%m', c.created_at)
                    WHERE DATE(c.created_at) BETWEEN ? AND ?
                    GROUP BY strftime('%Y-%m', c.created_at)
                    ORDER BY month DESC
                """, (date_from, date_to))
                
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels([
                    'Month', 'New Customers', 'Active Customers', 'Revenue'
                ])
                
                for row in data:
                    model.appendRow([
                        QStandardItem(row['month']),
                        QStandardItem(str(row['new_customers'] or 0)),
                        QStandardItem(str(row['customers_with_orders'] or 0)),
                        QStandardItem(f"${float(row['monthly_revenue'] or 0):,.2f}")
                    ])
                
            else:  # Customer Segmentation
                data = self.db.fetchall("""
                    SELECT 
                        CASE 
                            WHEN COALESCE(total_spent, 0) >= 10000 THEN 'VIP (10k+)'
                            WHEN COALESCE(total_spent, 0) >= 5000 THEN 'Gold (5k-10k)'
                            WHEN COALESCE(total_spent, 0) >= 1000 THEN 'Silver (1k-5k)'
                            WHEN COALESCE(total_spent, 0) > 0 THEN 'Bronze (<1k)'
                            ELSE 'Prospect (0)'
                        END as segment,
                        COUNT(*) as customer_count,
                        COALESCE(SUM(total_spent), 0) as segment_total,
                        COALESCE(AVG(total_spent), 0) as avg_spent
                    FROM vw_customer_orders
                    GROUP BY segment
                    ORDER BY segment_total DESC
                """)
                
                model = QStandardItemModel()
                model.setHorizontalHeaderLabels([
                    'Segment', 'Customers', 'Total Value', 'Avg Value'
                ])
                
                for row in data:
                    model.appendRow([
                        QStandardItem(row['segment']),
                        QStandardItem(str(row['customer_count'] or 0)),
                        QStandardItem(f"${float(row['segment_total'] or 0):,.2f}"),
                        QStandardItem(f"${float(row['avg_spent'] or 0):,.2f}")
                    ])
            
            self.customer_report_table.setModel(model)
            self.status_bar.showMessage(f"Generated {report_type} report")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")



            
    def load_audit_users(self):
        """Load users for audit filter"""
        try:
            users = self.db.fetchall("""
                SELECT staff_id, staff_name FROM staff ORDER BY staff_name
            """)
            
            self.audit_user.clear()
            self.audit_user.addItem("All Users", None)
            
            for user in users:
                self.audit_user.addItem(user['staff_name'], user['staff_id'])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {str(e)}")
    def export_report(self):
        """Export current report to CSV"""
        try:
            current_tab = self.tab_widget.currentIndex()
            
            # Determine which table to export based on current tab
            if current_tab == 0:  # Dashboard tab
                QMessageBox.warning(self, "Export", "Please select a specific report tab (Sales, Inventory, Audit, or Customer) to export.")
                return
                
            elif current_tab == 1:  # Sales Reports
                model = self.sales_table.model()
                report_type = self.sales_report_type.currentText()
                
            elif current_tab == 2:  # Inventory Reports
                model = self.inventory_table.model()
                report_type = self.inv_report_type.currentText()
                
            elif current_tab == 3:  # Audit Logs
                model = self.audit_table.model()
                report_type = "Audit Logs"
                
            elif current_tab == 4:  # Customer Reports
                model = self.customer_report_table.model()
                report_type = self.cust_report_type.currentText()
                
            else:
                QMessageBox.warning(self, "Export", "Please select a report tab to export")
                return
                
            if not model or model.rowCount() == 0:
                QMessageBox.warning(self, "Warning", "No data to export")
                return
                
            # Get save file path
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"{report_type.replace(' ', '_')}_{date_str}.csv"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Export Report", 
                default_filename,
                "CSV Files (*.csv);;All Files (*)"
            )
            
            if not file_path:
                return  # User cancelled
                
            # Ensure .csv extension
            if not file_path.lower().endswith('.csv'):
                file_path += '.csv'
                
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Write headers
                    headers = []
                    for col in range(model.columnCount()):
                        header = model.headerData(col, Qt.Orientation.Horizontal)
                        # Escape commas in headers
                        if header and ',' in header:
                            header = f'"{header}"'
                        headers.append(header or f'Column{col+1}')
                    f.write(','.join(headers) + '\n')
                    
                    # Write data rows
                    for row in range(model.rowCount()):
                        row_data = []
                        for col in range(model.columnCount()):
                            item = model.item(row, col)
                            if item:
                                cell_text = item.text()
                                # Escape commas and quotes in cell text
                                if ',' in cell_text or '"' in cell_text:
                                    cell_text = f'"{cell_text.replace('"', '""')}"'
                                row_data.append(cell_text)
                            else:
                                row_data.append('')
                        f.write(','.join(row_data) + '\n')
                        
                QMessageBox.information(
                    self, 
                    "Export Successful", 
                    f"Report has been exported to:\n{file_path}"
                )
                
                self.status_bar.showMessage(f"Report exported: {file_path}")
                
            except PermissionError:
                QMessageBox.critical(
                    self, 
                    "Permission Error", 
                    "Cannot write to file. It may be open in another program."
                )
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Export Error", 
                    f"Failed to export report:\n{str(e)}"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")
            
    def load_audit_logs(self):
        """Load audit logs based on filters"""
        try:
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")
            audit_type = self.audit_type.currentText()
            user_id = self.audit_user.currentData()
            
            query = """
                SELECT 'Product' as type, ph.changed_at, s.staff_name as changed_by,
                       p.product_name as entity, ph.change_type, ph.remarks
                FROM products_history ph
                JOIN staff s ON ph.changed_by = s.staff_id
                JOIN products p ON ph.product_id = p.product_id
                WHERE DATE(ph.changed_at) BETWEEN ? AND ?
            """
            
            params = [date_from, date_to]
            
            if user_id:
                query += " AND ph.changed_by = ?"
                params.append(user_id)
                
            if audit_type != "All" and audit_type != "Product Changes":
                # For other types, we would query different tables
                query = query.replace("products_history", "orders_history")
                query = query.replace("p.product_name", "'Order #' || oh.order_id")
                
            query += " ORDER BY ph.changed_at DESC LIMIT 100"
            
            data = self.db.fetchall(query, params)
            
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels([
                'Type', 'Timestamp', 'Changed By', 'Entity', 'Change Type', 'Remarks'
            ])
            
            for row in data:
                model.appendRow([
                    QStandardItem(row['type']),
                    QStandardItem(row['changed_at']),
                    QStandardItem(row['changed_by']),
                    QStandardItem(str(row['entity'])),
                    QStandardItem(row['change_type']),
                    QStandardItem(row['remarks'] or '')
                ])
            
            self.audit_table.setModel(model)
            self.status_bar.showMessage(f"Loaded {len(data)} audit logs")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load audit logs: {str(e)}")
            
