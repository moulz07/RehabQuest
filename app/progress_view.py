"""
Progress View
---------------
Patient recovery trajectory tracking with interactive line charts for Range of Motion (ROM),
accuracy, and movement smoothness across consecutive sessions.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from progress_chart import ProgressChart
from stat_card import make_stat_card
from local_data import (
    get_current_streak, get_best_streak, get_total_sessions,
    get_session_history
)

CHART_CONFIGS = [
    {
        "title": "Active Range of Motion (ROM)",
        "y_max": 90,
        "y_suffix": "\u00b0",
        "series": [
            {"key": "rom", "label": "Active ROM", "color": "#7E5BE8"},
            {"key": "flexion_rom", "label": "Flexion", "color": "#A878E0"},
        ],
    },
    {
        "title": "Movement Trajectory Accuracy",
        "y_max": 100,
        "y_suffix": "%",
        "series": [
            {"key": "accuracy", "label": "Accuracy", "color": "#38A169"},
        ],
    },
]


class ProgressView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_user_id = "PATIENT_01"
        self._charts = []
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(12)

        # Header
        hdr_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title = QLabel("Recovery Progress & Trends")
        t_font = QFont("Segoe UI", 18)
        t_font.setWeight(QFont.Weight.Bold)
        title.setFont(t_font)
        title.setStyleSheet("color: #2F2154; background: transparent;")
        title_col.addWidget(title)

        subtitle = QLabel("Long-term motor recovery curves and kinematics progress")
        subtitle.setStyleSheet("color: #7A6C9B; font-size: 11px; background: transparent;")
        title_col.addWidget(subtitle)
        hdr_row.addLayout(title_col)
        hdr_row.addStretch()
        main_layout.addLayout(hdr_row)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(0, 4, 10, 10)
        content_layout.setSpacing(16)

        # Top Stat Cards
        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        card1, self.lbl_current_streak = make_stat_card("5", "Current Streak", "#7E5BE8")
        card2, self.lbl_best_streak = make_stat_card("5", "Best Streak", "#2B6CB0")
        card3, self.lbl_total_sessions = make_stat_card("5", "Total Sessions", "#38A169")

        stats_row.addWidget(card1)
        stats_row.addWidget(card2)
        stats_row.addWidget(card3)
        content_layout.addLayout(stats_row)

        # Charts Section
        for cfg in CHART_CONFIGS:
            chart_panel = QFrame()
            chart_panel.setObjectName("chartPanel")
            chart_panel.setStyleSheet("""
                QFrame#chartPanel {
                    background-color: rgba(255, 255, 255, 225);
                    border-radius: 18px;
                    border: 1px solid rgba(133, 103, 232, 25);
                }
                QLabel {
                    border: none;
                    background: transparent;
                }
            """)
            c_layout = QVBoxLayout(chart_panel)
            c_layout.setContentsMargins(18, 14, 18, 14)
            c_layout.setSpacing(8)

            c_hdr = QHBoxLayout()
            c_title = QLabel(cfg["title"])
            c_title.setStyleSheet("color: #4C397A; font-weight: bold; font-size: 13px; background: transparent;")
            c_hdr.addWidget(c_title)
            c_hdr.addStretch()

            for s in cfg["series"]:
                legend_lbl = QLabel(f"● {s['label']}")
                legend_lbl.setStyleSheet(f"color: {s['color']}; font-size: 11px; font-weight: bold; background: transparent;")
                c_hdr.addWidget(legend_lbl)

            c_layout.addLayout(c_hdr)

            chart = ProgressChart()
            c_layout.addWidget(chart)
            self._charts.append((chart, cfg))
            content_layout.addWidget(chart_panel)

        content_layout.addStretch()
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

    def refresh_for_user(self, user_id):
        self._current_user_id = user_id
        self.lbl_current_streak.setText(str(get_current_streak(user_id)))
        self.lbl_best_streak.setText(str(get_best_streak(user_id)))
        self.lbl_total_sessions.setText(str(get_total_sessions(user_id)))

        history = get_session_history(user_id, "reach_and_collect")
        for chart, cfg in self._charts:
            chart.load(
                history=history,
                series=cfg["series"],
                y_max=cfg.get("y_max"),
                y_suffix=cfg.get("y_suffix", "")
            )
