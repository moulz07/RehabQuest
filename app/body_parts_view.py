"""
Target Limbs & Body Parts View for RehabQuest
---------------------------------------------
Comprehensive anatomical rehabilitation matrix displaying target limbs,
clinical biomechanics, active exercises, and planned game roadmaps.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QLinearGradient

LIMB_DATA = [
    {
        "id": "wrist_hand",
        "icon": "\U0001F590\ufe0f",
        "title": "Wrist & Hand",
        "badge": "1 ACTIVE \u2022 2 IN DEV",
        "badge_color": "#2E7D32",
        "badge_bg": "rgba(46, 125, 50, 0.12)",
        "subtitle": "Distal upper-limb motor rehabilitation & dexterity",
        "biomechanics": "Wrist Flexion/Extension ROM, Target Trajectory Accuracy, Movement Smoothness, Pinch Grip Hold",
        "games": [
            ("Reach & Collect", "Active", "3D spatial target reach with markerless tracking"),
            ("Bloom Forest", "Phase 2", "Guided wrist flexion/extension reps & steady hold"),
            ("Cosmic Weaver", "Phase 2", "Active grip strength verification & carry loop"),
        ],
        "cv_module": "hand_tracking.py, unified_movement_analysis.py",
        "can_play": True,
    },
    {
        "id": "shoulder_arm",
        "icon": "\U0001F4AA",
        "title": "Shoulder & Elbow",
        "badge": "IN DEVELOPMENT",
        "badge_color": "#C05621",
        "badge_bg": "rgba(192, 86, 33, 0.12)",
        "subtitle": "Proximal upper-limb reach & overhead elevation",
        "biomechanics": "Shoulder Abduction/Adduction Angle, Elbow Extension ROM, 3D Hemispheric Reaching Radius",
        "games": [
            ("Sky Reach", "Roadmap", "Overhead reaching & multi-angle star retrieval"),
            ("Arc Painter", "Roadmap", "Smooth continuous trajectory arc painting"),
        ],
        "cv_module": "shoulder_angle.py, joint_rom.py",
        "can_play": False,
    },
    {
        "id": "knee_lower",
        "icon": "\U0001F9B5",
        "title": "Knee & Lower Limb",
        "badge": "ROADMAP (PHASE 3)",
        "badge_color": "#2B6CB0",
        "badge_bg": "rgba(43, 108, 176, 0.12)",
        "subtitle": "Lower extremity functional mobility & weight bearing",
        "biomechanics": "Knee Flexion/Extension Angle, Sit-to-Stand Speed, Squat Depth & Symmetry",
        "games": [
            ("Step Quest", "Roadmap", "Rhythmic step cadence & guided knee bend cycles"),
            ("Stride Hero", "Roadmap", "Virtual path traversal & gait pacing"),
        ],
        "cv_module": "knee_angle.py, knee_rom.py, lower_body_tracking.py",
        "can_play": False,
    },
    {
        "id": "trunk_core",
        "icon": "\U0001F9CD",
        "title": "Trunk & Postural Stability",
        "badge": "INTEGRATED ANALYSIS",
        "badge_color": "#6B46C1",
        "badge_bg": "rgba(107, 70, 193, 0.12)",
        "subtitle": "Core equilibrium & compensatory movement prevention",
        "biomechanics": "Torso Lateral Lean Ratio, Compensatory Shoulder Shrug Detection, Center of Mass Sway",
        "games": [
            ("Posture Guardian", "Roadmap", "Visual postural alignment boundary feedback"),
            ("Balance Horizon", "Roadmap", "Equilibrium board challenge with core stabilization"),
        ],
        "cv_module": "compensatory_movement.py, full_body_tracking.py",
        "can_play": False,
    },
]


class LimbCard(QFrame):
    play_requested = pyqtSignal(str)

    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data
        self.setObjectName("limbCard")
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

        # Header Row
        hdr = QHBoxLayout()
        icon_lbl = QLabel(self.data["icon"])
        icon_lbl.setStyleSheet("font-size: 24px; background: transparent; border: none;")
        hdr.addWidget(icon_lbl)

        title = QLabel(self.data["title"])
        t_font = QFont("Segoe UI", 14)
        t_font.setWeight(QFont.Weight.Bold)
        title.setFont(t_font)
        title.setStyleSheet("color: #2F2154; background: transparent; border: none;")
        hdr.addWidget(title)
        hdr.addStretch()

        badge = QLabel(self.data["badge"])
        badge.setStyleSheet(f"""
            QLabel {{
                color: {self.data["badge_color"]};
                background-color: {self.data["badge_bg"]};
                border-radius: 8px;
                padding: 4px 8px;
                font-size: 9px;
                font-weight: bold;
                letter-spacing: 0.5px;
                border: none;
            }}
        """)
        hdr.addWidget(badge)
        layout.addLayout(hdr)

        sub = QLabel(self.data["subtitle"])
        sub.setStyleSheet("color: #7A6C9B; font-size: 11px; background: transparent; border: none;")
        layout.addWidget(sub)

        # Biomechanics text (no bounding box)
        bio_lbl = QLabel(f"<span style='color: #6B46C1; font-weight: bold;'>Key Kinematics:</span> {self.data['biomechanics']}")
        bio_lbl.setStyleSheet("color: #4C397A; font-size: 10px; line-height: 1.4; background: transparent; border: none;")
        bio_lbl.setWordWrap(True)
        layout.addWidget(bio_lbl)

        # Games List
        games_hdr = QLabel("Mapped Rehabilitation Exercises:")
        games_hdr.setStyleSheet("color: #382C5E; font-size: 11px; font-weight: bold; background: transparent; border: none; margin-top: 4px;")
        layout.addWidget(games_hdr)

        for name, status, desc in self.data["games"]:
            g_row = QHBoxLayout()
            g_row.setSpacing(6)
            dot = QLabel("●")
            dot_color = "#38A169" if status == "Active" else "#7E5BE8"
            dot.setStyleSheet(f"color: {dot_color}; font-size: 9px; background: transparent; border: none;")
            g_row.addWidget(dot)

            g_name = QLabel(f"<b>{name}</b> ({status}) \u2014 {desc}")
            g_name.setStyleSheet("color: #55447A; font-size: 10px; background: transparent; border: none;")
            g_name.setWordWrap(True)
            g_row.addWidget(g_name, 1)
            layout.addLayout(g_row)

        layout.addStretch()

        # Action button
        btn_row = QHBoxLayout()
        cv_lbl = QLabel(f"CV: {self.data['cv_module']}")
        cv_lbl.setStyleSheet("color: #8C7EA8; font-size: 9px; font-style: italic; background: transparent; border: none;")
        btn_row.addWidget(cv_lbl)
        btn_row.addStretch()

        if self.data["can_play"]:
            play_btn = QPushButton("\u25b6 Launch Exercise")
            play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            play_btn.setFixedHeight(32)
            play_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7E5BE8, stop:1 #A878E0);
                    color: #FFFFFF;
                    border-radius: 8px;
                    font-size: 11px;
                    font-weight: bold;
                    padding: 0 16px;
                    border: none;
                }
                QPushButton:hover { background: #6A48D7; }
            """)
            play_btn.clicked.connect(lambda: self.play_requested.emit("reach_and_collect"))
            btn_row.addWidget(play_btn)
        else:
            info_btn = QPushButton("View Roadmap")
            info_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            info_btn.setFixedHeight(30)
            info_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(126, 91, 232, 20);
                    color: #6546C9;
                    border-radius: 8px;
                    font-size: 10px;
                    font-weight: bold;
                    padding: 0 12px;
                    border: 1px solid rgba(126, 91, 232, 40);
                }
                QPushButton:hover { background-color: rgba(126, 91, 232, 35); }
            """)
            info_btn.clicked.connect(self._show_info)
            btn_row.addWidget(info_btn)

        layout.addLayout(btn_row)

    def _show_info(self):
        msg = QMessageBox(self)
        msg.setWindowTitle(f"{self.data['title']} Rehabilitation Roadmap")
        games_list_html = "".join([f"<li><b>{g[0]}</b> ({g[1]}): {g[2]}</li>" for g in self.data["games"]])
        msg.setText(
            f"<h3>{self.data['icon']} {self.data['title']} Rehab Architecture</h3>"
            f"<p><b>Clinical Objective:</b> {self.data['subtitle']}</p>"
            f"<p><b>Kinematics Algorithms:</b> <code>{self.data['cv_module']}</code></p>"
            f"<p><b>Planned Exercises:</b></p><ul>{games_list_html}</ul>"
            "<p><i>This anatomical module is scheduled for Phase 2/3 game engine integration.</i></p>"
        )
        msg.setStyleSheet("""
            QMessageBox { background-color: #FFFFFF; }
            QLabel { color: #2F2154; font-size: 12px; }
            QPushButton { background-color: #7E5BE8; color: white; border-radius: 8px; padding: 6px 16px; font-weight: bold; }
        """)
        msg.exec()


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
        hdr = QVBoxLayout()
        hdr.setSpacing(2)
        title = QLabel("Target Limbs & Rehabilitation Matrix")
        t_font = QFont("Segoe UI", 18)
        t_font.setWeight(QFont.Weight.Bold)
        title.setFont(t_font)
        title.setStyleSheet("color: #2F2154; background: transparent;")
        hdr.addWidget(title)

        sub = QLabel("Prescribed anatomical regions and their corresponding gamified motor therapy protocols")
        sub.setStyleSheet("color: #7A6C9B; font-size: 11px; background: transparent;")
        hdr.addWidget(sub)
        main_layout.addLayout(hdr)

        # Scrollable Grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        grid = QGridLayout(scroll_content)
        grid.setSpacing(14)
        grid.setContentsMargins(0, 4, 10, 10)

        for idx, item in enumerate(LIMB_DATA):
            card = LimbCard(item, self)
            card.play_requested.connect(self.exercise_selected.emit)
            row, col = divmod(idx, 2)
            grid.addWidget(card, row, col)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)
