from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QProgressBar
)
from PySide6.QtCore import Qt

class Ui_Settings(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        self.title = QLabel("Model Status")
        self.title.setObjectName("h1")
        layout.addWidget(self.title)

        self.subtitle = QLabel("Manage model loading and application configurations.")
        self.subtitle.setObjectName("subtitle")
        layout.addWidget(self.subtitle)

        # Model Loading Status Container
        self.status_card = QFrame()
        self.status_card.setObjectName("card")
        status_layout = QVBoxLayout(self.status_card)
        
        status_header = QLabel("AI MODELS STATUS")
        status_header.setObjectName("subtitle")
        status_layout.addWidget(status_header)

        self.model_status_container = QVBoxLayout()
        status_layout.addLayout(self.model_status_container)
        
        layout.addWidget(self.status_card)
        layout.addStretch()

    def add_model_status(self, model_name):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 5, 0, 5)
        
        name_label = QLabel(model_name)
        name_label.setFixedWidth(150)
        
        progress = QProgressBar()
        progress.setFixedHeight(10)
        progress.setTextVisible(False)
        progress.setRange(0, 0) # Indeterminate initially
        
        status_label = QLabel("Loading...")
        status_label.setFixedWidth(80)
        
        row_layout.addWidget(name_label)
        row_layout.addWidget(progress)
        row_layout.addWidget(status_label)
        
        self.model_status_container.addWidget(row)
        return progress, status_label