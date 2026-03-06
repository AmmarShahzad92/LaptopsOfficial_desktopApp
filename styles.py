STYLES = {
    "main": """
        QMainWindow {
            background-color: #2b2b2b;
        }
        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
        }
    """,
    
    "welcome": """
        QPushButton {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 20px;
            text-align: center;
            text-decoration: none;
            font-size: 18px;
            font-weight: bold;
            margin: 10px;
            border-radius: 10px;
            min-width: 300px;
            min-height: 100px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        QLabel {
            color: white;
            font-size: 24px;
            font-weight: bold;
        }
    """,
    
    "table": """
        QTableView {
            background-color: white;
            alternate-background-color: #f2f2f2;
            selection-background-color: #4CAF50;
            selection-color: white;
            border: 1px solid #ddd;
        }
        QHeaderView::section {
            background-color: #4CAF50;
            color: white;
            padding: 8px;
            border: 1px solid #ddd;
            font-weight: bold;
        }
    """,
    
    "form": """
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: white;
        }
        QLabel {
            color: #333;
            font-weight: bold;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #4CAF50;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
    """
}