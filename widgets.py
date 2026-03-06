from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import styles

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
# In widgets.py
from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import pyqtSignal

class SearchBox(QLineEdit):
    textChanged = pyqtSignal(str)  # Add this line
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.search_input = QLineEdit() 
        self.setFixedHeight(35)
        self.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)

class DataTable(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(styles.STYLES["table"])
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.horizontalHeader().setStretchLastSection(True)
        
class SectionTitle(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #4CAF50;
                padding: 10px 0;
                border-bottom: 2px solid #4CAF50;
            }
        """)