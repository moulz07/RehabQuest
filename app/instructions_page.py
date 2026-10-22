"""
Instructions Page
--------------------
Step-by-step carousel explaining exercise posture, tracking calibration,
and goals before launching the session.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

STEPS = [
    {
        "icon": "\U0001FA9F",
        "title": "1. Position Yourself",
        "desc": "Sit upright approximately 0.8 meters in front of your webcam with your upper body clearly visible in good lighting.",
    },
    {
        "icon": "\u270B",
        "title": "2. Align Your Wrist",
        "desc": "Raise your active hand toward the camera. MediaPipe markerless tracking will automatically detect your wrist coordinates in 3D.",
    },
    {
        "icon": "\U0001F3AF",
        "title": "3. Reach Dynamic Targets",
        "desc": "Move your hand across your range of motion to reach the glowing targets in Unity before their timer runs out.",
    },
    {
        "icon": "\U0001F4C8",
        "title": "4. Clinical Feedback",
        "desc": "Try to move smoothly without compensating by leaning your torso. Your ROM, smoothness, and trajectory will be analyzed upon completion.",
    },
]


class InstructionsPage(QWidget):
    play_confirmed = pyqtSignal(str)
    back_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_step = 0
        self._game_id = "reach_and_collect"
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(14)

        # Header row
        hdr_row = QHBoxLayout()
        back_btn = QPushButton("\u2190 Back")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #7E5BE8;
                font-weight: bold;
                font-size: 13px;
                border: none;
                padding: 4px 8px;
            }
            QPushButton:hover { color: #5B3FC2; }
        """)
        back_btn.clicked.connect(self.back_requested.emit)
        hdr_row.addWidget(back_btn)

        title = QLabel("Session Guide: Reach & Collect")
        title_font = QFont("Segoe UI", 16)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #2F2154; background: transparent;")
        hdr_row.addWidget(title)
        hdr_row.addStretch()
        layout.addLayout(hdr_row)

        # Main Card Carousel
        self.card = QFrame()
        self.card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 240);
                border-radius: 22px;
                border: 1px solid rgba(133, 103, 232, 30);
            }
        """)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(36, 32, 36, 32)
        card_layout.setSpacing(12)

        self.step_icon = QLabel("\U0001FA9F")
        self.step_icon.setStyleSheet("font-size: 48px; background: transparent;")
        self.step_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.step_icon)

        self.step_title = QLabel("1. Position Yourself")
        st_font = QFont("Segoe UI", 18)
        st_font.setWeight(QFont.Weight.Bold)
        self.step_title.setFont(st_font)
        self.step_title.setStyleSheet("color: #2F2154; background: transparent;")
        self.step_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.step_title)

        self.step_desc = QLabel("Description goes here")
        self.step_desc.setStyleSheet("color: #6C5D8C; font-size: 13px; line-height: 1.5; background: transparent;")
        self.step_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.step_desc.setWordWrap(True)
        card_layout.addWidget(self.step_desc)

        card_layout.addStretch()

        # Step Indicator Dots
        dots_row = QHBoxLayout()
        dots_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dots_row.setSpacing(8)
        self._dots = []
        for i in range(len(STEPS)):
            dot = QFrame()
            dot.setFixedSize(10, 10)
            dot.setStyleSheet("background-color: rgba(126, 91, 232, 40); border-radius: 5px;")
            dots_row.addWidget(dot)
            self._dots.append(dot)
        card_layout.addLayout(dots_row)

        layout.addWidget(self.card, 1)

        # Bottom Navigation
        nav_row = QHBoxLayout()
        self.prev_btn = QPushButton("\u2039 Previous")
        self.prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prev_btn.setStyleSheet("color: #7E5BE8; font-weight: bold; background: transparent; border: none;")
        self.prev_btn.clicked.connect(self._prev_step)
        nav_row.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next \u203a")
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.setStyleSheet("color: #7E5BE8; font-weight: bold; background: transparent; border: none;")
        self.next_btn.clicked.connect(self._next_step)
        nav_row.addWidget(self.next_btn)

        nav_row.addStretch()

        launch_btn = QPushButton("\u25b6  Launch Camera & Tracking")
        launch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        launch_btn.setFixedHeight(44)
        launch_btn.setStyleSheet("""
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
        launch_btn.clicked.connect(lambda: self.play_confirmed.emit(self._game_id))
        nav_row.addWidget(launch_btn)

        layout.addLayout(nav_row)

        self._update_step()

    def _update_step(self):
        step = STEPS[self._current_step]
        self.step_icon.setText(step["icon"])
        self.step_title.setText(step["title"])
        self.step_desc.setText(step["desc"])

        for i, dot in enumerate(self._dots):
            if i == self._current_step:
                dot.setStyleSheet("background-color: #7E5BE8; border-radius: 5px;")
            else:
                dot.setStyleSheet("background-color: rgba(126, 91, 232, 40); border-radius: 5px;")

        self.prev_btn.setEnabled(self._current_step > 0)
        self.next_btn.setEnabled(self._current_step < len(STEPS) - 1)

    def _next_step(self):
        if self._current_step < len(STEPS) - 1:
            self._current_step += 1
            self._update_step()

    def _prev_step(self):
        if self._current_step > 0:
            self._current_step -= 1
            self._update_step()

    def load(self, game_id):
        self._game_id = game_id
        self._current_step = 0
        self._update_step()
