from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import styles
from widgets import *
from app.database.db import Database 
from datetime import datetime
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PyQt6.QtGui import QTextDocument, QPainter, QPageLayout

class POSWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database() 
        self.setWindowTitle("Point of Sale - Generate Receipts")
        self.setGeometry(150, 150, 1400, 900)
        
        self.cart_items = []
        self.current_customer = None
        
        self.init_ui()
        self.load_products()
        self.load_customers() 
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - Product selection
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Product search
        search_layout = QHBoxLayout()
        self.product_search = QLineEdit()
        self.product_search.setPlaceholderText("Search products...")
        self.product_search.textChanged.connect(self.search_products)
        search_layout.addWidget(self.product_search)
        
        left_layout.addLayout(search_layout)
        
        # Products list
        self.products_list = QListWidget()
        self.products_list.setStyleSheet("""
            QListWidget {
                font-size: 12px;
                background-color: white;
                border: 1px solid #ddd;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
                color: white;
            }
        """)
        self.products_list.itemDoubleClicked.connect(self.add_to_cart)
        left_layout.addWidget(self.products_list)
        
        # Right panel - Cart and checkout
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Customer selection
        customer_group = QGroupBox("Customer Information")
        customer_layout = QVBoxLayout()
        
        customer_select_layout = QHBoxLayout()
        self.customer_combo = QComboBox()
        
        
        new_customer_btn = ModernButton("New Customer")
        new_customer_btn.clicked.connect(self.create_customer)
        
        customer_select_layout.addWidget(QLabel("Customer:"))
        customer_select_layout.addWidget(self.customer_combo, 1)
        customer_select_layout.addWidget(new_customer_btn)
        
        customer_layout.addLayout(customer_select_layout)
        
        # Customer details
        self.customer_details = QLabel("Select a customer")
        self.customer_details.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        customer_layout.addWidget(self.customer_details)
        
        customer_group.setLayout(customer_layout)
        right_layout.addWidget(customer_group)
        
        # Cart items table
        cart_group = QGroupBox("Cart Items")
        cart_layout = QVBoxLayout()
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels([
            'Product', 'Code', 'Price', 'Qty', 'Total', 'Action'
        ])
        self.cart_table.horizontalHeader().setStretchLastSection(True)
        cart_layout.addWidget(self.cart_table)
        
        cart_group.setLayout(cart_layout)
        right_layout.addWidget(cart_group)
        
        # Cart totals
        totals_group = QGroupBox("Order Summary")
        totals_layout = QVBoxLayout()
        
        self.subtotal_label = QLabel("Subtotal: $0.00")
        self.tax_label = QLabel("Tax (13%): $0.00")
        self.total_label = QLabel("TOTAL: $0.00")
        
        for label in [self.subtotal_label, self.tax_label, self.total_label]:
            label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    padding: 5px;
                }
            """)
            
        totals_layout.addWidget(self.subtotal_label)
        totals_layout.addWidget(self.tax_label)
        totals_layout.addWidget(self.total_label)
        
        totals_group.setLayout(totals_layout)
        right_layout.addWidget(totals_group)
        
        # Payment buttons
        button_layout = QHBoxLayout()
        
        self.clear_cart_btn = ModernButton("Clear Cart")
        self.clear_cart_btn.clicked.connect(self.clear_cart)
        
        self.print_receipt_btn = ModernButton("Print Receipt")
        
        
        self.process_payment_btn = ModernButton("Process Payment")
        self.process_payment_btn.clicked.connect(self.process_payment)
        self.process_payment_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        button_layout.addWidget(self.clear_cart_btn)
        button_layout.addWidget(self.print_receipt_btn)
        button_layout.addWidget(self.process_payment_btn)
        
        right_layout.addLayout(button_layout)
        
        # Add panels to main layout
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 3)
        
        # Connect customer selection
        self.customer_combo.currentIndexChanged.connect(self.update_customer_details)
    
    
    def load_customers(self):
        """Load customers into combo box"""
        try:
            customers = self.db.fetchall("""
                SELECT customer_id, customer_name, contact_no, email
                FROM customers 
                ORDER BY customer_name
            """)
            
            self.customer_combo.clear()
            self.customer_combo.addItem("Select Customer", None)
            
            for customer in customers:
                display_text = f"{customer['customer_name']} - {customer['contact_no']}"
                self.customer_combo.addItem(display_text, customer['customer_id'])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load customers: {str(e)}")


    # def load_products(self):
    #     """Load products into list"""
    #     try:
    #         products = self.db.fetchall("""
    #             SELECT p.product_id, p.product_name, p.product_code, 
    #                 p.sale_price, c.category_brand, c.model_name,
    #                 COALESCE(SUM(s.qty_stocked), 0) as stock
    #             FROM products p
    #             JOIN categories c ON p.category_id = c.category_id
    #             LEFT JOIN stocks s ON p.product_id = s.product_id
    #             WHERE p.is_active = 1
    #             GROUP BY p.product_id, p.product_name, p.product_code, 
    #                     p.sale_price, c.category_brand, c.model_name
    #             ORDER BY p.product_name
    #         """)
            
    #         self.products_list.clear()
    #         self.all_products = products
            
    #         for product in products:
    #             item = QListWidgetItem()
    #             text = f"{product['product_name']} ({product['category_brand']} {product['model_name']})\n"
    #             text += f"Code: {product['product_code']} | Price: ${product['sale_price']:.2f} | Stock: {product['stock']}"
    #             item.setText(text)
    #             item.setData(Qt.UserRole, product)
    #             self.products_list.addItem(item)
                
    #     except Exception as e:
    #         QMessageBox.critical(self, "Error", f"Failed to load products: {str(e)}")
    #         print(f"Error details: {str(e)}")  # For debugging
    #         """Load customers into combo box"""
    #         try:
    #             customers = self.db.fetchall("""
    #                 SELECT customer_id, customer_name, contact_no, email
    #                 FROM customers 
    #                 ORDER BY customer_name
    #             """)
                
    #             self.customer_combo.clear()
    #             self.customer_combo.addItem("Select Customer", None)
                
    #             for customer in customers:
    #                 display_text = f"{customer['customer_name']} - {customer['contact_no']}"
    #                 self.customer_combo.addItem(display_text, customer['customer_id'])
                    
    #         except Exception as e:
    #             QMessageBox.critical(self, "Error", f"Failed to load customers: {str(e)}")
            
    def load_products(self):
        """Load products into list"""
        try:
            products = self.db.fetchall("""
                SELECT p.product_id, p.product_name, p.product_code, 
                    p.sale_price, c.category_brand, c.model_name,
                    COALESCE(SUM(s.qty_stocked), 0) as stock
                FROM products p
                JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN stocks s ON p.product_id = s.product_id
                WHERE p.is_active = 1
                GROUP BY p.product_id, p.product_name, p.product_code, 
                        p.sale_price, c.category_brand, c.model_name
                ORDER BY p.product_name
            """)
            
            self.products_list.clear()
            self.all_products = products
            
            for product in products:
                item = QListWidgetItem()
                text = f"{product['product_name']} ({product['category_brand']} {product['model_name']})\n"
                text += f"Code: {product['product_code']} | Price: ${product['sale_price']:.2f} | Stock: {product['stock']}"
                item.setText(text)
                item.setData(Qt.UserRole, product)
                self.products_list.addItem(item)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load products: {str(e)}")
            print(f"Error details: {str(e)}")



    def search_products(self):
        """Search products based on text"""
        search_text = self.product_search.text().lower()
        
        for i in range(self.products_list.count()):
            item = self.products_list.item(i)
            product = item.data(Qt.UserRole)
            
            matches = (search_text in product['product_name'].lower() or 
                      search_text in product['product_code'].lower() or
                      search_text in product['category_brand'].lower())
            
            item.setHidden(not matches)
            
    def add_to_cart(self, item):
        """Add product to cart"""
        product = item.data(Qt.UserRole)
            
            # Check stock
        if product['stock'] <= 0:
                QMessageBox.warning(self, "Out of Stock", 
                                    f"Product '{product['product_name']}' is out of stock!")
                return
            
            # Check if already in cart
        for cart_item in self.cart_items:
                if cart_item['product_id'] == product['product_id']:
                    if cart_item['quantity'] + 1 > product['stock']:
                        QMessageBox.warning(self, "Stock Limit", 
                                            f"Cannot add more. Only {product['stock']} available.")
                        return
                    cart_item['quantity'] += 1
                    cart_item['total'] = cart_item['quantity'] * cart_item['price']
                    self.update_cart_table()
                    self.calculate_totals()
                    return
                    
            # Add new item to cart
        cart_item = {
                'product_id': product['product_id'],
                'product_code': product['product_code'],
                'product_name': product['product_name'],
                'price': product['sale_price'],
                'quantity': 1,
                'total': product['sale_price']
            }
            
        self.cart_items.append(cart_item)
        self.update_cart_table()
        self.calculate_totals()

        
    def update_cart_table(self):
        """Update cart table display"""
        self.cart_table.setRowCount(len(self.cart_items))
        
        for row, item in enumerate(self.cart_items):
            # Product name
            name_cell = QTableWidgetItem(item['product_name'])
            name_cell.setFlags(name_cell.flags() & ~Qt.ItemIsEditable)
            
            # Product code
            code_cell = QTableWidgetItem(item['product_code'])
            code_cell.setFlags(code_cell.flags() & ~Qt.ItemIsEditable)
            
            # Price
            price_cell = QTableWidgetItem(f"${item['price']:.2f}")
            price_cell.setFlags(price_cell.flags() & ~Qt.ItemIsEditable)
            
            # Quantity spinbox
            qty_spin = QSpinBox()
            qty_spin.setMinimum(1)
            qty_spin.setMaximum(999)
            qty_spin.setValue(item['quantity'])
            qty_spin.valueChanged.connect(lambda value, r=row: self.update_quantity(r, value))
            
            # Total
            total_cell = QTableWidgetItem(f"${item['total']:.2f}")
            total_cell.setFlags(total_cell.flags() & ~Qt.ItemIsEditable)
            
            # Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.clicked.connect(lambda checked, r=row: self.remove_from_cart(r))
            
            # Set cells
            self.cart_table.setItem(row, 0, name_cell)
            self.cart_table.setItem(row, 1, code_cell)
            self.cart_table.setItem(row, 2, price_cell)
            self.cart_table.setCellWidget(row, 3, qty_spin)
            self.cart_table.setItem(row, 4, total_cell)
            self.cart_table.setCellWidget(row, 5, remove_btn)
            
        self.cart_table.resizeColumnsToContents()
        
    def update_quantity(self, row, quantity):
        """Update quantity of cart item"""
        if 0 <= row < len(self.cart_items):
            self.cart_items[row]['quantity'] = quantity
            self.cart_items[row]['total'] = quantity * self.cart_items[row]['price']
            self.update_cart_table()
            self.calculate_totals()
            
    def remove_from_cart(self, row):
        """Remove item from cart"""
        if 0 <= row < len(self.cart_items):
            self.cart_items.pop(row)
            self.update_cart_table()
            self.calculate_totals()
            
    def calculate_totals(self):
        """Calculate order totals"""
        subtotal = sum(item['total'] for item in self.cart_items)
        tax = subtotal * 0.13  # 13% tax
        total = subtotal + tax
        
        self.subtotal_label.setText(f"Subtotal: ${subtotal:.2f}")
        self.tax_label.setText(f"Tax (13%): ${tax:.2f}")
        self.total_label.setText(f"TOTAL: ${total:.2f}")
        
    def clear_cart(self):
        """Clear all items from cart"""
        self.cart_items.clear()
        self.update_cart_table()
        self.calculate_totals()
        
    def update_customer_details(self, index):
        """Update customer details display"""
        customer_id = self.customer_combo.itemData(index)
        
        if customer_id:
            try:
                customer = self.db.fetchone("""
                    SELECT customer_name, contact_no, email, address
                    FROM customers WHERE customer_id = ?
                """, (customer_id,))
                
                if customer:
                    details = f"<b>Name:</b> {customer['customer_name']}<br>"
                    details += f"<b>Contact:</b> {customer['contact_no'] or 'N/A'}<br>"
                    details += f"<b>Email:</b> {customer['email'] or 'N/A'}<br>"
                    details += f"<b>Address:</b> {customer['address'] or 'N/A'}"
                    self.customer_details.setText(details)
                    self.current_customer = customer_id
                    
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load customer: {str(e)}")
        else:
            self.customer_details.setText("Select a customer")
            self.current_customer = None
            
    def create_customer(self):
        """Open dialog to create new customer"""
        dialog = QDialog(self)
        dialog.setWindowTitle("New Customer")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        
        name_input = QLineEdit()
        contact_input = QLineEdit()
        email_input = QLineEdit()
        address_input = QTextEdit()
        address_input.setMaximumHeight(80)
        
        form.addRow("Name:", name_input)
        form.addRow("Contact:", contact_input)
        form.addRow("Email:", email_input)
        form.addRow("Address:", address_input)
        
        layout.addLayout(form)
        
        button_layout = QHBoxLayout()
        save_btn = ModernButton("Save")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        def save_customer():
            try:
                with self.db.transaction() as cursor:
                    cursor.execute("""
                        INSERT INTO customers (customer_name, contact_no, email, address)
                        VALUES (?, ?, ?, ?)
                    """, (name_input.text(), contact_input.text(), 
                          email_input.text(), address_input.toPlainText()))
                    
                    customer_id = cursor.lastrowid
                    
                QMessageBox.information(dialog, "Success", "Customer added!")
                self.load_customers()
                self.customer_combo.setCurrentIndex(self.customer_combo.findData(customer_id))
                dialog.accept()
                
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to save: {str(e)}")
                
        save_btn.clicked.connect(save_customer)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
        
    def process_payment(self):
        """Process the payment and create order"""
        if not self.current_customer:
            QMessageBox.warning(self, "Warning", "Please select a customer first")
            return
            
        if not self.cart_items:
            QMessageBox.warning(self, "Warning", "Cart is empty")
            return
            
        # Payment method dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Payment Method")
        dialog.setFixedSize(300, 200)
        
        layout = QVBoxLayout(dialog)
        
        method_combo = QComboBox()
        method_combo.addItems(['cash', 'card', 'bank_transfer'])
        
        layout.addWidget(QLabel("Select Payment Method:"))
        layout.addWidget(method_combo)
        
        subtotal = sum(item['total'] for item in self.cart_items)
        tax = subtotal * 0.13
        total = subtotal + tax
        
        layout.addWidget(QLabel(f"Subtotal: ${subtotal:.2f}"))
        layout.addWidget(QLabel(f"Tax: ${tax:.2f}"))
        layout.addWidget(QLabel(f"<b>Total: ${total:.2f}</b>"))
        
        button_layout = QHBoxLayout()
        process_btn = ModernButton("Complete Payment")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(process_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        def complete_payment():
            try:
                with self.db.transaction() as cursor:
                    # Create order - FIXED: Match columns with values
                    cursor.execute("""
                        INSERT INTO orders 
                        (customer_id, order_type, location_id, status, subtotal,
                        shipping_fee, payment_method, delivery_method)
                        VALUES (?, 'physical', 1, 'processing', ?, 0, ?, 'take_away')
                    """, (self.current_customer, subtotal, 
                        method_combo.currentText()))
                    
                    order_id = cursor.lastrowid
                    
                    # Add order items
                    for item in self.cart_items:
                        cursor.execute("""
                            INSERT INTO order_items 
                            (order_id, product_id, qty, unit_price)
                            VALUES (?, ?, ?, ?)
                        """, (order_id, item['product_id'], 
                            item['quantity'], item['price']))
                        
                        # Update stock (assuming location_id = 1 for store)
                        cursor.execute("""
                            UPDATE stocks 
                            SET qty_stocked = qty_stocked - ?
                            WHERE product_id = ? AND location_id = 1
                        """, (item['quantity'], item['product_id']))
                        
                    # Create invoice - FIXED: Match columns with values
                    cursor.execute("""
                        INSERT INTO invoices 
                        (order_id, customer_id, customer_name, invoice_date,
                        payment_method, subtotal, shipping_fee, discount_amount,
                        created_by, location_id)
                        SELECT 
                            ?, c.customer_id, c.customer_name, CURRENT_TIMESTAMP,
                            ?, ?, 0, 0, 1, 1
                        FROM customers c
                        WHERE c.customer_id = ?
                    """, (order_id, method_combo.currentText(), subtotal, 
                        self.current_customer))
                    
                    invoice_id = cursor.lastrowid
                    
                    # Add invoice items
                    cursor.execute("""
                        INSERT INTO invoice_items 
                        (invoice_id, order_item_id, product_id, quantity_sold, unit_price)
                        SELECT 
                            ?, oi.item_id, oi.product_id, oi.qty, oi.unit_price
                        FROM order_items oi
                        WHERE oi.order_id = ?
                    """, (invoice_id, order_id))
                    
                QMessageBox.information(self, "Success", 
                    f"Order #{order_id} created successfully!\nInvoice #{invoice_id} generated.")
                
                # Clear cart
                self.clear_cart()
                dialog.accept()
                
                # Show receipt
                self.show_receipt(invoice_id)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Payment failed: {str(e)}")
                
        process_btn.clicked.connect(complete_payment)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
        
    # def show_receipt(self, invoice_id):
    #     """Display receipt for the invoice"""
    #     try:
    #         invoice = Database.fetchone("""
    #             SELECT i.*, c.customer_name, c.contact_no, l.location_name
    #             FROM invoices i
    #             JOIN customers c ON i.customer_id = c.customer_id
    #             JOIN locations l ON i.location_id = l.location_id
    #             WHERE i.invoice_id = ?
    #         """, (invoice_id,))
            
    #         items = self.Database.fetchall("""
    #             SELECT ii.*, p.product_name, p.product_code
    #             FROM invoice_items ii
    #             JOIN products p ON ii.product_id = p.product_id
    #             WHERE ii.invoice_id = ?
    #         """, (invoice_id,))


    def show_receipt(self, invoice_id):
        """Display receipt for the invoice"""
        try:
            # Fixed: Removed Python comments from SQL string
            invoice = self.db.fetchone("""
                SELECT i.*, c.customer_name, c.contact_no, l.location_name
                FROM invoices i
                JOIN customers c ON i.customer_id = c.customer_id
                JOIN locations l ON i.location_id = l.location_id
                WHERE i.invoice_id = ?
            """, (invoice_id,))
            
            # Fixed: Removed Python comments from SQL string
            items = self.db.fetchall("""
                SELECT ii.*, p.product_name, p.product_code
                FROM invoice_items ii
                JOIN products p ON ii.product_id = p.product_id
                WHERE ii.invoice_id = ?
            """, (invoice_id,))
            
            if not invoice:
                QMessageBox.warning(self, "Warning", f"Invoice #{invoice_id} not found")
                return
                
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Receipt - Invoice #{invoice_id}")
            dialog.setFixedSize(500, 700)
            
            layout = QVBoxLayout(dialog)
            
            # Receipt header
            header = QLabel("<h2>INVOICE RECEIPT</h2>")
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(header)
            
            # Company info
            company_info = QLabel("""
                <b>Laptops Official</b><br>
                123 Main Street, Karachi<br>
                Phone: +92-21-1234567<br>
                Email: info@store.com
            """)
            company_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(company_info)
            
            # Invoice details
            details = QLabel(f"""
                <b>Invoice #:</b> {invoice['invoice_id']}<br>
                <b>Date:</b> {invoice['invoice_date']}<br>
                <b>Customer:</b> {invoice['customer_name']}<br>
                <b>Contact:</b> {invoice['contact_no'] or 'N/A'}
            """)
            layout.addWidget(details)
            
            # Items table
            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(['Product', 'Qty', 'Price', 'Total'])
            
            table.setRowCount(len(items))
            for row, item in enumerate(items):
                table.setItem(row, 0, QTableWidgetItem(item['product_name']))
                table.setItem(row, 1, QTableWidgetItem(str(item['quantity_sold'])))
                table.setItem(row, 2, QTableWidgetItem(f"${item['unit_price']:.2f}"))
                table.setItem(row, 3, QTableWidgetItem(f"${item['line_total']:.2f}"))
                
            table.resizeColumnsToContents()
            layout.addWidget(table)
            
            # Format payment method for display
            payment_method = invoice['payment_method']
            if payment_method == 'cash':
                payment_display = 'Cash'
            elif payment_method == 'card':
                payment_display = 'Card'
            elif payment_method == 'bank_transfer':
                payment_display = 'Bank Transfer'
            else:
                payment_display = payment_method
            
            # Totals
            totals = QLabel(f"""
                <hr>
                <b>Subtotal:</b> ${invoice['subtotal']:.2f}<br>
                <b>Shipping:</b> ${invoice['shipping_fee']:.2f}<br>
                <b>Discount:</b> ${invoice['discount_amount']:.2f}<br>
                <b style='font-size: 16px;'>GRAND TOTAL: ${invoice['grand_total']:.2f}</b><br><br>
                <b>Payment Method:</b> {payment_display}<br>
                <b>Thank you for your business!</b>
            """)
            layout.addWidget(totals)
            
            # Print button
            print_btn = ModernButton("Print Receipt")
            print_btn.clicked.connect(lambda: self.print_dialog(dialog))
            layout.addWidget(print_btn)
            
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate receipt: {str(e)}")
            print(f"Error details: {e}")  # For debugging
        
            
    def print_dialog(self, dialog):
        """Print the receipt dialog"""
        try:
            # Get the widget content
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPageSize(QPageSize.A5))
            printer.setOrientation(QPrinter.Portrait)
            
            # Simple print without dialog
            painter = QPainter()
            painter.begin(printer)
            
            # Scale to fit the page
            scale_factor = printer.pageRect().width() / dialog.width()
            painter.scale(scale_factor, scale_factor)
            
            # Render the dialog as image
            dialog.render(painter)
            painter.end()
            
            QMessageBox.information(self, "Print", "Receipt sent to printer!")
            
        except Exception as e:
            QMessageBox.warning(self, "Print Error", f"Failed to print: {str(e)}")