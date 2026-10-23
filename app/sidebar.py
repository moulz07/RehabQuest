
"""
Sidebar for RehabQuest
-----------------------
Navigation panel with a branded gradient, active indicators,
rehabilitation streak, and patient profile.
"""

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QVBoxLayout,
    QButtonGroup,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QLinearGradient, QPainter, QColor


NAV_ITEMS = [
    ("home", "🏠", "Home"),
    ("games", "🎮", "Games"),
    ("body_parts", "🎯", "Target Limbs"),
    ("report", "📋", "Report"),
    ("progress", "📈", "Progress"),
]


class Sidebar(QFrame):
    nav_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("sidebar")
        self.setMinimumWidth(0)
        self.setMaximumWidth(200)

        self._nav_buttons = {}
        self._user_name = "Patient"
        self._streak_count = 0

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
        painter.end()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 22, 16, 18)
        layout.setSpacing(0)

        # Brand
        brand_row = QHBoxLayout()
        brand_row.setSpacing(8)

        logo = QLabel("⚕")
        logo.setStyleSheet(
            "background: transparent; font-size: 20px;"
        )
        brand_row.addWidget(logo)

        brand_label = QLabel("REHABQUEST")
        brand_font = QFont("Segoe UI", 11)
        brand_font.setWeight(QFont.Weight.Bold)
        brand_font.setLetterSpacing(
            QFont.SpacingType.AbsoluteSpacing, 1.2
        )
        brand_label.setFont(brand_font)
        brand_label.setStyleSheet(
            "color: #FFFFFF; background: transparent;"
        )

        brand_row.addWidget(brand_label)
        brand_row.addStretch()
        layout.addLayout(brand_row)
        layout.addSpacing(28)

        # Navigation buttons
        self._btn_group = QButtonGroup(self)
        self._btn_group.setExclusive(True)

        for key, icon, label in NAV_ITEMS:
            button = QPushButton(f"  {icon}   {label}")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setFixedHeight(44)
            button.setStyleSheet(self._nav_button_style())

            button.clicked.connect(
                lambda checked=False, k=key: self._on_nav_clicked(k)
            )

            self._btn_group.addButton(button)
            self._nav_buttons[key] = (button, icon, label)

            layout.addWidget(button)
            layout.addSpacing(6)

        layout.addSpacing(14)
        layout.addStretch()

        # Streak card
        streak_card = QFrame()
        streak_card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 220);
                border-radius: 14px;
            }
        """)

        streak_layout = QVBoxLayout(streak_card)
        streak_layout.setContentsMargins(12, 12, 12, 12)
        streak_layout.setSpacing(4)

        streak_header = QHBoxLayout()

        flame = QLabel("🔥")
        flame.setStyleSheet(
            "background: transparent; font-size: 16px;"
        )
        streak_header.addWidget(flame)

        self._streak_label = QLabel("0 Day Streak")
        self._streak_label.setStyleSheet("""
            color: #583BB8;
            font-weight: bold;
            font-size: 12px;
            background: transparent;
        """)

        streak_header.addWidget(self._streak_label)
        streak_header.addStretch()
        streak_layout.addLayout(streak_header)

        streak_subtitle = QLabel("Keep the momentum going!")
        streak_subtitle.setWordWrap(True)
        streak_subtitle.setStyleSheet("""
            color: #7B6D9E;
            font-size: 10px;
            background: transparent;
        """)
        streak_layout.addWidget(streak_subtitle)

        layout.addWidget(streak_card)
        layout.addSpacing(14)

        # Patient profile
        user_row = QHBoxLayout()
        user_row.setSpacing(10)

        avatar = QLabel("👤")
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
        self._user_label.setWordWrap(True)
        self._user_label.setMaximumWidth(110)
        self._user_label.setStyleSheet("""
            color: #FFFFFF;
            font-weight: bold;
            font-size: 11px;
            background: transparent;
        """)
        user_info.addWidget(self._user_label)

        patient_tag = QLabel("Motor Rehab")
        patient_tag.setStyleSheet("""
            color: #D3C6F7;
            font-size: 9px;
            background: transparent;
        """)
        user_info.addWidget(patient_tag)

        user_row.addLayout(user_info)
        user_row.addStretch()
        layout.addLayout(user_row)

    @staticmethod
    def _nav_button_style():
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

    def _on_nav_clicked(self, key):
        self.set_active(key)
        self.nav_changed.emit(key)

    def set_active(self, key):
        if key not in self._nav_buttons:
            return

        for nav_key, (button, _icon, _label) in self._nav_buttons.items():
            button.setChecked(nav_key == key)

    def set_user_name(self, name):
        self._user_name = str(name).strip() if name else "Patient"
        self._user_label.setText(self._user_name)

    def set_streak(self, streak):
        try:
            self._streak_count = max(0, int(streak))
        except (TypeError, ValueError):
            self._streak_count = 0

        self._streak_label.setText(
            f"{self._streak_count} Day Streak"
        )
