# main.py - Entry point for Laptops Official
import sys
import os
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from welcome_window import WelcomeWindow

class InventoryApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setStyle('Fusion')
        
    def show_splash(self):
        """Show splash screen"""
        splash_pix = QPixmap(400, 300)
        splash_pix.fill(Qt.GlobalColor.darkGray)
        
        splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
        splash.show()
        
        # Simulate loading time
        QTimer.singleShot(2000, splash.close)
        return splash

def main():
    app = InventoryApp(sys.argv)
    
    # Show splash screen
    splash = app.show_splash()
    app.processEvents()
    
    # Create and show main window
    window = WelcomeWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()