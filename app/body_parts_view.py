
"""
Target Limbs & Body Parts View for RehabQuest
---------------------------------------------
Anatomical rehabilitation matrix displaying target limbs,
biomechanics, active exercises, and planned game roadmaps.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QMessageBox,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


PURPLE = "#7E5BE8"
DARK_PURPLE = "#2F2154"
MUTED_PURPLE = "#7A6C9B"


LIMB_DATA = [
    {
        "id": "wrist_hand",
        "icon": "🖐️",
        "title": "Wrist & Hand",
        "badge": "1 ACTIVE • 2 IN DEV",
        "badge_color": "#2E7D32",
        "badge_bg": "rgba(46, 125, 50, 0.12)",
        "subtitle": (
            "Distal upper-limb motor rehabilitation & dexterity"
        ),
        "biomechanics": (
            "Wrist Flexion/Extension ROM, Target Trajectory "
            "Accuracy, Movement Smoothness, Pinch Grip Hold"
        ),
        "games": [
            (
                "Reach & Collect",
                "Active",
                "3D spatial target reach with markerless tracking",
            ),
            (
                "Bloom Forest",
                "Phase 2",
                "Guided wrist flexion/extension repetitions and steady holds",
            ),
            (
                "Cosmic Weaver",
                "Phase 2",
                "Grip-related interaction and virtual object carrying",
            ),
        ],
        "cv_module": (
            "hand_tracking.py, unified_movement_analysis.py"
        ),
        "can_play": True,
    },
    {
        "id": "shoulder_arm",
        "icon": "💪",
        "title": "Shoulder & Elbow",
        "badge": "IN DEVELOPMENT",
        "badge_color": "#C05621",
        "badge_bg": "rgba(192, 86, 33, 0.12)",
        "subtitle": (
            "Proximal upper-limb reach & overhead elevation"
        ),
        "biomechanics": (
            "Shoulder Abduction/Adduction Angle, Elbow Extension "
            "ROM, 3D Hemispheric Reaching Radius"
        ),
        "games": [
            (
                "Sky Reach",
                "Roadmap",
                "Overhead reaching and multi-angle star retrieval",
            ),
            (
                "Arc Painter",
                "Roadmap",
                "Smooth continuous trajectory arc painting",
            ),
        ],
        "cv_module": "shoulder_angle.py, joint_rom.py",
        "can_play": False,
    },
    {
        "id": "knee_lower",
        "icon": "🦵",
        "title": "Knee & Lower Limb",
        "badge": "ROADMAP (PHASE 3)",
        "badge_color": "#2B6CB0",
        "badge_bg": "rgba(43, 108, 176, 0.12)",
        "subtitle": (
            "Lower extremity functional mobility & weight bearing"
        ),
        "biomechanics": (
            "Knee Flexion/Extension Angle, Sit-to-Stand Speed, "
            "Squat Depth & Symmetry"
        ),
        "games": [
            (
                "Step Quest",
                "Roadmap",
                "Rhythmic step cadence and guided knee bend cycles",
            ),
            (
                "Stride Hero",
                "Roadmap",
                "Virtual path traversal and gait pacing",
            ),
        ],
        "cv_module": (
            "knee_angle.py, knee_rom.py, lower_body_tracking.py"
        ),
        "can_play": False,
    },
    {
        "id": "trunk_core",
        "icon": "🧍",
        "title": "Trunk & Postural Stability",
        "badge": "INTEGRATED ANALYSIS",
        "badge_color": "#6B46C1",
        "badge_bg": "rgba(107, 70, 193, 0.12)",
        "subtitle": (
            "Core equilibrium & compensatory movement prevention"
        ),
        "biomechanics": (
            "Torso Lateral Lean Ratio, Compensatory Shoulder Shrug "
            "Detection, Center of Mass Sway"
        ),
        "games": [
            (
                "Posture Guardian",
                "Roadmap",
                "Visual postural alignment boundary feedback",
            ),
            (
                "Balance Horizon",
                "Roadmap",
                "Equilibrium challenge with core stabilization",
            ),
        ],
        "cv_module": (
            "compensatory_movement.py, full_body_tracking.py"
        ),
        "can_play": False,
    },
]


class LimbCard(QFrame):
    play_requested = pyqtSignal(str)

    def __init__(self, data, parent=None):
        super().__init__(parent)

        self.data = data

        self.setObjectName("limbCard")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
        )

        self.setStyleSheet("""
            QFrame#limbCard {
                background-color: rgba(255, 255, 255, 235);
                border-radius: 18px;
                border: 1px solid rgba(133, 103, 232, 35);
            }

            QLabel {
                border: none;
                background: transparent;
            }
        """)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        # Header
        header = QHBoxLayout()
        header.setSpacing(8)

        icon_label = QLabel(self.data["icon"])
        icon_label.setStyleSheet("font-size: 24px;")
        header.addWidget(icon_label)

        title = QLabel(self.data["title"])
        title_font = QFont("Segoe UI", 14)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(
            f"color: {DARK_PURPLE};"
        )
        title.setWordWrap(True)
        header.addWidget(title, 1)

        badge = QLabel(self.data["badge"])
        badge.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        badge.setWordWrap(True)
        badge.setStyleSheet(f"""
            color: {self.data["badge_color"]};
            background-color: {self.data["badge_bg"]};
            border-radius: 8px;
            padding: 5px 8px;
            font-size: 9px;
            font-weight: bold;
        """)
        header.addWidget(badge)

        layout.addLayout(header)

        # Subtitle
        subtitle = QLabel(self.data["subtitle"])
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(f"""
            color: {MUTED_PURPLE};
            font-size: 11px;
        """)
        layout.addWidget(subtitle)

        # Biomechanics
        biomechanics = QLabel(
            "<span style='color: #6B46C1; font-weight: bold;'>"
            "Key Kinematics:</span> "
            + self.data["biomechanics"]
        )
        biomechanics.setWordWrap(True)
        biomechanics.setStyleSheet("""
            color: #4C397A;
            font-size: 10px;
        """)
        layout.addWidget(biomechanics)

        # Exercise list
        games_heading = QLabel(
            "Mapped Rehabilitation Exercises:"
        )
        games_heading.setStyleSheet("""
            color: #382C5E;
            font-size: 11px;
            font-weight: bold;
            margin-top: 4px;
        """)
        layout.addWidget(games_heading)

        for name, status, description in self.data["games"]:
            game_row = QHBoxLayout()
            game_row.setSpacing(7)

            dot = QLabel("●")
            dot_color = (
                "#38A169"
                if status == "Active"
                else "#7E5BE8"
            )
            dot.setStyleSheet(
                f"color: {dot_color}; font-size: 9px;"
            )
            game_row.addWidget(
                dot,
                0,
                Qt.AlignmentFlag.AlignTop,
            )

            game_label = QLabel(
                f"<b>{name}</b> ({status}) — {description}"
            )
            game_label.setWordWrap(True)
            game_label.setStyleSheet("""
                color: #55447A;
                font-size: 10px;
            """)
            game_row.addWidget(game_label, 1)

            layout.addLayout(game_row)

        layout.addStretch()

        # Footer
        footer = QHBoxLayout()
        footer.setSpacing(8)

        cv_label = QLabel(
            f"CV: {self.data['cv_module']}"
        )
        cv_label.setWordWrap(True)
        cv_label.setStyleSheet("""
            color: #8C7EA8;
            font-size: 9px;
            font-style: italic;
        """)
        footer.addWidget(cv_label, 1)

        if self.data["can_play"]:
            play_button = QPushButton(
                "▶ Launch Exercise"
            )
            play_button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )
            play_button.setFixedHeight(34)
            play_button.setStyleSheet("""
                QPushButton {
                    background: #7E5BE8;
                    color: #FFFFFF;
                    border-radius: 8px;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 0 14px;
                    border: none;
                }

                QPushButton:hover {
                    background: #6A48D7;
                }
            """)

            play_button.clicked.connect(
                lambda checked=False:
                self.play_requested.emit(
                    "reach_and_collect"
                )
            )

            footer.addWidget(play_button)

        else:
            roadmap_button = QPushButton(
                "View Roadmap"
            )
            roadmap_button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )
            roadmap_button.setFixedHeight(32)
            roadmap_button.setStyleSheet("""
                QPushButton {
                    background: rgba(126, 91, 232, 20);
                    color: #6546C9;
                    border-radius: 8px;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 0 12px;
                    border: 1px solid rgba(126, 91, 232, 40);
                }

                QPushButton:hover {
                    background: rgba(126, 91, 232, 35);
                }
            """)

            roadmap_button.clicked.connect(
                self._show_info
            )
            footer.addWidget(roadmap_button)

        layout.addLayout(footer)

    def _show_info(self):
        """Show roadmap details for this anatomical category."""
        data = self.data

        message = QMessageBox(self)
        message.setWindowTitle(
            f"{data['title']} Rehabilitation Roadmap"
        )
        message.setIcon(
            QMessageBox.Icon.Information
        )

        games_html = "".join(
            f"<li><b>{name}</b> ({status}): "
            f"{description}</li>"
            for name, status, description in data["games"]
        )

        message.setText(
            f"<h3>{data['icon']} {data['title']} Roadmap</h3>"
            f"<p><b>Clinical objective:</b> "
            f"{data['subtitle']}</p>"
            f"<p><b>Related CV modules:</b><br>"
            f"<code>{data['cv_module']}</code></p>"
            f"<p><b>Mapped exercises:</b></p>"
            f"<ul>{games_html}</ul>"
            "<p><i>These exercises are planned and may require "
            "future game-engine integration.</i></p>"
        )

        message.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
            }

            QLabel {
                color: #2F2154;
                font-size: 12px;
                min-width: 360px;
            }

            QPushButton {
                background-color: #7E5BE8;
                color: white;
                border-radius: 8px;
                padding: 6px 16px;
                font-weight: bold;
            }
        """)

        message.exec()


class BodyPartsView(QWidget):
    exercise_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(12)

        # Header
        header = QVBoxLayout()
        header.setSpacing(3)

        title = QLabel(
            "Target Limbs & Rehabilitation Matrix"
        )
        title_font = QFont("Segoe UI", 18)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(
            f"color: {DARK_PURPLE}; background: transparent;"
        )
        title.setWordWrap(True)
        header.addWidget(title)

        subtitle = QLabel(
            "Explore anatomical regions, associated movement "
            "metrics, active exercises, and planned rehabilitation games."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(f"""
            color: {MUTED_PURPLE};
            font-size: 11px;
            background: transparent;
        """)
        header.addWidget(subtitle)

        main_layout.addLayout(header)

        # Scrollable card grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet(
            "background: transparent;"
        )

        grid = QGridLayout(scroll_content)
        grid.setSpacing(14)
        grid.setContentsMargins(0, 4, 10, 10)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        for index, item in enumerate(LIMB_DATA):
            card = LimbCard(item, scroll_content)

            card.play_requested.connect(
                self.exercise_selected.emit
            )

            row, column = divmod(index, 2)
            grid.addWidget(card, row, column)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)
