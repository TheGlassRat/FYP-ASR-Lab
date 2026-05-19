from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton, 
    QHBoxLayout, QFileDialog, QLabel
)
from PySide6.QtCore import Qt
import os

class ValidationDialog(QDialog):
    def __init__(self, parent=None, initial_text=""):
        super().__init__(parent)
        self.setWindowTitle("Add Validation Ground Truth")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        layout.addWidget(QLabel("Enter ground truth text or upload a .txt file:"))
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Type valid transcription here...")
        self.text_edit.setText(initial_text)
        layout.addWidget(self.text_edit)
        
        btn_layout = QHBoxLayout()
        
        self.upload_btn = QPushButton(" Upload .txt")
        self.upload_btn.setFixedHeight(40)
        self.upload_btn.clicked.connect(self.upload_file)
        btn_layout.addWidget(self.upload_btn)
        
        btn_layout.addStretch()
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setFixedHeight(40)
        self.ok_btn.setFixedWidth(100)
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.setFixedWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)

    def upload_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Upload Text", "", "Text Files (*.txt)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.text_edit.setText(f.read().strip())
            except Exception as e:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"Could not read file: {e}")

    def get_text(self):
        return self.text_edit.toPlainText().strip()