"""
Sidebar for RehabQuest
-----------------------
Left-hand persistent navigation with branded gradient, active indicators,
streak card, and patient profile badge.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QLinearGradient, QPainter, QColor

NAV_ITEMS = [
    ("home", "\U0001F3E0", "Home"),
    ("games", "\U0001F3AE", "Games"),
    ("body_parts", "\U0001FA7A", "Target Limbs"),
    ("report", "\U0001F4CB", "Report"),
    ("progress", "\U0001F4C8", "Progress"),
]


class Sidebar(QFrame):

    nav_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(200)
        self._nav_buttons = {}
        self._user_name = "Alex Mercer"
        self._streak_count = 5
        self._build_ui()
        self.set_active("home")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#7E5BE8"))
        gradient.setColorAt(1.0, QColor("#5B3FC2"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(self.rect(), 22, 22)
        super().paintEvent(event)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 22, 16, 18)
        layout.setSpacing(0)

        # Brand row
        brand_row = QHBoxLayout()
        brand_row.setSpacing(8)
        logo = QLabel("\u2695\ufe0f")
        logo.setStyleSheet("background: transparent; font-size: 20px;")
        brand_row.addWidget(logo)

        brand_label = QLabel("REHABQUEST")
        brand_font = QFont("Segoe UI", 11)
        brand_font.setWeight(QFont.Weight.Bold)
        brand_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.2)
        brand_label.setFont(brand_font)
        brand_label.setStyleSheet("color: #FFFFFF; background: transparent;")
        brand_row.addWidget(brand_label)
        brand_row.addStretch()
        layout.addLayout(brand_row)
        layout.addSpacing(28)

        # Nav Buttons
        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)
        for key, icon, label in NAV_ITEMS:
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(44)
            btn.setStyleSheet(self._nav_button_style())
            btn.clicked.connect(lambda _, k=key: self._on_nav_clicked(k))
            self._set_nav_text(btn, icon, label, active=(key == "home"))
            self._btn_group.addButton(btn)
            self._nav_buttons[key] = (btn, icon, label)
            layout.addWidget(btn)
            layout.addSpacing(6)

        layout.addSpacing(14)
        layout.addStretch()

        # Streak Card
        streak_card = QFrame()
        streak_card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 220);
                border-radius: 14px;
            }
        """)
        streak_layout = QVBoxLayout(streak_card)
        streak_layout.setContentsMargins(14, 12, 14, 12)
        streak_layout.setSpacing(2)

        streak_hdr = QHBoxLayout()
        flame = QLabel("\U0001F525")
        flame.setStyleSheet("background: transparent; font-size: 16px;")
        streak_hdr.addWidget(flame)
        self._streak_label = QLabel(f"{self._streak_count} Day Streak")
        self._streak_label.setStyleSheet("color: #583BB8; font-weight: bold; font-size: 12px; background: transparent;")
        streak_hdr.addWidget(self._streak_label)
        streak_hdr.addStretch()
        streak_layout.addLayout(streak_hdr)

        sub = QLabel("Keep the momentum going!")
        sub.setStyleSheet("color: #7B6D9E; font-size: 10px; background: transparent;")
        streak_layout.addWidget(sub)
        layout.addWidget(streak_card)

        layout.addSpacing(14)

        # User profile row
        user_row = QHBoxLayout()
        user_row.setSpacing(10)
        avatar = QLabel("\U0001F464")
        avatar.setStyleSheet("""
            background-color: rgba(255, 255, 255, 45);
            border-radius: 16px;
            font-size: 14px;
            padding: 4px;
        """)
        avatar.setFixedSize(32, 32)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        user_row.addWidget(avatar)

        user_info = QVBoxLayout()
        user_info.setSpacing(1)
        self._user_label = QLabel(self._user_name)
        self._user_label.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 11px; background: transparent;")
        user_info.addWidget(self._user_label)
        tag = QLabel("Motor Rehab")
        tag.setStyleSheet("color: #D3C6F7; font-size: 9px; background: transparent;")
        user_info.addWidget(tag)
        user_row.addLayout(user_info)
        user_row.addStretch()
        layout.addLayout(user_row)

    def _nav_button_style(self):
        return """
            QPushButton {
                text-align: left;
                padding-left: 14px;
                border-radius: 12px;
                border: none;
                background-color: transparent;
                color: rgba(255, 255, 255, 210);
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 30);
                color: #FFFFFF;
            }
            QPushButton:checked {
                background-color: rgba(255, 255, 255, 240);
                color: #553BB0;
                font-weight: bold;
            }
        """

    def _set_nav_text(self, btn, icon, label, active=False):
        btn.setText(f"  {icon}   {label}")

    def _on_nav_clicked(self, key):
        self.set_active(key)
        self.nav_changed.emit(key)

    def set_active(self, key):
        for k, (btn, icon, label) in self._nav_buttons.items():
            is_active = (k == key)
            btn.setChecked(is_active)
            self._set_nav_text(btn, icon, label, active=is_active)

    def set_user_name(self, name):
        self._user_name = name
        self._user_label.setText(name)

    def set_streak(self, streak):
        self._streak_count = streak
        self._streak_label.setText(f"{streak} Day Streak")
