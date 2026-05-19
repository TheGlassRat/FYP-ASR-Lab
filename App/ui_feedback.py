from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QProgressBar, QFrame, QSlider, QComboBox
)
from PySide6.QtCore import Qt, QSize

class Ui_Feedback(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(25)

        # Header
        top_h = QHBoxLayout()
        header_v = QVBoxLayout()
        self.title = QLabel("Transcription") # Renamed
        self.title.setObjectName("h1")
        self.subtitle = QLabel("Record or upload audio to generate prediction.")
        self.subtitle.setObjectName("subtitle")
        header_v.addWidget(self.title)
        header_v.addWidget(self.subtitle)
        top_h.addLayout(header_v)
        top_h.addStretch()
        
        self.rec_indicator = QLabel() # Will hold the icons8-recording-96.png
        self.rec_indicator.setFixedSize(60, 60)
        self.rec_indicator.setScaledContents(True)
        self.rec_indicator.setVisible(False)
        top_h.addWidget(self.rec_indicator)
        layout.addLayout(top_h)

        # Controls Card
        ctrl_card = QFrame()
        ctrl_card.setObjectName("card")
        ctrl_layout = QVBoxLayout(ctrl_card)
        ctrl_layout.setSpacing(15)
        
        btn_row = QHBoxLayout()
        self.record_btn = QPushButton("Start Recording")
        self.record_btn.setFixedHeight(55)
        
        self.upload_btn = QPushButton("Upload Audio")
        self.upload_btn.setObjectName("secondary_btn")
        self.upload_btn.setFixedHeight(55)
        
        btn_row.addWidget(self.record_btn, 2)
        btn_row.addWidget(self.upload_btn, 1)
        ctrl_layout.addLayout(btn_row)

        # Status & Smooth Timer Bar
        self.status_label = QLabel("READY")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #888; font-weight: bold;")
        ctrl_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        ctrl_layout.addWidget(self.progress_bar)
        
        # Player Row (Moved here to save space)
        self.player_card = QFrame()
        self.player_card.setObjectName("player_card")
        self.player_card.setMaximumHeight(50)
        player_layout = QHBoxLayout(self.player_card)
        player_layout.setContentsMargins(0, 0, 0, 0)
        
        self.play_btn = QPushButton()
        self.play_btn.setObjectName("play_btn")
        self.play_btn.setFixedSize(44, 44)
        
        self.play_slider = QSlider(Qt.Horizontal)
        self.play_slider.setObjectName("audio_slider")
        self.play_slider.setFixedHeight(20)
        
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet("font-family: 'JetBrains Mono'; font-size: 11px; background: transparent;")
        
        player_layout.addWidget(self.play_btn)
        player_layout.addWidget(self.play_slider)
        player_layout.addWidget(self.time_label)
        self.player_card.setVisible(True)
        ctrl_layout.addWidget(self.player_card)
        
        layout.addWidget(ctrl_card)

        # Visuals Container (HORIZONTAL STACKED as requested)
        viz_container = QHBoxLayout()
        viz_container.setSpacing(20)
        
        self.spec_label = QLabel("Spectrogram")
        self.spec_label.setObjectName("viz_label")
        self.spec_label.setAlignment(Qt.AlignCenter)
        self.spec_label.setMinimumHeight(280) # Reduced to 280
        
        self.mfcc_label = QLabel("MFCC")
        self.mfcc_label.setObjectName("viz_label")
        self.mfcc_label.setAlignment(Qt.AlignCenter)
        self.mfcc_label.setMinimumHeight(280) # Reduced to 280
        
        viz_container.addWidget(self.spec_label)
        viz_container.addWidget(self.mfcc_label)
        layout.addLayout(viz_container)

        # Action Area: Model Selection + Predict
        action_card = QFrame()
        action_card.setObjectName("card")
        action_layout = QVBoxLayout(action_card)
        action_layout.setContentsMargins(20, 20, 20, 20)
        action_layout.setSpacing(15)

        # Controls Row
        bottom_row = QHBoxLayout()
        # Model Selection
        sel_v = QVBoxLayout()
        sel_header = QHBoxLayout()
        sel_label = QLabel("MODEL SELECTION")
        sel_label.setObjectName("subtitle")
        sel_header.addWidget(sel_label)
        sel_header.addStretch()
        
        self.model_status_tag = QLabel("NOT LOADED")
        self.model_status_tag.setStyleSheet("color: #cf6679; font-weight: bold; font-size: 11px;")
        sel_header.addWidget(self.model_status_tag)
        sel_v.addLayout(sel_header)
        
        self.model_selector = QComboBox()
        self.model_selector.setFixedHeight(45)
        self.model_selector.setMinimumWidth(300)
        sel_v.addWidget(self.model_selector)
        bottom_row.addLayout(sel_v)
        
        bottom_row.addStretch()

        self.predict_btn = QPushButton("Predict Text")
        self.predict_btn.setFixedHeight(55)
        self.predict_btn.setMinimumWidth(200)
        bottom_row.addWidget(self.predict_btn)
        
        action_layout.addLayout(bottom_row)
        layout.addWidget(action_card)
        
        # Spacer
        layout.addStretch()