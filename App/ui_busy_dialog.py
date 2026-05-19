from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect, QWidget
from PySide6.QtCore import Qt, QSize, QTimer, QRectF
from PySide6.QtGui import QColor, QPainter, QPen
import os

class LoadingSpinner(QWidget):
    def __init__(self, parent=None, color=QColor("#ffffff")):
        super().__init__(parent)
        self.color = color
        self._angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_animation)
        self.timer.start(16)
        self.setFixedSize(60, 60)

    def _update_animation(self):
        self._angle = (self._angle + 6) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen_width = 4
        rect = QRectF(pen_width, pen_width, self.width() - 2*pen_width, self.height() - 2*pen_width)
        
        bg_color = QColor(self.color)
        bg_color.setAlpha(40)
        painter.setPen(QPen(bg_color, pen_width, Qt.SolidLine, Qt.RoundCap))
        painter.drawEllipse(rect)
        
        painter.setPen(QPen(self.color, pen_width, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(rect, -self._angle * 16, 100 * 16)

class BusyDialog(QDialog):
    def __init__(self, parent=None, title="Processing", message="Please wait...", is_dark=True):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(360, 200)
        
        # Parent must be valid for minimization behavior
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        
        bg_color = "#1a1a2e" if is_dark else "#fcfcfd"
        text_color = "#ffffff" if is_dark else "#111827"
        border_color = "#3a3a5e" if is_dark else "#e5e7eb"
        accent_color = QColor("#5e5ce6") if is_dark else QColor("#2563eb")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.container = QFrame(self)
        self.container.setObjectName("busyContainer")
        self.container.setStyleSheet(f"""
            #busyContainer {{
                background-color: {bg_color};
                border-radius: 16px;
                border: 1px solid {border_color};
            }}
        """)
        main_layout.addWidget(self.container)
        
        content_layout = QVBoxLayout(self.container)
        content_layout.setAlignment(Qt.AlignCenter)
        content_layout.setSpacing(15)
        
        self.spinner = LoadingSpinner(self.container, color=accent_color)
        content_layout.addWidget(self.spinner, 0, Qt.AlignCenter)
        
        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet(f"font-weight: 500; font-size: 14px; color: {text_color}; background: transparent; border: none; padding: 0 30px;")
        content_layout.addWidget(self.label)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.container.setGraphicsEffect(shadow)

    def update_message(self, message):
        self.label.setText(message)