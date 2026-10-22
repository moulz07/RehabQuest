"""
Stat Card
-----------
Clean rounded "big number + label" card widget used across Report and Progress tabs.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class StatCard(QFrame):
    clicked = pyqtSignal()

    def __init__(self, clickable=False, parent=None):
        super().__init__(parent)
        self._clickable = clickable
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


def make_stat_card(value_text, label_text, accent="#7C5CE0", clickable=False):
    card = StatCard(clickable=clickable)
    card.setFixedHeight(88)
    card.setObjectName("statCard")
    hover_extra = "QFrame#statCard:hover { background-color: rgba(255, 255, 255, 255); }" if clickable else ""
    card.setStyleSheet(f"""
        QFrame#statCard {{
            background-color: rgba(255, 255, 255, 225);
            border-radius: 16px;
            border: 1px solid rgba(133, 103, 232, 25);
        }}
        {hover_extra}
        QLabel {{
            border: none;
            background: transparent;
        }}
    """)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(18, 14, 18, 14)
    layout.setSpacing(2)

    value = QLabel(value_text)
    value_font = QFont("Segoe UI", 20)
    value_font.setWeight(QFont.Weight.Bold)
    value.setFont(value_font)
    value.setStyleSheet(f"color: {accent}; background: transparent;")
    layout.addWidget(value)

    label_row_text = label_text + ("  \u203A" if clickable else "")
    label = QLabel(label_row_text)
    label.setStyleSheet("color: #7A6C9B; background: transparent; font-size: 11px; font-weight: 500;")
    label.setWordWrap(True)
    layout.addWidget(label)
    layout.addStretch()

    return card, value
