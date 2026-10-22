"""
Weekly Activity Card
-----------------------
Displays a 7-day strip (Mon-Sun) highlighting sessions completed this week.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from local_data import DAY_LETTERS, get_today_index

DOT_EMPTY_STYLE = "background-color: rgba(124, 92, 224, 30); border-radius: 6px;"
DOT_FILLED_STYLE = "background-color: #7C5CE0; border-radius: 6px;"
DOT_TODAY_RING = "border: 2px solid #B983C9;"


def _summary_for(sessions):
    active_days = sum(1 for v in sessions if v)
    if active_days >= 5:
        return "Amazing consistency this week!"
    if active_days >= 3:
        return "Great progress this week!"
    if active_days >= 1:
        return "Nice start — keep it up!"
    return "Let's get moving today!"


class WeeklyActivityCard(QFrame):
    def __init__(self, parent=None, dot_size=13):
        super().__init__(parent)
        self._dot_size = dot_size
        self._dots = []
        self._sessions = [False] * 7
        self._today_idx = get_today_index()
        self.setObjectName("weeklyActivityCard")
        self.setStyleSheet("""
            QFrame#weeklyActivityCard {
                background-color: rgba(255, 255, 255, 225);
                border-radius: 18px;
                border: 1px solid rgba(133, 103, 232, 25);
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        header_row = QHBoxLayout()
        title = QLabel("WEEKLY ACTIVITY")
        title_font = QFont("Segoe UI", 9)
        title_font.setWeight(QFont.Weight.DemiBold)
        title_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.0)
        title.setFont(title_font)
        title.setStyleSheet("color: #8A7CB0; background: transparent;")
        header_row.addWidget(title)
        header_row.addStretch()

        self._streak_tag = QLabel("\U0001F525 On track")
        self._streak_tag.setStyleSheet("color: #7C5CE0; font-size: 11px; font-weight: bold; background: transparent;")
        header_row.addWidget(self._streak_tag)
        layout.addLayout(header_row)

        self._summary_label = QLabel("Loading activity...")
        self._summary_label.setStyleSheet("color: #382C5E; font-size: 13px; font-weight: bold; background: transparent;")
        layout.addWidget(self._summary_label)
        layout.addSpacing(4)

        # 7-day row
        days_row = QHBoxLayout()
        days_row.setSpacing(10)
        self._dots = []
        for i, letter in enumerate(DAY_LETTERS):
            col = QVBoxLayout()
            col.setSpacing(6)
            col.setAlignment(Qt.AlignmentFlag.AlignCenter)

            dot = QFrame()
            dot.setFixedSize(self._dot_size, self._dot_size)
            dot.setStyleSheet(DOT_EMPTY_STYLE)
            col.addWidget(dot)
            self._dots.append(dot)

            lbl = QLabel(letter)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            is_today = (i == self._today_idx)
            lbl_color = "#7C5CE0" if is_today else "#9F92BE"
            lbl_weight = "bold" if is_today else "normal"
            lbl.setStyleSheet(f"color: {lbl_color}; font-size: 11px; font-weight: {lbl_weight}; background: transparent;")
            col.addWidget(lbl)

            days_row.addLayout(col)

        layout.addLayout(days_row)

    def set_sessions(self, sessions_bool_list):
        self._sessions = sessions_bool_list
        self._summary_label.setText(_summary_for(self._sessions))
        for i, (dot, active) in enumerate(zip(self._dots, self._sessions)):
            base_style = DOT_FILLED_STYLE if active else DOT_EMPTY_STYLE
            ring = DOT_TODAY_RING if i == self._today_idx else ""
            dot.setStyleSheet(base_style + ring)
