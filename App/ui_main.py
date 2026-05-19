from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, 
    QFrame, QStackedWidget, QListWidget, QPushButton
)
from PySide6.QtCore import Qt

class Ui_Main(QWidget):
    def __init__(self):
        super().__init__()

        # Main horizontal layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # --- Sidebar ---
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 30, 15, 30)
        sidebar_layout.setSpacing(10)

        self.sidebar_title = QLabel("ASR LAB")
        self.sidebar_title.setObjectName("sidebar_title")
        sidebar_layout.addWidget(self.sidebar_title)

        self.nav_list = QListWidget()
        self.nav_list.addItem("  Transcription") # Renamed from Feedback
        self.nav_list.addItem("  Model Hub")      # Renamed from Comparison
        self.nav_list.addItem("  Manager")        # Renamed from Analytics/History
        self.nav_list.addItem("  Model Status")
        self.nav_list.setCurrentRow(0)
        sidebar_layout.addWidget(self.nav_list)
        
        sidebar_layout.addStretch()
        
        self.theme_btn = QPushButton("Light Mode")
        self.theme_btn.setObjectName("secondary_btn")
        self.theme_btn.setMinimumHeight(40)
        sidebar_layout.addWidget(self.theme_btn)

        self.layout.addWidget(self.sidebar)

        # --- Content Area ---
        self.content_stack = QStackedWidget()
        self.layout.addWidget(self.content_stack)