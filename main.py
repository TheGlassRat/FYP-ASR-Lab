import sys
from PySide6.QtWidgets import QApplication
from App.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    from PySide6.QtGui import QFont
    app.setFont(QFont("Segoe UI", 10))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()