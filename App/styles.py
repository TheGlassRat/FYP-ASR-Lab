"""
Central Design System for the ASR Feedback Application.
"""

DARK_THEME = """
QMainWindow, QWidget { background-color: #121218; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }

QFrame#sidebar { background-color: #1a1a24; border-right: 1px solid #2a2a3a; }
QLabel#sidebar_title { background: transparent; font-weight: bold; font-size: 20px; color: #3b86ff; margin-bottom: 20px; padding-left: 10px; }

QListWidget { background: transparent; border: none; outline: none; }
QListWidget::item { padding: 15px; border-radius: 8px; margin: 5px 0; font-size: 16px; }
QListWidget::item:selected { background-color: #3b86ff; color: white; font-weight: bold; }
QListWidget::item:hover:!selected { background-color: #2a2a3a; }

QFrame#card { background-color: #1a1a24; border: 1px solid #3a3a4a; border-radius: 15px; }

QPushButton { 
    background-color: #3b86ff; 
    color: white; 
    font-size: 14px; 
    font-weight: bold; 
    border-radius: 10px; 
    padding: 10px 20px; 
    border: none;
}
QPushButton:hover { background-color: #5a9bff; }
QPushButton:pressed { background-color: #2a6bcc; }
QPushButton:disabled { background-color: #2a2a3a; color: #555; }

QPushButton#secondary_btn { background-color: #2a2a3a; color: #ccc; border: 1px solid #3a3a4a; }
QPushButton#secondary_btn:hover { background-color: #3a3a4a; color: white; border: 1px solid #3b86ff; }

/* Icon-Only Player Buttons */
QPushButton#play_btn, QPushButton#play_pause_btn { 
    background-color: transparent; 
    border-radius: 22px;
    border: none;
    padding: 0;
}
QPushButton#play_btn:hover, QPushButton#play_pause_btn:hover { 
    background-color: rgba(59, 134, 255, 0.15); 
}

QLabel { background: transparent; }
QFrame { background: transparent; border: none; }
QFrame#card { background-color: #1a1a24; border-radius: 15px; border: 1px solid #2a2a3a; }

QPushButton#danger_btn { background-color: #cf6679; color: white; border-radius: 10px; font-weight: bold; }
QPushButton#danger_btn:hover { background-color: #e57373; }

QPushButton[recording="true"] { background-color: #ef5350; }
QPushButton[recording="true"]:hover { background-color: #f44336; }

QComboBox { 
    background-color: #14141c; 
    border: 1px solid #2a2a3a; 
    border-radius: 12px; 
    padding: 10px; 
    color: #e0e0e0; 
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 30px;
    border-left: 1px solid #2a2a3a;
}
QComboBox::down-arrow {
    image: url(App/Assets/icons8-tick-48.png); /* Fallback arrow */
    width: 12px;
    height: 12px;
}

QLabel#viz_label { background-color: transparent; border-radius: 12px; border: 1px solid #3a3a4a; color: #444; }

QTableWidget { 
    background-color: transparent; 
    border: 1px solid #2a2a3a; 
    border-radius: 12px; 
    gridline-color: transparent;
    alternate-background-color: transparent;
    outline: none;
}
QTableWidget::item { padding: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.03); color: #e0e0e0; }
QTableWidget::item:selected { background-color: rgba(59, 134, 255, 0.1); color: #e0e0e0; border: none; outline: none; }
QTableWidget::item:focus { border: none; outline: none; }
QTableWidget::indicator { width: 22px; height: 22px; border: 2px solid #3a3a4a; border-radius: 6px; background: #14141c; }
QTableWidget::indicator:checked { background: #3b86ff; border-color: #3b86ff; }
QTableWidget::item:hover { background-color: rgba(255, 255, 255, 0.03); }

QHeaderView::section { background-color: #1a1a24; color: #888; padding: 12px; border: none; font-weight: bold; }
QHeaderView { background: transparent; }

/* Scrollbar Dark */
QScrollBar:vertical { border: none; background: #1a1a24; width: 10px; margin: 0; border-radius: 5px; }
QScrollBar::handle:vertical { background: #3a3a4a; min-height: 20px; border-radius: 5px; }
QScrollBar::handle:vertical:hover { background: #3b86ff; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }

QScrollBar:horizontal { border: none; background: #1a1a24; height: 10px; margin: 0; border-radius: 5px; }
QScrollBar::handle:horizontal { background: #3a3a4a; min-width: 20px; border-radius: 5px; }
QScrollBar::handle:horizontal:hover { background: #3b86ff; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { border: none; background: none; }

QProgressBar { background-color: rgba(59, 134, 255, 0.1); border-radius: 6px; border: none; text-align: center; color: transparent; }
QProgressBar::chunk { background-color: #3b86ff; border-radius: 6px; }

QLabel { background: transparent; border: none; }
QLabel#h1 { font-size: 24px; font-weight: bold; }
QLabel#subtitle { font-size: 14px; color: #888; }
QLabel#path_label { font-size: 11px; color: #666; font-family: 'Consolas', monospace; }

/* Player & Misc Transparency */
QFrame#player_card, QGroupBox, QWidget#status_row, QSlider { background: transparent !important; border: none; }
QSlider::groove:horizontal { border: none; height: 6px; background: rgba(59, 134, 255, 0.15); border-radius: 3px; }
QSlider::handle:horizontal { background: #3b86ff; width: 14px; height: 14px; margin: -4px 0; border-radius: 7px; }
"""

LIGHT_THEME = """
QMainWindow, QWidget { background-color: #f8f9fa; color: #212529; font-family: 'Segoe UI', sans-serif; }

/* Scrollbar Light */
QScrollBar:vertical { border: none; background: #f1f3f5; width: 10px; margin: 0; border-radius: 5px; }
QScrollBar::handle:vertical { background: #dee2e6; min-height: 20px; border-radius: 5px; }
QScrollBar::handle:vertical:hover { background: #3b86ff; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }

QScrollBar:horizontal { border: none; background: #f1f3f5; height: 10px; margin: 0; border-radius: 5px; }
QScrollBar::handle:horizontal { background: #dee2e6; min-width: 20px; border-radius: 5px; }
QScrollBar::handle:horizontal:hover { background: #3b86ff; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { border: none; background: none; }

QFrame#sidebar { background-color: #ffffff; border-right: 1px solid #dee2e6; }
QLabel#sidebar_title { background: transparent; font-weight: bold; font-size: 20px; color: #3b86ff; margin-bottom: 20px; padding-left: 10px; }

QListWidget { background: transparent; border: none; outline: none; }
QListWidget::item { padding: 15px; border-radius: 8px; margin: 5px 0; font-size: 16px; color: #495057; }
QListWidget::item:selected { background-color: #3b86ff; color: white; font-weight: bold; }
QListWidget::item:hover:!selected { background-color: #e9ecef; }

QFrame#card { background-color: #ffffff; border: 1px solid #d1d5db; border-radius: 15px; }

QPushButton { 
    background-color: #3b86ff; 
    color: white; 
    font-size: 14px; 
    font-weight: bold; 
    border-radius: 10px; 
    padding: 10px 20px; 
    border: none;
}
QPushButton:hover { background-color: #5a9bff; }
QPushButton:pressed { background-color: #2a6bcc; }
QPushButton:disabled { background-color: #e9ecef; color: #aaa; }

QPushButton#secondary_btn { background-color: #f1f3f5; color: #495057; border: 1px solid #ced4da; }
QPushButton#secondary_btn:hover { background-color: #e9ecef; color: #212529; border: 1px solid #3b86ff; }

/* Icon-Only Player Buttons */
QPushButton#play_btn, QPushButton#play_pause_btn { 
    background-color: transparent; 
    border-radius: 22px;
    border: none;
    padding: 0;
}
QPushButton#play_btn:hover, QPushButton#play_pause_btn:hover { 
    background-color: rgba(0, 0, 0, 0.05); 
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 30px;
    border-left: 1px solid #cbd5e0;
}
QComboBox::down-arrow {
    image: url(App/Assets/icons8-tick-48.png); 
    width: 12px;
    height: 12px;
}

QLabel#viz_label { background-color: transparent; border-radius: 12px; border: 1px solid #cbd5e0; color: #aaa; }

QTableWidget { 
    background-color: transparent; 
    border: 1px solid #dee2e6; 
    border-radius: 12px; 
    gridline-color: #f1f3f5;
    outline: none;
}
QTableWidget::item { padding: 12px; border-bottom: 1px solid #eee; color: #212529; }
QTableWidget::item:selected { background-color: rgba(59, 134, 255, 0.1); color: #212529; border: none; outline: none; }
QTableWidget::item:focus { border: none; outline: none; }
QTableWidget::indicator { width: 22px; height: 22px; border: 2px solid #cbd5e0; border-radius: 6px; background: #ffffff; }
QTableWidget::indicator:checked { background: #3b86ff; border-color: #3b86ff; }
QTableWidget::item:hover { background-color: #f8f9fa; }

QHeaderView::section { background-color: #f1f3f5; color: #495057; padding: 12px; border: none; font-weight: bold; }

QProgressBar { background-color: rgba(0, 0, 0, 0.05); border-radius: 6px; border: none; text-align: center; color: transparent; }
QProgressBar::chunk { background-color: #3b86ff; border-radius: 6px; }

QLabel { background: transparent; border: none; }
QLabel#h1 { font-size: 24px; font-weight: bold; }
QLabel#subtitle { font-size: 14px; color: #495057; }

/* Player & Misc Transparency */
QFrame#player_card, QGroupBox, QWidget#status_row, QSlider { background: transparent !important; border: none; }
QSlider::groove:horizontal { border: none; height: 6px; background: rgba(0, 0, 0, 0.05); border-radius: 3px; }
QSlider::handle:horizontal { background: #3b86ff; width: 14px; height: 14px; margin: -4px 0; border-radius: 7px; }
"""

SUCCESS = "#4caf50"
WARNING = "#ffa726"
DANGER = "#ef5350"