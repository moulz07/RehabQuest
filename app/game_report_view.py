"""
Game Report View
------------------
Clinical rehabilitation report displaying kinematics and biomechanics computed by
cv/unified_movement_analysis.py alongside game session results.
"""

import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from stat_card import make_stat_card
from local_data import get_latest_session_summary, get_game_display_name, import_unity_session


REPORT_SECTIONS = [
    {
        "title": "\U0001FA7A Biomechanics & Clinical Kinematics",
        "cards": [
            ("rom", "\u00b0", 1, "Active ROM", "#7E5BE8"),
            ("accuracy", "%", 1, "Trajectory Accuracy", "#38A169"),
            ("smoothness", "", 3, "Movement Smoothness", "#2B6CB0"),
            ("trajectory_deviation", "", 3, "Path Deviation", "#D69E2E"),
            ("avg_speed", " m/s", 2, "Average Speed", "#7E5BE8"),
            ("compensation_ratio", "", 3, "Compensatory Ratio", "#E53E3E"),
        ],
    },
    {
        "title": "\U0001F3AE Session Performance",
        "cards": [
            ("score", " pts", 0, "Session Score", "#7E5BE8"),
            ("targets_collected", "", 0, "Targets Collected", "#38A169"),
            ("best_streak", "", 0, "Best Target Streak", "#2B6CB0"),
            ("session_duration", "s", 0, "Session Duration", "#7E5BE8"),
        ],
    },
]


def _fmt(value, suffix="", decimals=1):
    if value is None:
        return "\u2014"
    try:
        return f"{float(value):.{decimals}f}{suffix}"
    except (TypeError, ValueError):
        return f"{value}{suffix}"


class GameReportView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_user_id = "PATIENT_01"
        self._current_game_id = "reach_and_collect"
        self._card_labels = {}
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(12)

        # Header row
        hdr_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title = QLabel("Rehabilitation Clinical Report")
        t_font = QFont("Segoe UI", 18)
        t_font.setWeight(QFont.Weight.Bold)
        title.setFont(t_font)
        title.setStyleSheet("color: #2F2154; background: transparent;")
        title_col.addWidget(title)

        self._subtitle = QLabel("Metrics powered by RehabQuest Unified Kinematics Engine")
        self._subtitle.setStyleSheet("color: #7A6C9B; font-size: 11px; background: transparent;")
        title_col.addWidget(self._subtitle)
        hdr_row.addLayout(title_col)
        hdr_row.addStretch()

        self._game_badge = QLabel("Reach & Collect")
        self._game_badge.setStyleSheet("""
            background-color: rgba(126, 91, 232, 25);
            color: #7E5BE8;
            font-weight: bold;
            font-size: 11px;
            padding: 6px 14px;
            border-radius: 12px;
            border: 1px solid rgba(126, 91, 232, 40);
        """)
        hdr_row.addWidget(self._game_badge)

        self.sync_btn = QPushButton("\u21bb Sync Latest Session")
        self.sync_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sync_btn.setFixedHeight(30)
        self.sync_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7E5BE8, stop:1 #A878E0);
                color: #FFFFFF;
                font-weight: bold;
                font-size: 11px;
                padding: 0 14px;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover { background: #6A48D7; }
        """)
        self.sync_btn.clicked.connect(self._sync_and_reload)
        hdr_row.addWidget(self.sync_btn)

        main_layout.addLayout(hdr_row)


        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(0, 4, 10, 10)
        content_layout.setSpacing(16)

        # Build report sections
        for section in REPORT_SECTIONS:
            sec_title = QLabel(section["title"])
            sec_font = QFont("Segoe UI", 12)
            sec_font.setWeight(QFont.Weight.Bold)
            sec_title.setFont(sec_font)
            sec_title.setStyleSheet("color: #4C397A; background: transparent;")
            content_layout.addWidget(sec_title)

            grid = QGridLayout()
            grid.setSpacing(12)
            for idx, (key, suffix, decimals, label, accent) in enumerate(section["cards"]):
                card, val_lbl = make_stat_card("\u2014", label, accent=accent)
                self._card_labels[key] = (val_lbl, suffix, decimals)
                row, col = divmod(idx, 3)
                grid.addWidget(card, row, col)

            content_layout.addLayout(grid)

        # Clinical Assessment Note
        note_card = QFrame()
        note_card.setObjectName("noteCard")
        note_card.setStyleSheet("""
            QFrame#noteCard {
                background-color: rgba(255, 255, 255, 220);
                border-radius: 16px;
                border-left: 4px solid #7E5BE8;
                padding: 12px;
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)
        note_layout = QVBoxLayout(note_card)
        note_layout.setContentsMargins(16, 12, 16, 12)
        note_hdr = QLabel("Clinical Assessment & Summary")
        note_hdr.setStyleSheet("color: #2F2154; font-weight: bold; font-size: 12px; background: transparent;")
        note_layout.addWidget(note_hdr)

        self._assessment_lbl = QLabel(
            "Session demonstrated progressive improvement in target reach accuracy with reduced tremor "
            "and stabilized shoulder compensation. Patient is advancing toward target active ROM."
        )
        self._assessment_lbl.setStyleSheet("color: #6C5D8C; font-size: 11px; line-height: 1.4; background: transparent;")
        self._assessment_lbl.setWordWrap(True)
        note_layout.addWidget(self._assessment_lbl)
        content_layout.addWidget(note_card)

        content_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

    def load(self, user_id, game_id="reach_and_collect"):
        self._current_user_id = user_id
        self._current_game_id = game_id
        self._game_badge.setText(get_game_display_name(game_id))

        summary = get_latest_session_summary(user_id, game_id)
        if not summary:
            for key, (lbl, suffix, decimals) in self._card_labels.items():
                lbl.setText("\u2014")
            self._assessment_lbl.setText("No recorded sessions for this exercise yet. Complete a session to view kinematics.")
            return

        for key, (lbl, suffix, decimals) in self._card_labels.items():
            val = summary.get(key)
            lbl.setText(_fmt(val, suffix, decimals))

        if summary.get("compensation_status"):
            self._assessment_lbl.setText(
                f"Movement Analysis Summary: {summary.get('compensation_status')}. "
                f"Active ROM reached {summary.get('rom', 0):.1f}\u00b0 with {summary.get('accuracy', 0):.1f}% target precision."
            )

    def _sync_and_reload(self):
        userprofile = Path(os.environ.get("USERPROFILE", ""))
        search_dirs = [
            userprofile / "AppData" / "LocalLow" / "DefaultCompany" / "RehabQuest-Unity" / "RehabQuestSessions",
            Path(__file__).resolve().parent.parent / "RehabQuestSessions",
        ]
        found = []
        for d in search_dirs:
            if d.exists():
                found.extend(list(d.glob("reach_and_collect_session_*.json")))

        if found:
            latest = max(found, key=lambda f: f.stat().st_mtime)
            import_unity_session(str(latest), self._current_user_id)

        self.load(self._current_user_id, self._current_game_id)

