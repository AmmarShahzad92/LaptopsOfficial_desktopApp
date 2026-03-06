from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import styles
from widgets import *
from app.database.db import Database

class InventoryWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.db = Database() 
        self.setWindowTitle("Inventory System - Stock Management")
        self.setGeometry(150, 150, 1400, 900)
        
        self.init_ui()
        self.load_inventory()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Title
        title = SectionTitle("Inventory System - Stock Management")
        main_layout.addWidget(title)
        
        # Top controls
        controls_layout = QHBoxLayout()
        
        self.search_box = SearchBox("Search inventory...")
        self.search_box.search_input.textChanged.connect(self.search_inventory)
        controls_layout.addWidget(self.search_box)
        
        self.add_stock_btn = ModernButton("Add Stock")
        self.add_stock_btn.clicked.connect(self.add_stock)
        controls_layout.addWidget(self.add_stock_btn)
        
        self.adjust_stock_btn = ModernButton("Adjust Stock")
        self.adjust_stock_btn.clicked.connect(self.adjust_stock)
        controls_layout.addWidget(self.adjust_stock_btn)
        
        self.move_stock_btn = ModernButton("Move Stock")
        self.move_stock_btn.clicked.connect(self.move_stock)
        controls_layout.addWidget(self.move_stock_btn)
        
        self.purchase_btn = ModernButton("New Purchase")
        self.purchase_btn.clicked.connect(self.new_purchase)
        controls_layout.addWidget(self.purchase_btn)
        
        controls_layout.addStretch()
        main_layout.addLayout(controls_layout)
        
        # Inventory table
        self.inventory_table = DataTable()
        self.inventory_table.setSelectionBehavior(QTableView.SelectRows)
        main_layout.addWidget(self.inventory_table)
        
        # Bottom summary
        summary_layout = QHBoxLayout()
        
        self.total_items_label = QLabel("Total Items: 0")
        self.total_qty_label = QLabel("Total Quantity: 0")
        self.total_value_label = QLabel("Total Value: $0.00")
        self.low_stock_label = QLabel("Low Stock Items: 0")
        
        for label in [self.total_items_label, self.total_qty_label, 
                     self.total_value_label, self.low_stock_label]:
            label.setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    padding: 10px;
                    background-color: #f0f0f0;
                    border-radius: 5px;
                    margin: 5px;
                }
            """)
            summary_layout.addWidget(label)
            
        summary_layout.addStretch()
        main_layout.addLayout(summary_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
    def load_inventory(self):
        """Load inventory data"""
        try:
            inventory = self.db.fetchall("""
                SELECT i.*, p.product_code, p.product_name, 
                       c.category_brand, c.model_name, s.supplier_name,
                       p.cost_price, p.wholesale_price, p.sale_price,
                       (SELECT GROUP_CONCAT(l.location_name || ': ' || st.qty_stocked, ' | ')
                        FROM stocks st 
                        JOIN locations l ON st.location_id = l.location_id
                        WHERE st.product_id = i.product_id) as stock_locations
                FROM inventory i
                JOIN products p ON i.product_id = p.product_id
                JOIN categories c ON p.category_id = c.category_id
                JOIN suppliers s ON p.supplier_id = s.supplier_id
                WHERE p.is_active = 1
                ORDER BY i.inventory_amount DESC
            """)
            
            # Create model
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels([
                'ID', 'Code', 'Product', 'Category', 'Supplier',
                'Quantity', 'Unit Cost', 'Total Value', 'Stock Locations'
            ])
            
            total_items = 0
            total_qty = 0
            total_value = 0
            low_stock_count = 0
            
            for row in inventory:
                total_items += 1
                total_qty += row['total_qty']
                total_value += row['inventory_amount']
                
                if row['total_qty'] <= 10:
                    low_stock_count += 1
                
                # Color code low stock items
                items = [
                    QStandardItem(str(row['product_id'])),
                    QStandardItem(row['product_code']),
                    QStandardItem(row['product_name']),
                    QStandardItem(row['category_brand']),
                    QStandardItem(row['supplier_name']),
                    QStandardItem(str(row['total_qty'])),
                    QStandardItem(f"${row['unit_cost']:.2f}"),
                    QStandardItem(f"${row['inventory_amount']:.2f}"),
                    QStandardItem(row['stock_locations'] or '')
                ]
                
                # Highlight low stock in red
                if row['total_qty'] <= 5:
                    for item in items:
                        item.setBackground(QColor(255, 200, 200))
                elif row['total_qty'] <= 10:
                    for item in items:
                        item.setBackground(QColor(255, 255, 200))
                        
                model.appendRow(items)
            
            self.inventory_table.setModel(model)
            
            # Update summary
            self.total_items_label.setText(f"Total Items: {total_items}")
            self.total_qty_label.setText(f"Total Quantity: {total_qty}")
            self.total_value_label.setText(f"Total Value: ${total_value:,.2f}")
            self.low_stock_label.setText(f"Low Stock Items: {low_stock_count}")
            
            self.status_bar.showMessage(f"Loaded {total_items} inventory items")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load inventory: {str(e)}")
            
    def search_inventory(self, text):
        """Search inventory items"""
        model = self.inventory_table.model()
        
        if not model:
            return
            
        for row in range(model.rowCount()):
            match = False
            for col in range(model.columnCount()):
                item = model.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
                    
            self.inventory_table.setRowHidden(row, not match)
            
    def add_stock(self):
        """Add stock to existing product"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Stock")
        dialog.setFixedSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Product selection
        product_layout = QHBoxLayout()
        product_layout.addWidget(QLabel("Product:"))
        
        self.product_combo = QComboBox()
        self.load_products_combo()
        product_layout.addWidget(self.product_combo, 1)
        
        layout.addLayout(product_layout)
        
        # Location selection
        location_layout = QHBoxLayout()
        location_layout.addWidget(QLabel("Location:"))
        
        self.location_combo = QComboBox()
        self.load_locations_combo()
        location_layout.addWidget(self.location_combo, 1)
        
        layout.addLayout(location_layout)
        
        # Quantity and cost
        form_layout = QFormLayout()
        
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(1)
        self.quantity_input.setMaximum(9999)
        self.quantity_input.setValue(1)
        
        self.unit_cost_input = QDoubleSpinBox()
        self.unit_cost_input.setMinimum(0)
        self.unit_cost_input.setMaximum(999999)
        self.unit_cost_input.setPrefix("$ ")
        self.unit_cost_input.setDecimals(2)
        
        form_layout.addRow("Quantity:", self.quantity_input)
        form_layout.addRow("Unit Cost:", self.unit_cost_input)
        
        layout.addLayout(form_layout)
        
        # Notes
        layout.addWidget(QLabel("Notes:"))
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        layout.addWidget(self.notes_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = ModernButton("Save")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        def save_stock():
            try:
                product_id = self.product_combo.currentData()
                location_id = self.location_combo.currentData()
                quantity = self.quantity_input.value()
                unit_cost = self.unit_cost_input.value()
                notes = self.notes_input.toPlainText()
                
                if not product_id:
                    QMessageBox.warning(dialog, "Warning", "Please select a product")
                    return
                    
                if not location_id:
                    QMessageBox.warning(dialog, "Warning", "Please select a location")
                    return
                    
                with self.db.transaction() as cursor:
                    # Check if stock already exists at location
                    existing = cursor.execute("""
                        SELECT stock_id, qty_stocked FROM stocks 
                        WHERE product_id = ? AND location_id = ?
                    """, (product_id, location_id)).fetchone()
                    
                    if existing:
                        # Update existing stock
                        new_qty = existing['qty_stocked'] + quantity
                        cursor.execute("""
                            UPDATE stocks 
                            SET qty_stocked = ?, unit_cost = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE stock_id = ?
                        """, (new_qty, unit_cost, existing['stock_id']))
                        
                        # Record history
                        cursor.execute("""
                            INSERT INTO stocks_history 
                            (stock_id, product_id, location_id, old_qty, new_qty,
                             change_type, changed_by, remarks)
                            VALUES (?, ?, ?, ?, ?, 'add', 1, ?)
                        """, (existing['stock_id'], product_id, location_id,
                              existing['qty_stocked'], new_qty, notes))
                    else:
                        # Create new stock record
                        cursor.execute("""
                            INSERT INTO stocks 
                            (product_id, location_id, qty_stocked, unit_cost, manager_id)
                            VALUES (?, ?, ?, ?, 1)
                        """, (product_id, location_id, quantity, unit_cost))
                        
                        stock_id = cursor.lastrowid
                        
                        # Record history
                        cursor.execute("""
                            INSERT INTO stocks_history 
                            (stock_id, product_id, location_id, old_qty, new_qty,
                             change_type, changed_by, remarks)
                            VALUES (?, ?, ?, 0, ?, 'add', 1, ?)
                        """, (stock_id, product_id, location_id, quantity, notes))
                        
                    # Update inventory table (trigger should handle this, but we update manually)
                    cursor.execute("""
                        UPDATE inventory 
                        SET total_qty = total_qty + ?, 
                            unit_cost = (SELECT AVG(unit_cost) FROM stocks WHERE product_id = ?),
                            last_updated = CURRENT_TIMESTAMP
                        WHERE product_id = ?
                    """, (quantity, product_id, product_id))
                    
                QMessageBox.information(dialog, "Success", "Stock added successfully!")
                dialog.accept()
                self.load_inventory()
                
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to add stock: {str(e)}")
                
        save_btn.clicked.connect(save_stock)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
        
    def adjust_stock(self):
        """Adjust stock quantity"""
        selection = self.inventory_table.selectionModel().selectedRows()
        
        if not selection:
            QMessageBox.warning(self, "Warning", "Please select an item to adjust")
            return
            
        row = selection[0].row()
        model = self.inventory_table.model()
        product_id = model.item(row, 0).text()
        product_name = model.item(row, 2).text()
        current_qty = int(model.item(row, 5).text())
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Adjust Stock - {product_name}")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel(f"<b>Product:</b> {product_name}"))
        layout.addWidget(QLabel(f"<b>Current Quantity:</b> {current_qty}"))
        
        # Adjustment type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Adjustment Type:"))
        
        self.adjust_type = QComboBox()
        self.adjust_type.addItems(["Add Stock", "Remove Stock", "Set Quantity"])
        type_layout.addWidget(self.adjust_type)
        layout.addLayout(type_layout)
        
        # Quantity
        layout.addWidget(QLabel("Quantity:"))
        self.adjust_qty = QSpinBox()
        self.adjust_qty.setMinimum(1)
        self.adjust_qty.setMaximum(9999)
        layout.addWidget(self.adjust_qty)
        
        # Reason
        layout.addWidget(QLabel("Reason:"))
        self.adjust_reason = QTextEdit()
        self.adjust_reason.setMaximumHeight(60)
        layout.addWidget(self.adjust_reason)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = ModernButton("Save Adjustment")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        def save_adjustment():
            try:
                adjustment_type = self.adjust_type.currentText()
                quantity = self.adjust_qty.value()
                reason = self.adjust_reason.toPlainText()
                
                with self.db.transaction() as cursor:
                    if adjustment_type == "Add Stock":
                        cursor.execute("""
                            UPDATE inventory 
                            SET total_qty = total_qty + ?, last_updated = CURRENT_TIMESTAMP
                            WHERE product_id = ?
                        """, (quantity, product_id))
                        
                        # Add to default location (location_id = 1)
                        cursor.execute("""
                            UPDATE stocks 
                            SET qty_stocked = qty_stocked + ?, updated_at = CURRENT_TIMESTAMP
                            WHERE product_id = ? AND location_id = 1
                        """, (quantity, product_id))
                        
                    elif adjustment_type == "Remove Stock":
                        if quantity > current_qty:
                            QMessageBox.warning(dialog, "Warning", 
                                               f"Cannot remove more than current quantity ({current_qty})")
                            return
                            
                        cursor.execute("""
                            UPDATE inventory 
                            SET total_qty = total_qty - ?, last_updated = CURRENT_TIMESTAMP
                            WHERE product_id = ?
                        """, (quantity, product_id))
                        
                        # Remove from default location
                        cursor.execute("""
                            UPDATE stocks 
                            SET qty_stocked = qty_stocked - ?, updated_at = CURRENT_TIMESTAMP
                            WHERE product_id = ? AND location_id = 1
                        """, (quantity, product_id))
                        
                    else:  # Set Quantity
                        cursor.execute("""
                            UPDATE inventory 
                            SET total_qty = ?, last_updated = CURRENT_TIMESTAMP
                            WHERE product_id = ?
                        """, (quantity, product_id))
                        
                        # Set at default location
                        cursor.execute("""
                            UPDATE stocks 
                            SET qty_stocked = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE product_id = ? AND location_id = 1
                        """, (quantity, product_id))
                    
                    # Record inventory history
                    cursor.execute("""
                        INSERT INTO inventory_history 
                        (inventory_id, product_id, old_total_qty, new_total_qty,
                         change_type, changed_by, remarks)
                        SELECT inventory_id, product_id, ?, ?, 'adjust', 1, ?
                        FROM inventory WHERE product_id = ?
                    """, (current_qty, quantity, reason, product_id))
                    
                QMessageBox.information(dialog, "Success", "Stock adjusted successfully!")
                dialog.accept()
                self.load_inventory()
                
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to adjust stock: {str(e)}")
                
        save_btn.clicked.connect(save_adjustment)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
        
    def move_stock(self):
        """Move stock between locations"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Move Stock Between Locations")
        dialog.setFixedSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Product selection
        product_layout = QHBoxLayout()
        product_layout.addWidget(QLabel("Product:"))
        
        self.move_product_combo = QComboBox()
        self.load_products_combo()
        product_layout.addWidget(self.move_product_combo, 1)
        layout.addLayout(product_layout)
        
        # From location
        from_layout = QHBoxLayout()
        from_layout.addWidget(QLabel("From Location:"))
        
        self.from_location_combo = QComboBox()
        self.load_locations_combo()
        from_layout.addWidget(self.from_location_combo, 1)
        layout.addLayout(from_layout)
        
        # To location
        to_layout = QHBoxLayout()
        to_layout.addWidget(QLabel("To Location:"))
        
        self.to_location_combo = QComboBox()
        self.load_locations_combo()
        to_layout.addWidget(self.to_location_combo, 1)
        layout.addLayout(to_layout)
        
        # Check available stock button
        check_btn = ModernButton("Check Available Stock")
        layout.addWidget(check_btn)
        
        # Available stock label
        self.available_stock_label = QLabel("Available stock: -")
        layout.addWidget(self.available_stock_label)
        
        # Quantity to move
        layout.addWidget(QLabel("Quantity to Move:"))
        self.move_qty = QSpinBox()
        self.move_qty.setMinimum(1)
        self.move_qty.setMaximum(9999)
        layout.addWidget(self.move_qty)
        
        # Buttons
        button_layout = QHBoxLayout()
        move_btn = ModernButton("Move Stock")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(move_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        def check_stock():
            product_id = self.move_product_combo.currentData()
            from_location_id = self.from_location_combo.currentData()
            
            if product_id and from_location_id:
                stock = self.db.fetchone("""
                    SELECT qty_stocked FROM stocks 
                    WHERE product_id = ? AND location_id = ?
                """, (product_id, from_location_id))
                
                available = stock['qty_stocked'] if stock else 0
                self.available_stock_label.setText(f"Available stock: {available}")
                self.move_qty.setMaximum(available)
                
        def move_stock():
            try:
                product_id = self.move_product_combo.currentData()
                from_location_id = self.from_location_combo.currentData()
                to_location_id = self.to_location_combo.currentData()
                quantity = self.move_qty.value()
                
                if not all([product_id, from_location_id, to_location_id]):
                    QMessageBox.warning(dialog, "Warning", "Please fill all fields")
                    return
                    
                if from_location_id == to_location_id:
                    QMessageBox.warning(dialog, "Warning", "Cannot move to same location")
                    return
                    
                with self.db.transaction() as cursor:
                    # Check source stock
                    source_stock = cursor.execute("""
                        SELECT stock_id, qty_stocked FROM stocks 
                        WHERE product_id = ? AND location_id = ?
                    """, (product_id, from_location_id)).fetchone()
                    
                    if not source_stock or source_stock['qty_stocked'] < quantity:
                        QMessageBox.warning(dialog, "Warning", "Insufficient stock at source location")
                        return
                    
                    # Remove from source
                    new_source_qty = source_stock['qty_stocked'] - quantity
                    cursor.execute("""
                        UPDATE stocks 
                        SET qty_stocked = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE stock_id = ?
                    """, (new_source_qty, source_stock['stock_id']))
                    
                    # Add to destination
                    dest_stock = cursor.execute("""
                        SELECT stock_id, qty_stocked FROM stocks 
                        WHERE product_id = ? AND location_id = ?
                    """, (product_id, to_location_id)).fetchone()
                    
                    if dest_stock:
                        new_dest_qty = dest_stock['qty_stocked'] + quantity
                        cursor.execute("""
                            UPDATE stocks 
                            SET qty_stocked = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE stock_id = ?
                        """, (new_dest_qty, dest_stock['stock_id']))
                    else:
                        # Get unit cost from source
                        unit_cost = cursor.execute("""
                            SELECT unit_cost FROM stocks 
                            WHERE stock_id = ?
                        """, (source_stock['stock_id'],)).fetchone()['unit_cost']
                        
                        cursor.execute("""
                            INSERT INTO stocks 
                            (product_id, location_id, qty_stocked, unit_cost)
                            VALUES (?, ?, ?, ?)
                        """, (product_id, to_location_id, quantity, unit_cost))
                    
                    # Create movement record
                    cursor.execute("""
                        INSERT INTO stock_movement_records 
                        (product_id, from_location_id, to_location_id, 
                         quantity_moved, unit_cost, approved_by, remarks)
                        SELECT ?, ?, ?, ?, unit_cost, 1, 'Stock movement'
                        FROM stocks WHERE product_id = ? AND location_id = ?
                        LIMIT 1
                    """, (product_id, from_location_id, to_location_id, 
                          quantity, product_id, from_location_id))
                    
                QMessageBox.information(dialog, "Success", "Stock moved successfully!")
                dialog.accept()
                self.load_inventory()
                
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to move stock: {str(e)}")
        
        check_btn.clicked.connect(check_stock)
        move_btn.clicked.connect(move_stock)
        cancel_btn.clicked.connect(dialog.reject)
        
        # Connect combobox changes
        self.move_product_combo.currentIndexChanged.connect(check_stock)
        self.from_location_combo.currentIndexChanged.connect(check_stock)
        
        dialog.exec_()
        
    def new_purchase(self):
        """Create new purchase order"""
        dialog = QDialog(self)
        dialog.setWindowTitle("New Purchase Order")
        dialog.setFixedSize(700, 600)
        
        layout = QVBoxLayout(dialog)
        
        # Supplier selection
        supplier_layout = QHBoxLayout()
        supplier_layout.addWidget(QLabel("Supplier:"))
        
        self.supplier_combo = QComboBox()
        suppliers = self.db.fetchall("SELECT supplier_id, supplier_name FROM suppliers ORDER BY supplier_name")
        for supplier in suppliers:
            self.supplier_combo.addItem(supplier['supplier_name'], supplier['supplier_id'])
        supplier_layout.addWidget(self.supplier_combo, 1)
        layout.addLayout(supplier_layout)
        
        # Purchase items table
        layout.addWidget(QLabel("<b>Purchase Items:</b>"))
        
        self.purchase_table = QTableWidget()
        self.purchase_table.setColumnCount(5)
        self.purchase_table.setHorizontalHeaderLabels([
            'Product', 'Quantity', 'Unit Cost', 'Total', 'Action'
        ])
        layout.addWidget(self.purchase_table)
        
        # Add item button
        add_item_btn = ModernButton("Add Item")
        add_item_btn.clicked.connect(self.add_purchase_item)
        layout.addWidget(add_item_btn)
        
        # Totals
        self.purchase_total_label = QLabel("<b>Purchase Total: $0.00</b>")
        layout.addWidget(self.purchase_total_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_purchase_btn = ModernButton("Save Purchase Order")
        cancel_purchase_btn = ModernButton("Cancel")
        
        button_layout.addWidget(save_purchase_btn)
        button_layout.addWidget(cancel_purchase_btn)
        layout.addLayout(button_layout)
        
        self.purchase_items = []
        
        def save_purchase():
            try:
                supplier_id = self.supplier_combo.currentData()
                
                if not supplier_id:
                    QMessageBox.warning(dialog, "Warning", "Please select a supplier")
                    return
                    
                if not self.purchase_items:
                    QMessageBox.warning(dialog, "Warning", "Please add at least one item")
                    return
                    
                with self.db.transaction() as cursor:
                    for item in self.purchase_items:
                        cursor.execute("""
                            INSERT INTO purchases 
                            (supplier_id, product_id, quantity, unit_cost,
                             received_by, location_id, remarks)
                            VALUES (?, ?, ?, ?, 1, 1, 'Purchase order')
                        """, (supplier_id, item['product_id'], item['quantity'], 
                              item['unit_cost']))
                        
                        # Add to stock
                        existing_stock = cursor.execute("""
                            SELECT stock_id, qty_stocked FROM stocks 
                            WHERE product_id = ? AND location_id = 1
                        """, (item['product_id'],)).fetchone()
                        
                        if existing_stock:
                            new_qty = existing_stock['qty_stocked'] + item['quantity']
                            cursor.execute("""
                                UPDATE stocks 
                                SET qty_stocked = ?, unit_cost = ?, updated_at = CURRENT_TIMESTAMP
                                WHERE stock_id = ?
                            """, (new_qty, item['unit_cost'], existing_stock['stock_id']))
                        else:
                            cursor.execute("""
                                INSERT INTO stocks 
                                (product_id, location_id, qty_stocked, unit_cost, manager_id)
                                VALUES (?, 1, ?, ?, 1)
                            """, (item['product_id'], item['quantity'], item['unit_cost']))
                            
                    # Update inventory
                    for item in self.purchase_items:
                        cursor.execute("""
                            UPDATE inventory 
                            SET total_qty = total_qty + ?, 
                                unit_cost = (SELECT AVG(unit_cost) FROM stocks WHERE product_id = ?),
                                last_updated = CURRENT_TIMESTAMP
                            WHERE product_id = ?
                        """, (item['quantity'], item['product_id'], item['product_id']))
                        
                QMessageBox.information(dialog, "Success", "Purchase order created and stock updated!")
                dialog.accept()
                self.load_inventory()
                
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to create purchase: {str(e)}")
                
        save_purchase_btn.clicked.connect(save_purchase)
        cancel_purchase_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()
        
    def add_purchase_item(self):
        """Add item to purchase order"""
        item_dialog = QDialog(self)
        item_dialog.setWindowTitle("Add Purchase Item")
        item_dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(item_dialog)
        
        # Product selection
        product_layout = QHBoxLayout()
        product_layout.addWidget(QLabel("Product:"))
        
        product_combo = QComboBox()
        products = self.db.fetchall("""
            SELECT p.product_id, p.product_code, p.product_name, 
                   c.category_brand, c.model_name, p.cost_price
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            WHERE p.is_active = 1
            ORDER BY p.product_name
        """)
        
        for product in products:
            text = f"{product['product_name']} ({product['product_code']})"
            product_combo.addItem(text, product)
        product_layout.addWidget(product_combo, 1)
        layout.addLayout(product_layout)
        
        # Quantity
        layout.addWidget(QLabel("Quantity:"))
        quantity_input = QSpinBox()
        quantity_input.setMinimum(1)
        quantity_input.setMaximum(9999)
        layout.addWidget(quantity_input)
        
        # Unit cost
        layout.addWidget(QLabel("Unit Cost:"))
        unit_cost_input = QDoubleSpinBox()
        unit_cost_input.setMinimum(0)
        unit_cost_input.setMaximum(999999)
        unit_cost_input.setPrefix("$ ")
        unit_cost_input.setDecimals(2)
        
        # Set default cost from product
        def update_cost():
            product = product_combo.currentData()
            if product:
                unit_cost_input.setValue(product['cost_price'])
                
        product_combo.currentIndexChanged.connect(update_cost)
        update_cost()
        
        layout.addWidget(unit_cost_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        add_btn = ModernButton("Add")
        cancel_btn = ModernButton("Cancel")
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        def add_item():
            product = product_combo.currentData()
            quantity = quantity_input.value()
            unit_cost = unit_cost_input.value()
            
            if not product:
                QMessageBox.warning(item_dialog, "Warning", "Please select a product")
                return
                
            item = {
                'product_id': product['product_id'],
                'product_name': product['product_name'],
                'product_code': product['product_code'],
                'quantity': quantity,
                'unit_cost': unit_cost,
                'total': quantity * unit_cost
            }
            
            self.purchase_items.append(item)
            
            # Update purchase table
            row = self.purchase_table.rowCount()
            self.purchase_table.insertRow(row)
            
            self.purchase_table.setItem(row, 0, QTableWidgetItem(product['product_name']))
            self.purchase_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
            self.purchase_table.setItem(row, 2, QTableWidgetItem(f"${unit_cost:.2f}"))
            self.purchase_table.setItem(row, 3, QTableWidgetItem(f"${item['total']:.2f}"))
            
            # Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.clicked.connect(lambda: self.remove_purchase_item(row))
            self.purchase_table.setCellWidget(row, 4, remove_btn)
            
            # Update total
            total = sum(item['total'] for item in self.purchase_items)
            self.purchase_total_label.setText(f"<b>Purchase Total: ${total:.2f}</b>")
            
            item_dialog.accept()
            
        add_btn.clicked.connect(add_item)
        cancel_btn.clicked.connect(item_dialog.reject)
        
        item_dialog.exec_()
        
    def remove_purchase_item(self, row):
        """Remove item from purchase order"""
        if 0 <= row < len(self.purchase_items):
            self.purchase_items.pop(row)
            self.purchase_table.removeRow(row)
            
            # Update total
            total = sum(item['total'] for item in self.purchase_items)
            self.purchase_total_label.setText(f"<b>Purchase Total: ${total:.2f}</b>")
            
    def load_products_combo(self):
        """Load products into combo box"""
        products = self.db.fetchall("""
            SELECT product_id, product_name, product_code 
            FROM products WHERE is_active = 1 
            ORDER BY product_name
        """)
        
        # Only clear and load if the combo box exists
        if hasattr(self, 'product_combo'):
            self.product_combo.clear()
            for product in products:
                text = f"{product['product_name']} ({product['product_code']})"
                self.product_combo.addItem(text, product['product_id'])
        
        # Only clear and load if the combo box exists
        if hasattr(self, 'move_product_combo'):
            self.move_product_combo.clear()
            for product in products:
                text = f"{product['product_name']} ({product['product_code']})"
                self.move_product_combo.addItem(text, product['product_id'])
        
    def load_locations_combo(self):
        """Load locations into combo box"""
        locations = self.db.fetchall("""
            SELECT location_id, location_name, location_type 
            FROM locations WHERE location_status = 'active'
            ORDER BY location_name
        """)
        
        # Only clear and load if the combo box exists
        if hasattr(self, 'location_combo'):
            self.location_combo.clear()
            for location in locations:
                text = f"{location['location_name']} ({location['location_type']})"
                self.location_combo.addItem(text, location['location_id'])
        
        # Only clear and load if the combo box exists
        if hasattr(self, 'from_location_combo'):
            self.from_location_combo.clear()
            for location in locations:
                text = f"{location['location_name']} ({location['location_type']})"
                self.from_location_combo.addItem(text, location['location_id'])
        
        # Only clear and load if the combo box exists
        if hasattr(self, 'to_location_combo'):
            self.to_location_combo.clear()
            for location in locations:
                text = f"{location['location_name']} ({location['location_type']})"
                self.to_location_combo.addItem(text, location['location_id'])