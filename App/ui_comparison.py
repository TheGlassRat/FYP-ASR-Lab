from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, 
    QHBoxLayout, QPushButton, QHeaderView, QFrame, QTextEdit,
    QAbstractItemView, QTableWidgetItem, QScrollArea
)
from PySide6.QtCore import Qt

class Ui_Comparison(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        self.title = QLabel("Model Hub")
        self.title.setObjectName("h1")
        self.subtitle = QLabel("Benchmark accuracy and performance across selected engines.")
        self.subtitle.setObjectName("subtitle")
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)

        # Container for side-by-side cards
        h_cards_layout = QHBoxLayout()
        h_cards_layout.setSpacing(25)

        # Primary Result Component
        self.result_card = QFrame()
        self.result_card.setObjectName("card")
        res_v = QVBoxLayout(self.result_card)
        
        res_header = QHBoxLayout()
        res_header.addWidget(QLabel("PRIMARY TRANSCRIPTION"))
        self.confidence_label = QLabel("")
        self.confidence_label.setStyleSheet("font-weight: bold;")
        res_header.addWidget(self.confidence_label)
        res_header.addStretch()
        res_v.addLayout(res_header)
        
        self.transcription_box = QTextEdit()
        self.transcription_box.setPlaceholderText("Prediction will appear here...")
        self.transcription_box.setFixedHeight(120)
        self.transcription_box.setStyleSheet("background: transparent; border: 1px solid #2a2a3a;")
        res_v.addWidget(self.transcription_box)
        
        h_cards_layout.addWidget(self.result_card, 1)

        # Validation Ground Truth Card
        self.val_card = QFrame()
        self.val_card.setObjectName("card")
        val_card_layout = QVBoxLayout(self.val_card)
        
        val_card_header = QHBoxLayout()
        val_v_label = QLabel("VALIDATION GROUND TRUTH")
        val_card_header.addWidget(val_v_label)
        val_card_header.addStretch()
        
        self.val_btn = QPushButton(" Add Validation Text")
        self.val_btn.setFixedHeight(40)
        self.val_btn.setFixedWidth(200)
        val_card_header.addWidget(self.val_btn)
        val_card_layout.addLayout(val_card_header)
        
        self.validation_display = QTextEdit()
        self.validation_display.setReadOnly(True)
        self.validation_display.setPlaceholderText("No validation text provided...")
        self.validation_display.setFixedHeight(120) # Match transcription box
        self.validation_display.setStyleSheet("background: transparent; border: 1px solid #2a2a3a; color: #888;")
        val_card_layout.addWidget(self.validation_display)
        
        h_cards_layout.addWidget(self.val_card, 1)
        
        layout.addLayout(h_cards_layout)

        # Comparison Section
        self.comp_card = QFrame()
        self.comp_card.setObjectName("card")
        self.comp_card.setMinimumHeight(450) # Expanded
        comp_layout = QVBoxLayout(self.comp_card)
        
        comp_header = QHBoxLayout()
        engine_label = QLabel("ENGINE COMPARISON")
        comp_header.addWidget(engine_label)
        comp_header.addStretch()
        
        self.status_display = QLabel("READY")
        self.status_display.setAlignment(Qt.AlignCenter)
        self.status_display.setStyleSheet("color: #888; font-weight: bold; background: transparent;")
        comp_header.addWidget(self.status_display)
        
        comp_header.addStretch()

        self.compare_btn = QPushButton(" Run Multi-Model Comparison")
        self.compare_btn.setFixedHeight(45)
        self.compare_btn.setFixedWidth(240)
        comp_header.addWidget(self.compare_btn)
        comp_layout.addLayout(comp_header)

        self.table = QTableWidget()
        self.table.setColumnCount(7) 
        self.table.setHorizontalHeaderLabels([
            "Model Selection", "Inference Status", "Transcription", 
            "Confidence", "Latency", "WER", "RTFx"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 180) # Wide enough
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("background: transparent;")
        comp_layout.addWidget(self.table)
        
        # New Export Button location (Bottom Right of card)
        export_row = QHBoxLayout()
        export_row.addStretch()
        self.export_btn = QPushButton(" Export Comparison Results")
        self.export_btn.setFixedHeight(40)
        self.export_btn.setFixedWidth(220)
        export_row.addWidget(self.export_btn)
        comp_layout.addLayout(export_row)
        
        layout.addWidget(self.comp_card)
        layout.addStretch()

