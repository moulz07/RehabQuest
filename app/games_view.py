"""
Games View for RehabQuest
-------------------------
Interactive game selection cards displaying the active Reach & Collect game
and the Cosmic Weaver advanced motor rehabilitation game.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QLinearGradient


class GameCard(QFrame):
    start_clicked = pyqtSignal(str)

    def __init__(self, game_id, icon, title, tag, description, button_text, is_primary=True, parent=None):
        super().__init__(parent)
        self.game_id = game_id
        self.icon = icon
        self.title_text = title
        self.tag_text = tag
        self.desc_text = description
        self.button_text = button_text
        self.is_primary = is_primary
        self.setFixedSize(310, 370)
        self._build_ui()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, 0, self.height())
        if self.is_primary:
            gradient.setColorAt(0.0, QColor("#FFFFFF"))
            gradient.setColorAt(1.0, QColor("#F4EEFB"))
        else:
            gradient.setColorAt(0.0, QColor("#FBF9FD"))
            gradient.setColorAt(1.0, QColor("#EDE7F6"))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(self.rect(), 22, 22)
        super().paintEvent(event)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 22)
        layout.setSpacing(10)

        # Top icon & tag
        top_row = QHBoxLayout()
        icon_lbl = QLabel(self.icon)
        icon_lbl.setStyleSheet("font-size: 28px; background: transparent;")
        top_row.addWidget(icon_lbl)
        top_row.addStretch()

        tag_lbl = QLabel(self.tag_text)
        tag_color = "#7E5BE8" if self.is_primary else "#9A73C9"
        tag_bg = "rgba(126, 91, 232, 25)" if self.is_primary else "rgba(154, 115, 201, 25)"
        tag_lbl.setStyleSheet(f"""
            color: {tag_color};
            background-color: {tag_bg};
            border-radius: 8px;
            padding: 4px 8px;
            font-size: 9px;
            font-weight: bold;
            letter-spacing: 0.5px;
        """)
        top_row.addWidget(tag_lbl)
        layout.addLayout(top_row)

        layout.addSpacing(6)

        title = QLabel(self.title_text)
        title_font = QFont("Segoe UI", 16)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #2F2154; background: transparent;")
        layout.addWidget(title)

        desc = QLabel(self.desc_text)
        desc.setStyleSheet("color: #6C5D8C; font-size: 11px; line-height: 1.4; background: transparent;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

        btn = QPushButton(self.button_text)
        btn.setFixedHeight(42)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if self.is_primary:
            btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7E5BE8, stop:1 #A878E0);
                    color: #FFFFFF;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: bold;
                    border: none;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8E6BF8, stop:1 #B888F0);
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(126, 91, 232, 25);
                    color: #6546C9;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: bold;
                    border: 1px solid rgba(126, 91, 232, 50);
                }
                QPushButton:hover {
                    background-color: rgba(126, 91, 232, 45);
                }
            """)
        btn.clicked.connect(lambda: self.start_clicked.emit(self.game_id))
        layout.addWidget(btn)


class GamesView(QWidget):
    game_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(14)

        header = QLabel("Rehabilitation Exercises")
        hdr_font = QFont("Segoe UI", 18)
        hdr_font.setWeight(QFont.Weight.Bold)
        header.setFont(hdr_font)
        header.setStyleSheet("color: #2F2154; background: transparent;")
        layout.addWidget(header)

        sub = QLabel("Select an exercise to begin your guided motor therapy session.")
        sub.setStyleSheet("color: #7A6C9B; font-size: 12px; background: transparent;")
        layout.addWidget(sub)
        layout.addSpacing(10)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(20)

        # Card 1: Reach & Collect
        self.card_reach = GameCard(
            game_id="reach_and_collect",
            icon="\U0001F3AF",
            title="Reach & Collect",
            tag="ACTIVE SESSION",
            description="Target-directed motor therapy. Track your wrist in real-time, stretch towards dynamic spatial targets, and receive continuous ROM and trajectory feedback.",
            button_text="\u25b6  Start Exercise",
            is_primary=True,
            parent=self
        )
        self.card_reach.start_clicked.connect(self.game_selected.emit)
        cards_row.addWidget(self.card_reach)

        # Card 2: Cosmic Weaver
        self.card_cosmic = GameCard(
            game_id="cosmic_weaver",
            icon="\U0001F30C",
            title="Cosmic Weaver",
            tag="PHASE 2 ROADMAP",
            description="Advanced neuro-motor therapy inspired by RehabVerse. Features active pinch/fist grip detection, carry-to-portal loops, and forced left/right hand selection.",
            button_text="\u2139  View Mechanics",
            is_primary=False,
            parent=self
        )
        self.card_cosmic.start_clicked.connect(self._show_cosmic_info)
        cards_row.addWidget(self.card_cosmic)

        cards_row.addStretch()
        layout.addLayout(cards_row)
        layout.addStretch()

    def _show_cosmic_info(self, _):
        msg = QMessageBox(self)
        msg.setWindowTitle("Cosmic Weaver Mechanics")
        msg.setText(
            "<b>Cosmic Weaver — Advanced Motor Rehab Concept</b><br><br>"
            "Inspired by RehabVerse, this game mode introduces:<br>"
            "• <b>Active Grip Verification</b>: Using MediaPipe hand landmarks to calculate thumb-to-finger distance and register grip/grasp.<br>"
            "• <b>Carry & Deposit Loop</b>: Requiring patients to sustain muscular hold while transporting the star to an energy portal.<br>"
            "• <b>Bilateral Hand Cueing</b>: Enforcing left-only or right-only reaching for hemiparetic recovery.<br><br>"
            "<i>Status: Scheduled for Phase 2 integration into the RehabQuest engine.</i>"
        )
        msg.setStyleSheet("""
            QMessageBox { background-color: #FFFFFF; }
            QLabel { color: #2F2154; font-size: 12px; }
            QPushButton { background-color: #7E5BE8; color: white; border-radius: 8px; padding: 6px 16px; font-weight: bold; }
        """)
        msg.exec()
