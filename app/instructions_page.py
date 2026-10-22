
"""
Instructions Page
-----------------
Step-by-step preparation guide for RehabQuest exercises.

Explains patient positioning, webcam tracking, target reaching,
and movement feedback before launching a rehabilitation session.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


STEPS = [
    {
        "icon": "🪑",
        "title": "1. Position Yourself",
        "desc": (
            "Sit comfortably and upright approximately 0.8 metres "
            "from your webcam. Make sure your upper body and active "
            "arm are visible, with sufficient lighting and a clear "
            "space for movement."
        ),
    },
    {
        "icon": "✋",
        "title": "2. Align Your Hand",
        "desc": (
            "Keep your active hand visible to the camera. "
            "MediaPipe detects hand landmarks and provides wrist "
            "coordinates to control the rehabilitation game. "
            "Avoid covering your hand or moving outside the camera view."
        ),
    },
    {
        "icon": "🎯",
        "title": "3. Reach the Targets",
        "desc": (
            "Move your hand toward the targets displayed in the "
            "Reach & Collect game. Follow the targets at a comfortable "
            "pace and remain within your safe, comfortable range of motion."
        ),
    },
    {
        "icon": "📈",
        "title": "4. Review Your Movement",
        "desc": (
            "After the session, review the recorded game results and "
            "available movement metrics, such as range of motion, "
            "trajectory accuracy, speed, and smoothness. Avoid leaning "
            "your torso excessively to reach a target."
        ),
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
        self._update_step()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 16)
        main_layout.setSpacing(14)

        # --------------------------------------------------
        # Header
        # --------------------------------------------------
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        self.back_btn = QPushButton("← Back")
        self.back_btn.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.back_btn.setAccessibleName(
            "Return to exercise selection"
        )
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #7E5BE8;
                font-weight: bold;
                font-size: 13px;
                border: none;
                padding: 4px 8px;
            }

            QPushButton:hover {
                color: #5B3FC2;
            }
        """)
        self.back_btn.clicked.connect(
            self.back_requested.emit
        )

        header_row.addWidget(self.back_btn)

        self.header_title = QLabel(
            "Session Guide: Reach & Collect"
        )
        header_font = QFont("Segoe UI", 16)
        header_font.setWeight(QFont.Weight.Bold)

        self.header_title.setFont(header_font)
        self.header_title.setStyleSheet(
            "color: #2F2154; background: transparent;"
        )
        self.header_title.setWordWrap(True)

        header_row.addWidget(self.header_title)
        header_row.addStretch()

        main_layout.addLayout(header_row)

        # --------------------------------------------------
        # Instructions card
        # --------------------------------------------------
        self.card = QFrame()
        self.card.setObjectName("instructionsCard")
        self.card.setStyleSheet("""
            QFrame#instructionsCard {
                background-color: rgba(255, 255, 255, 240);
                border-radius: 22px;
                border: 1px solid rgba(133, 103, 232, 30);
            }

            QLabel {
                background: transparent;
                border: none;
            }
        """)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(
            36, 28, 36, 28
        )
        card_layout.setSpacing(12)

        self.step_counter = QLabel("STEP 1 OF 4")
        self.step_counter.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.step_counter.setStyleSheet("""
            color: #7E5BE8;
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 1px;
        """)
        card_layout.addWidget(self.step_counter)

        self.step_icon = QLabel()
        self.step_icon.setStyleSheet(
            "font-size: 48px; background: transparent;"
        )
        self.step_icon.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        card_layout.addWidget(self.step_icon)

        self.step_title = QLabel()
        title_font = QFont("Segoe UI", 18)
        title_font.setWeight(QFont.Weight.Bold)

        self.step_title.setFont(title_font)
        self.step_title.setStyleSheet(
            "color: #2F2154; background: transparent;"
        )
        self.step_title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.step_title.setWordWrap(True)

        card_layout.addWidget(self.step_title)

        self.step_desc = QLabel()
        self.step_desc.setStyleSheet("""
            color: #6C5D8C;
            font-size: 13px;
            background: transparent;
        """)
        self.step_desc.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.step_desc.setWordWrap(True)

        card_layout.addWidget(self.step_desc)
        card_layout.addStretch()

        # Step indicator dots
        dots_row = QHBoxLayout()
        dots_row.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        dots_row.setSpacing(8)

        self._dots = []

        for index in range(len(STEPS)):
            dot = QFrame()
            dot.setFixedSize(10, 10)
            dot.setAccessibleName(
                f"Instruction step {index + 1}"
            )

            dots_row.addWidget(dot)
            self._dots.append(dot)

        card_layout.addLayout(dots_row)

        main_layout.addWidget(self.card, 1)

        # --------------------------------------------------
        # Bottom navigation
        # --------------------------------------------------
        nav_row = QHBoxLayout()
        nav_row.setSpacing(10)

        self.prev_btn = QPushButton("‹ Previous")
        self.prev_btn.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.prev_btn.setStyleSheet("""
            QPushButton {
                color: #7E5BE8;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 8px;
            }

            QPushButton:disabled {
                color: #BDB3D3;
            }
        """)
        self.prev_btn.clicked.connect(
            self._prev_step
        )

        nav_row.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next ›")
        self.next_btn.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.next_btn.setStyleSheet("""
            QPushButton {
                color: #7E5BE8;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 8px;
            }

            QPushButton:disabled {
                color: #BDB3D3;
            }
        """)
        self.next_btn.clicked.connect(
            self._next_step
        )

        nav_row.addWidget(self.next_btn)
        nav_row.addStretch()

        self.launch_btn = QPushButton(
            "▶  Launch Camera & Tracking"
        )
        self.launch_btn.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.launch_btn.setFixedHeight(44)
        self.launch_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7E5BE8, stop:1 #A878E0
                );
                color: #FFFFFF;
                border-radius: 14px;
                font-size: 13px;
                font-weight: bold;
                padding: 0 20px;
                border: none;
            }

            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8E6BF8, stop:1 #B888F0
                );
            }

            QPushButton:disabled {
                background-color: #B9A9E8;
            }
        """)

        self.launch_btn.clicked.connect(
            self._launch_session
        )

        nav_row.addWidget(self.launch_btn)
        main_layout.addLayout(nav_row)

    def _update_step(self):
        """Refresh the carousel to display the current instruction."""
        step = STEPS[self._current_step]

        self.step_counter.setText(
            f"STEP {self._current_step + 1} OF {len(STEPS)}"
        )
        self.step_icon.setText(step["icon"])
        self.step_title.setText(step["title"])
        self.step_desc.setText(step["desc"])

        for index, dot in enumerate(self._dots):
            if index == self._current_step:
                dot.setStyleSheet("""
                    background-color: #7E5BE8;
                    border-radius: 5px;
                """)
            else:
                dot.setStyleSheet("""
                    background-color: rgba(126, 91, 232, 40);
                    border-radius: 5px;
                """)

        self.prev_btn.setEnabled(
            self._current_step > 0
        )
        self.next_btn.setEnabled(
            self._current_step < len(STEPS) - 1
        )

    def _next_step(self):
        if self._current_step < len(STEPS) - 1:
            self._current_step += 1
            self._update_step()

    def _prev_step(self):
        if self._current_step > 0:
            self._current_step -= 1
            self._update_step()

    def _launch_session(self):
        """Request the dashboard to launch the selected game."""
        self.play_confirmed.emit(self._game_id)

    def load(self, game_id):
        """Load a selected exercise and reset the instructions."""
        self._game_id = (
            game_id or "reach_and_collect"
        )
        self._current_step = 0

        display_name = (
            self._game_id.replace("_", " ").title()
        )
        self.header_title.setText(
            f"Session Guide: {display_name}"
        )

        self._update_step()
