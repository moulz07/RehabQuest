
"""
Stat Card
---------
Reusable rounded statistic card for RehabQuest Report and Progress tabs.

Displays a prominent value and descriptive label, with optional
click interaction for navigation or drill-down actions.
"""

from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class StatCard(QFrame):
    """Reusable statistic card with optional click support."""

    clicked = pyqtSignal()

    def __init__(self, clickable=False, parent=None):
        super().__init__(parent)

        self._clickable = clickable

        self.setObjectName("statCard")
        self.setAccessibleName("Statistic card")

        if self._clickable:
            self.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

        self.setFocusPolicy(
            Qt.FocusPolicy.StrongFocus
            if clickable
            else Qt.FocusPolicy.NoFocus
        )

    def mousePressEvent(self, event):
        if (
            self._clickable
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self.clicked.emit()
            event.accept()
            return

        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if (
            self._clickable
            and event.key() in (
                Qt.Key.Key_Return,
                Qt.Key.Key_Enter,
                Qt.Key.Key_Space,
            )
        ):
            self.clicked.emit()
            event.accept()
            return

        super().keyPressEvent(event)


def make_stat_card(
    value_text,
    label_text,
    accent="#7C5CE0",
    clickable=False,
):
    """
    Create a statistic card.

    Args:
        value_text: Main statistic, such as '12' or '85%'.
        label_text: Description displayed below the statistic.
        accent: Accent color for the main statistic.
        clickable: Enables click and keyboard activation.

    Returns:
        A tuple containing (card_widget, value_label).
        The returned label can be updated using setText().
    """

    card = StatCard(clickable=clickable)
    card.setFixedHeight(88)
    card.setMinimumWidth(100)

    hover_style = ""

    if clickable:
        hover_style = """
            QFrame#statCard:hover {
                background-color: rgba(255, 255, 255, 255);
                border: 1px solid rgba(126, 91, 232, 100);
            }

            QFrame#statCard:focus {
                border: 2px solid #7E5BE8;
            }
        """

    card.setStyleSheet(f"""
        QFrame#statCard {{
            background-color: rgba(255, 255, 255, 225);
            border-radius: 16px;
            border: 1px solid rgba(133, 103, 232, 25);
        }}

        {hover_style}

        QLabel {{
            border: none;
            background: transparent;
        }}
    """)

    layout = QVBoxLayout(card)
    layout.setContentsMargins(18, 12, 18, 12)
    layout.setSpacing(2)

    # Main statistic
    value = QLabel(str(value_text))
    value.setObjectName("statValue")

    value_font = QFont("Segoe UI", 20)
    value_font.setWeight(QFont.Weight.Bold)
    value.setFont(value_font)

    value.setStyleSheet(
        f"color: {accent}; background: transparent;"
    )

    value.setTextInteractionFlags(
        Qt.TextInteractionFlag.NoTextInteraction
    )

    layout.addWidget(value)

    # Descriptive label
    label_text = str(label_text)

    if clickable:
        label_text += "  ›"

    label = QLabel(label_text)
    label.setObjectName("statLabel")
    label.setWordWrap(True)

    label.setStyleSheet("""
        color: #7A6C9B;
        background: transparent;
        font-size: 11px;
        font-weight: 500;
    """)

    layout.addWidget(label)
    layout.addStretch()

    card.setAccessibleDescription(
        f"{label_text}: {value_text}"
    )

    return card, value
