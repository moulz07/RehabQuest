"""
Home View for RehabQuest
------------------------
Overview screen featuring patient greeting, quick session launcher, daily quote,
and weekly activity consistency tracker.
"""

from datetime import date
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import QFont, QPainter, QLinearGradient, QRadialGradient, QColor, QPainterPath

from decorative_shapes import draw_star_field
from local_data import get_current_streak, get_weekly_session_days, get_random_quote
from weekly_activity import WeeklyActivityCard


class DashboardHeroCard(QFrame):
    play_now_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user_name = "Alex Mercer"
        self._streak = 5
        self._build_ui()

    def paintEvent(self, event):
        w, h = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        gradient = QLinearGradient(0, 0, w * 0.4, h)
        gradient.setColorAt(0.0, QColor("#EFE8FC"))
        gradient.setColorAt(1.0, QColor("#E2D4F7"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(gradient)
        painter.drawRoundedRect(rect, 24, 24)

        painter.save()
        path = QPainterPath()
        path.addRoundedRect(0, 0, w, h, 24, 24)
        painter.setClipPath(path)

        glow = QRadialGradient(QPointF(w * 0.8, h * 0.25), w * 0.28)
        glow.setColorAt(0.0, QColor(190, 160, 240, 100))
        glow.setColorAt(1.0, QColor(190, 160, 240, 0))
        painter.setBrush(glow)
        painter.drawEllipse(QPointF(w * 0.8, h * 0.25), w * 0.28, w * 0.28)

        draw_star_field(painter, w, h * 0.8, count=16, seed=7, color=QColor(140, 120, 200))
        painter.restore()

        super().paintEvent(event)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(6)

        date_lbl = QLabel(date.today().strftime("%A, %B %d, %Y").upper())
        date_lbl.setStyleSheet("color: #8C78B8; font-size: 10px; font-weight: bold; letter-spacing: 1px; background: transparent;")
        layout.addWidget(date_lbl)

        self._greeting_label = QLabel(f"Welcome back,\n{self._user_name}")
        greet_font = QFont("Segoe UI", 20)
        greet_font.setWeight(QFont.Weight.Bold)
        self._greeting_label.setFont(greet_font)
        self._greeting_label.setStyleSheet("color: #2F2154; background: transparent;")
        layout.addWidget(self._greeting_label)
        layout.addSpacing(4)

        self._streak_text = QLabel(f"You have completed {self._streak} consecutive days of upper-limb rehabilitation. Keep up the high range of motion!")
        self._streak_text.setStyleSheet("color: #6C5D8C; font-size: 12px; line-height: 1.4; background: transparent;")
        self._streak_text.setWordWrap(True)
        layout.addWidget(self._streak_text)

        layout.addStretch()

        btn_row = QHBoxLayout()
        play_btn = QPushButton("\u25b6  Start Daily Session")
        play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        play_btn.setFixedHeight(44)
        play_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7E5BE8, stop:1 #A878E0);
                color: #FFFFFF;
                border-radius: 14px;
                font-size: 13px;
                font-weight: bold;
                padding: 0 24px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8E6BF8, stop:1 #B888F0);
            }
        """)
        play_btn.clicked.connect(self.play_now_clicked.emit)
        btn_row.addWidget(play_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def set_user(self, name, streak):
        self._user_name = name
        self._streak = streak
        self._greeting_label.setText(f"Welcome back,\n{name}")
        self._streak_text.setText(f"You have completed {streak} consecutive days of upper-limb rehabilitation. Keep up the high range of motion!")


class HomeView(QWidget):
    play_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(18)

        # Left: Hero card
        self.hero = DashboardHeroCard(self)
        self.hero.play_now_clicked.connect(self.play_requested.emit)
        main_layout.addWidget(self.hero, 1)

        # Right column
        right_col = QVBoxLayout()
        right_col.setSpacing(14)

        # Quote card
        quote_card = QFrame()
        quote_card.setObjectName("quoteCard")
        quote_card.setStyleSheet("""
            QFrame#quoteCard {
                background-color: rgba(255, 255, 255, 225);
                border-radius: 18px;
                border: 1px solid rgba(133, 103, 232, 25);
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)
        q_layout = QVBoxLayout(quote_card)
        q_layout.setContentsMargins(20, 16, 20, 16)
        q_layout.setSpacing(6)

        q_tag = QLabel("\U0001F4A1 DAILY MOTIVATION")
        q_tag.setStyleSheet("color: #8A7CB0; font-size: 9px; font-weight: bold; letter-spacing: 1px; background: transparent;")
        q_layout.addWidget(q_tag)

        self._quote_label = QLabel(get_random_quote())
        self._quote_label.setStyleSheet("color: #382C5E; font-size: 12px; font-style: italic; background: transparent;")
        self._quote_label.setWordWrap(True)
        q_layout.addWidget(self._quote_label)
        right_col.addWidget(quote_card)

        # Weekly Activity card
        self.weekly = WeeklyActivityCard(self)
        right_col.addWidget(self.weekly)

        main_layout.addLayout(right_col, 1)

    def refresh_for_user(self, user_id, name="Patient"):
        streak = get_current_streak(user_id)
        self.hero.set_user(name, streak)
        self.weekly.set_sessions(get_weekly_session_days(user_id))
        self._quote_label.setText(get_random_quote())
