from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import styles
from widgets import ModernButton
from admin_panel import AdminPanel
from pos_window import POSWindow
from reports_window import ReportsWindow
from inventory_window import InventoryWindow

class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Laptops Official")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(styles.STYLES["main"])
        
        self.init_ui()
        
    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)
        
        # Title
        title = QLabel("Laptops Official")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #4CAF50;
                padding: 20px;
            }
        """)
        layout.addWidget(title)
        
        # Tagline
        subtitle = QLabel("Know It. Test It. Own It.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #ccc;
                padding: 10px;
            }
        """)
        layout.addWidget(subtitle)
        
        # Buttons grid
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # Admin Panel Button
        self.admin_btn = ModernButton("Admin Panel\n(Complete Management)")
        self.admin_btn.clicked.connect(self.open_admin_panel)
        grid.addWidget(self.admin_btn, 0, 0)
        
        # POS Button
        self.pos_btn = ModernButton("Point of Sale\n(Generate Receipts)")
        self.pos_btn.clicked.connect(self.open_pos)
        grid.addWidget(self.pos_btn, 0, 1)
        
        # Reports Button
        self.reports_btn = ModernButton("Audits & Reports\n(History & Analytics)")
        self.reports_btn.clicked.connect(self.open_reports)
        grid.addWidget(self.reports_btn, 1, 0)
        
        # Inventory Button
        self.inventory_btn = ModernButton("Inventory System\n(Stock Management)")
        self.inventory_btn.clicked.connect(self.open_inventory)
        grid.addWidget(self.inventory_btn, 1, 1)
        
        layout.addLayout(grid)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Set welcome style
        central_widget.setStyleSheet(styles.STYLES["welcome"])
        
    def open_admin_panel(self):
        self.admin_panel = AdminPanel()
        self.admin_panel.show()
        
    def open_pos(self):
        self.pos_window = POSWindow()
        self.pos_window.show()
        
    def open_reports(self):
        self.reports_window = ReportsWindow()
        self.reports_window.show()
        
    def open_inventory(self):
        self.inventory_window = InventoryWindow()
        self.inventory_window.show()