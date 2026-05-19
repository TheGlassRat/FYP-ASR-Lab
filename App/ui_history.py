from PySide6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QPushButton, QTableWidget,
    QHBoxLayout, QLineEdit, QLabel, QHeaderView, QAbstractItemView,
    QTextEdit, QSlider
)
from PySide6.QtCore import QSize, Qt

class Ui_History(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Header
        header_layout = QVBoxLayout()
        self.title = QLabel("Audio Manager") # Renamed
        self.title.setObjectName("h1")
        
        self.subtitle = QLabel("Review, play, and manage your previous voice submissions.")
        self.subtitle.setObjectName("subtitle")
        
        header_layout.addWidget(self.title)
        header_layout.addWidget(self.subtitle)
        layout.addLayout(header_layout)

        # Search and Actions
        top_bar = QHBoxLayout()
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search transcriptions...")
        self.search_box.setFixedHeight(45)
        self.search_box.setMinimumWidth(1000)
        
        self.export_btn = QPushButton(" Export CSV")
        self.export_btn.setObjectName("secondary_btn")
        self.export_btn.setFixedHeight(45)
        self.export_btn.setFixedWidth(160)

        top_bar.addStretch()
        top_bar.addWidget(self.search_box)
        top_bar.addWidget(self.export_btn)
        top_bar.setSpacing(20)
        layout.addLayout(top_bar)

        # Table
        self.table_card = QFrame()
        self.table_card.setObjectName("card")
        table_layout = QVBoxLayout(self.table_card)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Timestamp", "Transcription", "Audio File"])
        self.table.verticalHeader().setVisible(False) # Remove 1, 2, 3... numbering
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setColumnWidth(0, 50)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setStyleSheet("background: transparent;")
        
        table_layout.addWidget(self.table)
        layout.addWidget(self.table_card)

        # Preview & Player
        preview_card = QFrame()
        preview_card.setObjectName("card")
        preview_card.setMaximumHeight(180) # Shrink height
        preview_layout = QVBoxLayout(preview_card)
        
        preview_header_row = QHBoxLayout()
        preview_header = QLabel("SELECTED RECORD DETAILS")
        preview_header.setObjectName("subtitle")
        preview_header_row.addWidget(preview_header)
        preview_header_row.addStretch()
        
        self.path_display_label = QLabel("")
        self.path_display_label.setObjectName("path_label")
        preview_header_row.addWidget(self.path_display_label)
        preview_layout.addLayout(preview_header_row)
        
        self.transcription_detail = QTextEdit()
        self.transcription_detail.setReadOnly(True)
        self.transcription_detail.setPlaceholderText("Select a record to view details...")
        self.transcription_detail.setMaximumHeight(60) # Shrink detail box
        self.transcription_detail.setStyleSheet("background: transparent; border: 1px solid #2a2a3a;")
        preview_layout.addWidget(self.transcription_detail)
        
        # Mini Player (Transparent)
        mini_player = QHBoxLayout()
        self.play_pause_btn = QPushButton()
        self.play_pause_btn.setObjectName("play_pause_btn")
        self.play_pause_btn.setFixedSize(44, 44)
        
        self.audio_slider = QSlider(Qt.Horizontal)
        self.audio_slider.setObjectName("audio_slider")
        
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("font-family: 'JetBrains Mono'; font-size: 11px;")
        
        mini_player.addWidget(self.play_pause_btn)
        mini_player.addWidget(self.audio_slider)
        mini_player.addWidget(self.time_label)
        preview_layout.addLayout(mini_player)
        
        layout.addWidget(preview_card)

        # Bottom Actions
        btn_layout = QHBoxLayout()
        
        self.transcribe_selected_btn = QPushButton("Transcribe Selected") # Renamed from Compare
        self.transcribe_selected_btn.setObjectName("secondary_btn")
        self.transcribe_selected_btn.setFixedHeight(50)
        self.transcribe_selected_btn.setFixedWidth(180)
        
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.setObjectName("danger_btn")
        self.delete_btn.setFixedHeight(50)
        self.delete_btn.setFixedWidth(160)

        self.delete_all_btn = QPushButton("Clear Database")
        self.delete_all_btn.setObjectName("danger_btn")
        self.delete_all_btn.setFixedHeight(50)
        self.delete_all_btn.setFixedWidth(160)

        btn_layout.addStretch()
        btn_layout.addWidget(self.transcribe_selected_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.delete_all_btn)
        layout.addLayout(btn_layout)
